import os
import csv
import time
from PyQt6.QtGui import QAction
from PyQt6.QtWidgets import QDialog, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from qgis.core import QgsProject, QgsVectorLayer, QgsField, QgsFeature
from qgis.PyQt.QtCore import QVariant
from .ui_main import Ui_Dialog


class Plugin:
    def __init__(self, iface):
        """Inicjalizacja"""
        self.iface = iface
        self.plugin_dir = os.path.dirname(__file__)
        self.dialog = None
        self.action = None

        # Mapowanie województw na kody TERYT
        self.voivodeship_codes = {
            'dolnośląskie': '02',
            'kujawsko-pomorskie': '04',
            'lubelskie': '06',
            'lubuskie': '08',
            'łódzkie': '10',
            'małopolskie': '12',
            'mazowieckie': '14',
            'opolskie': '16',
            'podkarpackie': '18',
            'podlaskie': '20',
            'pomorskie': '22',
            'śląskie': '24',
            'świętokrzyskie': '26',
            'warmińsko-mazurskie': '28',
            'wielkopolskie': '30',
            'zachodniopomorskie': '32'
        }

    def initGui(self):
        """Inicjalizacja interfejsu użytkownika"""
        self.action = QAction("Integrator danych PKW", self.iface.mainWindow())
        self.action.triggered.connect(self.run)
        self.iface.addPluginToMenu("Integrator danych PKW", self.action)
        self.iface.addToolBarIcon(self.action)

    def unload(self):
        """Usuwanie wtyczki"""
        self.iface.removePluginMenu("Integrator danych PKW", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):
        """Uruchomienie głównego okna dialogowego"""
        if not self.dialog:
            self.dialog = Dialog(self)
        self.dialog.show()


