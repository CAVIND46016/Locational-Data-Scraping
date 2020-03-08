import pickle
import csv
import re
import re
import urllib.parse as urlparse
from urllib.parse import parse_qs
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
    print("Unpickling great clips store url's from file to set object...")
    with open('great_clips_store_urls.pkl', 'rb') as pkl_file:
        all_store_urls = pickle.load(pkl_file)

    driver = get_browser()
    
    with open('great_clips.csv', 'w', encoding='utf8') as csv_file:
        csv_writer = csv.writer(csv_file, lineterminator='\n')
        csv_writer.writerow(['Store Number',
                             'Store Name',
                             'Address',
                             'Latitude',
                             'Longitude'])
        
        for idx, page_url in enumerate(all_store_urls):
            can_geocode = True
            print(f"Processing url {idx+1} of {len(all_store_urls)} - {page_url}...")
            try:
                driver.set_page_load_timeout(40)
                driver.get(page_url)
            except TimeoutException:
                print(f"\t{page_url} - Timed out receiving message from renderer")
                continue
            except RemoteDisconnected:
                print(f"\tError 404: {page_url} not found.")
                continue
    
            WebDriverWait(driver, timeout=40).until(EC.presence_of_element_located((By.CLASS_NAME, "salon-details")))
            try:
                WebDriverWait(driver, timeout=80).until(EC.presence_of_element_located((By.CLASS_NAME, "E0MQPE-d-a")))
            except TimeoutException:
                can_geocode = False
                
            soup = BeautifulSoup(driver.page_source, "html.parser")

            store_num = re.findall(r'\d+', page_url)[0]
            title_tag = soup.find("h1", attrs={"class": "salon-title"})
            title = title_tag.find("span", attrs={"itemprop": "name"}).text.strip() if title_tag else None
            
            address_tag = soup.find("div", attrs={"itemprop": "address"})
            address = ' '.join([re.sub(r'\s+', ' ', k.text.strip().replace("\n", "")) for k in address_tag.find_all("div")]) \
                        if address_tag else None
    
            latitude, longitude = '0', '0'
            map_tag = soup.find("div", attrs={"class": "salon-map-container"})
            if map_tag and can_geocode:
                map_url = map_tag.find("img", attrs={"class": "E0MQPE-d-a"})['src']
                parsed = urlparse.urlparse(map_url)
                lat_lon = parse_qs(parsed.query)['center']
                if lat_lon:
                    latitude, longitude  = lat_lon[0].split(',')
                
            csv_writer.writerow([store_num, title, address, latitude, longitude])
            print(f"\t{store_num}, {title}, {address}, ({latitude}, {longitude})\n")
            time.sleep(6)
            
    driver.quit()
            
    print("DONE!!!")
    

if __name__ == "__main__":
    main()
