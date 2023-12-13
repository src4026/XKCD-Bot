import json
import os
import random
import time
import re
import urllib.request
from datetime import date, datetime

import discord
from discord.ext import commands, tasks

from keep_alive import keep_alive

intents = discord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix="~", intents=intents, help_command=None)


def today_xkcd():
  with urllib.request.urlopen("https://xkcd.com/info.0.json") as url:
    data = json.load(url)
    return data


def random_xkcd():
  with urllib.request.urlopen("https://xkcd.com/info.0.json") as url:
    data = json.load(url)
  return data


def makeXKCDEmbed(data):
  Embed = discord.Embed(title=data["safe_title"], color=0xA13FDA)
  Embed.set_image(url=data["img"])
  Embed.set_footer(text=f"Source: https://xkcd.com/{data['num']}")
  return Embed


@tasks.loop(seconds=60)
async def daily():
  # Load existing data
  try:
    with open('channelID.json', 'r') as f:
      server_data = json.load(f)
  except FileNotFoundError:
    server_data = {}

  # Load titles
  with open('comic.txt', 'r') as f:
    last_title = f.read()
  latest_title = str(today_xkcd()["num"])

  if last_title != latest_title:

    #time.sleep(2)

    with open('comic.txt', 'w') as f:
      f.write(latest_title)
    weekly_comics_sent = []

    for channelID in server_data.values():
      channel = bot.get_channel(channelID)
      weekly_comics_sent.append(today_xkcd()["num"])
      dailyEmbed = makeXKCDEmbed(today_xkcd())
      await channel.send(embed=dailyEmbed)


@bot.event
async def on_ready():
  print("I'm in")
  print(bot.user)
  await bot.tree.sync()
  daily.start()


@bot.hybrid_command(name="help", description="The saviour of all commands.")
async def help(ctx):
  helpEmbed = discord.Embed(
      title="XKCD Bot Help",
      description=
      """The help page for the <@1128735049014054994>. Prefixes: `/` | `~`
    Available commands: `/help`, `/random`, and `/today`.""",
      color=0xA13FDA)
  helpEmbed.add_field(
      name=":book: What am I?",
      value=
      "XKCDs galore! Wait for the daily XKCD to come or fetch it yourself," +
      " or a random one to spark another age long discussion. The power lies" +
      " within you to invoke. Welcome to the help page.",
      inline=False)
  helpEmbed.add_field(name=":game_die: Commands",
                      value="""
**i. `~help`**
Self explanatory: *the saviour of all commands*.

**ii. `~today`**
Fetches the xkcd comic of the day.

**iii. `~random`**
Fetches a random xkcd comic.

**iv. `start_daily`**
Enables the daily XKCD comic task which sends a new XKCD comic when a new one is uploaded on the XKCD website.

**v. `end_daily`**
Disables the daily XKCD comic task.

""")
  await ctx.send(embed=helpEmbed)


@bot.hybrid_command(
    name="today",
    description="Fetches the xkcd comic of the day.",
)
async def today(ctx):
  data = today_xkcd()
  todayEmbed = discord.Embed(title=data["safe_title"], color=0xA13FDA)
  todayEmbed.set_image(url=data["img"])
  todayEmbed.set_footer(text=f"Source: https://xkcd.com/{data['num']}")
  await ctx.send(embed=todayEmbed)


@bot.hybrid_command(
    name="random",
    description="Fetches a random xkcd comic.",
)
async def random_comic(ctx):
  data = random_xkcd()
  num = int(data["num"])
  rand_img_link = f"https://xkcd.com/{random.randint(1, num)}/info.0.json"
  with urllib.request.urlopen(rand_img_link) as url:
    data = json.load(url)
    randomEmbed = discord.Embed(title=data["safe_title"], color=0xA13FDA)
    randomEmbed.set_image(url=data["img"])
    randomEmbed.set_footer(text=f"Source: https://xkcd.com/{data['num']}")
  await ctx.send(embed=randomEmbed)


@bot.hybrid_command(name="start_daily",
                    description="Enables the daily XKCD comic task.")
@commands.has_permissions(administrator=True)
async def start_daily(ctx, channel):
  channelID = int(re.findall("<#([0-9]+)>", channel)[0])
  serverID = ctx.guild.id

  # Load existing data
  try:
    with open('channelID.json', 'r') as f:
      server_data = json.load(f)
  except FileNotFoundError:
    server_data = {}

  # Check if server ID exists in the data
  if str(serverID) in server_data:
    runningEmbed = discord.Embed(
        description=
        "***Daily XKCD comic task is already running for this server. To reset it, please disable using `/end_daily` and re-enable using `/start_daily`***",
        color=0xff0000)
    await ctx.send(embed=runningEmbed)
  else:
    # Update data
    server_data[str(serverID)] = channelID

    # Save updated data
    with open('channelID.json', 'w') as f:
      json.dump(server_data, f)

    setEmbed = discord.Embed(
        description=
        f"***The daily XKCD comic task is now enabled for <#{channelID}> :white_check_mark:***",
        color=0x00ff00)
    await ctx.send(embed=setEmbed)


@bot.hybrid_command(name="end_daily",
                    description="Disables the daily XKCD comic task.")
@commands.has_permissions(administrator=True)
async def end_daily(ctx):
  serverID = ctx.guild.id

  # Load existing data
  try:
    with open('channelID.json', 'r') as f:
      server_data = json.load(f)
  except FileNotFoundError:
    server_data = {}

  # Check if server ID exists in the data
  if str(serverID) in server_data:
    # Delete server ID from data
    del server_data[str(serverID)]

    # Save updated data
    with open('channelID.json', 'w') as f:
      json.dump(server_data, f)

    endEmbed = discord.Embed(
        description=
        "***Daily XKCD comic task is now disabled :white_check_mark:***",
        color=0x00ff00)
    await ctx.send(embed=endEmbed)
  else:
    noneEmbed = discord.Embed(
        description=
        "***Daily XKCD comic task is not running for this server***",
        color=0x0000ff)
    await ctx.send(embed=noneEmbed)


keep_alive()
my_secret = os.environ['DISCORD_BOT_SECRET']
bot.run(my_secret)
