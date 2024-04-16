from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import os

# Constantes
SEARCH_BOX_XPATH = "//*[@id='search']/input"
FIRST_RESULT_XPATH = "//*[@id='resultList']/div[2]/div[1]/div/div[2]/div[1]/a/div"
DESCRIPTION_XPATH = "//*[@id='resultList']/div[2]/div[1]/div/div[2]/div[2]/p"
TITLE_XPATH = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[1]/div[2]/h1"
DATE_XPATH = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[2]/div[1]/div[1]/div[1]/div[2]/div[2]/p"
IMAGE_XPATH = "//*[@id='__nuxt']/div/div/main/div[2]/section[1]/div/div[2]/div[2]/div[1]/figure/div/div/div/div/img"

def open_gothamist():
    # Inicializar o driver do Selenium
    driver = webdriver.Chrome()
    # Maximize a janela do navegador
    driver.maximize_window()
    # Abrir o site do LA Times
    driver.get("https://gothamist.com/")
    return driver

def search(driver, search_phrase):
    try:
        # Inserir a frase de busca, se fornecida
        if search_phrase:
            icon_button = driver.find_element(By.XPATH, "//*[@id='__nuxt']/div/div/main/header/div[1]/div[2]/div[2]/button/span[1]")
            icon_button.click()
            # Wait for the search box to be present on the page
            search_box = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, SEARCH_BOX_XPATH)))
            search_box.send_keys(search_phrase)
            search_box.send_keys(Keys.RETURN)
            return True
    except TimeoutException:
        print("Page load timed out.")
        return False

def scrape_description(driver):
    try:
        # Esperar até que a página carregue completamente
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, DESCRIPTION_XPATH)))
        # Obter a descrição
        description_element = driver.find_element(By.XPATH, DESCRIPTION_XPATH)
        return description_element.text
    except TimeoutException:
        print("Page load timed out.")
        return None

def scrape_news_info(driver, search_phrase):
    try:
        # Obter a descrição antes de clicar no primeiro resultado
        description = scrape_description(driver)
        if not description:
            return None

        # Clicar no primeiro resultado
        first_result = driver.find_element(By.XPATH, FIRST_RESULT_XPATH)
        first_result.click()
        
        # Verifica se o elemento foi carregado
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, TITLE_XPATH)))

        # Título
        title_element = driver.find_element(By.XPATH, TITLE_XPATH)
        title = title_element.text

        # Data
        date_element = driver.find_element(By.XPATH, DATE_XPATH)
        date = date_element.text

         # URL da imagem
        image_element = driver.find_element(By.XPATH, IMAGE_XPATH)
        image_url = image_element.get_attribute("src")

        # Contagem de frases de busca no título e na descrição
        title_search_count = title.lower().count(search_phrase.lower())
        description_search_count = description.lower().count(search_phrase.lower())

        # Verdadeiro ou Falso, dependendo se o título ou descrição contém algum valor monetário
        money_keywords = ["$", "dollars", "USD"]
        title_contains_money = any(keyword in title.lower() for keyword in money_keywords)
        description_contains_money = any(keyword in description.lower() for keyword in money_keywords)

        # Retornar os resultados
        return title, date, description, image_url, title_search_count, description_search_count, title_contains_money, description_contains_money
    except TimeoutException:
        print("Page load timed out.")
        return None
