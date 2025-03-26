from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
import datetime
from model import Product


def scrape_with_selenium(url):
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)

    try:
        driver.get(url)
        time.sleep(1)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, 'product-card-wrapper'))
        )
        time.sleep(1)

        position = 0
        for i in range(10):
            position += driver.execute_script("return window.innerHeight")
            driver.execute_script(f"window.scrollTo(0,{position})")
            time.sleep(0.1)

        products = driver.find_elements(By.CLASS_NAME, 'product-card-wrapper')
        print(f'products found: {len(products)}')

        with sessionmaker(bind=create_engine('sqlite:///products.db'))() as session:

            for product in products:
                # driver.execute_script(f"window.scrollTo(0,{product.location['y']})")
                name = product.find_element(By.CLASS_NAME, 'product-title__text').text
                price = product.find_element(By.CLASS_NAME, 'price__main-value').text
                item_url = product.find_element(By.CLASS_NAME, 'product-title__text').get_attribute("href")
                # Save to database
                new_product = Product(
                    name=name,
                    price=price,
                    item_url=item_url,
                    datetime=str(datetime.datetime.now())
                )
                session.add(new_product)
            session.commit()

    finally:
        print('done')
        driver.quit()


if __name__ == "__main__":
    target_url = "https://www.mvideo.ru/product-list-page?q=samsung+galaxy"
    scrape_with_selenium(target_url)