class Dialog(QDialog, Ui_Dialog):
    def __init__(self, plugin):
        """Inicjalizacja"""
        super().__init__()
        self.plugin = plugin
        self.setupUi(self)
        self.setWindowTitle("Integrator danych PKW")
        self.csv_file_path = ""

        # Połączenia sygnałów
        self.pushButton.clicked.connect(self.select_csv_file)
        self.pushButton_3.clicked.connect(self.generate)

    def select_csv_file(self):
        """Wybór pliku CSV"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Wybierz plik CSV", "", "CSV files (*.csv)"
        )
        if file_path:
            self.csv_file_path = file_path
            self.lineEdit.setText(file_path)

    def generate(self):
        """Główna funkcja generowania"""
        if not self.csv_file_path:
            QMessageBox.warning(self, "Błąd", "Proszę wybrać plik CSV")
            return

        # Sprawdzenie czy plik jest w formacie CSV
        if not self.csv_file_path.lower().endswith('.csv'):
            QMessageBox.warning(self, "Błąd", "Wybrany plik nie jest w formacie CSV")
            return

        try:
            start_time = time.time()

            # Wczytanie i analiza pliku CSV
            csv_data, headers = self.read_csv_file()
            if not csv_data:
                return

            # Określenie typu jednostki administracyjnej
            unit_type = self.determine_unit_type(headers)
            if not unit_type:
                QMessageBox.warning(self, "Błąd",
                                    "Nie można określić typu jednostki administracyjnej. "
                                    "Plik CSV musi zawierać kolumnę z nazwą 'województwo', 'powiat' lub 'gmina'.")
                return

            # Przygotowanie danych CSV
            csv_data = self.prepare_csv_data(csv_data, headers, unit_type)

            # Wybór odpowiedniego shapefile
            shapefile_path = self.get_shapefile_path(unit_type)
            if not shapefile_path:
                return

            # Integracja danych
            synchronized_count = self.integrate_data(csv_data, shapefile_path, unit_type)

            end_time = time.time()
            duration = round(end_time - start_time, 2)

            QMessageBox.information(self, "Sukces",
                                    f"Pomyślnie zsynchronizowano {synchronized_count} jednostek.\n"
                                    f"Czas operacji: {duration} sekund.")

        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Wystąpił błąd: {str(e)}")

    def read_csv_file(self):
        """Wczytanie pliku CSV"""
        try:
            with open(self.csv_file_path, 'r', encoding='utf-8') as file:
                # Próba automatycznego wykrycia separatora
                sample = file.read(1024)
                file.seek(0)

                sniffer = csv.Sniffer()
                delimiter = ';'  # Domyślny separator dla polskich CSV
                try:
                    delimiter = sniffer.sniff(sample).delimiter
                except:
                    pass

                reader = csv.DictReader(file, delimiter=delimiter)
                headers = reader.fieldnames
                data = list(reader)

                return data, headers
        except Exception as e:
            QMessageBox.critical(self, "Błąd", f"Nie można wczytać pliku CSV: {str(e)}")
            return None, None

    def determine_unit_type(self, headers):
        """Określenie typu jednostki administracyjnej na podstawie nagłówków"""
        headers_lower = [h.lower() for h in headers]

        for header in headers_lower:
            if 'województwo' in header:
                return 'wojewodztwa'
            elif 'powiat' in header:
                return 'powiaty'
            elif 'gmina' in header:
                return 'gminy'
        return None

    def prepare_csv_data(self, csv_data, headers, unit_type):
        """Przygotowanie danych CSV - dodanie kodów TERYT dla województw"""
        # Sprawdzenie czy istnieje kolumna z kodami TERYT
        teryt_column = None
        for header in headers:
            if 'teryt' in header.lower():
                teryt_column = header
                break

        if unit_type == 'wojewodztwa' and not teryt_column:
            # Szukanie kolumny z nazwami województw
            voivodeship_column = None
            for header in headers:
                if 'województwo' in header.lower():
                    voivodeship_column = header
                    break

            if voivodeship_column:
                # Dodanie kolumny z kodami TERYT
                for row in csv_data:
                    voivodeship_name = row[voivodeship_column].lower().strip()
                    teryt_code = self.plugin.voivodeship_codes.get(voivodeship_name, '')
                    row['Kod TERYT'] = teryt_code

        return csv_data

    def get_shapefile_path(self, unit_type):
        """Wybór odpowiedniego pliku shapefile"""
        shapefiles_dir = os.path.join(self.plugin.plugin_dir, 'prg_shapefiles')

        shapefile_map = {
            'wojewodztwa': 'A01_Granice_wojewodztw.shp',
            'powiaty': 'A02_Granice_powiatow.shp',
            'gminy': 'A03_Granice_gmin.shp'
        }

        shapefile_name = shapefile_map.get(unit_type)
        if not shapefile_name:
            QMessageBox.warning(self, "Błąd", f"Nieznany typ jednostki: {unit_type}")
            return None

        shapefile_path = os.path.join(shapefiles_dir, shapefile_name)

        if not os.path.exists(shapefile_path):
            QMessageBox.warning(self, "Błąd",
                                f"Nie znaleziono pliku shapefile: {shapefile_path}")
            return None

        return shapefile_path

    def integrate_data(self, csv_data, shapefile_path, unit_type):
        """Integracja danych CSV z warstwą shapefile"""
        # Wczytanie warstwy shapefile
        layer = QgsVectorLayer(shapefile_path, f"PRG_{unit_type}", "ogr")
        if not layer.isValid():
            raise Exception(f"Nie można wczytać warstwy: {shapefile_path}")

        # Szukanie kolumny z kodami TERYT w CSV
        teryt_column_csv = None
        csv_headers = list(csv_data[0].keys()) if csv_data else []
        for header in csv_headers:
            if 'teryt' in header.lower():
                teryt_column_csv = header
                break

        if not teryt_column_csv:
            raise Exception("Nie znaleziono kolumny z kodami TERYT w pliku CSV")

        # Szukanie kolumny z kodami TERYT w shapefile - różne nazwy dla różnych typów jednostek
        teryt_column_shp = None
        shapefile_fields = [field.name() for field in layer.fields()]
        
        # Definicja możliwych nazw kolumn TERYT dla różnych typów jednostek
        possible_names_by_type = {
            'wojewodztwa': ['Województwo', 'wojewodztwo'],
            'powiaty': ['Kod TERYT', 'teryt'],
            'gminy': ['Kod TERYT', 'teryt']
        }
        
        possible_names = possible_names_by_type.get(unit_type, ['Kod TERYT', 'teryt'])
        
        # Szukanie kolumny TERYT w shapefile
        for field_name in shapefile_fields:
            field_lower = field_name.lower()
            for possible_name in possible_names:
                if possible_name.lower() in field_lower or field_lower in possible_name.lower():
                    teryt_column_shp = field_name
                    break
            if teryt_column_shp:
                break

        # Jeśli nie znaleziono, spróbuj pierwszej kolumny która może zawierać kod
        if not teryt_column_shp:
            for field_name in shapefile_fields:
                # Sprawdź czy pole zawiera kod-podobne wartości
                sample_features = list(layer.getFeatures())[:3]
                if sample_features:
                    sample_value = str(sample_features[0][field_name]).strip()
                    # Dla województw sprawdź czy to 2-cyfrowy kod
                    if unit_type == 'wojewodztwa' and sample_value.isdigit() and len(sample_value) <= 4:
                        teryt_column_shp = field_name
                        break
                    # Dla powiatów i gmin sprawdź czy to kod TERYT
                    elif unit_type in ['powiaty', 'gminy'] and sample_value.isdigit() and len(sample_value) >= 4:
                        teryt_column_shp = field_name
                        break

        if not teryt_column_shp:
            # Pokaż dostępne pola w komunikacie błędu
            fields_info = []
            for field in layer.fields():
                sample_values = []
                for i, feature in enumerate(layer.getFeatures()):
                    if i >= 3:  # Pokaż tylko 3 przykładowe wartości
                        break
                    sample_values.append(str(feature[field.name()]))
                fields_info.append(f"{field.name()}: {', '.join(sample_values)}")
            
            raise Exception(f"Nie znaleziono kolumny z kodami TERYT w warstwie shapefile.\n"
                        f"Dostępne pola z przykładowymi wartościami:\n" + 
                        "\n".join(fields_info))

        # Funkcja do normalizacji kodów TERYT
        def normalize_teryt_code(code, target_unit_type):
            """Normalizacja kodów TERYT do odpowiedniego formatu"""
            code = str(code).strip()
            if not code or not code.isdigit():
                return code
                
            if target_unit_type == 'wojewodztwa':
                # Dla województw - tylko 2 pierwsze cyfry
                return code[:2].zfill(2)
            elif target_unit_type == 'powiaty':
                # Dla powiatów - pierwsze 4 cyfry
                return code[:4].zfill(4)
            elif target_unit_type == 'gminy':
                # Dla gmin - pełny 7-cyfrowy kod
                return code[:7].zfill(7)
            return code

        # Utworzenie słownika z danymi CSV - normalizacja kodów TERYT
        csv_dict = {}
        for row in csv_data:
            teryt_code = row.get(teryt_column_csv, '')
            normalized_code = normalize_teryt_code(teryt_code, unit_type)
            if normalized_code:
                csv_dict[normalized_code] = row

        print(f"Słownik z danymi CSV (pierwsze 10): {list(csv_dict.keys())[:10]}")

        # Sprawdzanie przykładowych kodów TERYT z shapefile
        sample_shp_codes = []
        for feature in layer.getFeatures():
            if len(sample_shp_codes) < 5:
                shp_code = normalize_teryt_code(feature[teryt_column_shp], unit_type)
                sample_shp_codes.append(shp_code)
            else:
                break
        print(f"Kody TERYT: {sample_shp_codes}")

        # Tworzenie nowej warstwy memory
        layer_name = f"Wybory_{unit_type}"

        # Pobieranie wszystkich pól z oryginalnej warstwy
        original_fields = layer.fields()

        # Dodanie nowych pól z CSV (oprócz kolumny TERYT)
        new_fields = []
        excluded_headers = [teryt_column_csv, 'Województwo', 'Powiat', 'Gmina']
        csv_data_headers = [h for h in csv_headers if h.lower() not in [eh.lower() for eh in excluded_headers]]
        
        for header in csv_data_headers:
            # Sprawdzanie czy pole już nie istnieje w oryginalnej warstwie
            field_exists = False
            for orig_field in original_fields:
                if orig_field.name().lower() == header.lower():
                    field_exists = True
                    break
            
            if not field_exists:
                new_fields.append(QgsField(header, QVariant.Int, len=10))

        print(f"Nowe pola: {[f.name() for f in new_fields]}")

        # String z definicją pól dla warstwy memory
        geom_type = layer.geometryType()
        geom_type_names = {0: "Point", 1: "LineString", 2: "Polygon"}
        geom_name = geom_type_names.get(geom_type, "Polygon")

        # Nowa warstwa memory
        memory_layer = QgsVectorLayer(f"{geom_name}?crs={layer.crs().authid()}", layer_name, "memory")
        memory_provider = memory_layer.dataProvider()

        # Wszystkie pola (oryginalne + nowe)
        all_fields = []
        for field in original_fields:
            all_fields.append(field)
        for field in new_fields:
            all_fields.append(field)

        memory_provider.addAttributes(all_fields)
        memory_layer.updateFields()

        # Mapowanie nazw pól na indeksy
        field_name_to_index = {}
        for i, field in enumerate(memory_layer.fields()):
            field_name_to_index[field.name()] = i

        print(f"Mapowanie nazw pól: {field_name_to_index}")

        # Kopiowanie features z oryginalnej warstwy i dodaj dane z CSV
        synchronized_count = 0
        features_to_add = []

        for original_feature in layer.getFeatures():
            new_feature = QgsFeature(memory_layer.fields())

            # Kopiowanie geometrii
            new_feature.setGeometry(original_feature.geometry())

            # Lista atrybutów o odpowiedniej długości
            new_attributes = [None] * len(memory_layer.fields())

            # Kopiowanie oryginalnych atrybutów
            for i, field in enumerate(original_fields):
                if i < len(original_feature.attributes()):
                    new_attributes[i] = original_feature.attributes()[i]

            # Pobieranie kodów TERYT z shapefile i normalizuj
            teryt_code_shp = normalize_teryt_code(original_feature[teryt_column_shp], unit_type)

            print(f"Pobieranie kodu TERYT: {teryt_code_shp}")

            # Jeśli znajdzie pasujący kod TERYT w CSV, wypełnia dane
            if teryt_code_shp in csv_dict:
                csv_row = csv_dict[teryt_code_shp]
                print(f"Znaleziono pasujący wiersz CSV dla TERYT: {teryt_code_shp}")

                # Wypełnienie nowych pól danymi z CSV
                for header in csv_data_headers:
                    if header in field_name_to_index:
                        field_index = field_name_to_index[header]
                        value = str(csv_row.get(header, ''))
                        new_attributes[field_index] = value
                        print(f"  Set {header} = {value} at index {field_index}")

                synchronized_count += 1
            else:
                print(f"Nie znaleziono pasującego wiersza CSV dla TERYT: {teryt_code_shp}")

            new_feature.setAttributes(new_attributes)
            features_to_add.append(new_feature)

        # Dodawanie wszystkich features do warstwy
        memory_provider.addFeatures(features_to_add)
        memory_layer.updateExtents()

        # Dodawanie warstw do projektu
        QgsProject.instance().addMapLayer(memory_layer)

        print(f"Zsynchronizowano: {synchronized_count}")
        return synchronized_count
