import os
import time
import json
import logging
from gothamist import open_gothamist, search, scrape_news_info
from excel import write_to_excel
from robocorp import storage
from robocorp import workitems
from robocorp.tasks import task

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
EnvironmentVariables = storage.get_json('EnvironmentVariables')

def retry_search(driver, search_phrase):
    # Attempt to perform a search multiple times
    for retry in range(EnvironmentVariables['MAX_RETRIES']):
        try:
            if search(driver, search_phrase):
                news_data = scrape_news_info(driver, search_phrase)
                if news_data:
                    return news_data
        except Exception as e:
            logger.error(f"Exception caught: {e}. Retrying...")
            time.sleep(EnvironmentVariables['WAIT_TIME_BETWEEN_RETRIES'])
    return None

@task
def main():
    # Get the current directory path
    current_directory = os.path.dirname(__file__)

    # Construct the path to the input file within the 'input' directory
    input_file_path = os.path.join(current_directory, 'input', 'input.json')

    # Load data from the input JSON file
    with open(input_file_path, 'r') as f:
        data = json.load(f)
        search_phrases = data.get('titles', [])
        logger.info("Received search phrases: %s", search_phrases)

        # Initialize a list to store data for all news articles
        all_news_data = []

        # Open the browser
        logger.info("Opening the browser...")
        driver = open_gothamist()

        # Iterate over each search phrase
        for search_phrase in search_phrases:
            # Attempt to retrieve news information
            logger.info("Searching for: %s", search_phrase)
            news_data = retry_search(driver, search_phrase)
            if news_data:
                all_news_data.append(news_data)

        # Close the browser
        logger.info("Closing the browser...")
        driver.quit()

        # Write all news data to the final output file
        if all_news_data:
            logger.info("Writing news data to Excel...")
            write_to_excel(all_news_data, EnvironmentVariables['OUTPUT_DIRECTORY'])
            logger.info("News data written successfully.")

if __name__ == "__main__":
    main()
