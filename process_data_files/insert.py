#!/usr/bin/python3

import pymongo
import glob, os
import json
import re
mongodb_host = "mongodb://localhost:27017/"
db = "tfm"
collection = "test3"

product_name_replacement = {
    "Aceite de oliva oliva": "Aceite de oliva",
    "Total aceite de oliva": "Aceite de oliva",
    "Agua de bebida con gas": "Agua mineral con gas",
    "Agua de bebida sin gas": "Agua mineral sin gas",
    "Agua de bebida envasada": "Agua mineral",
    "Cocidos y otros corte": "Cocidos y otros al corte",
    "Despojos otr. proced.": "Despojos otra procedencia",
    "Otros productos curados corte": "Otros productos curados al corte",
    "Tocino": "Tocino y manteca",
    "Chocolates/cacaos/sucedaneos": "Chocolates/cacaos/sucedáneos",
    "Fruta en conserva": "Fruta en conserva/almíbar",
    "Fruta y hortalizas congeladas": "Frutas y hortalizas congeladas",
    "Fruta en conserva/almibar": "Fruta en conserva/almíbar",
    "Frutas IV generación": "Frutas IV gama",
    "Bolleria/pastelería envasados": "Bolleria/pastelería envasada",
    "Frutos secos, almendra": "Almendras",
    "Frutos secos, cacahuetes": "Cacahuetes",
    "Frutos secos, nueces": "Nueces",
    "Pistacho": "Pistachos",
    "Avellana": "Avellanas",
    "Huevos kg": "Huevos (kg)",
    "Total huevos gallina (unidades)": "Huevos gallina (unidades)",
    "Total huevos gallina": "Huevos gallina (unidades)" ,
    "Huevos gallina": "Huevos gallina (unidades)",
    "Gallina (unidades)": "Huevos gallina (unidades)",
    "Especias y condemientos": "Especias y condimentos",
    "Mejillón": "Mejillones",
    "Platos preparados, otros": "Platos preparados: otros",
    "Platos preparados, sopas y cremas": "Platos preparados: sopas y cremas",
    "Total frutas y hortalizas transform.": "Total frutas y hortalizas transformadas",
    "Queso fresco bajo sal": "Queso fresco bajo en sal",
    "Bebidas refrescantes. cola": "Bebidas refrescantes cola",
    "Bebidas refrescantes, limón": "Bebidas refrescantes limón",
    "Bebidas refrescantes, naranja": "Bebidas refrescantes naranja",
    "Pminientos": "Pimientos",
    "Total de hortalizas frescas": "Total hortalizas frescas",
    "Verduras y hortalizas IV generación": "Verduras y hortalizas IV gama",
    "Zumos y néctares resto": "Zumo y néctar otros",
    "Zumo fruta refrigerado/exp.": "Zumo refrigerado/exprimido fruta",
    "Zumo conentrado piña y mezclas": "Zumo concentrado piña y mezclas",
}

category_name_replacement = {
    "Bolleria/Pastelería/Galletas/Cereales": "Bollería/Pastelería/Galletas/Cereales",
    "Zumo de frutas": "Zumos",
    "Vinos y bebidas alcohólicas": "Vinos, otras bebidas alcohólicas y vinagres",
}

region_name_replacement = {
    "Castilla León": "Castilla y León",
}

def insert_files_data(directory):
    for file_name in glob.glob("data/*.json".format(directory)):
        print("Procesing {0}".format(file_name))
        insert_file(file_name)

def insert_file(file_name):
    myclient = pymongo.MongoClient(mongodb_host)
    mydb = myclient[db]
    mycol = mydb[collection]

    data_file = open(file_name, "r")
    for line in data_file:
        data = json.loads(line)
        for document in data:
            document = parse_document(document)
            mycol.insert(document)
    data_file.close()

def parse_document(document):
    document["Producto"] = parse_product(document["Producto"])
    document["Categoría"] = parse_category(document["Categoría"])
    document["Región"] = parse_region(document["Región"])
    # The 2004 "Total zumo y néctar" is in the wrong category
    if document["Producto"] == "Total zumo y néctar":
        document["Categoría"] = "Zumos"
    document = transform_units(document)
    return document

def parse_product(product_name):
    new_product_name = re.sub(
           r'\s?/\s?',
           "/",
           product_name)
    if new_product_name in product_name_replacement:
        new_product_name = product_name_replacement[new_product_name]
    return new_product_name

def parse_category(category_name):
    new_category_name = category_name
    if new_category_name in category_name_replacement:
        new_category_name = category_name_replacement[new_category_name]
    return new_category_name

def parse_region(region_name):
    new_region_name = region_name
    if new_region_name in region_name_replacement:
        new_region_name = region_name_replacement[new_region_name]
    return new_region_name

def transform_units(document):
    new_document = {}
    columns_without_changes = ["Producto", "Categoría", "Mes", "Año", "Región", "Penetración (%)", "Consumo per capita", "Gasto per capita"]
    for field in columns_without_changes:
        new_document[field] = document[field]

    new_document["Valor"] = document["Valor (miles de €)"] * 1000
    if "unidades" in document["Producto"]:
        new_document["Unidades"] = document["Volumen (miles de kg)"] * 1000
        new_document["Precio medio unidad"] = document["Precio medio kg"]
    else:
        new_document["Masa"] = document["Volumen (miles de kg)"] * 1000
        new_document["Precio medio kg"] = document["Precio medio kg"]
    return new_document

insert_files_data("data")
