import requests
from bs4 import BeautifulSoup
from datetime import datetime
import unicodedata
import discord
from discord.ext import commands

#discord side code
client = commands.Bot(command_prefix ="!")

@client.event
async def on_ready():
    print("Bot is ready")

@client.command()
async def ping(ctx):
    await ctx.send(f'pong! {round(client.latency*1000)}ms')





#this function gets rid of accented letters
def strip_accents(text):
    try:
        text = unicode(text, 'utf-8')
    except NameError: # unicode is a default on python 3
        pass

    text = unicodedata.normalize('NFD', text)\
           .encode('ascii', 'ignore')\
           .decode("utf-8")

    return str(text)

#gets achievements of player
def get_achievements(name):
    try:
        wiki = 'https://en.wikipedia.org/wiki/'
        name = name.lower()
        name = name.title()
        print(name)
        name = name.replace(" ","_")
        url = wiki+name
        page = requests.get(url).text


        soup = BeautifulSoup(page,'lxml')

        #infobox =  soup.find('table',class_='infobox vcard')
        #tbody = infobox.tbody
        number = 0
        for tr in soup.find_all("tr"):

            try:
                stuff = tr.text
            except Exception as e:
                stuff = ""
            if stuff == 'Career highlights and awards':
                achievements = soup.find_all("tr")[number+1]
            number+=1

        return(achievements.text)
    except Exception as e:
        return("Sorry try again")

@client.command()
async def achieve(ctx,*,name):
    s= get_achievements(name)
    await ctx.send(f'```{name} \n{s}```')
#function that returns birthdate and age
def age(name):
    try:
        wiki = 'https://en.wikipedia.org/wiki/'
        name = name.lower()
        name = name.title()
        print(name)
        name = name.replace(" ","_")
        url = wiki+name
        page = requests.get(url).text


        soup = BeautifulSoup(page,'lxml')
        for tr in soup.find_all("tr"):
            try:
                stuff = tr.text
            except Exception as e:
                stuff = ""
            if 'Born' in stuff:
                birthdate = tr.find_all('span')[1].text
                age = tr.find_all('span')[2].text
                birthdate = str(datetime.strptime(birthdate,'%Y-%m-%d').strftime('%B %d,%Y'))
                return(f'{birthdate}{age}')
                print()

    except Exception as e:
        return("Sorry try again")

@client.command()
async def born(ctx,*,name):
    s = age(name)
    await ctx.send(f'{name}\nBorn:  {s}')
#function to get draft order
def draft(name):
    try:
        wiki = 'https://en.wikipedia.org/wiki/'
        name = name.lower()
        name = name.title()
        print(name)
        name = name.replace(" ","_")
        url = wiki+name
        page = requests.get(url).text


        soup = BeautifulSoup(page,'lxml')

        #infobox =  soup.find('table',class_='infobox vcard')

        draft_order = soup.find("a",title = 'NBA draft')

        draft_team = "Selected by the"

        for tr_tag in soup.find_all("tr"):
            try:
                stuff = tr_tag.td.text
            except Exception as e:
                stuff = ""
            if draft_order in tr_tag.find_all("a"):
                print(tr_tag.td.text)

            if draft_team in stuff:
                print(stuff)

    except Exception as e:
        print("none")

    print()

#function for getting stats of nba player(s)
def get_name(name):
    try:
        ref_name = ""
        n = 1
        while strip_accents(ref_name.lower()) != name.lower():

            url = "https://www.basketball-reference.com/players/"

            full_name = name.split()
            fname = full_name[0].lower()
            lname = full_name[1].lower()
            if "'" in lname:
                lname=lname.replace("'","")
            l_letter = lname[0]
            l_letter+="/"
            name = name.lower()

            if len(fname)>2:
                fname = fname[:2]
            if len(lname)>5:
                lname = lname[:5]

            n = f'{n:02}'
            url = url+l_letter+lname+fname+n+'.html'


            page = requests.get(url).text

            global soup
            soup = BeautifulSoup(page,'lxml')

            ref_name = soup.find("h1",itemprop = "name").text
            n = int(n)
            n+=1

        print(ref_name)
        #enters table of stats
        global table
        table = soup.find(id = "per_game")
        global thead

        thead = table.thead.tr
    except Exception as e:
        print('player not found')

