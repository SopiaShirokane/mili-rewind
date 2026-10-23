import sqlite3
import json
import discord
from discord.ext import commands
import requests
import os
import ast

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is not set. Please set it before running this script by using export API_KEY='your API key here'.")

con = sqlite3.connect("watch-history.db")
cur = con.cursor()

cur.execute("DROP TABLE IF EXISTS watchHistory")
cur.execute("""
    CREATE TABLE watchHistory(
    title TEXT,
    viewCount INTERGER,
    channel TEXT,
    videoId TEXT
    )
""")

def getApi(member):
    validNames = ["ミリプロ - MillionProduction -", "音ノ瀬らこ / Otonose Raco", "甘狼このみ / AmakamiKonomi🐺🍫", "小廻こま / Komawari Koma", "ゆらぎゆら / YuragiYura🌙🫧", "虹深°ぬふ / Nijipuka Nuhu", "海琳あおい / Mitama Aoi", "眠雲ツクリ / NemukumoTsukuri", "雨夜リズ / Amayo Liz", "夕霧レイ / YugiriRay", "音ノ乃のの / NononoNono", "あくび・でもんすぺーど / Akubi Demonspade", "鹿乃まほろ / Kano Mahoro"]
    handle = ["@Mil_Pro", "@OtonoseRaco", "@AmakamiKonomi", "@komawarikoma", "@_YuraYuragi", "@NijipukaNuhu", "@MitamaAoi", "@NemukumoTsukuri", "@Amayo_liz", "@YugiriRay", "@_nonono_nono", "@Akubi.demonspade", "@Kano_"]
    for i in range(len(validNames)):
        if member == validNames[i]:
            response = requests.get(
                "https://www.googleapis.com/youtube/v3/channels",
                params={f"part": "snippet, statistics, contentDetails", "forHandle": {handle[i]}, "key": API_KEY},
            )
    with open ("channel.json", "w", encoding="utf-8") as f:
        print(response.json(), file=f)
    with open("channel.json", "r", encoding="utf-8") as f:
        fileData = ast.literal_eval(f.read())
    with open("channel.json", "w", encoding="utf-8") as f:
        json.dump(fileData, f, ensure_ascii=False,  indent=2)
    with open("channel.json", "r", encoding="utf-8") as f:
        fileData = json.load(f)
    return fileData

with open("watch-history.json", "r", encoding="utf-8") as f:
    fileData = json.load(f)

miliChannels = ["ミリプロ - MillionProduction -", "音ノ瀬らこ / Otonose Raco", "甘狼このみ / AmakamiKonomi🐺🍫", "小廻こま / Komawari Koma", "ゆらぎゆら / YuragiYura🌙🫧", "虹深°ぬふ / Nijipuka Nuhu", "海琳あおい / Mitama Aoi", "眠雲ツクリ / NemukumoTsukuri", "雨夜リズ / Amayo Liz", "夕霧レイ / YugiriRay", "音ノ乃のの / NononoNono", "あくび・でもんすぺーど / Akubi Demonspade", "鹿乃まほろ / Kano Mahoro"]
watchedVideo = []
count = 0
for entry in fileData:
    subtitles = entry.get("subtitles")
    if not subtitles:
        continue
    if subtitles[0]["name"] in miliChannels:
        videoTitle = entry.get("title")
        channel = subtitles[0]["name"]
        videoId = entry.get("titleUrl")
        videoId = videoId.removeprefix("https://www.youtube.com/watch?v\u003d")
        if videoTitle.startswith("Watched "):
            videoTitle = videoTitle.removeprefix("Watched ")
            for item in watchedVideo:
                if item[0] == videoTitle:
                    item[1] += 1
                    break
            else:
                watchedVideo.append([videoTitle, 1, channel, videoId])
cur.executemany("INSERT INTO watchHistory VALUES(?, ?, ?, ?)", watchedVideo)
con.commit()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="m!", intents=intents, help_command=None)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    
@bot.command(name="topmember")
async def topmember(ctx, member):
    validNames = ["ミリプロ - MillionProduction -", "音ノ瀬らこ / Otonose Raco", "甘狼このみ / AmakamiKonomi🐺🍫", "小廻こま / Komawari Koma", "ゆらぎゆら / YuragiYura🌙🫧", "虹深°ぬふ / Nijipuka Nuhu", "海琳あおい / Mitama Aoi", "眠雲ツクリ / NemukumoTsukuri", "雨夜リズ / Amayo Liz", "夕霧レイ / YugiriRay", "音ノ乃のの / NononoNono", "あくび・でもんすぺーど / Akubi Demonspade", "鹿乃まほろ / Kano Mahoro"]
    if member not in validNames:
        await ctx.send(f"That doesn't look like a MilPro member's name, choose from: {", ".join(validNames)}")
        return
    fileData = getApi(member)

    embed = discord.Embed(title=f"Top 5 watched videos from {member}", color=0x8000FF)
    url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
    embed.set_thumbnail(url=url)
    totalChannelViews = 0
    for channelViewCount in cur.execute(f"SELECT viewCount FROM watchHistory WHERE channel='{member}'"):
        totalChannelViews += channelViewCount[0]
    embed.add_field(name=f"You've watched {member} {totalChannelViews} times this year!", inline=False, value="")
    for title, viewCount, link in cur.execute(f"SELECT title, viewCount, videoId FROM watchHistory WHERE channel='{member}' ORDER BY viewCount DESC LIMIT 5"):
        embed.add_field(name=title, inline=False, value=f"Views: {viewCount} \nLink: https://www.youtube.com/watch?v={link}")
    await ctx.send(embed=embed)

