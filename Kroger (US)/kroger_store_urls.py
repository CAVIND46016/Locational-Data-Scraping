import time
import json
import http
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument('--disable-notifications')
    driver = webdriver.Chrome(executable_path='C:\\Aptana Workspace\\chromedriver.exe',
                              options=chrome_options)
    return driver


def scrape():
    driver = get_browser()

    us_postal_codes_df = pd.read_csv("us_postal_codes.csv")
    us_postal_codes_df = us_postal_codes_df.loc[~us_postal_codes_df['Zip Code'].isnull()]

    us_postal_codes_df = us_postal_codes_df.loc[(us_postal_codes_df['State'] == 'Indiana') &
                                                (us_postal_codes_df['County'] == 'Monroe')]

    all_codes = us_postal_codes_df['Zip Code'].unique().tolist()
    length_of_all_codes = len(all_codes)

    store_urls = {}
    base_url = "https://www.kroger.com"

    for idx, zip_code in enumerate(all_codes):
        print(f"Processing {idx+1} of {length_of_all_codes}...\n\tzip_code: {zip_code}")
        page_no = 1
        while True:
            page_url = f"https://www.kroger.com/stores/search?searchText={zip_code}&selectedPage={page_no}"

            try:
                driver.set_page_load_timeout(30)
                driver.get(page_url)
            except http.client.RemoteDisconnected:
                print(f"Error 404: {page_url} not found.")
                continue

            time.sleep(2)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            store_result = soup.find("div", attrs={"class": "SearchResults-storeResultsDetails"})

            store_blocks = store_result.find_all("div", attrs={"class": "VanityNameLinkContainer"})

            if not store_blocks:
                break

            for store_block in store_blocks:
                a_tag = store_block.find("a")
                store_urls[f"{base_url}{a_tag['href']}"] = a_tag.text.strip()

            page_no += 1
            time.sleep(1)

        time.sleep(0.5)

    driver.quit()
    return store_urls


def main():
    outfile_name = 'kroger_store_location_urls.json'

    store_location_urls = scrape()

    print(f"Printing {len(store_location_urls.keys())} key-value pairs to {outfile_name}...")    
    with open(outfile_name, 'w') as outfile:
        json.dump(store_location_urls, outfile, indent=4)

    print("DONE!!!")


if __name__ == "__main__":
    main()
