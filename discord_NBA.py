import requests
from bs4 import Comment, BeautifulSoup
from datetime import datetime, date
import unicodedata
import discord
from discord.ext import commands
import re
from matplotlib import pyplot as plt


# discord side code
client = commands.Bot(command_prefix="!")


@client.event
async def on_ready():
    print("Bot is ready")


@client.command(help="use !ping for ping")
async def ping(ctx):
    await ctx.send(f"pong! {round(client.latency*1000)}ms")


# this function gets rid of accented letters
def strip_accents(text):
    try:
        text = unicode(text, "utf-8")
    except NameError:  # unicode is a default on python 3
        pass

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


# gets achievements of player
def get_achievements(name):
    try:
        wiki = "https://en.wikipedia.org/wiki/"
        name = name.lower()
        name = name.title()
        print(name)
        name = name.replace(" ", "_")
        url = wiki + name
        page = requests.get(url).text

        soup = BeautifulSoup(page, "lxml")

        # infobox =  soup.find('table',class_='infobox vcard')
        # tbody = infobox.tbody
        number = 0
        for tr in soup.find_all("tr"):

            try:
                stuff = tr.text
            except Exception:
                stuff = ""
            if stuff == "Career highlights and awards":
                achievements = soup.find_all("tr")[number + 1]
            number += 1

        return achievements.text
    except Exception:
        return "Sorry try again"


@client.command(help="use !achieve <player> for achievements and accolades")
async def achieve(ctx, *, name):
    s = get_achievements(name)
    await ctx.send(f"```{name} \n{s}```")


# function that returns birthdate and age


@client.command(help="use !born <player> for birthdate and age")
async def born(ctx, *, name):
    s = get_born(name)
    await ctx.send(f"{name}\nBorn:  {s}")


player_nicknames = {
    "kd": "Kevin Durant",
    "kat": "Karl-Anthony Towns",
    "boogie": "Demarcus Cousins",
    "flat earth": "Kyrie Irving",
    "king": "Lebron James",
    "ai": "Allen Iverson",
    "mamba": "Kobe Bryant",
    "unicorn": "Kristaps Porzingis",
    "kareem": "Kareem Abdul-Jabbar",
    "no d": "Trae Young",
    "beard": "James Harden",
    "bald mamba": "Alex Caruso",
    "sung roh": "Draymond Green",
    "joowon kim": "Nick Young",
    "frankie kim": "Klay Thompson",
    "elijah kim": "Isaiah Thomas",
    "jithu tirumala": "Buddy Hield",
    "kyeu lee": "Carmelo Anthony",
    "justin lee": "Davis Bertans",
    "sungmin kim": "Lou Williams",
    "michael im": "Jamal Crawford",
    "joung son": "Blake Griffin",
    "giannis": "Giannis Antetokounmpo",
    "nick cho": "kyle lowry",
}
# function for getting stats of nba player(s)
def get_name(name):
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

            global ref_code
            ref_code = lname[:5] + fname[:2] + num

            global url
            url = f_rl + l_letter + ref_code + ".html"

            page = requests.get(url).text

            global soup
            soup = BeautifulSoup(page, "lxml")

            global table
            table = soup.find(id="per_game")

            ref_name = soup.find("h1", {"itemprop": "name"}).text.strip().lower()

            n += 1

            adv = []
            for comments in soup.find_all(
                string=lambda text: isinstance(text, Comment)
            ):
                if "advanced" in comments:
                    data = BeautifulSoup(comments, "lxml")
                    advanced = data.find(id="div_advanced")
                    adv.append(advanced)

            global a_table
            a_table = adv[0]

            global needed

            needed = [
                "Season",
                "Age",
                "Tm",
                "Pos",
                "G",
                "PER",
                "TS%",
                "3PAr",
                "FTr",
                "USG%",
                "WS",
                "BPM",
                "VORP",
                "season",
                "age",
                "team_id",
                "pos",
                "g",
                "per",
                "ts_pct",
                "fg3a_per_fga_pct",
                "fta_per_fga_pct",
                "usg_pct",
                "ws",
                "bpm",
                "vorp",
            ]

            global not_needed

            not_needed = [
                "Lg",
                "2P",
                "2PA",
                "2P%",
                "DRB",
                "PF",
                "GS",
                "3PA",
                "ORB",
                "FG",
                "FGA",
                "3P",
                "eFG%",
                "FT",
                "FTA",
                "TOV",
                "Pos",
                "tov_per_g",
                "fga_per_g",
                "fg3_per_g",
                "pos",
                "efg_pct",
                "ft_per_g",
                "fta_per_g",
                "gs",
                "fg3a_per_g",
                "fg2_per_g",
                "fg2a_per_g",
                "fg2_pct",
                "orb_per_g",
                "drb_per_g",
                "pf_per_g",
                "lg_id",
                "fg_per_g",
            ]

        return name.title()
    except Exception:
        return "player not found"