@bot.command(name="rewind")
async def rewind(ctx):
    embed = discord.Embed(title="Your MilPro rewind", color=0x8000FF)
    embed.set_image(url="https://pbs.twimg.com/profile_banners/1628632642492198912/1786888616/1500x500")
    cons = sqlite3.connect("watch-history.db")
    curs = cons.cursor()
    channelTable = []
    curs.execute("DROP TABLE IF EXISTS channelViews")
    curs.execute("""
        CREATE TABLE channelViews(
        channelName TEXT,
        views INTERGER
        )
    """)
    for channel, viewCount in curs.execute("SELECT channel, viewCount FROM watchHistory ORDER BY viewCount DESC"):
        for channelItem in channelTable:
            if channelItem[0] == channel:
                channelItem[1] += viewCount
                break
        else:
            channelTable.append([channel, viewCount])
    curs.executemany("INSERT INTO channelViews VALUES(?, ?)", channelTable)
    curs.execute("SELECT channelName, views from channelViews ORDER BY views DESC")
    topChannels = curs.fetchmany(5)
    curs.execute("SELECT views FROM channelviews")
    total = curs.fetchall()
    totalViews = 0
    for views in total:
        totalViews += views[0]
    embed.add_field(name=f"This year, you watched videos from MilPro {totalViews} times!", inline=False, value="")
    embed.add_field(name="Top 5 channels", inline=True, value=f"{topChannels[0][0]}, {topChannels[0][1]} views 👑\n {topChannels[1][0]}, {topChannels[1][1]} views\n{topChannels[2][0]}, {topChannels[2][1]} views\n{topChannels[3][0]}, {topChannels[3][1]} views\n{topChannels[4][0]}, {topChannels[4][1]} views\n")
    embed.add_field(name="Your most watched videos", inline=False, value="")
    for title, viewCount, channelName, link in cur.execute("SELECT title, viewCount, channel, videoId FROM watchHistory ORDER BY viewcount DESC LIMIT 5"):
        embed.add_field(name=title, inline=False, value=f"Views: {viewCount} \nChannel: {channelName} \nLink: https://www.youtube.com/watch?v={link}")
    await ctx.send(embed=embed)

    fileData = getApi(topChannels[0][0])
    embedMember = discord.Embed(title="You probably knew, but the member you have been with the most is...", color=0x8000FF)
    if topChannels[0][0] == "ミリプロ - MillionProduction -":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="Okay genuinely why is this your most watched channel on here")
    if topChannels[0][0] == "音ノ瀬らこ / Otonose Raco":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="Feeling energetic are we?")
    if topChannels[0][0] == "甘狼このみ / AmakamiKonomi🐺🍫":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="You are either here at the beginning or think that the CEO is cool")
    if topChannels[0][0] == "小廻こま / Komawari Koma":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="You like vtubers that has a wide vocal range... or cute")
    if topChannels[0][0] == "ゆらぎゆら / YuragiYura🌙🫧":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="You either call her Yura-nee or Yura-mama")
    if topChannels[0][0] == "虹深°ぬふ / Nijipuka Nuhu":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="You think her designing her own model and can change her hair color is cool as hell (also she has a cute face and a cute voice and a cute everything)")
    if topChannels[0][0] == "海琳あおい / Mitama Aoi":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="Already a fan of her or not, welcome to MilPro, hope you enjoy your stay")
    if topChannels[0][0] == "眠雲ツクリ / NemukumoTsukuri":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="Cool girls are your cup of tea, also you like floating on clouds")
    if topChannels[0][0] == "雨夜リズ / Amayo Liz":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="You like quiet and reserved girls, and a little bit moody when it rains")
    if topChannels[0][0] == "夕霧レイ / YugiriRay":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="Now that's what I call a tomboy, great taste not gonna lie")
    if topChannels[0][0] == "音ノ乃のの / NononoNono":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="The chance of you being rejected when professing to her is 500%")
    if topChannels[0][0] == "あくび・でもんすぺーど / Akubi Demonspade":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="2000 years old loli demon? Really?")
    if topChannels[0][0] == "鹿乃まほろ / Kano Mahoro":
        url = fileData["items"][0]["snippet"]["thumbnails"]["high"]["url"]
        embedMember.set_thumbnail(url=url)
        embedMember.add_field(name=f"{topChannels[0][0]}!", inline=False, value="I can smell the osu gamers miles away... Jokes aside she already has a huge fanbase so, welcome?")
    await ctx.send(embed=embedMember)

@bot.command(name="details")
async def details(ctx):
    embed = discord.Embed(title="Every channels you have watched", color=0x8000FF)
    embed.set_image(url="https://pbs.twimg.com/profile_banners/1628632642492198912/1786888616/1500x500")
    channelTable = []
    cur.execute("DROP TABLE IF EXISTS channelViews")
    cur.execute("""
        CREATE TABLE channelViews(
        channelName TEXT,
        views INTERGER
        )
    """)
    for channel, viewCount in cur.execute("SELECT channel, viewCount FROM watchHistory ORDER BY viewCount DESC"):
        for channelItem in channelTable:
            if channelItem[0] == channel:
                channelItem[1] += viewCount
                break
        else:
            channelTable.append([channel, viewCount])
    cur.executemany("INSERT INTO channelViews VALUES(?, ?)", channelTable)
    for channelName, views in cur.execute("SELECT channelName, views from channelViews ORDER BY views DESC"):
        embed.add_field(name=channelName, inline=False, value=f"Views: {views}")
    await ctx.send(embed=embed)

bot.run()
