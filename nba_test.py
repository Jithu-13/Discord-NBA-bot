from bs4 import BeautifulSoup
import requests
from playerfunc import check_team, strip_accents, get_playoff_matchups

url = "https://www.basketball-reference.com/awards/all_league.html"

years = [2015, 2016, 2017, 2018, 2019, 2020]

page = requests.get(url).text
soup = BeautifulSoup(page, "lxml")

table = soup.find("tbody")

tags = ["lg_id", "all_team"]

yrs = []

for i in range(len(years)):
    yr_first = int(years[i]) - 1
    yr_id = str(yr_first) + "-" + str(years[i])[-2:]
    yrs.append(yr_id)

all_nba = {}

for i in range(len(yrs)):
    for tr in table.find_all("tr"):
        if tr.th.text == yrs[i]:
            for td in tr.find_all("td"):
                if td["data-stat"] not in tags:
                    player = td.a.text
                    player = strip_accents(player)
                    tm = check_team(years[i], player)
                    if player not in all_nba.keys():
                        all_nba[player] = [(years[i], tm)]
                    else:
                        all_nba[player].append((years[i], tm))


for i, j in all_nba.items():
    print(i, j)

