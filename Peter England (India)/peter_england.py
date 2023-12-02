import pickle
import csv
import re
from http.client import RemoteDisconnected
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException


def get_browser():
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(
        executable_path="C:\\Aptana Workspace\\chromedriver.exe", options=chrome_options
    )
    return driver


def main():
    print("Unpickling peter england store url's from file to list object...")
    with open("peter_england_store_urls.pkl", "rb") as pkl_file:
        all_store_urls = pickle.load(pkl_file)

    driver = get_browser()

    with open("peter_england.csv", "w", encoding="utf8") as csv_file:
        csv_writer = csv.writer(csv_file, lineterminator="\n")
        csv_writer.writerow(["Store Number", "Store Name", "Address", "Latitude", "Longitude"])

        for idx, page_url in enumerate(all_store_urls):
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

            WebDriverWait(driver, timeout=40).until(
                ec.presence_of_element_located((By.CLASS_NAME, "footer"))
            )
            soup = BeautifulSoup(driver.page_source, "html.parser")
            addr = soup.find("div", attrs={"class": "row store-address"})

            store_num = re.findall(r"\d+", page_url)[0]
            title_tag = addr.find_all("h3", attrs={"class": "lh-22"})
            title = " ".join([k.text.strip() for k in title_tag]) if title_tag else None

            address_tag = addr.find("p")
            address = address_tag.text.strip() if address_tag else None

            latitude, longitude = "0", "0"
            map_tag = addr.find("span", attrs={"data-toggle": "modal"})
            if map_tag:
                map_tag_text = (
                    map_tag.find("a")["onclick"].replace("initialize(", "").replace(")", "").strip()
                )
                latitude, longitude = map_tag_text.split(",")

            csv_writer.writerow([store_num, title, address, latitude, longitude])
            print(f"\t{store_num}, {title}, {address}, ({latitude}, {longitude})\n")
            time.sleep(6)

    driver.quit()

    print("DONE!!!")


if __name__ == "__main__":
    main()
