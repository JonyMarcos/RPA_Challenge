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
SEARCH_BUTTON = "//button[@aria-label='Go to search page']"
RESULTS_CONTAINER = "//div[@class='search-page-results pt-2']"
SEARCH_BOX = "//input[@class='search-page-input']"
FIRST_RESULT = "//div[@class='h2'][1]"
DESCRIPTION = "//p[@class='desc'][1]"
TITLE = "//h1[@class='mt-4 mb-3 h2'][1]"
DATE = "//p[@class='type-caption'][1]"
CONSENT_BUTTON = "//button[@aria-label='Consent']"
IMAGE = "//div[@class='simple-responsive-image-holder' and contains(@style, 'aspect-ratio: 3 / 2;')]//img[@class='image native-image prime-img-class']"

IMG_DIRECTORY = "./output/"

class GothamistScraper:
    def __init__(self):
        self.browser = None

    def open_gothamist(self):
        """Opens the Gothamist website."""
        try:
            self.browser = Selenium()
            self.browser.open_available_browser(GOTHAMIST_URL)
            self.browser.maximize_browser_window()
            self.browser.wait_until_page_contains_element(SEARCH_BUTTON)
            logger.info("Gothamist opened successfully.")
        except Exception as e:
            logger.error(f"Error opening Gothamist: {e}")
            raise

    def download_image(self, search_phrase, image_url):
        """Downloads and saves the image."""
        try:
            # Extract file name and extension from image URL
            parsed_url = urlparse(image_url)
            image_filename = os.path.basename(parsed_url.path)
            filename, _ = os.path.splitext(image_filename)

            # Build full path to save the file in the output folder
            os.makedirs(IMG_DIRECTORY, exist_ok=True)
            output_path = os.path.join(IMG_DIRECTORY, f"img_search_{search_phrase}.webp")

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

    def search(self, search_phrase, retry):
        """Performs a search on the Gothamist website."""
        try:
            if search_phrase:
                if self.browser.is_element_visible(CONSENT_BUTTON):
                    consent_button = self.browser.find_element(CONSENT_BUTTON)
                    consent_button.click()
                    logger.info("Consent button clicked.")

                self.browser.click_element(SEARCH_BUTTON)
                self.browser.wait_until_page_does_not_contain_element(CONSENT_BUTTON)
                self.browser.wait_until_element_is_visible(SEARCH_BOX)
                self.browser.clear_element_text(SEARCH_BOX)
                self.browser.input_text(SEARCH_BOX, search_phrase)
                self.browser.press_keys(SEARCH_BOX, "RETURN")
                time.sleep(5)
                self.browser.wait_until_element_is_visible(RESULTS_CONTAINER)
                results_count_element = self.browser.find_element(RESULTS_CONTAINER)
                results_count_text = results_count_element.text.strip()
                results_count = int(results_count_text.split()[0])
                if results_count > 0:
                    self.browser.wait_until_element_is_visible(FIRST_RESULT, 10)
                    logger.info(f"Search for '{search_phrase}' successful.")
                    return True
                elif retry == 3:
                    logger.info(f"No results found for '{search_phrase}'. Taking screenshot...")
                    self.browser.capture_page_screenshot(os.path.join(OUTPUT_DIRECTORY, f"no_results_{search_phrase}.png"))
                    return False
                else:
                    logger.info(f"No results found for '{search_phrase}'.")
                    return False
        except Exception as e:
            logger.error(f"Error while searching: {e}")
            raise

    def scrape_description(self):
        """Scrapes the description from the search results."""
        try:
            description_element = self.browser.find_elements(DESCRIPTION)
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

    def scrape_news_info(self, search_phrase):
        """Scrapes news information from the first search result."""
        try:
            description = self.scrape_description()
            title, date, image_url = self.get_title_date_image()
            image_path = self.download_image(search_phrase, image_url)
            title_search_count, description_search_count = self.get_search_counts(search_phrase, title, description)
            title_contains_money, description_contains_money = self.check_money_related(title, description)

            logger.info("News info scraped successfully.")
            return search_phrase, title, date, description, image_url, title_search_count, description_search_count, title_contains_money, description_contains_money
        except Exception as e:
            logger.error(f"Error while scraping news info: {e}")
            raise

    def get_title_date_image(self):
        """Gets title, date, and image URL from the first search result."""
        try:
            first_result = self.browser.find_element(FIRST_RESULT)
            first_result.click()
            self.browser.wait_until_element_is_visible(TITLE, 10)

            title = self.browser.get_text(TITLE)
            date = self.browser.get_text(DATE)
            image_url = self.browser.get_element_attribute(IMAGE, "src")

            return title, date, image_url
        except Exception as e:
            logger.error(f"Error while getting title, date, and image URL: {e}")
            raise

    def get_search_counts(self, search_phrase, title, description):
        """Gets search counts in title and description."""
        try:
            title_search_count = title.lower().count(search_phrase.lower())
            description_search_count = description.lower().count(search_phrase.lower())
            return title_search_count, description_search_count
        except Exception as e:
            logger.error(f"Error while getting search counts: {e}")
            raise

    def check_money_related(self, title, description):
        """Checks if title or description contains money-related keywords."""
        try:
            money_keywords = ["\$[\d,]+(?:\.\d+)?(?:[KMB]?(?:illion|illion|thousand))?", "\$[\d,]+(?:\.\d+)?(?:[KMB]?(?:illion|illion|thousand))?", "\$[\d,]+(?:\.\d+)?(?:[KMB]?(?:illion|illion|thousand))?"]
            title_contains_money = any(re.search(keyword, title, re.IGNORECASE) for keyword in money_keywords)
            description_contains_money = any(re.search(keyword, description, re.IGNORECASE) for keyword in money_keywords)
            
            title_contains_money_str = str(title_contains_money).lower()
            description_contains_money_str = str(description_contains_money).lower()
            
            return title_contains_money_str, description_contains_money_str
        except Exception as e:
            logger.error(f"Error while checking money-related keywords: {e}")
            raise

