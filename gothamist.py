import logging
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
SEARCH_BOX_XPATH = "//*[@id='search']/input"
FIRST_RESULT_XPATH = "//*[@id='resultList']/div[2]/div[1]/div/div[2]/div[1]/a/div"
DESCRIPTION_XPATH = "//*[@id='resultList']/div[2]/div[1]/div/div[2]/div[2]/p"
TITLE_XPATH = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[1]/div[2]/h1"
DATE_XPATH = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]/p"
IMAGE_XPATH = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/figure/div/div/div/div/img"
GOTHAMIST_URL = "https://gothamist.com/"

def open_gothamist():
    # Open Gothamist website in a Chrome browser.
    try:
       # Set the path to chromedriver.exe in the project root directory
        chrome_driver_path = os.path.join(os.getcwd(), "chromedriver.exe")
        
        # Configure the Chrome driver with the specified executable path
        service = Service(chrome_driver_path)
        
        # Initialize Selenium driver with the configured service
        driver = webdriver.Chrome(service=service)
        driver.maximize_window()
        # Open Gothamist website
        driver.get(GOTHAMIST_URL)
        logger.info("Gothamist opened successfully.")
        return driver
    except Exception as e:
        logger.error(f"Error opening Gothamist: {e}")
        raise

def search(driver, search_phrase):
    # Search for a phrase on Gothamist website.
    try:
        # Insert the search phrase, if provided
        if search_phrase:
            icon_button = driver.find_element(By.XPATH, "//*[@id='__nuxt']/div/div/main/header/div[1]/div[2]/div[2]/button/span[1]")
            icon_button.click()
            # Wait for the search box to be present on the page
            search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, SEARCH_BOX_XPATH)))
            search_box.send_keys(search_phrase)
            search_box.send_keys(Keys.RETURN)
            logger.info(f"Search for '{search_phrase}' successful.")
            return True
    except TimeoutException:
        logger.error("Timeout while searching.")
        raise
    except NoSuchElementException:
        logger.error("Search box element not found.")
        raise

def scrape_description(driver):
    # Scrape the description of the first search result.
    try:
        # Wait until the page loads completely
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, DESCRIPTION_XPATH)))
        # Get the description
        description_element = driver.find_element(By.XPATH, DESCRIPTION_XPATH)
        logger.info("Description scraped successfully.")
        return description_element.text
    except TimeoutException:
        logger.error("Timeout while scraping description.")
        raise
    except NoSuchElementException:
        logger.error("Description element not found.")
        raise

def scrape_news_info(driver, search_phrase):
    # Scrape news information from the first search result.
    try:
        # Get the description before clicking on the first result
        description = scrape_description(driver)
        if not description:
            raise Exception("No description found.")
        # Click on the first result
        first_result = driver.find_element(By.XPATH, FIRST_RESULT_XPATH)
        first_result.click()
        
        # Check if the element is loaded
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))

        # Title
        title_element = driver.find_element(By.XPATH, TITLE_XPATH)
        title = title_element.text

        # Date
        date_element = driver.find_element(By.XPATH, DATE_XPATH)
        date = date_element.text

        # Image URL
        image_element = driver.find_element(By.XPATH, IMAGE_XPATH)
        image_url = image_element.get_attribute("src")

        # Count of search phrases in title and description
        title_search_count = title.lower().count(search_phrase.lower())
        description_search_count = description.lower().count(search_phrase.lower())

        # True or False, depending on whether the title or description contains any monetary value
        money_keywords = ["$", "dollars", "USD"]
        title_contains_money = any(keyword in title.lower() for keyword in money_keywords)
        description_contains_money = any(keyword in description.lower() for keyword in money_keywords)

        # Return the results
        logger.info("News info scraped successfully.")
        return search_phrase, title, date, description, image_url, title_search_count, description_search_count, title_contains_money, description_contains_money
    except TimeoutException:
        logger.error("Timeout while scraping news info.")
        raise
    except NoSuchElementException:
        logger.error("News info element not found.")
        raise
    except Exception as e:
        logger.error(f"Business exception: {e}")
        raise
