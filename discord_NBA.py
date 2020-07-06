import requests
from bs4 import Comment,BeautifulSoup
from datetime import datetime,date
import unicodedata
import discord
from discord.ext import commands

#discord side code
client = commands.Bot(command_prefix ="!")

@client.event
async def on_ready():
    print("Bot is ready")

@client.command(help ='use !ping for ping')
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

@client.command(help = 'use !achieve <player> for achievements and accolades')
async def achieve(ctx,*,name):
    s= get_achievements(name)
    await ctx.send(f'```{name} \n{s}```')
#function that returns birthdate and age

@client.command(help='use !born <player> for birthdate and age')
async def born(ctx,*,name):
    s = get_born(name)
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
                order = tr_tag.td.text

            if draft_team in stuff:
                team = stuff

        return f'{order} {team}'
    except Exception as e:
        print("none")

    print()

#function for getting stats of nba player(s)
def get_name(name):
    try:
        ref_name = ""
        n = 1
        player_nicknames = {'kd':'Kevin Durant','kat':'Karl-Anthony Towns',
        'boogie':'Demarcus Cousins','flat earth':'Kyrie Irving',
        'king':'Lebron James','ai':'Allen Iverson','mamba':'Kobe Bryant',
        'unicorn':'Kristaps Porzingis','kareem':'Kareem Abdul-Jabbar','no d':'Trae Young',
        'beard':'James Harden','bald mamba':'Alex Caruso','sung roh':'Draymond Green',
        'joowon kim':'Nick Young','frankie kim':'Klay Thompson','elijah kim':'Isaiah Thomas','jithu tirumala':'Buddy Hield',
        'kyeu lee':'Carmelo Anthony','justin lee':'Davis Bertans','sungmin kim':'Lou Williams','michael im':'Jamal Crawford',
        'joung son':'Blake Griffin','giannis':'Giannis Antetokounmpo','nick cho':'kyle lowry'}
        if name.lower() in player_nicknames:
            name = player_nicknames[name]

        while strip_accents(ref_name.lower()) != name.lower():

            f_rl = "https://www.basketball-reference.com/players/"

            full_name = name.split()
            fname = full_name[0].lower()
            lname = full_name[1].lower()
            if "." in fname:
                fname=fname.replace(".","")
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
            global url
            url = f_rl+l_letter+lname+fname+n+'.html'


            page = requests.get(url).text

            global soup
            soup = BeautifulSoup(page,'lxml')

            ref_name = soup.find("h1",itemprop = "name").text
            n = int(n)
            n+=1

            adv=[]

            for comments in soup.find_all(string=lambda text: isinstance(text, Comment)):
                if "advanced" in comments:
                    data = BeautifulSoup(comments,'lxml')
                    advanced = data.find(id="div_advanced")
                    adv.append(advanced)

            global a_table
            a_table = adv[0]


            global needed

            needed = ['Season','Age','Tm','Pos','G','PER','TS%',
                    '3PAr','FTr','USG%','WS','BPM','VORP',
                    'season','age','team_id','pos','g','per','ts_pct',
                    'fg3a_per_fga_pct','fta_per_fga_pct','usg_pct',
                    'ws','bpm','vorp']

            global not_needed

            not_needed = ['Lg','2P','2PA','2P%','DRB','PF','GS','3PA','ORB','FG',
            'FGA','3P','eFG%','FT','FTA','TOV',
            'tov_per_g',
            'fga_per_g','fg3_per_g',
            'efg_pct','ft_per_g','fta_per_g',
            'gs','fg3a_per_g','fg2_per_g','fg2a_per_g','fg2_pct',
            'orb_per_g','drb_per_g','pf_per_g','lg_id','fg_per_g']



        #print(ref_name)
        #enters table of stats


        return(name.title())
    except Exception as e:
        return('player not found')

def get_header(name):
    try:

        get_name(name)
        table = soup.find(id = "per_game")
        header = [th.text for th in table.thead.tr.find_all("th") if th.text not in not_needed]


        header_format = "{:^7}"*(len(header)+1)
        header=str((header_format.format("",*header)))
        return header

    except Exception as e:
        return("Data not found")