def draft_pick(name):
    try:
        get_name(name)

        infobox = soup.find(id="info")

        for p in infobox.find_all("p"):
            if "Draft:" in p.text:
                draft = p.text

        draft = draft.replace("\n", "").split()[1:-2]
        return " ".join(draft)
    except Exception:

        return "Undrafted"


def get_curr_team(name):
    try:
        get_name(name)
        infobox = soup.find(id="info")
        for p in infobox.find_all("p"):
            if "Team" in p.text:
                team = p.a.text

        return team

    except Exception:
        return None


def get_header(name):
    try:

        get_name(name)
        table = soup.find(id="per_game")
        header = [
            th.text for th in table.thead.tr.find_all("th") if th.text not in not_needed
        ]

        header_format = "{:>7}" * (len(header) + 1)
        header = str((header_format.format("", *header)))
        return header

    except Exception:
        return "Data not found"


def get_stats(yr, name):
    # allows access to the correct basketball reference page
    try:
        name = get_name(name)
        # lists for printing header and stats
        stats = []

        table = soup.find(id="per_game")

        # list of unecessary stats

        stat_dict = {
            "PTS": "pts_per_g",
            "TRB": "trb_per_g",
            "AST": "ast_per_g",
            "FT%": "ft_pct",
            "3P%": "fg_3pct",
            "STL": "stl_per_g",
            "BLK": "blk_per_g",
            "MP": "mp_per_g",
            "3P": "fg3_per_g",
        }

        year = str(yr)
        if year.isdigit():
            year = int(year)
            tbody = table.tbody
            if year < 100:
                year -= 1
                stuff = tbody.find_all("tr")[year]

            elif year > 100:
                year = "per_game." + str(year)
                stuff = tbody.find(id=year)

            if stuff.has_attr("id"):
                for tag in stuff.find_all():
                    if tag.has_attr("data-stat"):
                        if tag["data-stat"] not in not_needed:
                            stats.append(tag.text)

            elif not stuff.has_attr("id"):
                for tag in stuff.find_all():
                    stat = tag.text
                    if "Did Not" in stat:
                        stat = "     " + stat
                    stats.append(stat)

            stat_format = "{:>7}" * (len(stats) + 1)
            stats = str((stat_format.format("", *stats)))
            return stats

        elif year.isalpha():
            if year == "career":
                for stat in table.tfoot.find("tr"):
                    if stat["data-stat"] not in not_needed:
                        stats.append(stat.text)

                stat_format = "{:>7}" * (len(stats) + 1)
                stats = str((stat_format.format("", *stats)))
                return f"{stats}"

            elif year == "last":
                seasons = len(table.tbody.find_all("tr"))
                last_num = seasons - 1
                stuff = table.tbody.find_all("tr")[last_num]

                if stuff.has_attr("id"):
                    for tag in stuff.find_all():
                        if tag.has_attr("data-stat"):
                            if tag["data-stat"] not in not_needed:
                                stats.append(tag.text)

                elif not stuff.has_attr("id"):
                    for tag in stuff.find_all():
                        stat = tag.text
                        stats.append(stat)

                    stats[2] = "   " + stats[2]

                stat_format = "{:>7}" * (len(stats) + 1)
                stats = str((stat_format.format("", *stats)))
                return f"{stats}"

            elif year == "rookie":
                for tr in table.tbody.find_all("tr"):
                    if tr.has_attr("id"):
                        stuff = tr
                        break

                for tag in stuff.find_all():
                    if tag.has_attr("data-stat"):
                        if tag["data-stat"] not in not_needed:
                            stats.append(tag.text)

                stat_format = "{:>7}" * (len(stats) + 1)
                stats = str((stat_format.format(" ", *stats)))
                return stats

            elif year in stat_dict:
                stat_needed = 0.0
                stuff = table.tbody
                index = 0
                all_stats = stuff.find_all(attrs={"data-stat": stat_dict[year]})
                for stat_get in all_stats:
                    if float(stat_get.text) > stat_needed:
                        stat_needed = float(stat_get.text)
                        high_year = stuff.find_all(attrs={"data-stat": "season"})[
                            index
                        ].text

                    index += 1

                stats.append(high_year)
                stats.append(stat_needed)

                stat_format = "{:>7}" * (len(stats) + 1)
                stats = str((stat_format.format(" ", *stats)))
                return f"{stats}"

    except Exception:
        print("Data not found")


