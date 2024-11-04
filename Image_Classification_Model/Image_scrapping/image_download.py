from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import requests
import time
import os


def create_folder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


def scroll_down(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)  # Wait for images to load


def fetch_image_urls(search_query, max_images):
    # Set up Chrome options for headless browsing
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize Chrome driver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(f"https://www.google.com/imghp?hl=en")

    # Search for the query in Google Images
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)

    image_urls = set()
    thumbnail_results = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")
    while len(image_urls) < max_images:
        for img in thumbnail_results[len(image_urls):]:
            try:
                img.click()
                time.sleep(1)
                actual_images = driver.find_elements(By.CSS_SELECTOR, "img.n3VNCb")
                for actual_image in actual_images:
                    if actual_image.get_attribute("src") and "http" in actual_image.get_attribute("src"):
                        image_urls.add(actual_image.get_attribute("src"))
                    if len(image_urls) >= max_images:
                        break
            except Exception:
                continue
        scroll_down(driver)
        thumbnail_results = driver.find_elements(By.CSS_SELECTOR, "img.Q4LuWd")

    driver.quit()
    return image_urls


def download_images(image_urls, folder_name):
    create_folder(folder_name)
    for idx, url in enumerate(image_urls):
        try:
            image_data = requests.get(url).content
            with open(os.path.join(folder_name, f"image_{idx+1}.jpg"), 'wb') as img_file:
                img_file.write(image_data)
            print(f"Downloaded {url}")
        except Exception as e:
            print(f"Could not download {url} - {e}")


if __name__ == "__main__":
    query = "puppies"  # Define your search query
    max_images = 10     # Number of images to download
    folder_name = "google_images"

    # Fetch and download images
    print(f"Fetching image URLs for '{query}'...")
    image_urls = fetch_image_urls(query, max_images)
    print(f"Found {len(image_urls)} images, downloading...")
    download_images(image_urls, folder_name)
    print("Download complete.")
