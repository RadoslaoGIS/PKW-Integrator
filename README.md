# Wtyczka QGIS – PKW Integrator

🧩 Wtyczka QGIS do integracji arkuszy danych wyborczych Państwowej Komisji Wyborczej z mapami granic z Państwowego Rejestru Granic (PRG).

---

## 📁 Struktura plików

```plaintext
pkw_integrator/
├── __pycache__/
│   ├── __init__.cpython-312.pyc
│   ├── plugin.cpython-312.pyc
│   └── ui_main.cpython-312.pyc
├── prg_shapefiles/              # Źródło: Państwowy Rejestr Granic (PRG)
│   ├── A01_Granice_wojewodztw.shp
│   ├── A02_Granice_powiatow.shp
│   └── A03_Granice_gmin.shp
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

1. Pobierz arkusz danych (CSV) dla województw, powiatów lub gmin ze strony **Państwowej Komisji Wyborczej**.
2. Wskaż lokalizację pobranego pliku w oknie wtyczki.
3. Wtyczka automatycznie:
   - Rozpozna stopień podziału administracyjnego,
   - Zintegruje dane z odpowiednią warstwą shapefile,
   - Wygeneruje nową warstwę z połączonymi informacjami.

---

## 📝 Uwagi

- ✅ Wtyczka zgodna z **Qt6**.
- 🧪 Testowana w wersji **QGIS 3.44.1 'Solothurn'**.
- 📅 Kompatybilna z arkuszami danych z **wyborów od 2023 roku**.
- 🔄 W przypadku starszych danych (przed 2023 r.), wymagane jest dostosowanie kodów **TERYT** do nowego formatu.
- 🧮 Po integracji dostępne będą **tylko dane liczbowe** z arkusza.
- 📊 Dalsze analizy (np. obliczenia procentowe kandydatów) należy wykonać samodzielnie — np. za pomocą **Pythona** lub **Kalkulatora pól** w QGIS.

---

**Autor:** [RadoslaoGIS](https://github.com/RadoslaoGIS)  
📌 Repozytorium: [PKW-Integrator](https://github.com/RadoslaoGIS/PKW-Integrator)
