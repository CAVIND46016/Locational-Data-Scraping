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
import pandas as pd


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(executable_path='C:\\Aptana Workspace\\chromedriver.exe',
                              options=chrome_options)
    return driver


def main():
    us_postal_codes_df = pd.read_csv("us_postal_codes.csv")
    us_postal_codes_df = us_postal_codes_df.loc[~us_postal_codes_df['Zip Code'].isnull()]

    us_postal_codes_df = us_postal_codes_df.loc[(us_postal_codes_df['State'] == 'New York') &
                                                (us_postal_codes_df['County'] == 'New York')]

    all_codes = us_postal_codes_df['Zip Code'].unique().tolist()
    length_of_all_codes = len(all_codes)

    driver = get_browser()

    base_url = "https://www.greatclips.com"
    page_url = "https://www.greatclips.com/#"

    try:
        driver.set_page_load_timeout(40)
        driver.get(page_url)
    except TimeoutException:
        raise Exception(f"\t{page_url} - Timed out receiving message from renderer")
    except RemoteDisconnected:
        raise Exception(f"\tError 404: {page_url} not found.")

    WebDriverWait(driver, timeout=40).until(EC.presence_of_element_located((By.CLASS_NAME, "fas-searchbar")))
    
    srch_bar = driver.find_element_by_id("term")
    srch_btn = driver.find_element_by_class_name("fas-search-btn")
    all_store_urls = set()
    
    for idx, zip_code in enumerate(all_codes):
        print(f"Processing zip code {idx+1} of {length_of_all_codes} - {zip_code}...")
        srch_bar.send_keys(str(zip_code))
        srch_btn.click()
        time.sleep(5)
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results_class = soup.find("div", attrs={"class": "fas-results"})
        salon_titles = results_class.find_all("h2", attrs={"class": "fas-salon-title"})
        
        for salon_title in salon_titles:
            href = salon_title.find("a")['href']
            all_store_urls.add(f"{base_url}{href}")

        srch_bar.clear()
            
    driver.quit()
    
    print(f"Pickling list of {len(all_store_urls)} store_urls to file...")
    with open('great_clips_store_urls.pkl', 'wb') as pkl_file:
        pickle.dump(all_store_urls, pkl_file)
    
    print(all_store_urls)
    print("DONE!!!")
    

if __name__ == "__main__":
    main()