def get_stats(yr,name):
    #allows access to the correct basketball reference page
    try:

        name=get_name(name)
        #lists for printing header and stats
        stats = []

        table = soup.find(id = "per_game")

        thead = table.thead.tr

        #list of unecessary stats

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
                year = "per_game."+str(year)
                stuff = tbody.find(id=year)

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

            stat_format = "{:^7}"*(len(stats)+1)
            stats=str((stat_format.format("",*stats)))
            return stats

        elif year.isalpha():
            if year=="career":
                for stat in table.tfoot.find("tr"):
                    if stat['data-stat'] not in not_needed:
                        stats.append(stat.text)

                stat_format = "{:>7}"*(len(stats)+1)
                stats=str((stat_format.format("",*stats)))
                return(f'{stats}')

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

                stat_format = "{:>7}"*(len(stats)+1)
                stats=str((stat_format.format("",*stats)))
                return(f'{stats}')

            elif year =="rookie":
                for tr in table.tbody.find_all("tr"):
                    if tr.has_attr('id'):
                        stuff = tr
                        break

                for tag in stuff.find_all():
                    if tag.has_attr('data-stat'):
                        if tag['data-stat'] not in not_needed:
                            stats.append(tag.text)

                stat_format = "{:^7}"*(len(stats)+1)
                stats=str((stat_format.format(" ",*stats)))
                return stats


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

                stat_format = "{:>7}"*(len(stats)+1)
                stats=str((stat_format.format(" ",*stats)))
                return(f'{stats}')

    except Exception as e:
        print("Data not found")

def get_adv_header(name):
    get_name(name)

    header =[th.text for th in a_table.thead.find_all("th") if th.text in needed]

    header_format = "{:>7}"*(len(header)+1)
    header=str((header_format.format("",*header)))

    return header

def get_adv_stats(yr,name):
    try:
        get_name(name)

        year = str(yr)

        if year.isdigit():
            year = int(year)
            tbody = a_table.tbody
            if year < 100:
                year -=1
                stuff = tbody.find_all("tr")[year]

            elif year >100:
                year = "advanced."+str(year)
                stuff = tbody.find(id=year)

            stats = [stat.text for stat in stuff if stat['data-stat'] in needed]


            stat_format = "{:>7}"*(len(stats)+1)
            stats=str((stat_format.format("",*stats)))
            return stats

        elif year.isalpha():
            if year =="career":
                stuff = a_table.table.tfoot.find("tr")

            elif year =="last":
                seasons = len(a_table.tbody.find_all("tr"))
                last_num = seasons-1
                stuff = a_table.tbody.find_all("tr")[last_num]

            elif year =="rookie":
                stuff = a_table.tbody.find("tr")


        stats = [stat.text for stat in stuff if stat['data-stat'] in needed]
        stat_format = "{:>7}"*(len(stats)+1)
        stats=str((stat_format.format("",*stats)))
        return stats



    except Exception as e:
        return ' '

def get_seasons(name):
    get_name(name)
    table = soup.find(id = "per_game")
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
        image = soup.find(class_='media-item')
        img = image.find('img')
        return img['src']
    except Exception as e:
        return ''

def get_pns(name):
    get_name(name)
    positions = {'Point Guard':'PG','Shooting Guard':'SG','Small Forward':'SF','Power Forward':'PF','Center':'C'}
    stuff = soup.find(id="info")
    for p in stuff.find_all("p"):
        if "Position" in p.text:
            pns = p.text

    pns=pns.split('\n')
    pns = [l for l in pns if l.strip()]
    #return ''.join(pns)
    stuff = pns[1]
    shoots = pns[4].strip()
    if "and" in stuff:
        pos = stuff.split('and')
    else:
        pos =[]
        pos.append(stuff)

    pos = [positions[pos[i].strip()] for i in range(len(pos))]
    pos = '/'.join(pos)
    return f'\nPosition: {pos}\nShoots: {shoots}'