def get_adv_header(name):
    get_name(name)

    header = [th.text for th in a_table.thead.find_all("th") if th.text in needed]

    header_format = "{:>7}" * (len(header) + 1)
    header = str((header_format.format("", *header)))

    return header


def get_adv_stats(yr, name):
    try:
        get_name(name)

        year = str(yr)

        if year.isdigit():
            year = int(year)
            tbody = a_table.tbody
            if year < 100:
                year -= 1
                stuff = tbody.find_all("tr")[year]

            elif year > 100:
                year = "advanced." + str(year)
                stuff = tbody.find(id=year)

            stats = [stat.text for stat in stuff if stat["data-stat"] in needed]

            stat_format = "{:>7}" * (len(stats) + 1)
            stats = str((stat_format.format("", *stats)))
            return stats

        elif year.isalpha():
            if year == "career":
                stuff = a_table.table.tfoot.find("tr")

            elif year == "last":
                seasons = len(a_table.tbody.find_all("tr"))
                last_num = seasons - 1
                stuff = a_table.tbody.find_all("tr")[last_num]

            elif year == "rookie":
                stuff = a_table.tbody.find("tr")

        stats = [stat.text for stat in stuff if stat["data-stat"] in needed]
        stat_format = "{:>7}" * (len(stats) + 1)
        stats = str((stat_format.format("", *stats)))
        return stats

    except Exception:
        return " "


def get_seasons(name):
    get_name(name)
    table = soup.find(id="per_game")
    tbody = table.tbody
    x = len(tbody.find_all("tr"))
    return x


def get_a_seasons(name):
    get_name(name)

    x = len(a_table.tbody.find_all("tr"))

    return x


def get_image(name):
    try:
        get_name(name)
        image = soup.find(class_="media-item")
        img = image.find("img")
        return img["src"]
    except Exception:
        return ""


def get_pns(name):
    get_name(name)
    positions = {
        "Point Guard": "PG",
        "Shooting Guard": "SG",
        "Small Forward": "SF",
        "Power Forward": "PF",
        "Center": "C",
    }
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
    return f"\nPosition: {pos}\nShoots: {shoots}"


def get_hnw(name):
    get_name(name)
    weight = soup.find(attrs={"itemprop": "weight"}).text
    height = soup.find(attrs={"itemprop": "height"}).text
    return f"{height}, {weight}"


def get_nickname(name):
    try:
        get_name(name)
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


def get_death(name):
    try:
        get_name(name)
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


def get_born(name):
    get_name(name)
    db = soup.find(id="necro-birth")["data-birth"]
    birthdate = datetime.strptime(db, "%Y-%m-%d").strftime("%b %d, %Y")
    if not get_death(name):
        current = datetime.today()
        db = datetime.strptime(db, "%Y-%m-%d")
        days = abs(current - db).days
        age = days // 365
        return f"{birthdate} (Age: {age})"
    else:
        return f"{birthdate}"


def get_bling(name):
    try:
        get_name(name)
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


