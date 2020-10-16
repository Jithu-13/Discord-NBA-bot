import discord
from discord.ext import commands
from player import Player
from leaguefunc import get_record_with


client = commands.Bot(command_prefix="!")


@client.event
async def on_ready():
    print("Bot is ready")


@client.command(help="use !ping for ping")
async def ping(ctx):
    await ctx.send(f"pong! {round(client.latency*1000)}ms")


@client.command(help="use !pinfo<name> for bio")
async def pinfo(ctx, *, name):
    player = Player(name)

    player.info()
    descript = player.description()

    embed = discord.Embed(title=player.name, description=descript)
    embed.set_thumbnail(url=player.image)
    embed.add_field(name="Born", value=player.born, inline=False)
    if player.death:
        embed.add_field(name="Death", value=player.death, inline=False)
    embed.add_field(name="Drafted", value=player.draft, inline=False)
    if player.team:
        embed.add_field(name="Team", value=player.team, inline=False)
    if player.bling:
        embed.add_field(name="Bling", value=player.bling, inline=False)
    await ctx.send(embed=embed)


@client.command(help="use !pyear<year><name> for season stat")
async def pyear(ctx, year, *, name):
    player = Player(name)
    stats = []
    stats.append(player.name)
    stats.append(player.basic_header())
    if year.lower() == "all":
        for i in range(1, player.seasons + 1):
            stats.append(player.basic_stats(i))
        stats.append(player.basic_stats("career"))
    else:
        stats.append(player.basic_stats(year))

    table = "\n".join(stats)

    await ctx.send(f"```{table}```")


@client.command(help="use !pstat<year><stat><name> for stat")
async def pstat(ctx, year, stat, *, name):
    player = Player(name)
    h, v = player.stat(year, stat)

    p = "Player" + (25 - len("Player")) * " "
    name = player.name + (25 - len(player.name)) * " "
    header = p + h
    value = name + v

    await ctx.send(f"```{header}\n{value}```")


@client.command(help="use !precord<yr><diff><stat><value><player>")
async def precord(ctx, year, diff, stat, value, *, name):
    n = get_record_with(year, diff, stat, value, name)
    await ctx.send(f"```{n}```")


@client.command()
async def pcomp(ctx, *, name):
    player = Player(name)
    comp_list = player.show_comp()

    await ctx.send(f"```{comp_list}```")


client.run("NzIzMjA4MDE4ODMzMTc4NzU0.XvFuVw.H7pu67wssksDs9PRHPXaajgY4sQ")

