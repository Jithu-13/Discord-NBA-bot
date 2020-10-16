from teamfunc import identifier
from dnl import nba_teams


class Team:
    def __init__(self, name):
        if name.title() in nba_teams or name.lower() in nba_teams.values():
            self.code = nba_teams.get(name.title(), name).upper()

    def set_attrs(self, year=None):
        if year == None:
            data = identifier(self.code)
            self.name = data[0]
            self.img = data[1]
            self.seasons = data[2]
            self.record = data[3]
            self.playoffs = data[4]
            self.champs = data[5]
            self.top_players = data[6]
            self.year = None
        elif year:
            data = identifier(self.code, year)
            self.soup = data[0]
            self.name = data[1]
            self.img = data[2]
            self.record = data[3]
            self.coach = data[4]
            self.exec = data[5]
            self.pts_g = data[6]
            self.opp_g = data[7]
            self.srs = data[8]
            self.pace = data[9]
            self.off_rtg = data[10]
            self.def_rtg = data[11]
            self.expected_WL = data[12]
            self.p_odds = data[13]
            self.arena = data[14]
            self.playoff_header = data[15]
            self.play_series = data[16]
            self.year = year

    def get_attrs(self):

        if self.year:
            print(f"Record: {self.record}")
            print(f"Coach: {self.coach}")
            print(f"Exectuive: {self.exec}")
            print(f"PTS/G: {self.pts_g}\tOpp PTS/G: {self.opp_g}")
            print(f"SRS: {self.srs}\tPace: {self.pace}")
            print(f"Off Rtg: {self.off_rtg}\tDef Rtg: {self.def_rtg}")
            print(f"Expected W-L: {self.expected_WL}")
            print(f"Preseason Odds: {self.p_odds}")
            print(f"Arena: {self.arena}")
            if self.play_series:
                print(f"{self.playoff_header}\n{self.play_series}")
        else:
            print(f"Seasons: {self.seasons}")
            print(f"Record: {self.record}")
            print(f"Playoff Appearances: {self.playoffs}")
            print(f"Championships: {self.champs}")
            print(f"All-Time Top 12 Players: \n{self.top_players}")


team = Team("dal")
team.set_attrs()
team.get_attrs()
