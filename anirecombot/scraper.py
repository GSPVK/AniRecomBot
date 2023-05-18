from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from sql_db import RecommendationsDB


def scrape(user: str) -> tuple:
    """
    Scrape the recommendations list from https://anime.ameo.dev/

    :param user: MAL username
    :return: List of anime links, recommendation page
    """
    url = f'https://anime.ameo.dev/user/{user}/recommendations'
    links = []
    driver = webdriver.Chrome()
    driver.get(url)
    sleep(2)
    html_text = driver.page_source
    soup = BeautifulSoup(html_text, 'lxml')
    recs = soup.find_all('div', class_='recommendation svelte-k28mqj')

    for i, _ in enumerate(recs, 1):
        driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[2]').click()
        link = driver.find_element(By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[1]/div/a')
        link = link.get_attribute('href')
        links.append(link)

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
        recs_list[i] = {}

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


def adding_recommendations(user: str):
    """
    Create a list of recommendations for the user and store it in the database.

    :param user: MAL username
    """
    anilinks, recs = scrape(user)
    anilist = get_recs(anilinks, recs)

    recs_db = RecommendationsDB('../recs_db.db')
    recs_db.add_recs(user, anilist)
