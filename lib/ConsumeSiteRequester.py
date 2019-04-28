import time
import json
import io
import uuid

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, UnexpectedTagNameException

class ConsumeSiteRequester(object):
    CATEGORY_FIELD = "grupo"
    PERIOD_FIELD = "periodo"
    REGION_FIELD = "CCAA"
    TABLE_XPATH = "/html/body/div/div/div[1]/div[2]/div/div[2]/div/div[13]/div/table[2]/tbody"

    m = {
        'Enero': 1,
        'Febrero': 2,
        'Marzo': 3,
        'Abril': 4,
        'Mayo': 5,
        'Junio': 6,
        'Julio': 7,
        'Agosto': 8,
        'Septiembre': 9,
        'Octubre': 10,
        'Noviembre': 11,
        'Diciembre': 12,
        }
    def __init__(self):
        self.driver = None

    def __del__(self):
        self.driver.quit()

    def process_file(self, input_file, output_file):
        with open(input_file, 'r') as json_file:
            combinations = json.load(json_file)
        print("Number of requests to do: {0}".format(len(combinations["requests"])))
        self.__request_combinations(combinations, output_file)

    def __request_combinations(self, combinations, output_file):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.get(combinations["url"])

        pending_combinations = combinations["requests"]
        f = open(output_file, 'w')
        while len(pending_combinations) > 0:

            start_request_time = time.time()
            failed_combinations = []
            for combination in pending_combinations:
                duration_time = time.time() - start_request_time
                print("Have pass {0} sends since previous request".format(duration_time))
                # If previous request took too much time
                if (duration_time) > 15:
                    print("Restarting the driver")
                    self.driver.close()
                    self.driver = webdriver.Firefox(options=options)

                start_request_time = time.time()
                try:
                    self.driver.get(combinations["url"])
                    print("Options to request: \n Category: {0}\n Period: {1}\n Region: {2}".format(combination["category"], combination["period"], combination["region"]))
                    data = self.__request_data(combination["category"], combination["period"], combination["region"])
                    f.write(str(json.dumps(data, ensure_ascii=False)))
                    f.write("\n")
                    combination["done"] = True
                except Exception as err:
                    print("Error: {0}".format(err))
                    print("Failed to request: \n Category: {0}\n Period: {1}\n Region: {2}".format(combination["category"], combination["period"], combination["region"]))
                    failed_combinations.append(combination)
                    time.sleep(10) # Wait some second, in case it is a network problem
            print("Failed combinations: {0}".format(failed_combinations))
            pending_combinations = failed_combinations
        f.close()

    def __request_data(self, category, period, region):
        data = []
        self.__select_options({self.CATEGORY_FIELD: category, self.PERIOD_FIELD: period, self.REGION_FIELD: region})
        if "/" in period: 
            month = period.split("/")[0]
            year = int(period.split("/")[1])
        else:
            month = period.split(" - ")[1]
            year = int(period.split(" - ")[0])
        aditional_data = \
            {"Categoría": category,
             "Mes": self.m[month],
             "Año": year,
             "Región": region,}
        self.driver.find_element_by_name("boton1").click()
        data_table = WebDriverWait(self.driver, 10).until(
          EC.presence_of_element_located((By.XPATH, self.TABLE_XPATH))
        )
        data_table = self.driver.find_element_by_xpath(self.TABLE_XPATH)
        parsed_data = self.__parse_data(data_table)
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
        
