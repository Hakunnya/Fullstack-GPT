from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
import pandas as pd

chromedriver_path = r'F:\ZE221208_works\Fullstack-GPT\chromedriver\chromedriver.exe'

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service)

def scrape_link(product_name):
    driver.get("https://www.google.com")
    search_box = driver.find_element("name", "q")
    search_box.send_keys(product_name)
    search_box.send_keys(Keys.RETURN)
    driver.implicitly_wait(5)
    for a in driver.find_elements("css selector", "div.g > div > div > a"):
        seller_url = a.get_attribute('href')
        if seller_url:
            return seller_url
        else:
            return None

df = pd.read_excel('url_test2.xlsx')
#df["url"] = df['제품명'].apply(scrape_link)

for index, row in df.iterrows():
    product_name = row['제품명']
    product_url = scrape_link(product_name)
    df.at[index, '판매url'] = product_url

df.to_excel('url_test_end2.xlsx')