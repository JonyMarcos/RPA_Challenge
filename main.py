import time
from gothamist import open_gothamist, search, scrape_news_info
from excel import write_to_excel
from robocorp.tasks import task

# Constantes
OUTPUT_DIRECTORY = "C:\\RPA_Challenge\\output\\"
SEARCH_PHRASE = "Games"
MAX_RETRIES = 3
WAIT_TIME_BETWEEN_RETRIES = 2

@task
def main():
    # Abrir o navegador
    driver = open_gothamist()

    # Tentar obter as informações da notícia
    for retry in range(MAX_RETRIES):
        if search(driver, SEARCH_PHRASE):
            news_data = scrape_news_info(driver, SEARCH_PHRASE)
            if news_data:
                write_to_excel(news_data, OUTPUT_DIRECTORY)
                break
        # Aguardar um curto período antes de tentar novamente
        time.sleep(WAIT_TIME_BETWEEN_RETRIES)

    # Fechar o navegador
    driver.quit()

if __name__ == "__main__":
    main()
