import pandas as pd
from iso3166 import countries
import scraping


def main():
    for country_info in countries:
        print(country_info[0])
        print(country_info[1])

        data = scraping.IMDB_scrape(country_info[1], 1000)

        print("\n------------------------")
        df = pd.DataFrame(data).T
        df = df.rename(columns={df.columns[0]: 'movieTitle'})
        df = df.rename(columns={df.columns[1]: 'movieDate'})
        df = df.rename(columns={df.columns[2]: 'movieRunTime'})
        df = df.rename(columns={df.columns[3]: 'movieGenre'})
        df = df.rename(columns={df.columns[4]: 'movieRating'})
        df = df.rename(columns={df.columns[5]: 'movieScore'})
        df = df.rename(columns={df.columns[6]: 'movieDescription'})
        df = df.rename(columns={df.columns[7]: 'movieDirector'})
        df = df.rename(columns={df.columns[8]: 'movieStars'})
        df = df.rename(columns={df.columns[9]: 'movieVotes'})
        df = df.rename(columns={df.columns[10]: 'movieGross'})
        df = df.rename(columns={df.columns[11]: 'movieCountry'})

        df.to_excel(r'/Users/tudormihai/PycharmProjects/IMDB/Data/output_dataset_test.xlsx', index=False)


if __name__ == "__main__":
    main()
