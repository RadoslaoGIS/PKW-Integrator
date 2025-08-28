# [QGIS][Python] Integrator danych PKW

**🧩 Wtyczka QGIS zgodna z Qt6 do integracji arkuszy danych wyborczych Państwowej Komisji Wyborczej z mapami granic z Państwowego Rejestru Granic (PRG)**

---

**Wersja 1.1**
- `ui_main.ui`: Wprowadzono drobne zmiany w UI wtyczki
- `plugin.py`: Ulepszono metodę `prepare_csv_data` w klasie `Dialog`

---

## 📁 Struktura plików

```plaintext
pkw_integrator/
├── __pycache__/
│   ├── __init__.cpython-312.pyc
│   ├── plugin.cpython-312.pyc
│   └── ui_main.cpython-312.pyc
├── prg_shapefiles/              # Źródło: Państwowy Rejestr Granic (PRG)
│   ├── A01_Granice_wojewodztw.dbf
│   ├── A01_Granice_wojewodztw.prj
│   ├── A01_Granice_wojewodztw.shp
│   ├── A01_Granice_wojewodztw.shx
│   ├── A02_Granice_powiatow.dbf
│   ├── A02_Granice_powiatow.prj
│   ├── A02_Granice_powiatow.shp
│   ├── A02_Granice_powiatow.shx
│   ├── A03_Granice_gmin.dbf
│   ├── A03_Granice_gmin.prj
│   ├── A03_Granice_gmin.shp
│   └── A03_Granice_gmin.shx
├── __init__.py                  # Inicjalizacja
├── plugin.py                    # Główna logika wtyczki
├── ui_main.py                   # Interfejs użytkownika (Python)
├── ui_main.ui                   # Interfejs użytkownika (Qt Designer)
└── metadata.txt                 # Metadane wtyczki
```

---

## 🔧 Instalacja

- ⬇️ Pobierz pliki
- 📁 Skopiuj folder **pkw_integrator** do folderu z wtyczkami (domyślnie dla Windowsa: C:\Users\Nazwa_użytkownika\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins)
- 📁 Z folderu skompresowanego **prg_shapefiles.zip** wypakuj folder **prg_shapefiles** i umieść go w folderze wtyczki **pkw_integrator**
- 💻 Uruchom QGIS (lub zamknij i uruchom ponownie, jeśli był już otwarty)
- Przejdź do Wtyczki → 🧩 Zarządzanie wtyczkami...
- Zaznacz ☑️🧩 **Integrator danych PKW**

## ⚙️ Jak używać?

1. ⬇️ Pobierz arkusz danych wyborczych w formacie .csv dla województw, powiatów lub gmin ze strony [Państwowej Komisji Wyborczej](https://pkw.gov.pl)
2. 📁 Wskaż lokalizację pobranego pliku
3. 🧩 Wtyczka automatycznie:
   - ✅ Rozpozna stopień podziału administracyjnego
   - ✅ Zintegruje dane z odpowiednią warstwą shapefile
   - ✅ Wygeneruje nową warstwę z połączonymi danymi

## ⚠️ Uwagi

- ✅ Wtyczka zgodna z **Qt6**
- 🧪 Testowana w wersji **QGIS 3.44.1 'Solothurn'**
- 📅 Kompatybilna z arkuszami danych z wyborów od 2024 roku
- 🔄 W przypadku starszych arkuszy danych może być wymagane ręczne dostosowanie plików CSV do nowych standardów
- 🧮 Po integracji danych dostępne będą tylko dane liczbowe z arkusza
- 📊 Dalsze analizy (np. wyniki procentowe kandydatów lub komitetów) należy wykonać samodzielnie, np. za pomocą Pythona lub Kalkulatora pól w QGIS
- 🗺️ Warstwy shapefile z mapami granic administracyjnych pochodzą z Państwowego Rejestru Granic (PRG), mapa granic gmin zawiera dodatkowo granice dzielnic Warszawy

## Wybory 2025 - przykładowy projekt

Folder "Wybory 2025" zawiera przykładowy projekt wykonany w QGIS wraz z warstwami, prezentujący możliwości wtyczki oraz przykłady dalszych operacji, które można wykonywać za pomocą Pythona po integracji danych:
- Dodawanie i modyfikacja kolumn
- Obliczanie wyników procentowych
- Klasyfikacja danych
- Tworzenie nowych warstw

---

**Autor:** [RadoslaoGIS](https://github.com/RadoslaoGIS), **Repozytorium GitHub:** [PKW-Integrator](https://github.com/RadoslaoGIS/PKW-Integrator)
