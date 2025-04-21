# Duplicate Finder

**Zastosowanie**: Głównym celem projektu jest optymalizacja wykorzystania pamięci w graficznych bazach danych poprzez analizę podobieństwa cosinusowego wektorów cech obrazów. Umożliwia identyfikację duplikatów (obrazów bardzo do siebie podobnych), co prowadzi do efektywniejszego zarządzania zasobami.

**Program** W chwili obecnej program przeszukuje obrazy w katalogu, do którego ścieżka została zapisana w pliku 'Data\settings.txt'. Program zapisuje w katalogu 'Data' wektory cech obrazów, dlatego wymaga dodatkowej pamięci (~1GB na 100 000 obrazów)

**Użycie**: Program obsługuje się w terminalu. Po piewszym wykonaniu programu, zostaje utworzony katalog Data, w miejscu gdzie zapisany jest program. Aby wybrać ścieżkę do katalogu z obrazami należy w pliku 'settings.txt' zapisać ścieżkę.<br>
Następnie można wykonywać program z: -an, -mnb, -c, -i<br>
-an - Przeszukuje katalog w celu znalezienia nowych obrazów i zapisania ich ścieżek<br>
-mnb - Tworzy serie wektorów cech ze zapisanych ścieżek<br>
-c - Wykonuje sprawdzenie zapisanych serii i kopiuje duplikaty z informacjami do katalogu 'Data\Duplicates'<br>
-i - Wyświetla informacje o programie

**Struktura plików**<br>
.<br>
├── Data/<br>
│   ├── batch/<br>
│   ├── batch_archives/<br>
│   ├── Duplicates/<br>
│   ├── paths/<br>
│   └── settings.txt<br>
└── Duplicate Finder.exe<br>

## Wymagania
- Python 3.8+
- Biblioteki: `numpy`, `Pillow`, `scikit-learn`, `tensorflow`  
  (zainstaluj przez `pip install -r requirements.txt`)

## Link do pobrania pliku exe
https://sourceforge.net/projects/duplicate-finder-nkn/

Wszystkie pytania proszę pisać na b.gabka.nkn@gmail.com