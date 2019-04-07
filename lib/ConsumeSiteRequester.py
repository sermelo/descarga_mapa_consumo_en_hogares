import time
import json
import io
import uuid

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, UnexpectedTagNameException

class ConsumeSiteRequester(object):
    CATEGORY_FIELD = "grupo"
    PERIOD_FIELD = "periodo"
    REGION_FIELD = "CCAA"

    def __init__(self, input_file):
        self.input_file = input_file
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)

    def __del__(self):
        self.driver.quit()

    def process_file(self):
        with open(self.input_file, 'r') as json_file:
            combinations = json.load(json_file)
        print("Number of requests to do: {0}".format(len(combinations["requests"])))
        data = self.__request_combinations(combinations)
        return data

    def __request_combinations(self, combinations):
        self.driver.get(combinations["url"])
        data = []
        pending_combinations = combinations["requests"]
        while len(pending_combinations) > 0:
            failed_combinations = []
            for combination in pending_combinations:
                print("{0} Options to request: \n Category: {1}\n Period: {2}\n Region: {3}".format(time.strftime("%d %H:%M:%S"), combination["category"], combination["period"], combination["region"]))
                try:
                    data.extend(self.__request_data(combination["category"], combination["period"], combination["region"]))
                    combination["done"] = True
                except NoSuchElementException as err:
                    print("NoSuchElementException error: {0}".format(err))
                    print("Failed to request: \n Category: {0}\n Period: {1}\n Region: {2}".format(combination["category"], combination["period"], combination["region"]))
                    failed_combinations.append(combination)
                except ElementClickInterceptedException as err:
                    print("ElementClickInterceptedException error: {0}".format(err))
                    print("Failed to request: \n Category: {0}\n Period: {1}\n Region: {2}".format(combination["category"], combination["period"], combination["region"]))
                    failed_combinations.append(combination)
                except UnexpectedTagNameException  as err:
                    print("UnexpectedTagNameException error: {0}".format(err))
                    print("Failed to request: \n Category: {0}\n Period: {1}\n Region: {2}".format(combination["category"], combination["period"], combination["region"]))
                    failed_combinations.append(combination)
            print("Failed combinations: {0}".format(failed_combinations))
            pending_combinations = failed_combinations

        return data

    def __request_data(self, category, period, region):
        data = []
        self.__select_options({self.CATEGORY_FIELD: category, self.PERIOD_FIELD: period, self.REGION_FIELD: region})
        aditional_data = \
            {"Categoría": category,
             "Mes": period.split("/")[0],
             "Año": period.split("/")[1],
             "Región": region,}
        
        self.driver.find_element_by_name("boton1").click()
        parsed_data = self.__parse_data(self.driver.find_element_by_xpath("/html/body/div/div/div[1]/div[2]/div/div[2]/div/div[13]/div/table[2]/tbody"))
        self.driver.back()
        
        for registry in parsed_data:
            registry.update(aditional_data)
            data.append(registry)
        return data

    def __select_options(self, options):
        for key, value in options.items():
            element = Select(self.driver.find_element_by_name(key))
            element.select_by_visible_text(value)

    def __parse_data(self, element):
        registries = []
        fields = []
        for row in element.find_elements_by_xpath(".//tr"):
            if len(fields) == 0:
                for data in row.find_elements_by_xpath(".//td"):
                    fields.append(data.text)
            else:
                c = 0
                registry = {}
                for data in row.find_elements_by_xpath(".//td"):
                    if c != 0:
                        registry[fields[c]] = self.__numerify(data.text)
                    else:
                        registry[fields[c]] = data.text
                    c += 1
                registries.append(registry)
        return registries

    def __numerify(self, string):
        string = string.replace(".", "")
        string = string.replace(",", ".")
        if string == "":
            return None
        return float(string)
        