def stats(yr,name):
    #allows access to the correct basketball reference page
    try:

        get_name(name)
        table = soup.find(id = "per_game")
        thead = table.thead.tr
        #lists for printing header and stats
        header = []
        stats = []

        #list of unecessary stats
        global not_needed

        not_needed = ['Lg','2P','2PA','2P%','DRB','PF','GS','3PA','ORB','FG',\
        'FGA','3P','eFG%','FT','FTA','Pos','TOV',\
        'pos','tov_per_g',\
        'fga_per_g','fg3_per_g',\
        'efg_pct','ft_per_g','fta_per_g',\
        'gs','fg3a_per_g','fg2_per_g','fg2a_per_g','fg2_pct',\
        'orb_per_g','drb_per_g','pf_per_g','lg_id','fg_per_g']

        for th in thead.find_all("th"):
                if th.text not in not_needed:
                    header.append(th.text)


        stat_dict = {"PTS":"pts_per_g","TRB":"trb_per_g"\
            ,"AST":"ast_per_g","FT%":"ft_pct"\
            ,"3P%":"fg_3pct","STL":"stl_per_g"\
            ,"BLK":"blk_per_g","MP":"mp_per_g"\
            ,"3P":"fg3_per_g"}


        year = str(yr)
        if year.isdigit():
            year = int(year)
            tbody = table.tbody
            if year < 100:
                year -= 1
                stuff = tbody.find_all("tr")[year]


            elif year > 100:
                for tr in tbody.find_all("tr"):
                    nba_year = tr.find().text[:2]
                    ind_yr=nba_year+tr.find().text[-2:]
                    if ind_yr == str(year):
                        stuff = tr

            if stuff.has_attr('id'):
                for tag in stuff.find_all():
                    if tag.has_attr('data-stat'):
                        if tag['data-stat'] not in not_needed:
                            stats.append(tag.text)

            elif not stuff.has_attr('id'):
                for tag in stuff.find_all():
                    stat = tag.text
                    if "Did Not" in stat:
                        stat = "     "+stat
                    stats.append(stat)

            header_format = "{:>7}"*(len(header)+1)
            header=str((header_format.format("",*header)))
            stat_format = "{:>7}"*(len(stats)+1)
            stats=str((stat_format.format("",*stats)))
            return(f'{header}\n{stats}')
        elif year.isalpha():
            if year=="career":
                for stat in table.tfoot.find("tr"):
                    if stat['data-stat'] not in not_needed:
                        stats.append(stat.text)

                row_format = "{:>7}"*(len(header)+1)
                print(row_format.format(" ",*header))
                print(row_format.format(" ",*stats))

            elif year == "last":
                seasons = len(table.tbody.find_all("tr"))
                last_num = seasons-1
                stuff = table.tbody.find_all("tr")[last_num]

                if stuff.has_attr('id'):
                    for tag in stuff.find_all():
                        if tag.has_attr('data-stat'):
                            if tag['data-stat'] not in not_needed:
                                stats.append(tag.text)

                elif not stuff.has_attr('id'):
                    for tag in stuff.find_all():
                        stat = tag.text
                        stats.append(stat)

                    stats[2] = "   "+stats[2]

                header_format = "{:>7}"*(len(header)+1)
                print(header_format.format(" ",*header))
                stat_format = "{:>7}"*(len(stats)+1)
                print(stat_format.format(" ",*stats))

            elif year =="rookie":
                for tr in table.tbody.find_all("tr"):
                    if tr.has_attr('id'):
                        stuff = tr
                        break

                for tag in stuff.find_all():
                    if tag.has_attr('data-stat'):
                        if tag['data-stat'] not in not_needed:
                            stats.append(tag.text)

                header_format = "{:>7}"*(len(header)+1)
                header_list=str((header_format.format(" ",*header)))
                stat_format = "{:>7}"*(len(stats)+1)
                stats_list=str((stat_format.format(" ",*stats)))
                return(f'{header_list}\n{stats_list}')
            elif year =="all": #have to fix
                header_format = "{:>7}"*(len(header)+1)
                header_list=(header_format.format(" ",*header))
                return(f'{header_list}\n{stats_list}')
                for stuff in table.tbody.find_all("tr"):

                    if stuff.has_attr('id'):
                        for tag in stuff.find_all():
                            if tag.has_attr('data-stat'):
                                if tag['data-stat'] not in not_needed:
                                    stats.append(tag.text)

                    elif not stuff.has_attr('id'):
                        for tag in stuff.find_all():
                            stat = tag.text
                            if "Did Not" in stat:
                                stat = "     "+stat
                            stats.append(stat)

                    stat_format = "{:>7}"*(len(stats)+1)
                    stats_list=(stat_format.format(" ",*stats))

                    stats=[]

            elif year in stat_dict:
                stat_needed = 0.0
                stuff = table.tbody
                index = 0
                all_stats = stuff.find_all(attrs={'data-stat':stat_dict[year]})
                for stat_get in all_stats:
                    if float(stat_get.text) > stat_needed:
                        stat_needed = float(stat_get.text)
                        high_year = stuff.find_all(attrs={'data-stat':'season'})[index].text

                    index+=1

                stats.append(high_year)
                stats.append(stat_needed)

                header = []
                header.append('Season')
                header.append(year)
                header_format = "{:>7}"*(len(header)+1)
                header_list=str((header_format.format(" ",*header)))
                stat_format = "{:>7}"*(len(stats)+1)
                stats_list=str((stat_format.format(" ",*stats)))
                return(f'{header_list}\n{stats_list}')



    except Exception as e:
        print("Data not found")


