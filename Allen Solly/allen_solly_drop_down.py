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
    chrome_options.add_argument("--disable-notifications")
    driver = webdriver.Chrome(
        executable_path="C:\\Aptana Workspace\\chromedriver.exe", options=chrome_options
    )
    return driver


def main():
    driver = get_browser()

    page_url = "https://www.allensolly.com/content/store-locators-9"

    try:
        driver.set_page_load_timeout(40)
        driver.get(page_url)
    except TimeoutException:
        raise Exception(f"\t{page_url} - Timed out receiving message from renderer")
    except RemoteDisconnected:
        raise Exception(f"\tError 404: {page_url} not found.")

    WebDriverWait(driver, timeout=40).until(
        EC.presence_of_element_located((By.CLASS_NAME, "as_footer"))
    )

    state_drop_down_element = driver.find_element_by_id("state")
    city_drop_down_element = driver.find_element_by_id("city")

    state_drop_down_element.click()
    soup = BeautifulSoup(driver.page_source, "html.parser")

    state_option_tag = soup.find("select", attrs={"id": "state"}).find_all("option")
    all_options = {k["value"]: list() for k in state_option_tag if k["value"] != ""}

    state_drop_down = Select(state_drop_down_element)
    for state_option in all_options.keys():
        state_drop_down.select_by_value(state_option)
        time.sleep(5)
        city_drop_down_element.click()
        soup = BeautifulSoup(driver.page_source, "html.parser")

        city_option_tag = soup.find("select", attrs={"id": "city"}).find_all("option")
        for city_option in city_option_tag:
            tmp = city_option["value"]
            if tmp != "":
                all_options[state_option].append(tmp)

        time.sleep(2)

    driver.quit()

    with open("allen_solly_drop_down_values.json", "w") as outfile:
        json.dump(all_options, outfile, indent=4)

    print("DONE!!!")


if __name__ == "__main__":
    main()
