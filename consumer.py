import logging
import time
import os
from gothamist import open_gothamist, search, scrape_news_info
from excel import write_to_excel
from robocorp import storage
from robocorp import workitems
from robocorp.tasks import task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Current directory where the Python script is located
CURRENT_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

# Load environment variables
EnvironmentVariables = storage.get_json('EnvironmentVariables')

# Output directory
OUTPUT_DIRECTORY = os.path.join(CURRENT_DIRECTORY, "output")


def retry_search(browser, search_phrase):
    """
    Retry search operation multiple times in case of failure.

    Args:
        browser: WebDriver instance.
        search_phrase: Phrase to search.

    Returns:
        Data if search is successful, None otherwise.
    """
    for retry in range(EnvironmentVariables.get('MAX_RETRIES', 3)):
        try:
            if search(browser, search_phrase):
                news_data = scrape_news_info(browser, search_phrase)
                if news_data:
                    return news_data
        except Exception as e:
            logger.error(f"Exception caught: {e}. Retrying...")
            browser.capture_page_screenshot(os.path.join(OUTPUT_DIRECTORY, f"error_screenshot_{search_phrase}_retry_{retry}.png"))
            # Wait before retrying
            time.sleep(EnvironmentVariables.get('WAIT_TIME_BETWEEN_RETRIES', 2))
    return None


def process_item(item):
    """
    Process each item.

    Args:
        item: Work item to process.

    Returns:
        List of news data.
    """
    all_news_data = []
    browser = open_gothamist()

    try:
        payload = item.payload
        if isinstance(payload, dict):  # Check if payload is a dictionary
            search_phrases = payload.get('Name', [])
            if isinstance(search_phrases, list):  # Check if payload['Name'] is a list
                for search_phrase in search_phrases:
                    logger.info("Searching for: %s", search_phrase)
                    news_data = retry_search(browser, search_phrase)
                    if news_data:
                        all_news_data.append(news_data)
            else:
                logger.error("Invalid payload format: %s", payload)
        else:
            logger.error("Invalid payload format: %s", payload)
    except Exception as e:
        logger.error(f"Error processing item: {e}")
    finally:
        try:
            logger.info("Closing the browser...")
            browser.close_all_browsers()
        except Exception as e:
            logger.error(f"Error closing the browser: {e}")

    return all_news_data


@task
def load_and_process_all():
    """
    Load and process all work items.
    """
    try:
        for item in workitems.inputs:
            all_news_data = process_item(item)
            logger.info("Received payload: %s", item.payload)
            if all_news_data:
                logger.info("Writing news data to Excel...")
                write_to_excel(all_news_data, OUTPUT_DIRECTORY)
                logger.info("News data written successfully.")
                # Mark the work item as done
                item.done()
            else:
                logger.warning("No news data found for item: %s", item.id)
                item.fail(
                    exception_type='APPLICATION',
                    code='NO_NEWS_DATA',
                    message='No news data found'
                )
    except Exception as e:
        logger.error(f"Error processing work items: {e}")


if __name__ == "__main__":
    load_and_process_all()