#for mobile print stats vertically instead
def mobile_stats(yr,name):
    #allows access to the correct basketball reference page
    try:

        get_name(name)
        table = soup.find(id = "per_game")
        thead = table.thead.tr
        #lists for printing header and stats
        header = []
        stats = []
        nba_dict ={}
        #list of unecessary stats
        global not_needed

        not_needed = ['Lg','2P','2PA','2P%','DRB','PF','GS','3PA','ORB','FG',\
        'FGA','3P','eFG%','FT','FTA','Pos','TOV',\
        'pos','tov_per_g',\
        'fga_per_g','fg3_per_g',\
        'efg_pct','ft_per_g','fta_per_g',\
        'gs','fg3a_per_g','fg2_per_g','fg2a_per_g','fg2_pct',\
        'orb_per_g','drb_per_g','pf_per_g','lg_id','fg_per_g']

        for th in thead.find_all("th"):
                if th.text not in not_needed:
                    header.append(th.text)


        stat_dict = {"PTS":"pts_per_g","TRB":"trb_per_g"\
            ,"AST":"ast_per_g","FT%":"ft_pct"\
            ,"3P%":"fg_3pct","STL":"stl_per_g"\
            ,"BLK":"blk_per_g","MP":"mp_per_g"\
            ,"3P":"fg3_per_g"}


        year = str(yr)
        if year.isdigit():
            year = int(year)
            tbody = table.tbody
            if year < 100:
                year -= 1
                stuff = tbody.find_all("tr")[year]


            elif year > 100:
                for tr in tbody.find_all("tr"):
                    nba_year = tr.find().text[:2]
                    ind_yr=nba_year+tr.find().text[-2:]
                    if ind_yr == str(year):
                        stuff = tr

            if stuff.has_attr('id'):
                for tag in stuff.find_all():
                    if tag.has_attr('data-stat'):
                        if tag['data-stat'] not in not_needed:
                            stats.append(tag.text)

            elif not stuff.has_attr('id'):
                for tag in stuff.find_all():
                    stat = tag.text
                    if "Did Not" in stat:
                        stat = "     "+stat
                    stats.append(stat)

            stats+=['']*(len(header)-len(stats))

            for x in range(len(header)):
                nba_dict[header[x]] = stats[x]
            return nba_dict
            #header_format = "{:<7}"*(len(header)+1)
            #header=str((header_format.format("",*header)))
            #stat_format = "{:<7}"*(len(stats)+1)
            #stats=str((stat_format.format("",*stats)))
            #return(f'{header}\n{stats}')
        '''elif year.isalpha():
            if year=="career":
                for stat in table.tfoot.find("tr"):
                    if stat['data-stat'] not in not_needed:
                        stats.append(stat.text)

                row_format = "{:>7}"*(len(header)+1)
                print(row_format.format(" ",*header))
                print(row_format.format(" ",*stats))

            elif year == "last":
                seasons = len(table.tbody.find_all("tr"))
                last_num = seasons-1
                stuff = table.tbody.find_all("tr")[last_num]

                if stuff.has_attr('id'):
                    for tag in stuff.find_all():
                        if tag.has_attr('data-stat'):
                            if tag['data-stat'] not in not_needed:
                                stats.append(tag.text)

                elif not stuff.has_attr('id'):
                    for tag in stuff.find_all():
                        stat = tag.text
                        stats.append(stat)

                    stats[2] = "   "+stats[2]

                header_format = "{:>7}"*(len(header)+1)
                print(header_format.format(" ",*header))
                stat_format = "{:>7}"*(len(stats)+1)
                print(stat_format.format(" ",*stats))

            elif year =="rookie":
                for tr in table.tbody.find_all("tr"):
                    if tr.has_attr('id'):
                        stuff = tr
                        break

                for tag in stuff.find_all():
                    if tag.has_attr('data-stat'):
                        if tag['data-stat'] not in not_needed:
                            stats.append(tag.text)

                header_format = "{:>7}"*(len(header)+1)
                header_list=str((header_format.format(" ",*header)))
                stat_format = "{:>7}"*(len(stats)+1)
                stats_list=str((stat_format.format(" ",*stats)))
                return(f'{header_list}\n{stats_list}')
            elif year =="all": #have to fix
                header_format = "{:>7}"*(len(header)+1)
                header_list=(header_format.format(" ",*header))
                return(f'{header_list}\n{stats_list}')
                for stuff in table.tbody.find_all("tr"):

                    if stuff.has_attr('id'):
                        for tag in stuff.find_all():
                            if tag.has_attr('data-stat'):
                                if tag['data-stat'] not in not_needed:
                                    stats.append(tag.text)

                    elif not stuff.has_attr('id'):
                        for tag in stuff.find_all():
                            stat = tag.text
                            if "Did Not" in stat:
                                stat = "     "+stat
                            stats.append(stat)

                    stat_format = "{:>7}"*(len(stats)+1)
                    stats_list=(stat_format.format(" ",*stats))

                    stats=[]

            elif year in stat_dict:
                stat_needed = 0.0
                stuff = table.tbody
                index = 0
                all_stats = stuff.find_all(attrs={'data-stat':stat_dict[year]})
                for stat_get in all_stats:
                    if float(stat_get.text) > stat_needed:
                        stat_needed = float(stat_get.text)
                        high_year = stuff.find_all(attrs={'data-stat':'season'})[index].text

                    index+=1

                stats.append(high_year)
                stats.append(stat_needed)

                header = []
                header.append('Season')
                header.append(year)
                header_format = "{:>7}"*(len(header)+1)
                header_list=str((header_format.format(" ",*header)))
                stat_format = "{:>7}"*(len(stats)+1)
                stats_list=str((stat_format.format(" ",*stats)))
                return(f'{header_list}\n{stats_list}')
'''


    except Exception as e:
        print("Data not found")

