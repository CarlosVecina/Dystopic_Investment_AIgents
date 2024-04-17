import argparse
import time
from bs4 import BeautifulSoup
import sqlite3
import datetime as dt
from itertools import zip_longest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_driver(use_proxy=False):

    chrome_options = Options()
    chrome_options = webdriver.ChromeOptions()

    if use_proxy:
        driver = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
        driver.get("https://sslproxies.org/")
        driver.execute_script("return arguments[0].scrollIntoView(true);", WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//th[contains(., 'IP Address')]"))))
        ips = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 1]")))]
        ports = [my_elem.get_attribute("innerHTML") for my_elem in WebDriverWait(driver, 5).until(EC.visibility_of_all_elements_located((By.XPATH, "//table[@class='table table-striped table-bordered dataTable']//tbody//tr[@role='row']/td[position() = 2]")))]
        proxies = []
        for i in range(0, len(ips)):
            proxies.append(ips[i]+':'+ports[i])
        chrome_options = webdriver.ChromeOptions()
        i = int(np.random.randint(low=0, high=5, size=(1,)))
        chrome_options.add_argument('--proxy-server={}'.format(proxies[i]))
        chrome_options.add_argument("start-maximized")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

    chrome_options.add_argument("start-maximized")
    service = Service()
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source":
        "const newProto = navigator.__proto__;"
        "delete newProto.webdriver;"
        "navigator.__proto__ = newProto;"
    })

    return driver

def check_key_exits(dict, key):
    if key in dict:
         return dict[key]
    else:
        return None


def mdy_to_ymd(d):
    return dt.datetime.strptime(d, '%b %d, %Y').strftime('%Y-%m-%d')


driver = get_driver()


class DriverConn():
    def __init__(self, driver) -> None:
        self.base_url = "https://crunchbase.com"
        self.organization_url = "/organization/"
        self.driver = driver


class Organization(DriverConn):
    def __init__(self, name_url, *args, **kwargs) -> None:
        super(Organization, self).__init__(*args, **kwargs)
        self.name = name_url
        self.organization_name = ''
        self.url_subdirectory_financials = "/company_financials"
        self.url_subdirectory_people = "/people"

    def get_url(self) -> None:
        self.driver.get(self.base_url + self.organization_url + self.name)

    def get_url_financials(self) -> None:
        self.driver.get(self.base_url + self.organization_url + self.name + self.url_subdirectory_financials)

    def get_url_people(self) -> None:
        self.driver.get(self.base_url + self.organization_url + self.name + self.url_subdirectory_people)

    def get_basic_financials(self) -> dict:
        self.get_url_financials()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        dict_data = dict()
        self.organization_name = soup.find_all(
            'h1', class_="profile-name")[0].text.strip()
        html_link_primary = soup.find_all(
            'a', class_="link-primary")
        [dict_data.update({html_person.text.split("\xa0")[0]: html_person.text.split("\xa0")[1]}) for html_person in html_link_primary]
        return dict_data

    def get_organization_people(self) -> list:
        self.get_url_people()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        self.organization_name = soup.find_all(
            'h1', class_="profile-name")[0].text.strip()
        span_people = soup.find_all(
            'span', class_="ng-star-inserted")
        div_positions = soup.find_all(
            'div', class_="job-title ng-star-inserted")
        list_people = [i.text for i in span_people if '206' in str(i)]
        list_postitions = [i.text for i in div_positions]
        list_people_positions = list(zip(list_people,list_postitions))
        return list_people_positions

    def upload_basic_financials(self) -> None:
        data = self.get_basic_financials()
        con = sqlite3.connect('crunchbase.db')
        cur = con.cursor()
        cur.execute('INSERT OR IGNORE into organizations values (null, ?, ?, ?, ?, ?, ?)',
            [self.organization_name,
            dt.date.today(),
            check_key_exits(data,'Funding Rounds'),
            check_key_exits(data, 'Total Funding Amount'),
            check_key_exits(data, 'Lead Investors'),
            check_key_exits(data, 'Investors')
            ]
        )
        con.commit()

    def upload_people_positions(self) -> None:
        list_people_positions = self.get_organization_people()
        con = sqlite3.connect('crunchbase.db')
        cur = con.cursor()
        for person in list_people_positions:
            cur.execute('INSERT OR IGNORE into organization_people values (null, ?, ?, ?, ?)',
                [person[0],
                dt.date.today(),
                self.organization_name,
                person[1]
                ]
            )
            con.commit()


