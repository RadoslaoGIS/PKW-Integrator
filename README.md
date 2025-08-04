# PKW-Integrator
Wtyczka QGIS do integracji arkuszy danych wyborczych Państwowej Komisji Wyborczej z mapami granic z Państwowego Rejestru Granic

**Struktura plików:**

pkw_integrator/
├── __pycache__/
  ├── __init__.cpython-312
  ├── plugin.cpython-312
  └── ui_main.cpython-312
├── prg_shapefiles/    # Źródło: Państwowy Rejestr Granic (PRG)
  ├── A01_Granice_wojewodztw.shp
  ├── A02_Granice_powiatow.shp
  └── A03_Granice_gmin.shp
├── __init__.py        # Inicjalizacja
├── plugin.py          # Główna logika wtyczki
├── ui_main.py         # Interfejs użytkownika (Python)
├── ui_main.ui         # Interfejs użytkownika (Qt Designer)
└── metadata.txt       # Metadane

**Jak używać?**
1. Pobierz arkusz danych dla województw, powiatów lub gmin w formacie CSV ze strony Państwowej Komisji Wyborczej
2. Wskaż lokalizację pobranego pliku
3. Wtyczka rozpozna stopień podziału administracyjnego i wygeneruje warstwę shapefile mapy ze zintegrowanymi danymi

**Uwagi**
Wtyczka zgodna z Qt6. Testowana w wersji QGIS 3.44.1 'Solothurn'.
Wtyczka kompatybilna z arkuszami danych z wyborów od 2023 roku. W celu integracji arkuszy danych z wyborów przeprowadzonych przed 2023 rokiem, należy dostosować kody TERYT do nowego formatu.
Po integracji będą dostępne jedynie dane liczbowe zawarte w arkuszu. Dalsze działania, takie jak na przykład wyniki procentowe kandydatów lub komitetów, należy wykonać samodzielnie za pomocą Pythona lub Kalkulatora pól.
