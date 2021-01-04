from player import Player
from bs4 import BeautifulSoup
import requests
from dnl import stat_full_name, nba_teams


def get_record_with(year, diff, stat, value, player):
    stat = str(stat)
    value = str(value)
    player = str(player)

    stats = stat.split(",")
    values = value.split(",")
    players = player.split(",")

    stat_full = []
    stat_verb = []
    for i in stats:
        stat_full.append(stat_full_name.get(i))
        if i in ["fg_pct", "fg3_pct", "fgp2_pct", "efg_pct", "ft_pct"]:
            stat_verb.append("shoot")
        elif i in ["mp"]:
            stat_verb.append("play")
        elif i in ["fg", "fg3", "fg2", "ft"]:
            stat_verb.append("make")
        elif i in ["fga", "fg3a", "fg2a", "fta"]:
            stat_verb.append("attempt")
        elif i in ["orb", "drb", "trb"]:
            stat_verb.append("grab")
        elif i in ["ast"]:
            stat_verb.append("dish")
        elif i in ["pts"]:
            stat_verb.append("score")
        else:
            stat_verb.append("get")

    values_full = []
    for i in values:
        i = float(i)
        if i < 1:
            i *= 100
        i = str(i)
        values_full.append(i)

    stat_r = {}
    for i in range(len(stats)):
        stat_r[stats[i]] = float(values[i])

    log_urls = []
    player_names = []
    for name in players:
        player = Player(name)
        player_names.append(player.name)
        log_urls.append(player.get_game_log(year))

    wins, losses = 0, 0

    if any(x == None for x in log_urls):
        return "Cannot find"
    else:
        tables = []
        for url in log_urls:
            page = requests.get(url).text
            soup = BeautifulSoup(page, "lxml")
            x = soup.find(id="pgl_basic")
            tables.append(x)
        same = []
        for x in tables:
            teams = []

            for tm in x.tbody.find_all("tr", class_=False):
                team = tm.find(attrs={"data-stat": "date_game"}).a["href"]
                if tm.find(attrs={"data-stat": "pts"}):
                    stat_true = []
                    for s, v in stat_r.items():
                        stat = tm.find(attrs={"data-stat": s}).text
                        if ":" in stat:
                            (m, s) = stat.split(":")
                            stat = int(m) + int(s) / 60
                        if diff == "more":
                            stat_true.append(float(stat) >= v)
                        elif diff == "less":
                            stat_true.append(float(stat) < v)
                    if all(x == True for x in stat_true):
                        teams.append(team)

            same.append(list(set(teams)))

        g_urls = set.intersection(*[set(l) for l in same])
        g_urls = list(g_urls)

        if len(g_urls) == 0:
            return "There are no games with these stat lines"

        soup = tables[0]

        for url in g_urls:
            for tm in soup.tbody.find_all("tr", class_=False):
                team = tm.find(attrs={"data-stat": "date_game"}).a["href"]
                if team == url:
                    result = tm.find(attrs={"data-stat": "game_result"}).text[0]
                    if result == "W":
                        wins += 1
                    elif result == "L":
                        losses += 1

    print(f"{wins}-{losses}")

    names = ", ".join(player_names)
    sentence = f"When {names}"
    stat_line = []

    for i in range(len(stat_full)):
        x = " "
        verb = stat_verb[i]
        if len(player_names) == 1:
            if verb == "dish":
                verb += "es"
            else:
                verb += "s"
        x += verb + f" {diff} than " + values_full[i] + " " + stat_full[i]
        stat_line.append(x)
    stat_line = " and ".join(stat_line)
    sentence += stat_line + ", "
    end = f"the team's record is: {wins}-{losses}"
    sentence += end
    return sentence

