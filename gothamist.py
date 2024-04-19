import logging
import re
from RPA.Browser.Selenium import Selenium

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Constants
GOTHAMIST_URL = "https://gothamist.com/"
ICON_BUTTON = "//span[contains(@class, 'pi-search')]"
SEARCH_BOX = "//input[@class='search-page-input']"
FIRST_RESULT_CLASS = "(//div[@class='h2'])[1]"
DESCRIPTION_CLASS = "(//p[@class='desc'])[1]"
TITLE_CLASS = "(//h1[@class='mt-4 mb-3 h2'])[1]"
DATE_CLASS = "(//p[@class='type-caption'])[1]"
IMAGE_CLASS = "(//div[@class='image-with-caption-image'])[1]"

def open_gothamist():
    """Opens the Gothamist website."""
    try:
        browser = Selenium()
        browser.open_available_browser(GOTHAMIST_URL)
        browser.maximize_browser_window()
        logger.info("Gothamist opened successfully.")
        return browser
    except Exception as e:
        logger.error(f"Error opening Gothamist: {e}")
        raise

def search(browser, search_phrase):
    """Performs a search on the Gothamist website."""
    try:
        if search_phrase:
            # Click the icon
            browser.click_element(ICON_BUTTON)
            # Wait until search box is visible
            browser.wait_until_element_is_visible(SEARCH_BOX)
            # Click search phrase
            browser.click_element(SEARCH_BOX)
            # Input search phrase
            browser.input_text(SEARCH_BOX, search_phrase)
            # Press Enter
            browser.press_keys(SEARCH_BOX, "RETURN")
            # Wait until search results are visible
            browser.wait_until_element_is_visible(FIRST_RESULT_CLASS)
            logger.info(f"Search for '{search_phrase}' successful.")
            return True
    except Exception as e:
        logger.error(f"Error while searching: {e}")
        raise

def scrape_description(browser):
    """Scrapes the description from the search results."""
    try:
        # Get the description text
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
        # Get the description before clicking on the first result
        description = scrape_description(browser)

        # Click on the first result
        first_result = browser.find_element(FIRST_RESULT_CLASS)
        first_result.click()

        # Wait for elements to load
        browser.wait_until_element_is_visible(TITLE_CLASS)

        # Extract information
        title = browser.get_text(TITLE_CLASS)
        date = browser.get_text(DATE_CLASS)
        image_url = browser.get_element_attribute(IMAGE_CLASS, "src")

        # Count of search phrases in title and description
        title_search_count = title.lower().count(search_phrase.lower())
        description_search_count = description.lower().count(search_phrase.lower())

        # Check for monetary symbols using regular expressions
        money_keywords = ["\$", "dollars", "USD"]
        title_contains_money = any(re.search(r'\b{}\b'.format(keyword), title, re.IGNORECASE) for keyword in money_keywords)
        description_contains_money = any(re.search(r'\b{}\b'.format(keyword), description, re.IGNORECASE) for keyword in money_keywords)

        # Return the results
        logger.info("News info scraped successfully.")
        return search_phrase, title, date, description, image_url, title_search_count, description_search_count, title_contains_money, description_contains_money
    except Exception as e:
        logger.error(f"Error while scraping news info: {e}")
        raise