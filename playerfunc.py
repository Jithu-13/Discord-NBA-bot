import unicodedata
import requests
from bs4 import BeautifulSoup, Comment
from dnl import player_nicknames, positions
from datetime import datetime, date


def strip_accents(text):
    try:
        text = unicode(text, "utf-8")
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def identifier(name):
    try:
        ref_name = ""
        n = 1
        if name.lower() in player_nicknames:
            name = player_nicknames[name]

        while strip_accents(ref_name) != name.lower():

            f_rl = "https://www.basketball-reference.com/players/"

            full_name = name.split()
            fname = full_name[0].lower()
            lname = full_name[1].lower()
            if "." in fname:
                fname = fname.replace(".", "")
            if "'" in lname:
                lname = lname.replace("'", "")
            l_letter = lname[0]
            l_letter += "/"
            name = name.lower()

            num = str(n).zfill(2)

            ref_code = lname[:5] + fname[:2] + num

            url = f_rl + l_letter + ref_code + ".html"

            page = requests.get(url).text

            soup = BeautifulSoup(page, "lxml")

            ref_name = soup.find("h1", {"itemprop": "name"}).text.strip().lower()

            n += 1

        name = name.title()

        return name, ref_code, soup, url
    except Exception:
        return None

    # def info(name):


def team(soup):
    try:
        infobox = soup.find(id="info")
        for p in infobox.find_all("p"):
            if "Team" in p.text:
                team = p.a.text

        return team

    except Exception:
        return None


def draft(soup):
    try:
        infobox = soup.find(id="info")

        for p in infobox.find_all("p"):
            if "Draft:" in p.text:
                draft = p.text

        draft = draft.replace("\n", "").split()[1:-2]
        return " ".join(draft)
    except Exception:
        return "Undrafted"


def image(soup):
    try:
        image = soup.find(class_="media-item")
        img = image.find("img")
        return img["src"]
    except Exception:
        return ""


def bling(soup):
    try:
        bling = soup.find(id="bling")
        # print(bling.prettify())
        accs = []
        for acc in bling.find_all("a"):
            accs.append(acc.text)
        r = [i + "\t" + j for i, j in zip(accs[::2], accs[1::2])]

        if len(accs) % 2 != 0:
            r.append(accs[-1])

        return "\n".join(accs)

    except Exception:
        return None


def pns(soup):

    stuff = soup.find(id="info")
    for p in stuff.find_all("p"):
        if "Position" in p.text:
            pns = p.text

    pns = pns.split("\n")
    pns = [l for l in pns if l.strip()]
    # return ''.join(pns)
    stuff = pns[1]
    shoots = pns[4].strip()
    if "and" in stuff:
        pos = stuff.split("and")
    else:
        pos = []
        pos.append(stuff)

    pos = [positions[pos[i].strip()] for i in range(len(pos))]
    pos = "/".join(pos)
    return pos, shoots


def nicknames(soup):
    try:
        nick = soup.find(id="info")
        for p in nick.find_all("p"):

            if not p.find("span") and not p.find("strong"):
                if "(" in p.text:
                    r = p.text
        r = r.replace("\n", "")
        if "," in r:
            x = r.split(",")
            r = ",".join(x[0:3])
            if ")" not in r:
                r += ")"

        return r

    except Exception:
        return " "


def hnw(soup):
    weight = soup.find(attrs={"itemprop": "weight"}).text
    height = soup.find(attrs={"itemprop": "height"}).text
    return height, weight


def death(soup):
    try:
        d = soup.find(id="necro-death")["data-death"]
        deathdate = datetime.strptime(d, "%Y-%m-%d").strftime("%b %d, %Y")
        d = datetime.strptime(d, "%Y-%m-%d")
        db = soup.find(id="necro-birth")["data-birth"]
        db = datetime.strptime(db, "%Y-%m-%d")
        days = abs(d - db).days
        age = days // 365
        return f"{deathdate} (Aged: {age})"
    except Exception:
        return None


def born(soup):
    db = soup.find(id="necro-birth")["data-birth"]
    birthdate = datetime.strptime(db, "%Y-%m-%d").strftime("%b %d, %Y")
    if not death(soup):
        current = datetime.today()
        db = datetime.strptime(db, "%Y-%m-%d")
        days = abs(current - db).days
        age = days // 365
        birthdate += f" ({age})"

    return birthdate


