# -*- coding: utf-8 -*-
"""
Edytor treści na żywo dla strony „Implant prącia".

Uruchom w folderze implant:
    python3 edit-server.py

Potem otwórz w przeglądarce:
    http://localhost:8000/

Na stronie pojawi się przycisk „Edytuj treść" (prawy dolny róg).
Klikasz, zmieniasz tekst wprost na stronie, klikasz „Zapisz" — zmiana
trafia na stałe do plików źródłowych we frag/ i strona się przebudowuje.
Zatrzymanie serwera: Ctrl+C.
"""
import http.server
import socketserver
import json
import base64
import subprocess
import sys
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, 'dist')
FRAG = os.path.join(ROOT, 'frag')
PORT = 8000


def rebuild():
    try:
        subprocess.run([sys.executable, os.path.join(ROOT, 'build.py')],
                       cwd=ROOT, check=False)
    except Exception as e:
        print('Rebuild error:', e)


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=DIST, **k)

    def log_message(self, *a):
        pass  # cisza w konsoli poza naszymi komunikatami

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        super().end_headers()

    def _json(self, code, obj):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(code)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/__ping':
            return self._json(200, {'ok': True})
        return super().do_GET()

    def do_POST(self):
        if self.path != '/__save':
            self.send_error(404)
            return
        try:
            n = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(n) or b'{}')
        except Exception:
            return self._json(400, {'saved': 0, 'failed': [{'error': 'bad request'}]})

        # grupuj po pliku: 1 odczyt + 1 zapis na plik
        by_file = {}
        for e in data.get('edits', []):
            by_file.setdefault(e.get('file', ''), []).append(e)

        saved = 0
        failed = []
        for fname, edits in by_file.items():
            path = os.path.join(FRAG, os.path.basename(fname))
            try:
                with open(path, encoding='utf-8') as f:
                    src = f.read()
            except OSError:
                failed.extend({'file': fname} for _ in edits)
                continue
            changed = False
            for e in edits:
                try:
                    orig = base64.b64decode(e['eo']).decode('utf-8')
                except Exception:
                    failed.append({'file': fname})
                    continue
                new = e.get('html', '')
                if orig == new:
                    continue  # brak realnej zmiany
                if src.count(orig) == 1:
                    src = src.replace(orig, new, 1)
                    saved += 1
                    changed = True
                else:
                    # 0 lub >1 dopasowań — nie ruszamy, żeby nic nie zepsuć
                    failed.append({'file': fname, 'matches': src.count(orig)})
            if changed:
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(src)

        if saved:
            rebuild()
            print(f'Zapisano {saved} zmian(y)' + (f', pominięto {len(failed)}' if failed else ''))
        return self._json(200, {'saved': saved, 'failed': failed})


def main():
    if not os.path.isdir(DIST):
        print('Brak folderu dist/. Najpierw zbuduj stronę:  python3 build.py')
        rebuild()
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', PORT), Handler) as s:
        print('=' * 52)
        print(f'  Edytor treści: http://localhost:{PORT}/')
        print('  Edytuj na stronie, klikaj Zapisz. Ctrl+C = koniec.')
        print('=' * 52)
        try:
            s.serve_forever()
        except KeyboardInterrupt:
            print('\nZatrzymano.')


if __name__ == '__main__':
    main()