class InvestmentFirm(DriverConn):
    def __init__(self, name_url, *args, **kwargs) -> None:
        super(InvestmentFirm, self).__init__(*args, **kwargs)
        self.name = name_url
        self.investmente_firm_name = ''
        self.recent_investments = '/recent_investments'

    def get_url(self) -> None:
        self.driver.get(self.base_url + self.organization_url + self.name)

    def get_url_recent_investments(self) -> None:
        self.driver.get(self.base_url + self.organization_url + self.name + self.recent_investments)

    def get_basic_financials(self) -> dict:
        self.get_url_recent_investments()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        dict_data = dict()
        self.investmente_firm_name = soup.find_all(
            'h1', class_="profile-name")[0].text.strip()
        html_link_primary = soup.find_all(
            'a', class_="link-primary")
        [dict_data.update({html_person.text.split("\xa0")[0]: html_person.text.split("\xa0")[1]}) for html_person in html_link_primary]
        return dict_data

    def get_round_investments(self) -> list:
        self.get_url_recent_investments()
        html = self.driver.page_source
        soup = BeautifulSoup(html)
        html_startup_name = soup.find_all(
            'div', class_="identifier-label")
        html_startup_date = soup.find_all(
            'span', class_="component--field-formatter field-type-date ng-star-inserted")
        list_startup_date = [mdy_to_ymd(i.text.strip()) for i in html_startup_date[::2][:10]]
        list_startup_name = [i.text.strip() for i in html_startup_name[::2][:10]]
        list_startup_rounds = [i.text.strip() for i in html_startup_name[1::2][:10]]
        list_rounds = list(zip_longest(list_startup_date, list_startup_rounds, list_startup_name, [self.investmente_firm_name]*len(list_startup_name)))
        return list_rounds

    def upload_investment_firm(self) -> None:
        data = self.get_basic_financials()
        con = sqlite3.connect('crunchbase.db')
        cur = con.cursor()
        cur.execute('INSERT OR IGNORE into investment_firms VALUES (null, ?, ?, ?, ?, ?, ?)',
            [self.investmente_firm_name,
            dt.date.today(),
            check_key_exits(data,'Investments'),
            check_key_exits(data, 'Lead Investments'),
            check_key_exits(data, 'Diversity Investments'),
            check_key_exits(data, 'Exits')
            ]
        )
        con.commit()

    def upload_round_investments(self) -> None:
        data_list_rounds = self.get_round_investments()
        con = sqlite3.connect('crunchbase.db')
        cur = con.cursor()
        for round in data_list_rounds:
            cur.execute('INSERT OR IGNORE into rounds VALUES (null, ?, ?, ?, ?, ?)',
                [round[1],
                round[0],
                dt.date.today(),
                round[2],
                round[3]
                ]
            )
            con.commit()


if __name__ == "__main__":
    parser=argparse.ArgumentParser()

    parser.add_argument("--sec_sleep", help="Do the bar option", default=5)
    parser.add_argument("--is_local", help="Foo the program", default=True)

    args=parser.parse_args()
    

    #_list = ['velca', 'return', 'klarna', 'aplazame', 'malferida', 'onbeams'
    #        'spotify', 'supercell', 'space-exploration-technologies', 'lime', 'internxt',
    #        'onbeams', 'cabify'
    #        ]
    _list = []
    list_organizations = []
    for name in _list:
        try:
            obj = Organization(driver=driver, name_url=name)
            time.sleep(args.time_sleep)
            obj.upload_basic_financials()
            time.sleep(args.time_sleep)
            list_organizations.append(obj)
        except:
            pass

    if args.is_local:
        iff = InvestmentFirm(driver=driver, name_url='dystopic-index-1')
        iff.upload_investment_firm()
        iff.upload_round_investments()