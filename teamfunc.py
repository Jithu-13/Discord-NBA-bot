from dnl import nba_teams
from bs4 import BeautifulSoup, Comment
import requests
import re

"""
def identifier(name, year=None):
    if name.title() in nba_teams or name.lower() in nba_teams.values():
        code = nba_teams.get(name.title(), name).upper()
    furl = "https://www.basketball-reference.com/teams/"

    url = furl + code + "/"

    if year:
        url += str(year) + ".html"

    page = requests.get(url).text

    soup = BeautifulSoup(page, "lxml")

    team_img = soup.find(class_="teamlogo")["src"]

    infobox = soup.find(id="info")

    team_name = infobox.find(itemprop="name").text.strip().replace("\n", " ")

    return team_name, code, soup, team_img, url

"""


def identifier(code, year=None):
    try:
        url = "https://www.basketball-reference.com/teams/"
        url += code + "/"
        if year:
            url += str(year) + ".html"
        page = requests.get(url).text

        soup = BeautifulSoup(page, "lxml")

        team_img = soup.find(class_="teamlogo")["src"]
        infobox = soup.find(id="info")

        team_name = infobox.find(itemprop="name").text.strip().replace("\n", " ")
        if year == None:
            for p in infobox.find_all("p"):
                if "Seasons" in p.text:
                    season = p.text
                if "Record" in p.text:
                    record = p.text
                if "Playoff Appearances" in p.text:
                    playoff = p.text
                if "Championships" in p.text:
                    champs = p.text

            season = season.replace("\n", "").replace(";", "").split()
            record = record.replace("\n", "").split()
            playoff = playoff.strip().split()
            champs = champs.strip().split()

            team_seasons = (
                season[1]
                + " ("
                + season[-3][:-2]
                + season[-1][:2]
                + season[-1][-2:]
                + ")"
            )
            team_record = " ".join(record[1:4])
            team_playoff_app = playoff[2]
            team_champ = champs[1]

            top_list = []
            for comments in soup.find_all(
                string=lambda text: isinstance(text, Comment)
            ):

                if "div_teams_ws_images" in comments:
                    data = BeautifulSoup(comments, "lxml")
                    top = data.find(id="div_teams_ws_images")

            for name in top.find_all("img"):
                top_list.append(name["data-tip"])

            max_len = 34

            for i in range(len(top_list)):
                p = top_list[i]
                space = " " * (max_len - len(p))
                place = p[: p.index(".") + 1]
                p = p[p.index(".") + 2 :]
                m = re.search(r"\d", p)
                name = p[: m.start() - 1]
                ws = p[m.start() :]
                full = place + name + space + ws
                top_list[i] = full

            top_twelve = "\n".join(top_list)
            return (
                team_name,
                team_img,
                team_seasons,
                team_record,
                team_playoff_app,
                team_champ,
                top_twelve,
            )
        elif year:
            for p in infobox.find_all("p"):
                if "Record" in p.text:
                    record = p.text.strip().replace("\n", "").split()
                if "Coach" in p.text:
                    coach = p.text.strip().split()[1:]
                if "Executive" in p.text:
                    executive = p.text.strip().split()[1:]
                if "PTS/G" in p.text:
                    pts_opp = p.text.strip().split()
                if "SRS" in p.text:
                    srs_pace = p.text.strip().split()
                if "Off Rtg" in p.text:
                    off_def = p.text.strip().split()
                if "Expected W-L" in p.text:
                    w_l = p.text.strip().split()[2:]
                if "Preseason Odds" in p.text:
                    podds = p.text.strip().split()[2:]
                if "Arena" in p.text:
                    arena = p.text.strip().split()[1:]
                if "Playoffs" in p.text:
                    playoff = (
                        p.text.replace("(Series Stats)", "")
                        .replace("versus", "vs.")
                        .replace("Eastern", "E")
                        .replace("Western", "W")
                        .replace("Conference", "Conf.")
                        .replace("\xa0", "")
                        .split("\n")
                    )
            team_record = " ".join(record[1:])
            team_coach = " ".join(coach)
            team_exec = " ".join(executive)
            pts_g = " ".join(pts_opp[1:5])
            opp_g = " ".join(pts_opp[7:])
            srs = " ".join(srs_pace[1:5])
            pace = " ".join(srs_pace[6:])
            off_rtg = " ".join(off_def[2:6])
            def_rtg = " ".join(off_def[8:])
            expected_WL = " ".join(w_l)
            p_odds = " ".join(podds)
            team_arena = " ".join(arena)
            if "playoff" in locals():
                playoff_header = playoff[0]
                play_series = "\n".join(playoff[1:])
            else:
                playoff_header = None
                play_series = None

            return (
                soup,
                team_name,
                team_img,
                team_record,
                team_coach,
                team_exec,
                pts_g,
                opp_g,
                srs,
                pace,
                off_rtg,
                def_rtg,
                expected_WL,
                p_odds,
                team_arena,
                playoff_header,
                play_series,
            )
    except Exception:
        return None