def get_hnw(name):
    get_name(name)
    weight = soup.find(attrs={"itemprop":"weight"}).text
    height = soup.find(attrs={"itemprop":"height"}).text
    return f'{height}, {weight}'

def get_nickname(name):
    try:
        get_name(name)
        nick = soup.find(id="info")
        for p in nick.find_all("p"):

            if not p.find("span") and not p.find("strong"):
                if "(" in p.text:
                    r = p.text
        r = r.replace("\n","")
        if "," in r:
            x = r.split(",")
            r = ",".join(x[0:3])
            if ")" not in r:
                r+=")"

        return r

    except Exception as e:
        return ' '

def get_death(name):
    try:
        get_name(name)
        d = soup.find(id='necro-death')['data-death']
        deathdate = datetime.strptime(d,'%Y-%m-%d').strftime('%b %d, %Y')
        d = datetime.strptime(d,'%Y-%m-%d')
        db = soup.find(id="necro-birth")['data-birth']
        db = datetime.strptime(db,'%Y-%m-%d')
        days = abs(d-db).days
        age = days//365
        return f'{deathdate} (Aged: {age})'
    except Exception as e:
        return None

def get_born(name):
    get_name(name)
    db = soup.find(id="necro-birth")['data-birth']
    birthdate = datetime.strptime(db,'%Y-%m-%d').strftime('%b %d, %Y')
    if not get_death(name):
        current = datetime.today()
        db = datetime.strptime(db,'%Y-%m-%d')
        days = abs(current-db).days
        age = days//365
        return f'{birthdate} (Age: {age})'
    else:
        return f'{birthdate}'

def get_bling(name):
    try:
        get_name(name)
        bling = soup.find(id="bling")
        #print(bling.prettify())
        accs = []
        for acc in bling.find_all("a"):
            accs.append(acc.text)
        r = [i+"\t"+j for i,j in zip(accs[::2], accs[1::2])]

        if len(accs)%2 != 0:
            r.append(accs[-1])

        x = "\n".join(r)

        return '\n'.join(accs)


    except Exception as e:
        return None

@client.command(help='use !<player> to get quick description of player')
async def info(ctx,*,name):
    n = get_name(name)
    birthdate = get_born(n)
    deathdate= get_death(n)
    nicknames = str(get_nickname(n))
    picture = get_image(n)
    pns = get_pns(n)
    hnw = get_hnw(n)
    accs = get_bling(n)
    descript = f'{nicknames}{pns}\n{hnw}'
    seasons = get_seasons(n)
    drafted = str(draft(name))
    embed=discord.Embed(title=n, description=descript)
    embed.set_thumbnail(url=picture)
    embed.add_field(name='Born', value=birthdate, inline=False)
    if deathdate:
       embed.add_field(name='Died', value=deathdate, inline=False)
    embed.add_field(name='Drafted', value=drafted, inline=False)
    embed.add_field(name='Current Team', value='stuff', inline=True)
    embed.add_field(name='Experience', value=seasons, inline=True)
    if accs:
        embed.add_field(name='Bling', value=accs, inline=False)
    await ctx.send(embed=embed)

@client.command(help='use !stat <year or NBA year> <player> for player stats')
async def stat(ctx,year,*,name):
    rando = []
    rando.append(get_name(name))
    rando.append(get_header(name))

    if year.lower()=="all":
        num = get_seasons(name)
        for x in range(1,num+1):
            rando.append(get_stats(x,name))
        rando.append(get_stats('career',name))

    else:
        rando.append(get_stats(year,name))

    r = "\n".join(rando)
    await ctx.send(f'```\n{r}\n```')

@client.command(help='use !astat <year or NBA year> <player> for player advanced stats')
async def astat(ctx,year,*,name):
    rando =[]
    rando.append(get_name(name))
    rando.append(get_adv_header(name))

    if year.lower()=="all":
        num = get_a_seasons(name)
        for x in range(1,num+1):
            rando.append(get_adv_stats(x,name))
        rando.append(get_adv_stats('career',name))
    else:
        rando.append(get_adv_stats(year,name))

    r = "\n".join(rando)
    await ctx.send(f"```\n{r}\n```")

