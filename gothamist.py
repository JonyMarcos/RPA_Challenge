import logging
import time
import os
import re
import requests
from urllib.parse import urlparse
from robocorp import storage
from RPA.Browser.Selenium import Selenium

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
EnvironmentVariables = storage.get_json('EnvironmentVariables')

# Current directory where the Python script is located
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Output directory
OUTPUT_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "output")

# Constants
GOTHAMIST_URL = "https://gothamist.com/"
ICON_BUTTON = "//button[@aria-label='Go to search page']"
RESULTS_CONTAINER = "//div[@class='search-page-results pt-2']"
SEARCH_BOX = "//input[@class='search-page-input']"
FIRST_RESULT_CLASS = "(//div[@class='h2'])[1]"
DESCRIPTION_CLASS = "(//p[@class='desc'])[1]"
TITLE_CLASS = "(//h1[@class='mt-4 mb-3 h2'])[1]"
DATE_CLASS = "(//p[@class='type-caption'])[1]"
IMAGE_CLASS = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/figure/div/div/div/div/img"
OVERLAY_ELEMENT = "//div[@class='fc-consent-root']//button[@aria-label='Consent']//p[@class='fc-button-label' and text()='Consent']"

IMG_DIRECTORY = "./output/"

def open_gothamist():
    """Opens the Gothamist website."""
    try:
        browser = Selenium()
        browser.open_available_browser(GOTHAMIST_URL)
        browser.maximize_browser_window()
        browser.wait_until_page_contains_element(ICON_BUTTON)
        logger.info("Gothamist opened successfully.")
        return browser
    except Exception as e:
        logger.error(f"Error opening Gothamist: {e}")
        raise

def download_and_save_image(image_url, output_dir, search_phrase):
    try:
        # Extract file name and extension from image URL
        parsed_url = urlparse(image_url)
        image_filename = os.path.basename(parsed_url.path)
        filename, _ = os.path.splitext(image_filename)

        # Build full path to save the file in the output folder  
        os.makedirs(output_dir, exist_ok=True)  
        output_path = os.path.join(output_dir, f"img_search_{search_phrase}.webp")  

        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()

        # Save the image at the specified path
        with open(output_path, "wb") as file:
            file.write(response.content)

        logger.info(f"Image downloaded successfully: {output_path}")

        return output_path
    except Exception as e:
        logger.error(f"Error downloading or saving image: {e}")
        return None

def search(browser, search_phrase, retry):
    """Performs a search on the Gothamist website."""
    try:
        if search_phrase:
            # Attempt to click on the consent button if present
            if browser.is_element_visible(OVERLAY_ELEMENT):
                consent_button = browser.find_element(OVERLAY_ELEMENT)
                consent_button.click()
                logger.info("Consent button clicked.")
            else:
                logger.info("Consent button not found. Continuing with search.")

            # Click on the search icon
            browser.click_element(ICON_BUTTON)
            # Wait until the overlay element is no longer present on the page
            browser.wait_until_page_does_not_contain_element(OVERLAY_ELEMENT)
            # Wait until the search box is visible
            browser.wait_until_element_is_visible(SEARCH_BOX)
            # Clear the content of the search box
            browser.clear_element_text(SEARCH_BOX)
            # Click on the search box
            browser.click_element(SEARCH_BOX)
            # Input the search phrase
            browser.input_text(SEARCH_BOX, search_phrase)
            # Press Enter to start the search
            browser.press_keys(SEARCH_BOX, "RETURN")
            # Wait
            time.sleep(5)
            # Wait until the search results container is visible
            browser.wait_until_element_is_visible(RESULTS_CONTAINER)
            # Get the search results count
            results_count_element = browser.find_element(RESULTS_CONTAINER)
            results_count_text = results_count_element.text.strip()
            results_count = int(results_count_text.split()[0])
            if results_count > 0:
                # Wait until the first search result is visible
                browser.wait_until_element_is_visible(FIRST_RESULT_CLASS, 10)
                logger.info(f"Search for '{search_phrase}' successful.")
                return True
            elif retry == 3:
                logger.info(f"No results found for '{search_phrase}'. Taking screenshot...")
                browser.capture_page_screenshot(os.path.join(OUTPUT_DIRECTORY, f"no_results_{search_phrase}.png"))
                return False
            else:
                logger.info(f"No results found for '{search_phrase}'.")
                return False
    except Exception as e:
        logger.error(f"Error while searching: {e}")
        raise




def scrape_description(browser):
    """Scrapes the description from the search results."""
    try:
        description_element = browser.find_elements(DESCRIPTION_CLASS)
        if description_element:
            description = description_element[0].text
            logger.info("Description scraped successfully.")
            return description
        else:
            logger.warning("No description found.")
            return None
    except Exception as e:
        logger.error(f"Error while scraping description: {e}")
        raise

def scrape_news_info(browser, search_phrase):
    """Scrapes news information from the first search result."""
    try:
        description = scrape_description(browser)
        first_result = browser.find_element(FIRST_RESULT_CLASS)
        first_result.click()
        browser.wait_until_element_is_visible(TITLE_CLASS, 10)

        title = browser.get_text(TITLE_CLASS)
        date = browser.get_text(DATE_CLASS)
        image_url = browser.get_element_attribute(IMAGE_CLASS, "src")
        image_path = download_and_save_image(image_url, IMG_DIRECTORY, search_phrase)

        title_search_count = title.lower().count(search_phrase.lower())
        description_search_count = description.lower().count(search_phrase.lower())

        money_keywords = ["\$", "dollars", "USD"]
        title_contains_money = any(re.search(r'\b{}\b'.format(keyword), title, re.IGNORECASE) for keyword in money_keywords)
        description_contains_money = any(re.search(r'\b{}\b'.format(keyword), description, re.IGNORECASE) for keyword in money_keywords)

        logger.info("News info scraped successfully.")
        return search_phrase, title, date, description, image_url, title_search_count, description_search_count, title_contains_money, description_contains_money
    except Exception as e:
        logger.error(f"Error while scraping news info: {e}")
        raise
