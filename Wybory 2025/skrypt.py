layer = QgsProject.instance().mapLayersByName("Wybory_gminy")[0]

# Dodanie nowych kolumn z wynikiem procentowym
from qgis.PyQt.QtCore import QVariant

if layer.fields().indexOf('T_%') == -1:
    layer.dataProvider().addAttributes([
        QgsField('T_%', QVariant.Double)
    ])
    layer.updateFields()

if layer.fields().indexOf('N_%') == -1:
    layer.dataProvider().addAttributes([
        QgsField('N_%', QVariant.Double)
    ])
    layer.updateFields()

# Funkcja do zmiany nazwy pola
def rename_field(layer, old_name, new_name):
    fields = layer.fields()
    idx = fields.indexOf(old_name)
    if idx == -1:
        print(f"Pole '{old_name}' nie istnieje.")
        return
    caps = layer.dataProvider().capabilities()
    if caps & QgsVectorDataProvider.ChangeAttributeValues:
        layer.dataProvider().renameAttributes({idx: new_name})
        layer.updateFields()
    else:
        print("Zmiana nazwy kolumny nie jest wspierana przez to źródło danych.")

# Zmiana nazw kolumn
rename_field(layer, 'Liczba głosów ważnych oddanych łącznie na wszystkich kandydatów', 'glosy')
rename_field(layer, 'TRZASKOWSKI Rafał Kazimierz', 'T')
rename_field(layer, 'NAWROCKI Karol Tadeusz', 'N')

# Obliczenie procentowego wyniku
layer.startEditing()
for feature in layer.getFeatures():
    votes = feature['glosy']
    trzaskowski = feature['T']
    if votes and votes > 0:
        result = round((trzaskowski / votes) * 100, 2)
    else:
        result = None
    layer.changeAttributeValue(feature.id(), layer.fields().indexOf('T_%'), result)
layer.commitChanges()

layer.startEditing()
for feature in layer.getFeatures():
    votes = feature['glosy']
    nawrocki = feature['N']
    if votes and votes > 0:
        result = round((nawrocki / votes) * 100, 2)
    else:
        result = None
    layer.changeAttributeValue(feature.id(), layer.fields().indexOf('N_%'), result)
layer.commitChanges()

from qgis.core import QgsVectorLayer, QgsProject, QgsFeature

src_layer = QgsProject.instance().mapLayersByName("Wybory_gminy")[0]

geom_type = src_layer.geometryType()
if geom_type == 0:
    geom_str = "Point"
elif geom_type == 1:
    geom_str = "LineString"
elif geom_type == 2:
    geom_str = "Polygon"
else:
    geom_str = "Unknown"

crs_str = src_layer.crs().authid()

t_layer   = QgsVectorLayer(f"{geom_str}?crs={crs_str}", "Trzaskowski", "memory")
n_layer   = QgsVectorLayer(f"{geom_str}?crs={crs_str}", "Nawrocki", "memory")
r_layer = QgsVectorLayer(f"{geom_str}?crs={crs_str}", "Remis", "memory")

for lyr in [t_layer, n_layer, r_layer]:
    lyr.dataProvider().addAttributes(src_layer.fields())
    lyr.updateFields()

feats_t, feats_n, feats_r = [], [], []

for f in src_layer.getFeatures():
    t = f["T"]
    n = f["N"]

    if t is not None and n is not None:
        if t > n:  # Trzaskowski wygrał
            ft = QgsFeature(t_layer.fields())
            ft.setGeometry(f.geometry())
            ft.setAttributes(f.attributes())
            feats_t.append(ft)
        elif n > t:  # Nawrocki wygrał
            fn = QgsFeature(n_layer.fields())
            fn.setGeometry(f.geometry())
            fn.setAttributes(f.attributes())
            feats_n.append(fn)
        else:  # remis
            fr = QgsFeature(r_layer.fields())
            fr.setGeometry(f.geometry())
            fr.setAttributes(f.attributes())
            feats_r.append(fr)

t_layer.dataProvider().addFeatures(feats_t)
n_layer.dataProvider().addFeatures(feats_n)
r_layer.dataProvider().addFeatures(feats_r)

QgsProject.instance().addMapLayer(t_layer)
QgsProject.instance().addMapLayer(n_layer)
QgsProject.instance().addMapLayer(r_layer)

print(f"Utworzono: Trzaskowski ({len(feats_t)}), Nawrocki ({len(feats_n)}), Remis ({len(feats_r)})")