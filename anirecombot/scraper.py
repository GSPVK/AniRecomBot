from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options

from sql_db import recs_db


def scrape(mal_nickname: str) -> tuple:
    """
    Scrape the recommendations list from https://anime.ameo.dev/

    sleep(2) is used to allow the page to fully load and make 50 recommendations available for scraping.
    Without this wait, the page will only load 20 recommendations.

    :param mal_nickname: MAL username
    :return: List of anime links, recommendation page
    """
    url = f'https://anime.ameo.dev/user/{mal_nickname}/recommendations'
    links = []
    chrome_options = Options()
    chrome_options.add_argument("--headless")

    # for debug remove options from string below
    driver = webdriver.Chrome(options=chrome_options)

    driver.get(url)
    sleep(2)
    WebDriverWait(driver, 5).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'recommendation'))
    )
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    recs = soup.find_all('div', class_='recommendation svelte-k28mqj')

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


def get_recs(anime_links: list, anime_list: list) -> dict:
    """
    Create a dictionary with information about recommendations.

    :param anime_links: List of anime links
    :param anime_list: Recommendation page
    :return: Dictionary of recommendations
    """
    recs_list = {}

    for i, anime in enumerate(anime_list, 1):
        title = anime.find('div', class_='title-text svelte-k28mqj').text
        genres = anime.find('div', class_='genres svelte-k28mqj').text
        syn = anime.find('div', class_='synopsis svelte-k28mqj').text
        plan = anime['data-plan-to-watch'].title()

        recs_list[i] = {'id': i,
                        'Title': title,
                        'Genres': genres,
                        'Synopsis': syn.split('\n')[0],
                        'Plan To Watch': plan,
                        'Link': anime_links[i - 1]}

    return recs_list


def create_recommendations(mal_nickname: str):
    """
    Create a list of recommendations for the user and store it in the database.

    :param mal_nickname: MAL username
    """
    anilinks, recs = scrape(mal_nickname)
    anilist = get_recs(anilinks, recs)

    recs_db.add_recs(mal_nickname, anilist)