@client.command(help="use !<player> to get quick description of player")
async def info(ctx, *, name):
    n = get_name(name)
    birthdate = get_born(n)
    deathdate = get_death(n)
    nicknames = str(get_nickname(n))
    picture = get_image(n)
    pns = get_pns(n)
    hnw = get_hnw(n)
    accs = get_bling(n)
    descript = f"{nicknames}{pns}\n{hnw}"
    seasons = get_seasons(n)
    drafted = draft_pick(n)
    curr = get_curr_team(name)
    embed = discord.Embed(title=n, description=descript)
    embed.set_thumbnail(url=picture)
    embed.add_field(name="Born", value=birthdate, inline=False)
    if deathdate:
        embed.add_field(name="Died", value=deathdate, inline=False)
    embed.add_field(name="Drafted", value=drafted, inline=False)
    if curr:
        embed.add_field(name="Current Team", value=curr, inline=True)
    embed.add_field(name="Experience", value=seasons, inline=True)
    if accs:
        embed.add_field(name="Bling", value=accs, inline=False)
    await ctx.send(embed=embed)


@client.command(help="use !year <year or NBA year> <player> for player stats")
async def year(ctx, year, *, name):
    rando = []
    rando.append(get_name(name))
    rando.append(get_header(name))

    if year.lower() == "all":
        num = get_seasons(name)
        for x in range(1, num + 1):
            rando.append(get_stats(x, name))
        rando.append(get_stats("career", name))

    else:
        rando.append(get_stats(year, name))

    r = "\n".join(rando)
    await ctx.send(f"```\n{r}\n```")


@client.command(help="use !astat <year or NBA year> <player> for player advanced stats")
async def astat(ctx, year, *, name):
    rando = []
    rando.append(get_name(name))
    rando.append(get_adv_header(name))

    if year.lower() == "all":
        num = get_a_seasons(name)
        for x in range(1, num + 1):
            rando.append(get_adv_stats(x, name))
        rando.append(get_adv_stats("career", name))
    else:
        rando.append(get_adv_stats(year, name))

    r = "\n".join(rando)
    await ctx.send(f"```\n{r}\n```")


@client.command(
    help="use !full <year or NBA year> <player> for player stats and advanced stats"
)
async def full(ctx, year, *, name):
    rando = []
    rando.append(get_name(name))
    rando.append(get_header(name))
    rando.append(get_stats(year, name))
    rando.append(get_adv_header(name))
    rando.append(get_adv_stats(year, name))

    r = "\n".join(rando)

    await ctx.send(f"```\n{r}\n```")


def standings(year, conference):
    url = "https://www.basketball-reference.com/leagues/NBA_"
    e_url = str(year) + "_standings.html"
    url += e_url
    page = requests.get(url).text
    stand = BeautifulSoup(page, "html.parser")
    max_ = 28
    space = " "
    lines = (" " * 7) + ("-" * 79)

    if conference.lower()[0] == "i":
        info = stand.find(id="meta")
        i = info.find_all("p")
        y = [p.text for p in i if p.text]
        x = y[2:]
        return "\n".join(x)

    if int(year) > 2015:
        if conference.lower()[0] == "e":
            con_id = "all_confs_standings_E"
        elif conference.lower()[0] == "w":
            con_id = "all_confs_standings_W"

        conf = stand.find(id=con_id)
        thead = conf.thead
        head = [th.text for th in thead.find_all("th") if thead.text]
        header_format = "{:^7}" * (len(head) + 1)
        body = conf.tbody
        space = " "
        teams = []
        head[0] += (max_ - len(head[0])) * space
        teams.append(str(header_format.format(" ", *head)))

        for tr in body.find_all("tr"):

            team = [stuff.text for stuff in tr]
            len_ = max_ - len(team[0])
            team[0] += space * len_
            teams.append(str(header_format.format(" ", *team)))

        teams.insert(9, lines)
        r = "\n".join(teams)

    elif int(year) <= 2015:

        if conference.lower()[0] == "e":
            con_id = "divs_standings_E"
        elif conference.lower()[0] == "w":
            con_id = "divs_standings_W"

        conf = stand.find(id=con_id)
        thead = conf.thead
        head = [th.text for th in thead.find_all("th") if thead.text]
        body = conf.find("tbody")
        header_format = "{:^7}" * (len(head) + 1)
        head[0] += (max_ - len(head[0])) * space
        header = str(header_format.format(" ", *head))

        amt_teams = len(body.find_all(class_="full_table"))
        table = [" "] * amt_teams

        for tr in body.find_all(class_="full_table"):
            team = [stuff.text for stuff in tr]
            num = ""
            name = team[0]
            for r in name:
                if r.isdigit():
                    num += r
            if "76" in num:
                num = num.replace("76", "")

            len_ = max_ - len(team[0])
            team[0] += space * len_
            table[int(num) - 1] = team

        dif = float(table[0][1]) - float(table[0][2])
        teams = []
        for team in table:

            dif = float(team[1]) - float(team[2])
            gb = str((dif - dif) / 2)
            if gb != "0.0":
                team[4] = gb

            teams.append(str(header_format.format(" ", *team)))

        teams.insert(0, header)

        lines = (" " * 7) + ("-" * 73)
        teams.insert(9, lines)

        r = "\n".join(teams)

    elif int(year) < 1971:
        return "Wrong number, homie. Try something higher"

    return r