@client.command()
async def stat(ctx,year,*,name):
    s = stats(year,name)
    await ctx.send(name)
    await ctx.send(f"```{s}```")

def born(name):
    try:
        get_name(name)

        div = soup.find(id = "info")

        for p in soup.find_all("p"):
            try:
                if "Born" in p.strong.text:
                    toe = p.text
            except Exception as e:
                continue
        print(toe)
        toenail = toe.split()
        return " ".join(toenail)
    except Exception as e:
        return "Try again"


@client.command()
async def mstat(ctx,year,*,name):
    s=mobile_stats(year,name)
    await ctx.send('```')
    for h,s in s.items():
        await ctx.send(f'```{h} : {s}```')
    await ctx.send('```')


@client.command()
async def testing(ctx):
    header_list = ["Season","AST","TRB","PTS"]
    stat_list = ['2018-19','9.5','7.8','17.8']
    header_format = "{:>7}"*(len(header_list)+1)
    stat_format = "{:>7}"*(len(stat_list)+1)
    await ctx.send(header_format.format(" ",*header_list))
    await ctx.send(stat_format.format(" ",*stat_list))



client.run('NzIzMjA4MDE4ODMzMTc4NzU0.XvAVtQ.Kkyre92gAgHjfvcj2x5VMV8T2Ck')




