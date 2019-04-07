import io
import json
import uuid

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.select import Select
from lib.ConsumeSiteRequester import ConsumeSiteRequester

class ConsumeSite(object):
    FIELDS_TO_IGNORE = ("XX")
    CATEGORY_FIELD = "grupo"
    PERIOD_FIELD = "periodo"
    REGION_FIELD = "CCAA"

    def get_data(self, url = None, input_file = None):
        if url == None and input_file == None:
            print("Needs a Url or an input file")
            exit(1)
        elif url != None:
            combinations_data = self.__generate_combinations(url)

            input_file = "combinations_{0}_{1}".format(url.split("/")[-1], uuid.uuid4().hex)
            with io.open(input_file, 'w', encoding='utf8') as json_file:
                json.dump(combinations_data, json_file, ensure_ascii=False)
            print("Combinations written to file: {0}".format(input_file))

        requester = ConsumeSiteRequester()
        data = requester.process_file(input_file)
        print("The generated data has {0} registries".format(len(data)))
        return data

    def __generate_combinations(self, url):
        options = Options()
        options.add_argument('--headless')
        self.driver = webdriver.Firefox(options=options)
        self.driver.get(url)

        categories = self.__get_categories()
        periods = self.__get_periods()
        regions = self.__get_regions()
        print("There are {0} categories, {1} periods and {2} regions what makes a total of {3} requests".format(len(categories), len(periods), len(regions), len(categories) * len(periods) * len(regions)))
        self.driver.quit()

        combinations_data = {"url": url, "requests": []}
        for category in categories:
            for period in periods:
                for region in regions:
                    combinations_data["requests"].append({"done": False, "category": category, "period": period, "region": region})
        return combinations_data

    def __get_categories(self):
        return self.__get_selector_options(self.CATEGORY_FIELD)

    def __get_periods(self):
        return self.__get_selector_options(self.PERIOD_FIELD)

    def __get_regions(self):
        return self.__get_selector_options(self.REGION_FIELD)

    def __get_selector_options(self, selector_name):
        options = []
        selector = Select(self.driver.find_element_by_name(selector_name))
        for option in selector.options:
            if option.get_attribute("value") in self.FIELDS_TO_IGNORE:
                continue
            options.append(option.text)
        return options
