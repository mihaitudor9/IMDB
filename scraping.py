import pandas as pd
import numpy as np
import re
from bs4 import BeautifulSoup
from requests import get
from typing import Tuple
from iso3166 import countries
import os
from datetime import datetime

# ================== CONFIGURATIONS ==================

current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
OUTPUT_PATH = os.path.join(os.path.expanduser("~"), "IMDB", "data", f"output_{current_time}.xlsx")
MIN_VOTES = 0

# ================== SCRAPING CLASS ==================

class IMDBScraper:
    """Class to scrape IMDB movie data based on country."""

    BASE_URL = "https://www.imdb.com/search/title/?title_type=feature,tv_series&num_votes={votes},&country_of_origin={country_code}&sort=user_rating,desc&start=0&ref_=adv_nxt"

    def __init__(self, country_code: str, min_votes: int):
        """
        Initialize scraper with a specific country and minimum votes.
        """
        self.url = self.BASE_URL.format(country_code=country_code, votes=min_votes)
        self.soup = BeautifulSoup(get(self.url).content, 'lxml')
        self.movie_data = {
            'title': [], 'date': [], 'runtime': [], 'genre': [],
            'rating': [], 'score': [], 'description': [],
            'director': [], 'stars': [], 'votes': [],
            'gross': [], 'country': []
        }

    def get_article_title(self) -> str:
        return self.soup.find("h1", class_="header").text.strip()

    def get_article_count(self) -> Tuple[str, int]:
        txt = self.soup.find(class_="desc").text.strip()
        counter = re.search(r'-(\d+)', txt)
        if counter:
            return counter.group(1), int(counter.group(1).replace(',', ''))
        return '', 0

    def get_body_content(self) -> BeautifulSoup:
        """
        Extract the main content body that contains the movie listings.
        """
        return self.soup.find(id="main").find_all("div", class_="lister-item mode-advanced")

    def extract_movie_data_from_content(self, content: BeautifulSoup):
        """
        Extract movie details like title, runtime, genre, etc.
        and populate the movie_data structure.
        """

        for movie in content:
            country = re.search(r'&country_of_origin=(.*?)&sort=user_rating', self.url)
            self.movie_data['country'].append(country.group(1) if country else np.nan)

            movie_first_line = movie.find("h3", class_="lister-item-header")
            self.movie_data['title'].append(movie_first_line.find("a").text)
            self.movie_data['date'].append(re.sub(r"[()]", "", movie_first_line.find_all("span")[-1].text))
            self.movie_data['runtime'].append(
                movie.find("span", class_="runtime").text[:-4] if movie.find("span", class_="runtime") else np.nan)
            self.movie_data['genre'].append(
                movie.find("span", class_="genre").text.rstrip().replace("\n", "").split(",") if movie.find("span",
                                                                                                            class_="genre") else np.nan)
            self.movie_data['rating'].append(movie.find("strong").text if movie.find("strong") else np.nan)
            self.movie_data['score'].append(
                movie.find("span", class_="metascore unfavorable").text.rstrip() if movie.find("span",
                                                                                               class_="metascore unfavorable") else np.nan)
            self.movie_data['description'].append(movie.find_all("p", class_="text-muted")[-1].text.lstrip())

            movie_cast = movie.find("p", class_="")

            try:
                casts = movie_cast.text.replace("\n", "").split('|')
                casts = [x.strip() for x in casts]
                casts = [casts[i].replace(j, "") for i, j in enumerate(["Director:", "Stars:"])]
                self.movie_data['director'].append(casts[0])
                self.movie_data['stars'].append([x.strip() for x in casts[1].split(",")])
            except:
                casts = movie_cast.text.replace("\n", "").strip()
                self.movie_data['director'].append(np.nan)
                self.movie_data['stars'].append([x.strip() for x in casts.split(",")])

            movie_numbers = movie.find_all("span", attrs={"name": "nv"})

            if len(movie_numbers) == 2:
                self.movie_data['votes'].append(movie_numbers[0].text)
                self.movie_data['gross'].append(movie_numbers[1].text)
            elif len(movie_numbers) == 1:
                self.movie_data['votes'].append(movie_numbers[0].text)
                self.movie_data['gross'].append(np.nan)
            else:
                self.movie_data['votes'].append(np.nan)
                self.movie_data['gross'].append(np.nan)

    def scrape_movie_data(self) -> pd.DataFrame:
        movie_content = self.get_body_content()
        self.extract_movie_data_from_content(movie_content)
        df = pd.DataFrame(self.movie_data)
        return df

# ================== MAIN FUNCTION ==================

def main():
    """
    Main function to iterate through countries, scrape data and save to an Excel.
    """
    for country_info in countries:
        print(f"Processing {country_info[0]} ({country_info[1]})")

        scraper = IMDBScraper(country_info[1], MIN_VOTES)
        df = scraper.scrape_movie_data()

        df.to_excel(OUTPUT_PATH, index=False)
        print(f"Saved data for {country_info[0]} to {OUTPUT_PATH}")

if __name__ == "__main__":
    main()
