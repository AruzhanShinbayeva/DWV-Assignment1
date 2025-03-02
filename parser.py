import json

import psycopg2
import requests
from bs4 import BeautifulSoup


def get_response_from_url(url):
    response = requests.get(url)
    attempts = 1
    while response.status_code != 200 and attempts < 3:
        response = requests.get(url)
    return response


def parse_title(infobox):
    return infobox.find("th", {"class": "infobox-above summary"}).text


def parse_directed_by(infobox):
    directed_by_row = infobox.find("th", class_="infobox-label", string="Directed by")
    if directed_by_row:
        directed_by_value = directed_by_row.find_next_sibling("td")
        for sup in directed_by_value.find_all("sup"):
            sup.decompose()
        if directed_by_value:
            return ", ".join([directed_by.strip() for directed_by in directed_by_value.stripped_strings])
    return None


def parse_release_year(infobox):
    film_dates = infobox.find("div", class_="plainlist film-date")
    dates = film_dates.find_all("li")
    release_year = None
    for date in dates:
        date_span = date.find("span", class_="bday")
        if date_span:
            year = int(date_span.get_text().split('-')[0])
            release_year = year if not release_year else min(year, release_year)
    return release_year


def parse_countries(infobox):
    countries_row = infobox.find("th", class_="infobox-label", string="Countries")
    if not countries_row:
        countries_row = infobox.find("th", class_="infobox-label", string="Country")

    if countries_row:
        countries_data = countries_row.find_next_sibling("td")
        for sup in countries_data.find_all("sup"):
            sup.decompose()
        return ", ".join([country.strip() for country in countries_data.stripped_strings])
    return None


def parse_revenue(row):
    elements = row.find_all("td")
    if len(elements) > 2:
        box_office_revenue_element = elements[2]
        if box_office_revenue_element:
            for sup in box_office_revenue_element.find_all("sup"):
                sup.decompose()
            text = box_office_revenue_element.text.strip()
            return text.replace('$', '').replace(',', '')
    return None


def parse_film(url):
    response = get_response_from_url(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        infobox = soup.find("table", {"class": "infobox vevent"})
        if infobox:
            title = parse_title(infobox)
            directed_by = parse_directed_by(infobox)
            release_year = parse_release_year(infobox)
            countries = parse_countries(infobox)
            return title, directed_by, release_year, countries
    else:
        return None, None, None, None


def parse_list_of_films(url):
    response = get_response_from_url(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")

        table = soup.find("table", {"class": "wikitable"})
        rows = table.find("tbody").find_all("tr")

        for row in rows:
            link_element = row.find("th").find("a")
            if not link_element:
                continue
            link_wiki = link_element.get("href")
            link = f"http://en.wikipedia.org{link_wiki}"
            title, directed_by, release_year, countries = parse_film(link)
            box_office_revenue = parse_revenue(row)
            if None in [title, directed_by, release_year, countries, box_office_revenue]:
                print("ERRRRROORRRR")
            print(f"Title: {title}, Directed By: {directed_by}, Release Year: {release_year}, "
                  f"Countries: {countries}, Box office: {box_office_revenue}")
            insert_to_database(title, directed_by, release_year, countries, box_office_revenue)
    else:
        print(f"Failed to retrieve page. Status code: {response.status_code}")


def insert_to_database(title, directed_by, release_year, countries, box_office_revenue):
    conn = psycopg2.connect(
        dbname="dwv",
        user="dwv",
        password="aruzhandwv",
        host="rc1a-mzvjv2gye43eo3jt.mdb.yandexcloud.net",
        port="6432"
    )
    cur  = conn.cursor()

    insert_query = """
        INSERT INTO films (title, director, release_year, country, box_office)
        VALUES (%s, %s, %s, %s, %s);
    """

    cur.execute(insert_query, (title, directed_by, release_year, countries, box_office_revenue))

    conn.commit()

    cur.close()
    conn.close()

    print("Data inserted successfully.")

def export_database_to_json():
    conn = psycopg2.connect(
        dbname="dwv",
        user="dwv",
        password="aruzhandwv",
        host="rc1a-mzvjv2gye43eo3jt.mdb.yandexcloud.net",
        port="6432"
    )
    cur = conn.cursor()

    cur.execute("SELECT title, director, release_year, country, box_office FROM films")
    films_data = cur.fetchall()

    films_list = []
    for row in films_data:
        film = {
            "title": row[0],
            "directed_by": row[1],
            "release_year": row[2],
            "countries": row[3],
            "box_office_revenue": row[4]
        }
        films_list.append(film)

    with open("films_data.json", "w") as json_file:
        json.dump(films_list, json_file, indent=4)

    cur.close()
    conn.close()
    print("Data exported to films_data.json.")

if __name__=="__main__":
    #parse_list_of_films("https://en.wikipedia.org/wiki/List_of_highest-grossing_films")
    #print(parse_film("https://en.wikipedia.org/wiki/Moana_2"))
    #insert_to_database("TEST", "Test", 2025, "Test", 1)
    export_database_to_json()
