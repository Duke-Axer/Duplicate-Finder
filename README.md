# Duplicate Finder

**Zastosowanie**: Głównym celem projektu jest optymalizacja wykorzystania pamięci w graficznych bazach danych poprzez analizę podobieństwa cosinusowego wektorów cech obrazów. Umożliwia identyfikację duplikatów (obrazów bardzo do siebie podobnych), co prowadzi do efektywniejszego zarządzania zasobami.

**Program** W chwili obecnej program przeszukuje obrazy w katalogu, do którego ścieżka została zapisana w pliku 'Data\settings.txt'. 

**Użycie**: Program obsługuje się w terminalu. Po piewszym wykonaniu programu, zostaje utworzony katalog Data, w miejscu gdzie zapisany jest program. Aby wybrać ścieżkę do katalogu z obrazami należy w pliku 'settings.txt' zapisać ścieżkę.
Następnie można wykonywać program z: -an, -mnb, -c, -i
-an - Przeszukuje katalog w celu znalezienia nowych obrazów i zapisania ich ścieżek
-mnb - Tworzy serie wektorów cech ze zapisanych ścieżek
-c - Wykonuje sprawdzenie zapisanych serii i kopiuje duplikaty z informacjami do katalogu 'Data\Duplicates'
-i - Wyświetla informacje o programie

**Struktura plików**
.
├── Data/
│   ├── batch/
│   ├── batch_archives/
│   ├── Duplicates/
│   ├── paths/
│   └── settings.txt
└── Duplicate Finder.exe

## Wymagania
- Python 3.8+
- Biblioteki: `numpy`, `Pillow`, `scikit-learn`, `tensorflow`  
  (zainstaluj przez `pip install -r requirements.txt`)