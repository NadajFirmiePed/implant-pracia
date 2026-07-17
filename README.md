# Implant prącia — strona (dr Anna Bonder-Nowicka)

Statyczny serwis marketingowy o implantach prącia. Zero zależności, czysty HTML/CSS/JS
generowany prostym skryptem Pythona z fragmentów.

## Jak uruchomić (podgląd na żywo pod localhost)

```bash
# 1. zbuduj strony do ./dist
python3 build.py

# 2. odpal lokalny serwer w folderze z wynikiem
cd dist
python3 -m http.server 3000
```

Otwórz w przeglądarce: **http://localhost:3000/**
Pojedynczy plik (cały serwis w jednym HTML): **http://localhost:3000/implant-pracia-JEDEN-PLIK.html**

Po każdej zmianie: `python3 build.py` w katalogu głównym, potem odśwież przeglądarkę (Shift+Cmd+R).
Serwer z kroku 2 może działać cały czas — wystarczy przebudować i odświeżyć.

## Edycja treści wprost na stronie (tryb „Edytuj")

Zamiast klepać w kodzie — możesz zmieniać teksty klikając w nie na stronie.

```bash
# w folderze implant (jedna komenda):
python3 edit-server.py
```

Otwórz **http://localhost:8000/** → w prawym dolnym rogu przycisk **„Edytuj treść"**.
Klikasz, zmieniasz tekst wprost na stronie, klikasz **„Zapisz"**. Zmiana zapisuje się
na stałe do plików źródłowych we `frag/`, strona automatycznie się przebudowuje i
przeładowuje. `Ctrl+C` w terminalu kończy pracę serwera.

Co można edytować: akapity, nagłówki, leady, punkty list, cytaty, komórki tabel.
Czego (na razie) nie: FAQ i bloki z ikonami/figurami SVG (są generowane) — te zmieniamy
w kodzie. Jeśli po „Zapisz" pojawi się „nie udało się", to znaczy że dany fragment jest
generowany albo powtarza się w pliku — zgłoś go, poprawię ręcznie.

## (Opcjonalnie) publiczny link — deploy

Masz konto Netlify. Z terminala:

```bash
# jednorazowo: npm i -g netlify-cli && netlify login
netlify deploy --dir=dist --prod
```

albo Vercel:

```bash
npm i -g vercel && vercel deploy dist --prod
```

## Struktura

```
build.py        # generator — składa strony z frag/ + style.css, wynik do dist/
style.css       # cały system wizualny (design system)
frag/           # treść każdej podstrony (fragmenty HTML)
  index.html, rodzaje-implantow.html, implant-hydrauliczny.html,
  implant-polsztywny.html, przebieg-leczenia.html, zycie-z-implantem.html,
  o-lekarce.html, fakty-i-mity.html, kontakt.html, warianty-animacji.html
dist/           # WYNIK builda (to serwujesz / to deployujesz)
```

W `build.py` na górze są m.in.: tokeny rozmiarów etykiet figur (LAB_MAIN_FS itd.),
definicje figur SVG (FIG_AE = animowany przekrój w hero), lista FAQ (jedno źródło dla
HTML i JSON-LD), lista PAGES (metadane stron) i NAV (nawigacja). Skrypt generuje też
`dist/implant-pracia-JEDEN-PLIK.html` — cały serwis w jednym pliku (nawigacja przez #hash).

## Design system (skrót)

- Klimat: „dokumentacja medyczna / rysunek patentowy".
- Kolory: paper #F1F2ED, ink #0F211E, petrol #175C54 / #0E413B, ochre #A97B22.
- Fonty (Google): STIX Two Text (nagłówki), Schibsted Grotesk (tekst), Spline Sans Mono (adnotacje).
- Sygnatura: animowane figury SVG „patentowe" + papier milimetrowy + mono-eyebrows + hairlines.

## Ton treści

Ciepły, bezpośredni — lekarka mówi do pacjenta jak w gabinecie. Bez copywriterskich ozdobników.
Fakty medyczne trzymać dokładnie takie, jak są (nie zmyślać liczb, cen, statystyk).
Cennik zawsze „wycena na konsultacji", bez konkretnych kwot.

## Do zrobienia przed wdrożeniem (TODO)

- Podmienić hotlinkowane zdjęcia (portret na index/o-lekarce) na własny hosting.
- Podpiąć formularz kontaktowy (teraz tryb mailto — patrz JS w build.py) pod prawdziwy endpoint.
- Uzupełnić domenę w canonical/OG (placeholder `TWOJA-DOMENA.pl` w `head()` w build.py).
- Ewentualnie baner cookie.

## Dane praktyki

Praktyka Lekarska Anna Bonder-Nowicka, Warszawa, NIP 5252152491.
Kontakt: kontakt@turbourolog.pl. Rejestracja: ZnanyLekarz. Strona-matka: turbourolog.pl.
