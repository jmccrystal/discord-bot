import os
import random
from time import sleep
import aiohttp
import alexflipnote
import discord
from dotenv import dotenv
from discord.ext import commands
from discord.ext.commands import Context

bot = commands.Bot(command_prefix='.')
bot.remove_command('help')
load_dotenv()

players = {}


@bot.event
async def on_ready():
    print('Bot is logged in and ready to go!')


@bot.event
async def on_member_join(member):
    print(f'{member} joined the server!')


@bot.command()
async def ping(ctx):
    await ctx.send(f'Ping: {round(bot.latency * 1000)} ms')


@bot.command(aliases=['8ball', '8'])
async def _8ball(ctx, *, question):
    responses = [
        'It is certain.',
        'It is decidedly so.',
        'Without a doubt.',
        'Yes – definitely.',
        'You may rely on it.',
        'As I see it, yes.',
        'Most likely.',
        'Outlook good.',
        'Yes.',
        'Signs point to yes.',
        'Reply hazy, try again.',
        'Ask again later.',
        'Better not tell you now.',
        'Cannot predict now.',
        'Concentrate and ask again.',
        "Don't count on it.",
        'My reply is no.',
        'My sources say no.',
        'Outlook not so good.',
        'Very doubtful.']
    await ctx.send(f'{question}\n\n{random.choice(responses)}')


@bot.command(aliases=['d', 'delete', 'purge', 'cls'])
@discord.ext.commands.has_role('Logger')
async def clear(ctx, amount=5):
    if amount == 0:
        await ctx.send("You can't clear zero messages, you silly billy!")
    await ctx.channel.purge(limit=25)


@bot.command()
async def help(ctx):
    await ctx.send(
        "```Log is a bot made by James McCrystal that is meant for server moderation and fun.\n\nIMPORTANT: In order "
        "to use the moderating features of this bot, the user must have a role named 'Logger'. If the user does not "
        "have the role then the moderation commands will do nothing and you will be confused and sad.\n\nPrefix: "
        ".\n\nCommands:\nhelp: Displays this message.\nclear [amount of messages]: Clears the chat by the amount of "
        "messages set in the parameter. Default is 5.\n8ball [question]: Answers all your questions with the help of "
        "magic.\nping: Displays bot latency to server.\nsadcat: Displays a random image of a sad cat.\ncat: Displays "
        "a random image of a cat.\nbirb: Displays a random image of a birb.\ndog: Displays a random image of a "
        "dog.\nsupreme [text]: Displays some text in supreme font and color.\nban [member] [reason]: Bans the given "
        "member for the given reason.\nkick [member] [reason]: Kicks the given member for the given reason.\nunban ["
        "member]: Unbans a given member.\nplay [oof | bruh | augh | slap | coins | coinsrape]: Joins voice channel, plays the given "
        "sound, and leaves.\ndidyoumean [search] [did you mean...]: Displays an image of Google's 'did you mean' "
        "function.```")


@bot.command(aliases=['bird'])
async def birb(ctx):

    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.alexflipnote.dev/birb') as r:
            if r.status == 200:
                js = await r.json()
                await ctx.send(js['file'])


@bot.command()
async def cat(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.alexflipnote.dev/cats') as r:
            if r.status == 200:
                js = await r.json()
                await ctx.send(js['file'])


@bot.command()
async def dog(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.alexflipnote.dev/dogs') as r:
            if r.status == 200:
                js = await r.json()
                await ctx.send(js['file'])


@bot.command()
async def sadcat(ctx):
    async with aiohttp.ClientSession() as session:
        async with session.get('https://api.alexflipnote.dev/sadcat') as r:
            if r.status == 200:
                js = await r.json()
                await ctx.send(js['file'])


@bot.command()
async def supreme(ctx, *, text):
    afa = alexflipnote.Client()
    await ctx.send(await afa.supreme(f"{text}", dark=False))


@bot.command()
@discord.ext.commands.has_role('Logger')
async def kick(ctx, member: discord.Member, *, reason=None):
    await member.kick(reason=reason)
    if reason is not None:
        await ctx.send(f'{member.mention} has been kicked for the reason "{reason}"!')
    else:
        await ctx.send(f'{member.mention} has been kicked!')


@bot.command()
@discord.ext.commands.has_role('Logger')
async def ban(ctx, member: discord.Member, *, reason=None):
    await member.ban(reason=reason)
    if reason is not None:
        await ctx.send(f'{member.mention} has been banned for the reason "{reason}"!')
    else:
        await ctx.send(f'{member.mention} has been banned!')


@bot.command()
@discord.ext.commands.has_role('Logger')
async def unban(ctx, *, member):
    member = member.replace('<', '')
    member = member.replace('>', '')
    member = member.replace('@', '')
    userId = member.replace('!', '')
    user = discord.Object(id=userId)
    await ctx.guild.unban(user)
    await ctx.send(f"{user} has been unbanned!")


"""
@bot.command()
async def join(ctx):
    channel = ctx.message.author.voice.channel
    if not channel:
        await ctx.send("You are not connected to a voice channel")
        return
    voice = get(bot.voice_clients, guild=ctx.guild)
    if voice and voice.is_connected():
        await voice.move_to(channel)
    else:
        voice = await channel.connect()
"""


@bot.command(aliases=['stop'])
async def leave(ctx):
    channel1 = ctx.message.guild.voice_client
    await channel1.disconnect()


@bot.command(aliases=['p'])
async def play(ctx: Context, sfx: str):
    files = {
        "augh": r"augh.mp3",
        "bruh": r"uh.mp3",
        "oof": r"oof.mp3",
        "slap": r"snap.mp3",
        "coins": r"coins.mp3",
        "coinsrape": r"coinsrape.mp3"
    }

    path = files.get(sfx)
    if path is None:
        await ctx.send("Not a valid voice command")
        return

    voice_channel = ctx.message.author.voice.channel
    channel = None
    print(voice_channel)
    if voice_channel is not None:
        channel = voice_channel.name
        vc = await voice_channel.connect()
        vc.play(discord.FFmpegPCMAudio(source=path))
        # Sleep while audio is playing.
        while vc.is_playing():
            sleep(.1)
        await vc.disconnect()
    else:
        await ctx.send("You are not in a channel.")
    # Delete command after the audio is done playing.
    await ctx.message.delete()


@bot.command()
async def didyoumean(ctx, search, *, morelike):
    await ctx.send(f'https://api.alexflipnote.dev/didyoumean?top={search}&bottom={morelike}')

# use the TOKEN env var
bot.run(os.getenv("TOKEN"))
