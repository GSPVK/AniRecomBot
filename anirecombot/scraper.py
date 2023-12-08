from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver import FirefoxOptions
from anirecombot.sql_db import recs_db


def scrape(mal_nickname: str) -> tuple:
    """
    Scrape the recommendations list from https://anime.ameo.dev/


    :param mal_nickname: MAL username
    :return: List of anime links, recommendation page
    """
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    # For a clear demonstration of scraping/debugging, remove "options" from the "driver" variable
    driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=firefox_options)

    url = f'https://anime.ameo.dev/user/{mal_nickname}/recommendations'
    driver.get(url)

    recs_num = 50  # number of recommendations to scrape (0...50)
    WebDriverWait(driver, 10).until(
        lambda browser: len(driver.find_elements(By.CSS_SELECTOR, '.recommendation.svelte-k28mqj')) == recs_num)
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'html.parser')
    recs = soup.find_all('div', class_='recommendation svelte-k28mqj')

    links = []
    for i in range(1, len(recs) + 1):
        WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[2]'))
        )
        driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[2]').click()
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[1]/div/a'))
        )
        link = driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[1]/div/a')
        link = link.get_attribute('href')
        links.append(link)

    driver.quit()
    return links, recs


def get_recs(links: list, recs: list) -> dict:
    """
    Create a dictionary with information about recommendations.

    :param links: List of anime links
    :param recs: Recommendation page
    :return: Dictionary of recommendations
    """
    recomms = {}

    for i, anime in enumerate(recs, 1):
        title = anime.find('div', class_='title-text svelte-k28mqj').text
        genres = anime.find('div', class_='genres svelte-k28mqj').text
        syn = anime.find('div', class_='synopsis svelte-k28mqj').text
        plan = anime['data-plan-to-watch'].title()

        recomms[i] = {'id': i,
                      'Title': title,
                      'Genres': genres,
                      'Synopsis': syn.split('\n')[0],
                      'Plan To Watch': plan,
                      'Link': links[i - 1]}

    return recomms


def create_recommendations(mal_nickname: str):
    """
    Create a dictionary of recommendations for the user and store it in the database.

    :param mal_nickname: MAL username
    """
    links, recs = scrape(mal_nickname)
    recomms = get_recs(links, recs)
    recs_db.add_recs(mal_nickname, recomms)
