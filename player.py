from playerfunc import (
    identifier,
    team,
    draft,
    image,
    bling,
    pns,
    nicknames,
    hnw,
    born,
    death,
    basic_seasons,
    advanced,
    check_comp,
    display_matchups,
)

from dnl import (
    stats_needed,
    stats_not_needed,
    per_game,
    advanced_stats,
    poss_stats,
    min_stats,
)


class Player:
    def __init__(self, player):
        data = identifier(player)
        self.name = data[0]
        self.code = data[1]
        self.soup = data[2]
        self.url = data[3]

    def info(self):
        self.team = team(self.soup)
        self.draft = draft(self.soup)
        self.image = image(self.soup)
        self.bling = bling(self.soup)

        self.position, self.shoots = pns(self.soup)
        self.nicknames = nicknames(self.soup)

        self.height, self.weight = hnw(self.soup)

        self.born = born(self.soup)
        self.death = death(self.soup)
        self.seasons = basic_seasons(self.soup)

    def tables(self):
        self.pm, self.poss, self.advanced, self.playoffs = advanced(self.soup)

    def description(self):
        descript = f"{self.nicknames}\nPosition: {self.position}\tShoots: {self.shoots}\nHeight: {self.height}\tWeight: {self.weight}"

        return descript

    def basic_header(self):
        try:

            table = self.soup.find(id="per_game")
            header = [
                th.text
                for th in table.thead.tr.find_all("th")
                if th.text not in stats_not_needed
            ]

            header_format = "{:>7}" * (len(header) + 1)
            header = str((header_format.format("", *header)))
            return header

        except Exception:
            return "Data not found"

    def basic_stats(self, year):
        try:
            stats = []

            table = self.soup.find(id="per_game")

            year = str(year)
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
                            if tag["data-stat"] not in stats_not_needed:
                                stats.append(tag.text)

                elif not stuff.has_attr("id"):
                    for tag in stuff.find_all():
                        stat = tag.text
                        if "Did Not" in stat:
                            stat = "     " + stat
                        stats.append(stat)

            elif year.isalpha():
                if year == "career":
                    for stat in table.tfoot.find("tr"):
                        if stat["data-stat"] not in stats_not_needed:
                            stats.append(stat.text)

                elif year == "last":
                    seasons = len(table.tbody.find_all("tr"))
                    last_num = seasons - 1
                    stuff = table.tbody.find_all("tr")[last_num]

                    if stuff.has_attr("id"):
                        for tag in stuff.find_all():
                            if tag.has_attr("data-stat"):
                                if tag["data-stat"] not in stats_not_needed:
                                    stats.append(tag.text)

                    elif not stuff.has_attr("id"):
                        for tag in stuff.find_all():
                            stat = tag.text
                            stats.append(stat)

                        stats[2] = "   " + stats[2]

                elif year == "rookie":
                    for tr in table.tbody.find_all("tr"):
                        if tr.has_attr("id"):
                            stuff = tr
                            break

                    for tag in stuff.find_all():
                        if tag.has_attr("data-stat"):
                            if tag["data-stat"] not in stats_not_needed:
                                stats.append(tag.text)

            stat_format = "{:>7}" * (len(stats) + 1)
            stats = str((stat_format.format("", *stats)))
            return stats
        except Exception:
            return "Data not found"

    def stat(self, year, stat):
        if stat in per_game or stat in per_game.values():
            stat = per_game.get(stat, stat)
            stat_id = "per_game."
            soup = self.soup

        elif stat in advanced_stats or stat in advanced_stats.values():
            stat = advanced_stats.get(stat, stat)
            stat_id = "advanced."
            soup = advanced(self.soup)[2]

        elif stat in min_stats or stat in min_stats.values():
            stat = min_stats.get(stat, stat)
            stat_id = "per_minute."
            soup = advanced(self.soup)[0]

        elif stat in poss_stats or stat in poss_stats.values():
            stat = poss_stats.get(stat, stat)
            stat_id = "per_poss."
            soup = advanced(self.soup)[1]

        stat_id += str(year)

        stat_row = soup.find(id=stat_id)

        header = soup.thead.find(attrs={"data-stat": stat}).text

        value = stat_row.find(attrs={"data-stat": stat}).text

        return header, value

    def get_game_log(self, year):
        x = self.soup.find(id="bottom_nav_container")
        url = "https://www.basketball-reference.com"
        log = None
        logs = x.find_all("ul")[0]

        for a in logs.find_all("a"):
            if str(year) == a["href"][-4:]:
                log = url + a["href"]

        return log

    def show_comp(self):
        return display_matchups(self.name)

