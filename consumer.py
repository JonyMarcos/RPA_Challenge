import logging
import time
import os
from gothamist import GothamistScraper
from excel import ExcelWriter
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


def retry_search(scraper, search_phrase):
    """
    Retry search operation multiple times in case of failure.

    Args:
        scraper: GothamistScraper instance.
        search_phrase: Phrase to search.

    Returns:
        Data if search is successful, None otherwise.
    """
    for retry in range(EnvironmentVariables.get('MAX_RETRIES', 3)):
        try:
            if scraper.search(search_phrase, retry + 1):  # Adding the retry number
                news_data = scraper.scrape_news_info(search_phrase)
                if news_data:
                    return news_data
        except Exception as e:
            logger.error(f"Exception caught: {e}. Retrying...")
            # Wait before retrying
            time.sleep(EnvironmentVariables.get('WAIT_TIME_BETWEEN_RETRIES', 2))
    return None


def process_item(item):
    """
    Process each item.
    """
    all_news_data = []
    scraper = GothamistScraper()
    excel_writer = ExcelWriter(OUTPUT_DIRECTORY)

    try:
        scraper.open_gothamist()
        payload = item.payload
        if not isinstance(payload, dict) or 'Name' not in payload:
            raise ValueError("Invalid payload format: %s" % payload)

        search_phrases = payload['Name']
        for search_phrase in search_phrases:
            logger.info("Searching for: %s", search_phrase)
            news_data = retry_search(scraper, search_phrase)
            if news_data:
                all_news_data.append(news_data)

        logger.info("Writing news data to Excel...")
        excel_writer.write_to_excel(all_news_data)
        logger.info("News data written successfully.")

    except ValueError as ve:
        logger.error(ve)
    except Exception as e:
        logger.error(f"Error processing item: {e}")
    finally:
        try:
            logger.info("Closing the browser...")
            scraper.browser.close_all_browsers()
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
