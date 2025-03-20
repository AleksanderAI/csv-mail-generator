# CSV Mail Generator

Aplikacja do generowania treści maili z plików CSV i otwierania ich w Thunderbird.

## Struktura projektu

```
csv-mail-generator/
├── app.py                  # Główny plik aplikacji
├── templates/             
│   └── index.html         # Interfejs użytkownika
├── requirements-dev.txt    # Zależności dla programistów
├── build.spec             # Konfiguracja PyInstaller
└── README.md              # Ten plik
```

## Dla użytkowników

### Windows
1. Pobierz plik `CSV Mail Generator.exe`
2. Uruchom aplikację dwukrotnym kliknięciem
3. Otwórz przeglądarkę pod adresem http://localhost:5017

### macOS
1. Pobierz plik `CSV Mail Generator.app`
2. Uruchom aplikację dwukrotnym kliknięciem
3. Otwórz przeglądarkę pod adresem http://localhost:5017

## Dla programistów

### Wymagania
- Python 3.8 lub nowszy
- pip (menedżer pakietów Python)

### Instalacja zależności
```bash
pip install -r requirements-dev.txt
```

### Uruchomienie w trybie deweloperskim
```bash
python app.py
```

### Budowanie aplikacji

#### Windows
```bash
pyinstaller build.spec
```
Plik wykonywalny pojawi się w `dist/CSV Mail Generator.exe`

#### macOS
```bash
pyinstaller build.spec
```
Aplikacja pojawi się w `dist/CSV Mail Generator.app`

## Modyfikacja kodu

1. Edytuj pliki źródłowe:
   - `app.py` - logika backendu
   - `templates/index.html` - interfejs użytkownika
2. Testuj zmiany uruchamiając `python app.py`
3. Po zakończeniu zmian, zbuduj nową wersję aplikacji używając PyInstaller