@client.command(help="use !<year> <conference/none> to get standings for year")
async def stand(ctx, year, conference=None):

    season = str(int(year) - 1) + "-" + str(year[-2:])

    if conference == None:
        e = standings(year, "east")
        w = standings(year, "west")
        i = standings(year, "info")

        await ctx.send(f"```Season: {season}\n{i}```")
        await ctx.send(f"```{e}```")
        await ctx.send(f"```{w}```")
    else:
        r = standings(year, conference)
        await ctx.send(f"```Season: {season}\n{r}```")


def get_team(year, name):
    try:
        year = str(year)
        global nba_teams
        nba_teams = {
            "Hawks": "atl",
            "Nets": "njn",
            "Celtics": "bos",
            "Hornets": "cha",
            "Bulls": "chi",
            "Cavs": "cle",
            "Mavs": "dal",
            "Pistons": "det",
            "Warriors": "gsw",
            "Rockets": "hou",
            "Pacers": "ind",
            "Clippers": "lac",
            "Lakers": "lal",
            "Grizzlies": "mem",
            "Heat": "mia",
            "Bucks": "mil",
            "Timberwolves": "min",
            "Pelicans": "noh",
            "Magic": "orl",
            "76ers": "phi",
            "Suns": "pho",
            "Blazers": "por",
            "Kings": "sac",
            "Spurs": "sas",
            "Raptors": "tor",
            "Jazz": "uta",
            "Wizards": "was",
            "Thunder": "okc",
            "Supersonics": "okc",
            "Nuggets": "den",
            "Knicks": "nyk",
        }
        if name.lower() in nba_teams.values():
            name = name.upper()
        elif name.title() in nba_teams:
            name = nba_teams[name.title()].upper()

        url = "https://www.basketball-reference.com/teams/"
        url += name + "/"
        if year.isdigit():
            url += year + ".html"
        page = requests.get(url).text

        team = BeautifulSoup(page, "lxml")

        global team_img
        team_img = team.find(class_="teamlogo")["src"]
        infobox = team.find(id="info")

        global team_name
        team_name = infobox.find(itemprop="name").text.strip().replace("\n", " ")
        print(team_name)
        # print(f'Image: {team_img}')

        if year.isalpha():
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

            global team_seasons
            team_seasons = (
                season[1]
                + " ("
                + season[-3][:-2]
                + season[-1][:2]
                + season[-1][-2:]
                + ")"
            )

            global team_record
            team_record = " ".join(record[1:4])

            global team_playoff_app
            team_playoff_app = playoff[2]

            global team_champ
            team_champ = champs[1]

            top_list = []
            for comments in team.find_all(
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

            global top_twelve
            top_twelve = "\n".join(top_list)

            print(f"Seasons: {team_seasons}")
            print(f"Record: {team_record}")
            print(f"Playoff Appearances: {team_playoff_app}")
            print(f"Championships: {team_champ}")
            print(f"All-Time Top 12 Players: \n{top_twelve}")
            print(f"max length: {max_len}")
            print()
        elif year.isdigit():
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

            global team_curr_team, team_coach, team_exec, pts_g, opp_g, srs, pace, off_rtg, def_rtg, expected_WL, p_odds, team_arena, playoff_header, play_series

            team_curr_team = " ".join(record[1:])
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

            print(f"Record: {team_curr_team}")
            print(f"Coach: {team_coach}")
            print(f"Exectuive: {team_exec}")
            print(f"PTS/G: {pts_g}\tOpp PTS/G: {opp_g}")
            print(f"SRS: {srs}\tPace: {pace}")
            print(f"Off Rtg: {off_rtg}\tDef Rtg: {def_rtg}")
            print(f"Expected W-L: {expected_WL}")
            print(f"Preseason Odds: {p_odds}")
            print(f"Arena: {team_arena}")
            print(f"{playoff_header}\n{play_series}")
    except Exception:
        return None


@client.command()
async def team(ctx, year, name):
    get_team(year, name)
    embed = discord.Embed(title=team_name)
    embed.set_thumbnail(url=team_img)
    if year.isalpha():
        embed.add_field(name="Seasons", value=team_seasons, inline=False)
        embed.add_field(name="Record", value=team_record, inline=False)
        embed.add_field(
            name="Playoff Appearances", value=team_playoff_app, inline=False
        )
        embed.add_field(name="Championships", value=team_champ, inline=False)
        embed.add_field(
            name="All-Time Top 12 Players", value=f"```{top_twelve}```", inline=False
        )
    elif year.isdigit():
        embed.add_field(name="Record", value=team_curr_team, inline=False)
        embed.add_field(name="Coach", value=team_coach, inline=False)
        embed.add_field(name="Executive", value=team_exec, inline=False)
        embed.add_field(name="PTS/G", value=pts_g, inline=True)
        embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
        embed.add_field(name="Opp PTS/G", value=opp_g, inline=True)
        embed.add_field(name="SRS", value=srs, inline=True)
        embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
        embed.add_field(name="Pace", value=pace, inline=True)
        embed.add_field(name="Off Rtg", value=off_rtg, inline=True)
        embed.add_field(name="\uFEFF", value="\uFEFF", inline=True)
        embed.add_field(name="Def Rtg", value=def_rtg, inline=True)
        embed.add_field(name="Expected W-L", value=expected_WL, inline=False)
        embed.add_field(name="Preseason Odds", value=p_odds, inline=False)
        embed.add_field(name="Arena", value=team_arena, inline=False)
        if playoff_header:
            embed.add_field(name=playoff_header, value=play_series, inline=False)

    await ctx.send(embed=embed)


def points(*names):
    players = []
    titles = []
    colors = ["blue", "red", "green", "orange", "black", "violet", "brown", "yellow"]
    for name in names:
        titles.append(get_name(name))
        players.append(
            [
                float(points.text)
                for points in table.tbody.find_all(attrs={"data-stat": "pts_per_g"})
            ]
        )

    max_p = len(max(players, key=len))
    for i in range(len(players)):
        p = players[i]
        p += [None] * (max_p - len(p))
        players[i] = p

    years = []
    yr = 0
    while yr < max_p:
        yr += 1
        years.append(yr)
    for i in range(len(players)):
        plt.plot(years, players[i], color=colors[i], label=titles[i])

    plt.xlabel("NBA Years")
    plt.ylabel("Points per game")
    plt.title("Points Per game by NBA Year")

    plt.legend()  # uses labels given to lines

    plt.grid()

    plt.savefig("plot.png")

    plt.show()

    print(players)


def get_stat(year, stat, name=None):
    url = "https://www.basketball-reference.com/leagues/NBA_"
    if name in player_nicknames:
        name = player_nicknames[name]

    key_words = ["SF", "SG", "PG", "C", "PF", "W", "E", "WEST", "EAST"]
    positions = [
        "SF",
        "SG",
        "PG",
        "C",
        "PF",
    ]
    conferences = {"e": "east", "w": "west"}

    west = [
        "LAL",
        "LAC",
        "DEN",
        "OKC",
        "UTA",
        "HOU",
        "DAL",
        "MEM",
        "POR",
        "SAS",
        "PHO",
        "SAC",
        "GSW",
        "MIN",
        "NOP",
    ]

    east = [
        "MIL",
        "TOR",
        "BOS",
        "MIA",
        "IND",
        "PHI",
        "ORL",
        "NJN",
        "WAS",
        "CHA",
        "CHI",
        "NYK",
        "DET",
        "ATL",
        "CLE",
    ]

    global nba_key, adv_key

    nba_key = {
        "pos": "pos",
        "age": "age",
        "tm": "team_id",
        "g": "g",
        "gs": "gs",
        "mp": "mp_per_g",
        "fg": "fg_per_g",
        "fga": "fga_per_g",
        "fg%": "fg_pct",
        "3p": "fg3_per_g",
        "3pa": "fg3a_per_g",
        "3p%": "fg3_pct",
        "2p": "fg2_per_g",
        "2pa": "fg2a_per_g",
        "2p%": "fg2_pct",
        "efg%": "efg_pct",
        "ft": "ft_per_g",
        "fta": "fta_per_g",
        "ft%": "ft_pct",
        "orb": "orb_per_g",
        "drb": "drb_per_g",
        "trb": "trb_per_g",
        "ast": "ast_per_g",
        "stl": "stl_per_g",
        "blk": "blk_per_g",
        "tov": "tov_per_g",
        "pf": "pf_per_g",
        "pts": "pts_per_g",
    }

    adv_key = {
        "per": "per",
        "ts%": "ts_pct",
        "3par": "fg3a_per_fga_pct",
        "ftr": "fta_per_fga_pct",
        "orb%": "orb_pct",
        "drb%": "brd_pct",
        "trb%": "trb_pct",
        "ast%": "ast_pct",
        "stl%": "stl_pct",
        "blk%": "blk_pct",
        "tov%": "tov_pct",
        "usg%": "usg_pct",
        "ows": "ows",
        "dws": "dws",
        "ws": "ws",
        "ws/48": "ws_per_48",
        "obpm": "obpm",
        "dbpm": "dbpm",
        "bpm": "bpm",
        "vorp": "vorp",
    }
    if stat in nba_key or stat in nba_key.values():
        url += str(year) + "_per_game.html"
        stat = nba_key.get(stat, stat)

    if stat in adv_key or stat in adv_key.values():
        url += str(year) + "_advanced.html"
        stat = adv_key.get(stat, stat)

    page = requests.get(url).text

    soup = BeautifulSoup(page, "lxml")

    global values, value

    players = {}

    number = "10"

    title = soup.thead.find(attrs={"data-stat": stat}).text

    if name:
        name = name.split()

        if name[0].upper() in key_words or name[0].isdigit():

            position = None
            conference = None
            for i in name:
                if i in conferences or i in conferences.values():
                    conference = conferences.get(i, i)
                if i.upper() in positions:
                    position = i.upper()
                if i.isdigit():
                    number = i

            for p in soup.tbody.find_all("tr", class_="full_table"):

                pos = p.find(attrs={"data-stat": "pos"}).text
                playa = p.find(attrs={"data-stat": "player"}).text
                value = p.find(attrs={"data-stat": stat}).text
                games = int(p.find(attrs={"data-stat": "g"}).text)
                if value[-1].isdigit():
                    value = float(value)
                team = p.find(attrs={"data-stat": "team_id"}).text
                if games >= 40:
                    if position:
                        if position in pos:
                            if conference == "west":
                                if team in west:
                                    players[playa] = float(value)
                            elif conference == "east":
                                if team in east:
                                    players[playa] = value
                            else:
                                players[playa] = value
                    else:
                        if conference == "west":
                            if team in west:
                                players[playa] = value
                        elif conference == "east":
                            if team in east:
                                players[playa] = value
                        else:
                            players[playa] = value

        else:

            name = " ".join(name)

            for p in soup.tbody.find_all(attrs={"data-stat": "player"}):
                play = strip_accents(p.text)
                play = play.replace("*", "")
                if play.lower() == name.lower():
                    player = p.parent
                    playa = p.text.replace("*", "")

            value = player.find(attrs={"data-stat": stat}).text

            if value[-1].isdigit():
                value = float(value)

            players[playa] = value

    elif not name:

        for p in soup.tbody.find_all("tr", class_="full_table"):
            playa = p.find(attrs={"data-stat": "player"}).text
            value = p.find(attrs={"data-stat": stat}).text
            games = int(p.find(attrs={"data-stat": "g"}).text)

            if value[-1].isdigit():
                value = float(value)

            if games >= 40:
                players[playa] = value

    sort_values = sorted(players.items(), key=lambda x: x[1], reverse=True)[
        : int(number)
    ]

    v = []
    t = ("Player", title)
    sort_values.insert(0, t)

    for i in sort_values:
        p = i[0] + ((25 - len(i[0])) * " ") + str(i[1])
        v.append(p)

    values = "\n".join(v)

    return values


@client.command()
async def stat(ctx, year, stat, *, name=None):

    get_stat(year, stat, name)

    await ctx.send(f"```{values}```")


def get_record(year, stats, values, names):

    stats = stats.split(",")
    values = values.split(",")

    stat_r = {}

    names = names.split(",")
    t = []
    r = []
    f_url = "https://www.basketball-reference.com"

    for name in names:
        get_name(name)
        get_stat(year, "tm", name)
        t.append(value)
        r.append(ref_code)

    for i in range(len(stats)):

        stat_r[stats[i]] = float(values[i])

    result = all(i == t[0] for i in t)

    if not result:
        print("sorry not on the same Team")
    else:

        team_id = t[0]
        url = f_url + "/teams/" + team_id + "/" + str(year) + "_games.html"

        wins, losses = 0, 0

        if stats[0] in nba_key or stats[0] in nba_key.values():
            box_id = "box-" + team_id + "-game-basic"
        elif stats[0] in adv_key or stats[0] in adv_key.values():
            box_id = "box-" + team_id + "-game-advanced"

        page = requests.get(url).text

        log = BeautifulSoup(page, "lxml")

        for game in log.tbody.find_all("tr", class_=False):
            gr = game.find(attrs={"data-stat": "game_result"}).text
            if gr == "W" or gr == "L":
                a_tag = game.find(attrs={"data-stat": "box_score_text"}).a["href"]

                box_url = f_url + a_tag

                b_page = requests.get(box_url).text

                box = BeautifulSoup(b_page, "lxml")

                b_table = box.find("table", id=box_id)

                b_result = []

                for r_code in r:

                    if b_table.find("th", attrs={"data-append-csv": r_code}):
                        s_playa = b_table.find(
                            "th", attrs={"data-append-csv": r_code}
                        ).parent

                        s_result = []

                        for s, v in stat_r.items():
                            if s_playa.find(attrs={"data-stat": s}):
                                s_stat = s_playa.find(attrs={"data-stat": s}).text
                                if ":" in s_stat:
                                    (m, s) = s_stat.split(":")
                                    s_stat = int(m) + int(s) / 60

                                if float(s_stat) >= v:
                                    s_result.append(True)
                                else:
                                    s_result.append(False)
                            else:
                                s_result.append(False)

                        b_result.append(all(i == True for i in s_result))

                    else:
                        b_result.append(False)

                stat_met = all(i == True for i in b_result)

                if stat_met == True:
                    if gr == "W":
                        wins += 1
                    else:
                        losses += 1

        players = ", ".join(names)

        sentence = "When " + players + " put(s) up "

        for s, v in stat_r.items():
            phrase = str(v) + " " + s + " "
            sentence += phrase

        sentence += "their record is:"

        print(sentence)
        print(f"W-L: {wins}-{losses}")

        global paragraph

        paragraph = sentence + f"\n{wins}-{losses}"


@client.command()
async def record(ctx, year, stats, values, *, names):
    get_record(year, stats, values, names)

    await ctx.send(f"```{paragraph}```")

client.run(client-token)




