import pickle
import json
from http.client import RemoteDisconnected
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(executable_path='C:\\Aptana Workspace\\chromedriver.exe',
                              options=chrome_options)
    return driver


def main():
    print("Reading the drop-down values...")
    with open('peter_england_drop_down_values.json', 'r') as file:
        drop_downs = json.load(file)

    driver = get_browser()

    page_url = "https://www.peterengland.com/content/store-locators-9"

    try:
        driver.set_page_load_timeout(40)
        driver.get(page_url)
    except TimeoutException:
        raise Exception(f"\t{page_url} - Timed out receiving message from renderer")
    except RemoteDisconnected:
        raise Exception(f"\tError 404: {page_url} not found.")

    WebDriverWait(driver, timeout=40).until(EC.presence_of_element_located((By.CLASS_NAME, "footer")))
    state_drop_down_element = driver.find_element_by_id('state')
    city_drop_down_element = driver.find_element_by_id('city')
    
    all_store_urls = []
    for key, value in drop_downs.items():
        state_drop_down_element.click()
        state_drop_down = Select(state_drop_down_element)
        state_drop_down.select_by_value(key)
        time.sleep(5)
        
        for val in value:
            city_drop_down_element.click()
            city_drop_down = Select(city_drop_down_element)
            city_drop_down.select_by_value(val)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            driver.find_element_by_id('storeLocBtn').click()
            time.sleep(1)
            loader = soup.find("div", attrs={"class": "bg_overlay"})
            while True:
                if loader['style'] == "display: none;":
                    break
            
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            store_url_tags = soup.find("div", attrs={"id": "store-locator"}).find_all("a")
            all_store_urls.extend([k['href'] for k in store_url_tags])
            
    driver.quit()
    
    print(f"Pickling list of {len(all_store_urls)} store_urls to file...")
    with open('peter_england_store_urls.pkl', 'wb') as pkl_file:
        pickle.dump(all_store_urls, pkl_file)
            
    print("DONE!!!")
    

if __name__ == "__main__":
    main()
