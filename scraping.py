import numpy as np
import re
from bs4 import BeautifulSoup
from requests import get
from typing import Final

movieTitle = []
movieDate = []
movieRunTime = []
movieGenre = []
movieRating = []
movieScore = []
movieDescription = []
movieDirector = []
movieStars = []
movieVotes = []
movieGross = []
movieCountry = []

class IMDB(object):

    def __init__(self, url):
        super(IMDB, self).__init__()
        page = get(url)

        self.soup = BeautifulSoup(page.content, 'lxml')

    def articleTitle(self):
        return self.soup.find("h1", class_="header").text.replace("\n", "")

    def articleCount(self):
        txt = self.soup.find(class_="desc").text.replace("\n", "")
        maxCount = 0

        counter = re.search('(.*)of', txt)

        if counter is not None:
            counter = counter.group(1)
            counter = re.search('-(.*)', counter)
            counter = counter.group(1)

            # Get String after substring occurrence
            maxCount = txt.partition(counter)[2]
            maxCount = maxCount.partition('titles')[0]
            maxCount = maxCount.split()[1]
            maxCount = int(maxCount.replace(',', ''))

        return counter, maxCount

    def bodyContent(self):
        content = self.soup.find(id="main")
        return content.find_all("div", class_="lister-item mode-advanced")

    def movieData(self, url):
        movieFrame = self.bodyContent()

        for movie in movieFrame:

            movieCountry.append(re.search(r'&country_of_origin=(.*?)&sort=user_rating', url).group(1))

            movieFirstLine = movie.find("h3", class_="lister-item-header")
            movieTitle.append(movieFirstLine.find("a").text)
            movieDate.append(re.sub(r"[()]", "", movieFirstLine.find_all("span")[-1].text))
            try:
                movieRunTime.append(movie.find("span", class_="runtime").text[:-4])
            except:
                movieRunTime.append(np.nan)

            try:
                movieGenre.append(movie.find("span", class_="genre").text.rstrip().replace("\n", "").split(","))
            except:
                movieGenre.append(np.nan)
            try:
                movieRating.append(movie.find("strong").text)
            except:
                movieRating.append(np.nan)
            try:
                movieScore.append(movie.find("span", class_="metascore unfavorable").text.rstrip())
            except:
                movieScore.append(np.nan)
            movieDescription.append(movie.find_all("p", class_="text-muted")[-1].text.lstrip())
            movieCast = movie.find("p", class_="")

            try:
                casts = movieCast.text.replace("\n", "").split('|')
                casts = [x.strip() for x in casts]
                casts = [casts[i].replace(j, "") for i, j in enumerate(["Director:", "Stars:"])]
                movieDirector.append(casts[0])
                movieStars.append([x.strip() for x in casts[1].split(",")])
            except:
                casts = movieCast.text.replace("\n", "").strip()
                movieDirector.append(np.nan)
                movieStars.append([x.strip() for x in casts.split(",")])

            movieNumbers = movie.find_all("span", attrs={"name": "nv"})

            if len(movieNumbers) == 2:
                movieVotes.append(movieNumbers[0].text)
                movieGross.append(movieNumbers[1].text)
            elif len(movieNumbers) == 1:
                movieVotes.append(movieNumbers[0].text)
                movieGross.append(np.nan)
            else:
                movieVotes.append(np.nan)
                movieGross.append(np.nan)

        movieData = [movieTitle, movieDate, movieRunTime, movieGenre, movieRating, movieScore, movieDescription,
                     movieDirector, movieStars, movieVotes, movieGross, movieCountry]
        return movieData


def IMDB_scrape(country_code, votes):
    print("---------------")
    maxTotal = 0
    maxPerPage = 50

    url = 'https://www.imdb.com/search/title/?title_type=feature,tv_series&num_votes=' + str(
        votes) + ',&country_of_origin=' + country_code + '&sort=user_rating,desc&start=0&ref_=adv_nxt'
    site = IMDB(url)
    subject = site.articleCount()
    print("Subject: ", subject)
    count = site.articleCount()[0]
    print("Count: ", count)
    maxTotal = site.articleCount()[1]
    print("Max: ", max)
    data = site.movieData(url)
    print(data)
    print(type(data))

    if maxTotal > maxPerPage:

        index = 0
        while index < maxPerPage:
            url = 'https://www.imdb.com/search/title/?title_type=feature,tv_series&num_votes=' + str(
                votes) + ',&country_of_origin=' + country_code + '&sort=user_rating,desc&start=' + str(
                index) + '&ref_=adv_nxt'
            site = IMDB(url)
            data = site.movieData(url)
            index += int(maxPerPage)

    return data