@client.command(help="use !full <year or NBA year> <player> for player stats and advanced stats")
async def full(ctx,year,*,name):
    rando = []
    rando.append(get_name(name))
    rando.append(get_header(name))
    rando.append(get_stats(year,name))
    rando.append(get_adv_header(name))
    rando.append(get_adv_stats(year,name))

    r = "\n".join(rando)

    await ctx.send(f'```\n{r}\n```')

def standings(year,conference):
    url = 'https://www.basketball-reference.com/leagues/NBA_'
    e_url = str(year)+'_standings.html'
    url+=e_url
    page = requests.get(url).text
    stand = BeautifulSoup(page,'html.parser')
    max_=28
    space = " "
    lines = (" "*7)+("-"*79)

    if conference.lower()[0]=='i':
        info = stand.find(id='meta')
        i = info.find_all('p')
        y = [p.text for p in i if p.text]
        x = y[2:]
        return "\n".join(x)

    if int(year) >2015:
        if conference.lower()[0]=='e':
            con_id = "all_confs_standings_E"
        elif conference.lower()[0]=='w':
            con_id = "all_confs_standings_W"

        conf  = stand.find(id=con_id)
        thead = conf.thead
        head = [th.text for th in thead.find_all('th') if thead.text]
        header_format = "{:^7}"*(len(head)+1)
        body = conf.tbody
        space = " "
        teams =[]
        head[0] += (max_-len(head[0]))*space
        teams.append(str(header_format.format(" ",*head)))

        for tr in body.find_all("tr"):

            team = [stuff.text for stuff in tr]
            len_ = max_ - len(team[0])
            team[0]+=space*len_
            teams.append(str(header_format.format(" ",*team)))

        teams.insert(9,lines)
        r = "\n".join(teams)

    elif int(year)<=2015:

        if conference.lower()[0]=='e':
            con_id = 'divs_standings_E'
        elif conference.lower()[0]=='w':
            con_id ='divs_standings_W'

        conf = stand.find(id=con_id)
        thead = conf.thead
        head =  [th.text for th in thead.find_all('th') if thead.text]
        body = conf.find('tbody')
        header_format = "{:^7}"*(len(head)+1)
        head[0] += (max_-len(head[0]))*space
        header = str(header_format.format(" ",*head))

        amt_teams = len(body.find_all(class_='full_table'))
        table =[' ']*amt_teams


        for tr in body.find_all(class_='full_table'):
            team = [stuff.text for stuff in tr]
            num = ''
            name = team[0]
            for r in name:
                if r.isdigit():
                    num+=r
            if '76' in num:
                num=num.replace('76','')

            len_ = max_ - len(team[0])
            team[0]+=space*len_
            table[int(num)-1] = team

        dif = float(table[0][1])-float(table[0][2])
        teams =[]
        for team in table:

            dif = float(team[1]) -float(team[2])
            gb = str((dif-dif)/2)
            if gb != '0.0':
                team[4] = gb

            teams.append(str(header_format.format(" ",*team)))


        teams.insert(0,header)


        lines = (" "*7)+("-"*73)
        teams.insert(9,lines)

        r = "\n".join(teams)

    elif int(year)<1971:
        return 'Wrong number, homie. Try something higher'

    return r

@client.command(help="use !<year> <conference/none> to get standings for year")
async def stand(ctx,year,conference=None):

    season = str(int(year)-1)+"-"+str(year[-2:])

    if conference ==None:
        e = standings(year,'east')
        w = standings(year,'west')
        i = standings(year,'info')

        await ctx.send(f'```Season: {season}\n{i}```')
        await ctx.send(f'```{e}```')
        await ctx.send(f'```{w}```')
    else:
        r = standings(year,conference)
        await ctx.send(f'```Season: {season}\n{r}```')

client.run(discord-token)




