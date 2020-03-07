import json
import csv
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
    print("Unpickling kroger store url's from file to dict object...")
    with open('kroger_store_location_urls.json', 'rb') as file:
        all_store_urls = json.load(file)

    driver = get_browser()
    
    with open('kroger.csv', 'w', encoding='utf8') as csv_file:
        csv_writer = csv.writer(csv_file, lineterminator='\n')
        csv_writer.writerow(['Store Number',
                             'Store Name',
                             'Address'])
        
        for idx, (page_url, store_name) in enumerate(all_store_urls.items()):
            print(f"Processing url {idx+1} of {len(all_store_urls.keys())} - {page_url}...")
            try:
                driver.set_page_load_timeout(40)
                driver.get(page_url)
            except TimeoutException:
                print(f"\t{page_url} - Timed out receiving message from renderer")
                continue
            except RemoteDisconnected:
                print(f"\tError 404: {page_url} not found.")
                continue
    
            WebDriverWait(driver, timeout=40).until(EC.presence_of_element_located((By.CLASS_NAME, "Page-footer-wrapper")))
            soup = BeautifulSoup(driver.page_source, "html.parser")
            addr = soup.find("div", attrs={"class": "StoreAddress-storeAddressGuts"})
            address = addr.text.strip() if addr else None
            
            store_num = page_url.replace("https://www.kroger.com/stores/details/", "").replace("/", "-")
                
            csv_writer.writerow([store_num, store_name, address])
            print(f"\t{store_num}, {store_name}, {address})\n")
            time.sleep(3)

            
    driver.quit()
            
    print("DONE!!!")
    

if __name__ == "__main__":
    main()
