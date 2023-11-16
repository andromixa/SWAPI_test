import pytest
import requests
from conftest import *
import logging
from colorama import Fore, Style


class ColoredFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": Style.DIM + Fore.CYAN,
        "INFO": Style.BRIGHT + Fore.GREEN,
        "WARNING": Style.BRIGHT + Fore.YELLOW,
        "ERROR": Style.BRIGHT + Fore.RED,
        "CRITICAL": Style.BRIGHT + Fore.RED + Fore.MAGENTA,
    }

    RESET = Style.RESET_ALL

    def format(self, record):
        log_message = super().format(record)
        log_level = record.levelname

        color_prefix = self.COLORS.get(log_level, Style.RESET_ALL)
        return f"{color_prefix}{log_message}{self.RESET}"


# Create a logger with the custom formatter
logger = logging.getLogger(__name__)
colored_formatter = ColoredFormatter()
console_handler = logging.StreamHandler()
console_handler.setFormatter(colored_formatter)
logger.addHandler(console_handler)
logger.setLevel(logging.DEBUG)


def get_response(code="", url=main_url):
    response = requests.get(f"{url}{code}")
    if response.status_code != 200:
        logger.error(
            f"No response from the server. status code: {response.status_code}"
        )
    result = response.json()
    return result


def get_list_of_entities(response, *results):
    if results:
        return response["results"]
    return list(response.keys())


def find_entity(code, search_obj):
    url = f"{main_url}{code}"
    params = {"search": search_obj}
    response = requests.get(url, params=params)
    if response.status_code != 200:
        logger.error(
            f"No response from the server. status code: {response.status_code}"
        )
    result = response.json()
    result = result.get("results", [])
    if not result:
        logger.error(f'Search gave no result. Entity "{search_obj}" not found.')
    return result[0]


def show_description(entity):
    for key, value in entity.items():
        logger.info(f"{key}: {value}")


def test_swapi():
    # Step 1: Получить список сущностей
    response = get_response()
    list_of_entities = get_list_of_entities(response)
    assert list_of_entities
    logger.info(f"List of all SWAPI entities: {list_of_entities}")

    # Step 2: Получить список фильмов (films) и информацию по одному фильму
    response = get_response("films")
    list_of_entities = get_list_of_entities(response, True)
    list_of_films = [film["title"] for film in list_of_entities]
    assert list_of_films
    logger.info(f"List of all films: {list_of_films}")

    chosen_film = find_entity("films", film_to_find)
    assert chosen_film
    logger.info(f'Description of "{film_to_find}":')
    show_description(chosen_film)

    # Step 3: Получить список планет (planets) и информацию по планете выбранного вами фильма
    response = get_response("planets")
    list_of_entities = get_list_of_entities(response, True)
    list_of_planets = [planet["name"] for planet in list_of_entities]
    assert list_of_planets
    logger.info(f"List of all planets: {list_of_planets}")

    assert chosen_film["planets"]
    logger.info(f'Planets of "{film_to_find}":')
    for planet in chosen_film["planets"]:
        logger.info("----------- ### -----------")
        planet_description = requests.get(planet)
        show_description(planet_description.json())

    # Step 4: Получить список рас (Species) народов одной из планет выбранного вами фильма
    logger.info(f'Species of "{planet_to_find}":')
    all_species_of_the_film_planet = [
        race
        for race in chosen_film["species"]
        if get_response(url=race)["homeworld"]
        == find_entity("planets", planet_to_find)["url"]
    ]
    assert all_species_of_the_film_planet
    logger.info(
        [get_response(url=race)["name"] for race in all_species_of_the_film_planet]
    )

    # Step 5: Получить список пилотов (peoples) космического корабля из выбранного вами фильма
    logger.info(f'Pilots of the starship "{starship_to_find}":')
    for pilot in find_entity("starships", starship_to_find)["pilots"]:
        logger.info("----------- ### -----------")
        show_description(get_response(url=pilot))