def basic_seasons(soup):
    table = soup.find(id="per_game")
    tbody = table.tbody
    x = len(tbody.find_all("tr"))
    return x


def advanced(soup):

    for comments in soup.find_all(string=lambda text: isinstance(text, Comment)):
        data = BeautifulSoup(comments, "lxml")
        if data.find(id="div_per_minute"):
            pm = data.find(id="div_per_minute")
        elif data.find(id="div_per_poss"):
            poss = data.find(id="div_per_poss")
        elif data.find(id="div_advanced"):
            advanced = data.find(id="div_advanced")
        elif data.find(id="div_playoffs_per_game"):
            playoffs_ppg = data.find(id="div_playoffs_per_game")

    return pm, poss, advanced, playoffs_ppg


def get_pteam(year, psoup):
    yr_id = "playoffs_per_game." + str(year)

    r = psoup.find(id=yr_id)

    team_id = r.find(attrs={"data-stat": "team_id"}).text

    return team_id


def check_team(year, name):
    try:
        soup = identifier(name)[2]

        yr_id = "per_game." + str(year)

        x = soup.find(id=yr_id)

        team = x.find(attrs={"data-stat": "team_id"}).text

        if team == "TOT":
            x = soup.find_all(id=yr_id)[-1]
            team = x.find(attrs={"data-stat": "team_id"}).text

        return team
    except Exception:
        return None


def all_nba(year):
    yr_first = int(year) - 1
    yr_id = str(yr_first) + "-" + str(year)[-2:]

    url = "https://www.basketball-reference.com/awards/all_league.html"

    page = requests.get(url).text
    soup = BeautifulSoup(page, "lxml")

    table = soup.find("tbody")

    tags = ["lg_id", "all_team"]

    player_team = {}

    for tr in table.find_all("tr"):
        if tr.th.text == yr_id:
            for td in tr.find_all("td"):
                if td["data-stat"] not in tags:
                    player = td.a.text
                    player = strip_accents(player)
                    player_team[player] = check_team(year, player)

    return player_team


def get_playoff_matchups(player):

    ref_code = identifier(player)[1]

    url = (
        "https://www.basketball-reference.com/players/"
        + ref_code[0]
        + "/"
        + ref_code
        + "/gamelog-playoffs/"
    )

    page = requests.get(url).text

    soup = BeautifulSoup(page, "lxml")

    table = soup.tbody
    comp_yr = []
    date = ""
    opp = ""

    for tr in table.find_all("tr"):
        if not tr.has_attr("class"):
            temp_date = tr.find("td", attrs={"data-stat": "date_game"}).text[:4]
            temp_opp = tr.find("td", attrs={"data-stat": "opp_id"}).text
            if temp_date != date:
                date = temp_date
                opp = temp_opp
                comp_yr.append((date, opp))
            elif temp_date == date:
                if temp_opp != opp:
                    opp = temp_opp
                    comp_yr.append((date, opp))

    return comp_yr


def check_comp(player):
    opp_teams = get_playoff_matchups(player)

    comp = []
    count = 0

    year = ""
    all_nba_team = ""
    plyr = "-"

    for yr_team in opp_teams:
        yr = yr_team[0]
        tm = yr_team[1]

        if year != yr:
            year = yr
            all_nba_team = all_nba(yr)

        if tm in all_nba_team.values():
            for player, team in all_nba_team.items():
                if team == tm:
                    comp.append((int(yr), tm, player))
                    count += 1
        else:
            comp.append((int(yr), tm, plyr))

    return comp, count


# x = check_comp("Lebron James")


def display_matchups(player):
    comps, count = check_comp(player)

    year = 0
    team = ""

    full_list = ""

    for matchup in comps:
        if matchup[0] != year:
            year = matchup[0]
            full_list += "\n" + str(year)

        if matchup[1] != team:
            team = matchup[1]
            full_list += "\n\t" + team

        full_list += "\n\t\t" + matchup[2]

    full_list = (
        full_list
        + f"\n{player} has faced a total of {count} all NBA players in his career"
    )

    return full_list

