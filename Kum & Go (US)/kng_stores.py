import csv
from http.client import RemoteDisconnected
import time
import re
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import pandas as pd


def get_browser(headless=False):
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(
        executable_path="C:\\Aptana Workspace\\chromedriver.exe", options=chrome_options
    )
    return driver


def main():
    us_postal_codes_df = pd.read_csv("us_postal_codes.csv")
    us_postal_codes_df = us_postal_codes_df.loc[~us_postal_codes_df["Zip Code"].isnull()]

    # According to Wikipedia - https://en.wikipedia.org/wiki/Kum_%26_Go
    kng_states = [
        "Missouri",
        "Kansas",
        "Arkansas",
        "Oklahoma",
        "Nebraska",
        "North Dakota",
        "South Dakota",
        "Minnesota",
        "Montana",
        "Colorado",
        "Wyoming",
        "Iowa",
    ]

    # Filtering state = 'Wyoming' as it has the least number of regions
    kng_states = kng_states[-2:-1]

    us_postal_codes_df = us_postal_codes_df.loc[us_postal_codes_df["State"].isin(kng_states)]
    us_postal_codes_df["searchable_place"] = (
        us_postal_codes_df["Place Name"] + ", " + us_postal_codes_df["State"]
    )
    all_regions = us_postal_codes_df["searchable_place"].unique().tolist()
    length_of_all_regions = len(all_regions)

    driver = get_browser(headless=True)

    store_sets = set()
    with open("kng_stores.csv", "w", encoding="utf8") as csv_file:
        csv_writer = csv.writer(csv_file, lineterminator="\n")
        csv_writer.writerow(
            [
                "Store Number",
                "Store Name",
                "Address",
                "Latitude",
                "Longitude",
                "Fresh Pizza",
                "F'Real",
                "E85",
                "Fresh Food",
                "Diesel",
                "Wi-Fi",
                "Seating",
                "Open 24hrs",
                "Redbox",
                "eBlend",
                "ATM",
                "Pay at the Pump",
            ]
        )

        for idx, region in enumerate(all_regions):
            region = region.replace(" ", "+").replace(",", "%2C")
            page_url = f"https://www.kumandgo.com/find-a-store/?addressline={region}"
            print(f"Processing url {idx+1} of {length_of_all_regions} - {page_url}...")

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
                ec.presence_of_element_located((By.CLASS_NAME, "search-results"))
            )

            soup = BeautifulSoup(driver.page_source, "html.parser")
            result_items = soup.find_all("div", attrs={"class": "block block--search-result"})

            for item in result_items:
                store_num = item["data-store-id"]
                if store_num in store_sets:
                    continue
                store_sets.add(store_num)

                title = item["data-title"]

                latitude, longitude = item["data-latitude"], item["data-longitude"]

                address_tag = item.find("div", attrs={"class": "block__address"})
                address = re.sub(r"\s+", " ", address_tag.text.strip().replace("\n", ""))

                tmp = item.find("div", attrs={"class": "block__iconset"}).find_all(
                    "span", attrs={"class": "fs-tooltip-element"}
                )
                fr_pizza, f_r, e85, fr_food, dsl, wf, stng, o24, rbx, eblnd, atm, pp = [
                    "0" for _ in range(12)
                ]
                for icon in tmp:
                    if icon["data-title"] == "Fresh Pizza":
                        fr_pizza = "1"

                    if icon["data-title"] == "F'Real":
                        f_r = "1"

                    if icon["data-title"] == "E85":
                        e85 = "1"

                    if icon["data-title"] == "Fresh Food":
                        fr_food = "1"

                    if icon["data-title"] == "Diesel":
                        dsl = "1"

                    if icon["data-title"] == "Wi-Fi":
                        wf = "1"

                    if icon["data-title"] == "Seating":
                        stng = "1"

                    if icon["data-title"] == "Open 24hrs":
                        o24 = "1"

                    if icon["data-title"] == "Redbox":
                        rbx = "1"

                    if icon["data-title"] == "eBlend":
                        eblnd = "1"

                    if icon["data-title"] == "ATM":
                        atm = "1"

                    if icon["data-title"] == "Pay at the Pump":
                        pp = "1"

                csv_writer.writerow(
                    [
                        store_num,
                        title,
                        address,
                        latitude,
                        longitude,
                        fr_pizza,
                        f_r,
                        e85,
                        fr_food,
                        dsl,
                        wf,
                        stng,
                        o24,
                        rbx,
                        eblnd,
                        atm,
                        pp,
                    ]
                )
                print(f"\t{store_num}, {title}, {address}, ({latitude}, {longitude})")
                time.sleep(1)

            time.sleep(4)

    driver.quit()
    print("DONE!!!")


if __name__ == "__main__":
    main()
