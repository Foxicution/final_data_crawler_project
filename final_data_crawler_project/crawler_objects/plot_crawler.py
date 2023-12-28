from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from datetime import datetime
import time
from ..utils.error_handler import text_value_error_handler
from ..utils.converters import convert_to_float
from pandas import DataFrame
from dataclasses import dataclass

@dataclass
class PlotObject:
    """
        Initializes the PlotObject.

        Parameters:
        - address (str): The address of the real estate.
        - url (str): The URL of the real estate listing.
        - price (float): The price of the real estate.
        - area (str): The area of the real estate.
        - purpose (str): The purpose of the real estate (e.g., residential, commercial).
    """
    address:str
    url:str
    price:float
    area:float
    purpose:str
    real_estate_type:str = "Plot"
    created:str = str(datetime.now())

class PlotEstateCrawler:
    BASE_URL = "https://www.aruodas.lt/"
    PLOT_URL = "sklypai/"
    SEARCH_URL = "?search_text="
    def __init__(self, search_text: str, time_limit: int) -> None:
        """
        Initializes the PlotEstateCrawler object.

        Parameters:
        - search_text (str): The region to search for (ex.: Vilnius).
        - time_limit (int): Time limit for crawler to get data.
        """
        checked_text=text_value_error_handler(search_text)
        self.search_text = checked_text
        self.mod_search_text = self.search_text.replace(" ", "%20")
        self.time_limit = int(time_limit)
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)

    def get_search_results(self):
        """
        Scrapes real estate data from the specified search region.

        Returns:
            pandas.DataFrame: A DataFrame containing all collected real estates. Each row in the DataFrame represents real estate,
                      with columns corresponding to the details of the real estate as provided by the aroudas.lt.

        Notes:
            - If the request for the first page fails, an empty DataFrame is returned.
            - If the specified time limit is reached before all pages are fetched, the process is terminated, and data
            collected up to that point is returned.
        """
        url = self.BASE_URL + self.PLOT_URL + self.SEARCH_URL + self.mod_search_text
        self.driver.get(url)
        cookie_element = self.driver.find_element(by="id", value="onetrust-reject-all-handler")
        cookie_element.click()

        objects = []
        start_time = time.time()

        while time.time() - start_time < self.time_limit:
            advert_wrapper = self.driver.find_elements(By.CSS_SELECTOR, ".list-row-v2.object-row")

            if not advert_wrapper:
                return DataFrame()
            
            for element in advert_wrapper:
                address_loc = element.find_element(By.CLASS_NAME, "list-adress-v2 ")
                object_link = address_loc.find_element(By.CSS_SELECTOR, "h3 a")
                object_address = object_link.text.replace("\n", " ")
                object_url = object_link.get_attribute("href")
                object_price = convert_to_float(address_loc.find_element(By.CSS_SELECTOR, "div span.list-item-price-v2").text.replace("€", "").replace(" ", ""))
                object_area = convert_to_float(element.find_element(By.CLASS_NAME, "list-AreaOverall-v2 ").text)
                object_purpose = element.find_element(By.CLASS_NAME, "list-Intendances-v2 ").text

                obj = PlotObject(object_address, object_url, object_price, object_area, object_purpose)
                objects.append(obj.__dict__)

            try:
                next_page_button = self.driver.find_element(By.XPATH, "//div[contains(@class, 'pagination')]/a[text()='»']")
            except NoSuchElementException:
                # If the "Next" button is not found, break out of the loop
                break

            if "disabled" in next_page_button.get_attribute("class"):
                # If the "Next" button is disabled, break out of the loop
                break
            else:
                next_page_button.click()
                time.sleep(2)

        return DataFrame(objects)

    def close_driver(self):
        """Closes the WebDriver."""
        self.driver.close()
