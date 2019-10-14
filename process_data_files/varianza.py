#!/usr/bin/env python3
import pymongo
import math
import csv

db_connection = "mongodb://localhost:27017/"
db_name = "tfm"
collection_name = "test3"

myclient = pymongo.MongoClient(db_connection)
mydb = myclient[db_name]
collection = mydb[collection_name]

class Product(object):
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

    def get_average(self, param, region):
        product_data = list(collection.aggregate([{"$match": {"Producto": self.name, "Región": region}},{"$group": { "_id": {"producto": "$Producto", "region": "$Región"}, "sum": {"$sum": "$" + param}, "count": { "$sum": 1 } }}]))
        if len(product_data) != 1:
            raise Exception("Expected one row getting average of {0} for {1},{2}. And found {3} rows".format(self.name, region, param, len(product_data)))
        #print(product_data)
        return product_data[0]["sum"] / product_data[0]["count"]

    def get_intermonthly_cv(self, param, region):
        average = self.get_average(param, region)
        months_data = list(collection.find({"Producto": self.name, "Región": region},{"_id": 0, param: 1}))
        print(months_data)
        variance = 0
        if average != 0 and average is not None:
            instances = 0
            for row in months_data:
                if row[param] is not None:
                  variance += (row[param] - average) ** 2
                  instances += 1
            variance = variance / instances
            cv = math.sqrt(variance) / average
        else:
            cv = 0
        return cv

    def get_interannual_cv(self, param, region):
        average = self.get_average(param, region)
        years_data = list(collection.aggregate([{"$match": {"Producto": self.name, "Región": region}},{"$group": { "_id": {"producto": "$Producto", "region": "$Región", "year": "$Año"}, "sum": {"$sum": "$" + param}, "count": { "$sum": 1 } }}]))
        variance = 0
        for row in years_data:
            variance += ((row["sum"]/row["count"]) - average) ** 2
        variance = variance / len(years_data)
        if average == 0:
            cv = 0
            print(years_data)
        else:
            cv = math.sqrt(variance) / average
        return cv



class DataManager(object):
    def __init__(self):
        myclient = pymongo.MongoClient(db_connection)
        mydb = myclient[db_name]
        self.collection = mydb[collection_name]

    def get_all_data(self):
        data = {}
        products = self.get_products()
        regions = self.get_regions()
         
        for param in self.get_parameters():
            param_data = []
            for region in regions:
                for product in products:
                    product_data = self.get_data(product, param, region)
                    print(product_data)
                    param_data.append(product_data)
            data[param] = param_data
        return data

    def get_parameters(self):
        return ["Penetración (%)",
                "Consumo per capita",
                "Gasto per capita",]
  #              "Precio medio kg"]

    def get_regions(self):
        regions = []
        for row in self.collection.aggregate([{"$group": {"_id":{"region": "$Región"}}}]):
            regions.append(row['_id']['region'])
        return regions

    def get_products(self):
        products = []
        for row in self.collection.aggregate([{"$group": {"_id":{"product": "$Producto"}}}]):
            products.append(Product(row['_id']['product']))
        return products

    def get_data(self, product, param, region):
        print("Calculating: -" + product.get_name() + "-" + param + "-" + region)
        return [
          product.get_name(),
          param,
          region,
          product.get_average(param, region),
          product.get_intermonthly_cv(param, region),
          product.get_interannual_cv(param, region)]

manager = DataManager()
data = manager.get_all_data()

for key in data.keys():
    with open(key + "_data.txt", 'w') as myfile:
        wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
        for row in data[key]:
            wr.writerow(row)

