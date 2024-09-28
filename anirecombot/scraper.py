from logging import getLogger
from typing import List

from bs4 import BeautifulSoup, Tag
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver import FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

logger = getLogger(__name__)


def parse_html(html_text: str):
    soup = BeautifulSoup(html_text, 'html.parser')
    recs = soup.find_all('div', class_='recommendation svelte-k28mqj')
    return recs


def get_links(recs: List[Tag], driver: WebDriver, timeout: int = 5):
    links = []
    for i in range(1, len(recs) + 1):
        try:
            button = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[2]'))
            )
            button.click()
            link = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, f'/html/body/div[1]/div[3]/div[2]/div[{i}]/div/div[1]/div/a'))
            )
            links.append(link.get_attribute('href'))
        except TimeoutException:
            logger.error(f'Failed to find or click the button/link for recommendation {i} on {driver.current_url}')
        except Exception as e:
            logger.error(f'Unexpected error for recommendation {i}: {e}')
    return links


def scrape(mal_nickname: str, recs_num: int = 50) -> tuple:
    """
    Scrape the recommendations list from https://anime.ameo.dev/


    :param mal_nickname: MAL username
    :param recs_num: Number of recommendations to scrape
    :return: List of anime links, recommendation page
    """
    firefox_options = FirefoxOptions()
    firefox_options.add_argument('--headless')

    with webdriver.Firefox(options=firefox_options) as driver:
        url = f'https://anime.ameo.dev/user/{mal_nickname}/recommendations'
        driver.get(url)
        try:
            WebDriverWait(driver, 10).until(
                lambda browser: len(driver.find_elements(By.CSS_SELECTOR, '.recommendation.svelte-k28mqj')) == recs_num
            )
        except TimeoutException:
            logger.error(
                f'Only {len(driver.find_elements(By.CSS_SELECTOR, ".recommendation.svelte-k28mqj"))} recommendations found.'
            )
        except Exception as e:
            logger.error(f'Unexpected error: {e}')

        recs = parse_html(html_text=driver.page_source)
        links = get_links(recs=recs, driver=driver)

    return links, recs


def create_cards(links: list, recs: list) -> list:
    """
    Create a dictionary with information about recommendations.

    :param links: List of anime links
    :param recs: Recommendation page
    :return: Dictionary of recommendations
    """
    cards = []

    for i, anime in enumerate(recs):
        title = anime.find('div', class_='title-text svelte-k28mqj').text
        genres = anime.find('div', class_='genres svelte-k28mqj').text
        syn = anime.find('div', class_='synopsis svelte-k28mqj').text.split('\n')[0]
        plan = anime['data-plan-to-watch'].title()

        cards.append(f'<b>Title:</b> {title}\n'
                     f'<b>Genres:</b> {genres}\n'
                     f'<b>Plan To Watch:</b> {plan}\n\n'
                     f'<b>Synopsis:</b> {syn}\n\n'
                     f'{links[i]}')

    return cards


def create_recommendations(mal_nickname: str) -> list:
    """
    Create a dictionary of recommendations for the user and store it in the database.

    :param mal_nickname: MAL username
    """
    links, recs = scrape(mal_nickname)
    recomms = create_cards(links, recs)
    return recomms
