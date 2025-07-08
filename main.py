import discord
from discord.ext import commands
import ctypes
import json
import os
import random
import requests
import asyncio
import string
import time
import datetime
from colorama import Fore
import platform
import itertools
from gtts import gTTS
import io
import qrcode
import pyfiglet

y = Fore.LIGHTYELLOW_EX
b = Fore.LIGHTBLUE_EX
w = Fore.LIGHTWHITE_EX

__version__ = "3.2"

start_time = datetime.datetime.now(datetime.timezone.utc)

with open("config/config.json", "r") as file:
    config = json.load(file)
    token = os.getenv("DISCORD_TOKEN") or config.get("token")
    prefix = config.get("prefix")
    message_generator = itertools.cycle(config["autoreply"]["messages"])

def save_config(config):
    with open("config/config.json", "w") as file:
        json.dump(config, file, indent=4)

def selfbot_menu(bot):
    if platform.system() == "Windows":
        os.system('cls')
    else:
        os.system('clear')
    print(f"""\n{Fore.RESET}
                            ██████╗ ████████╗██╗ ██████╗     ████████╗ ██████╗  ██████╗ ██╗     
                           ██╔═══██╗╚══██╔══╝██║██╔═══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║     
                           ██║██╗██║   ██║   ██║██║   ██║       ██║   ██║   ██║██║   ██║██║     
                           ██║██║██║   ██║   ██║██║   ██║       ██║   ██║   ██║██║   ██║██║     
                           ╚█║████╔╝   ██║   ██║╚██████╔╝       ██║   ╚██████╔╝╚██████╔╝███████╗
                            ╚╝╚═══╝    ╚═╝   ╚═╝ ╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝\n""".replace('█', f'{b}█{y}'))
    print(f"""{y}------------------------------------------------------------------------------------------------------------------------
{w}raadev {b}|{w} https://github.com/AstraaDev {b}|{w} https://github.com/AstraaDev {b}|{w} https://github.com/AstraaDev {b}|{w} https://github.com
{y}------------------------------------------------------------------------------------------------------------------------\n""")
    print(f"""{y}[{b}+{y}]{w} SelfBot Information:\n
\t{y}[{w}#{y}]{w} Version: v{__version__}
\t{y}[{w}#{y}]{w} Logged in as: {bot.user} ({bot.user.id})
\t{y}[{w}#{y}]{w} Cached Users: {len(bot.users)}
\t{y}[{w}#{y}]{w} Guilds Connected: {len(bot.guilds)}\n\n
{y}[{b}+{y}]{w} Settings Overview:\n
\t{y}[{w}#{y}]{w} SelfBot Prefix: {prefix}
\t{y}[{w}#{y}]{w} Remote Users Configured:""")
    if config["remote-users"]:
        for i, user_id in enumerate(config["remote-users"], start=1):
            print(f"\t\t{y}[{w}{i}{y}]{w} User ID: {user_id}")
    else:
        print(f"\t\t{y}[{w}-{y}]{w} No remote users configured.")
    print(f"""
\t{y}[{w}#{y}]{w} Active Autoreply Channels: {len(config["autoreply"]["channels"])}
\t{y}[{w}#{y}]{w} Active Autoreply Users: {len(config["autoreply"]["users"])}\n
\t{y}[{w}#{y}]{w} AFK Status: {'Enabled' if config["afk"]["enabled"] else 'Disabled'}
\t{y}[{w}#{y}]{w} AFK Message: "{config["afk"]["message"]}"\n
\t{y}[{w}#{y}]{w} Total Commands Loaded: 43\n\n
{y}[{Fore.GREEN}!{y}]{w} SelfBot is now online and ready!""")


bot = commands.Bot(command_prefix=prefix, description='not a selfbot', self_bot=True, help_command=None)

@bot.event
async def on_ready():
    if platform.system() == "Windows":
        ctypes.windll.kernel32.SetConsoleTitleW(f"SelfBot v{__version__} - Made By a5traa")
        os.system('cls')
    else:
        os.system('clear')
    selfbot_menu(bot)

@bot.event
async def on_message(message):
    if message.author.id in config["copycat"]["users"]:
        if message.content.startswith(config['prefix']):
            response_message = message.content[len(config['prefix']):]
            await message.reply(response_message)
        else:
            await message.reply(message.content)

    if config["afk"]["enabled"]:
        if bot.user in message.mentions and message.author != bot.user:
            await message.reply(config["afk"]["message"])
            return
        elif isinstance(message.channel, discord.DMChannel) and message.author != bot.user:
            await message.reply(config["afk"]["message"])
            return

    if message.author != bot.user:
        if str(message.author.id) in config["autoreply"]["users"]:
            autoreply_message = next(message_generator)
            await message.reply(autoreply_message)
            return
        elif str(message.channel.id) in config["autoreply"]["channels"]:
            autoreply_message = next(message_generator)
            await message.reply(autoreply_message)
            return

    if message.guild and message.guild.id == 1279905004181917808 and message.content.startswith(config['prefix']):
        await message.delete()
        await message.channel.send("> SelfBot commands are not allowed here. Thanks.", delete_after=5)
        return

    if message.author != bot.user and str(message.author.id) not in config["remote-users"]:
        return

    await bot.process_commands(message)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return

@bot.event
async def on_voice_state_update(member, before, after):
    # Check if the member is the user we want to follow
    if member.id in config["copycat"]["users"]:
        # Get the bot's current voice client for this guild
        voice_client = discord.utils.get(bot.voice_clients, guild=member.guild)

        # If the followed user joins a voice channel
        if after.channel and before.channel != after.channel:
            try:
                # If bot is already in a voice channel, disconnect first
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()

                # Join the same voice channel as the followed user
                await after.channel.connect()
                print(f"Following {member.name} to voice channel: {after.channel.name}")

            except Exception as e:
                print(f"Error joining voice channel: {e}")

        # If the followed user leaves voice chat
        elif before.channel and not after.channel:
            try:
                # If bot is in a voice channel, disconnect
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                print(f"{member.name} left voice, disconnecting bot")

            except Exception as e:
                print(f"Error leaving voice channel: {e}")

        # If the followed user switches voice channels
        elif before.channel and after.channel and before.channel != after.channel:
            try:
                # Disconnect from current channel and join new one
                if voice_client and voice_client.is_connected():
                    await voice_client.disconnect()
                await after.channel.connect()
                print(f"Following {member.name} from {before.channel.name} to {after.channel.name}")

            except Exception as e:
                print(f"Error switching voice channels: {e}")

@bot.command(aliases=["joinvc", "jvc"])
async def joinvoice(ctx, channel: discord.VoiceChannel=None):
    await ctx.message.delete()

    if not channel:
        # If no channel specified, join the user's current voice channel
        if ctx.author.voice:
            channel = ctx.author.voice.channel
        else:
            await ctx.send("> **[**ERROR**]**: You're not in a voice channel and no channel was specified.", delete_after=5)
            return

    try:
        # Disconnect from current channel if connected
        if ctx.guild.voice_client:
            await ctx.guild.voice_client.disconnect()

        # Connect to the new channel
        await channel.connect()
        await ctx.send(f"> Joined voice channel: `{channel.name}`", delete_after=5)
    except Exception as e:
        await ctx.send(f"> **[**ERROR**]**: Could not join voice channel: `{str(e)}`", delete_after=5)

@bot.command(aliases=["leavevc", "lvc"])
async def leavevoice(ctx):
    await ctx.message.delete()

    if ctx.guild.voice_client:
        await ctx.guild.voice_client.disconnect()
        await ctx.send("> Left voice channel", delete_after=5)
    else:
        await ctx.send("> **[**ERROR**]**: Not currently in a voice channel", delete_after=5)


@bot.command(aliases=['h'])
async def help(ctx):
    await ctx.message.delete()

    help_text = f"""
**Astraa SelfBot | Prefix: `{prefix}`**\n
**Commands:**\n
> :space_invader: `{prefix}astraa` - Show my social networks.
> :wrench: `{prefix}changeprefix <prefix>` - Change the bot's prefix.  
> :x: `{prefix}shutdown` - Stop the selfbot.  
> :notepad_spiral: `{prefix}uptime` - Returns how long the selfbot has been running.
> :closed_lock_with_key: `{prefix}remoteuser <@user>` - Authorize a user to execute commands remotely.
> :robot: `{prefix}copycat ON|OFF <@user>` - Automatically reply with the same message whenever the mentioned user speaks. 
> :pushpin: `{prefix}ping` - Returns the bot's latency.
> :pushpin: `{prefix}pingweb <url>` - Ping a website and return the HTTP status code (e.g., 200 if online).
> :gear: `{prefix}geoip <ip>` - Looks up the IP's location.
> :microphone: `{prefix}tts <text>` - Converts text to speech and sends an audio file (.wav).
> :hash: `{prefix}qr <text>` - Generate a QR code from the provided text and send it as an image.
> :detective: `{prefix}hidemention <display_part> <hidden_part>` - Hide messages inside other messages.
> :wrench: `{prefix}edit <message>` - Move the position of the (edited) tag.
> :arrows_counterclockwise: `{prefix}reverse <message>` - Reverse the letters of a message.
> :notepad_spiral: `{prefix}gentoken` - Generate an invalid but correctly patterned token.
> :woozy_face: `{prefix}hypesquad <house>` - Change your HypeSquad badge.
> :dart: `{prefix}nitro` - Generate a fake Nitro code.
> :hammer: `{prefix}whremove <webhook_url>` - Remove a webhook.
> :broom: `{prefix}purge <amount>` - Delete a specific number of messages.
> :broom: `{prefix}clear` - Clear messages from a channel. 
> :broom: `{prefix}cleardm <amount>` - Delete all DMs with a user."""
    await ctx.send(help_text)

    help_text = f"""
> :writing_hand: `{prefix}spam <amount> <message>` - Spams a message for a given amount of times.
> :tools: `{prefix}quickdelete <message>` - Send a message and delete it after 2 seconds.
> :tools: `{prefix}autoreply <ON|OFF>` - Enable or disable automatic replies.
> :zzz: `{prefix}afk <ON/OFF>` - Enable or disable AFK mode. Sends a custom message when receiving a DM or being mentioned.
> :busts_in_silhouette: `{prefix}fetchmembers` - Retrieve the list of all members in the server.
> :scroll: `{prefix}firstmessage` - Get the link to the first message in the current channel.
> :mega: `{prefix}dmall <message>` - Send a message to all members in the server.
> :mega: `{prefix}sendall <message>` - Send a message to all channels in the server.
> :busts_in_silhouette: `{prefix}guildicon` - Get the icon of the current server.
> :space_invader: `{prefix}usericon <@user>` - Get the profile picture of a user.
> :star: `{prefix}guildbanner` - Get the banner of the current server.
> :page_facing_up: `{prefix}tokeninfo <token>` - Scrape info with a token.
> :pager: `{prefix}guildinfo` - Get information about the current server.
> :memo: `{prefix}guildrename <new_name>` - Rename the server.
> :video_game: `{prefix}playing <status>` - Set the bot's activity status as "Playing".  
> :tv: `{prefix}watching <status>` - Set the bot's activity status as "Watching".  
> :x: `{prefix}stopactivity` - Reset the bot's activity status.
> :art: `{prefix}ascii <message>` - Convert a message to ASCII art.
> :airplane: `{prefix}airplane` - Sends a 9/11 attack (warning: use responsibly).
> :fire: `{prefix}dick <@user>` - Show the "size" of a user's dick.
> :x: `{prefix}minesweeper <width> <height>` - Play a game of Minesweeper with custom grid size.
> :robot: `{prefix}leetpeek <message>` - Speak like a hacker, replacing letters."""
    await ctx.send(help_text)

@bot.command()
async def uptime(ctx):
    await ctx.message.delete()

    now = datetime.datetime.now(datetime.timezone.utc)
    delta = now - start_time
    hours, remainder = divmod(int(delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    days, hours = divmod(hours, 24)

    if days:
        time_format = "**{d}** days, **{h}** hours, **{m}** minutes, and **{s}** seconds."
    else:
        time_format = "**{h}** hours, **{m}** minutes, and **{s}** seconds."

    uptime_stamp = time_format.format(d=days, h=hours, m=minutes, s=seconds)

    await ctx.send(uptime_stamp)

@bot.command()
async def ping(ctx):
    await ctx.message.delete()

    before = time.monotonic()
    message_to_send = await ctx.send("Pinging...")

    await message_to_send.edit(content=f"`{int((time.monotonic() - before) * 1000)} ms`")

@bot.command(aliases=['astra'])
async def astraa(ctx):
    await ctx.message.delete()

    embed = f"""**MY SOCIAL NETWORKS | Prefix: `{prefix}`**\n
    > :pager: `Discord Server`\n*https://discord.gg/PKR7nM9j9U*
    > :computer: `GitHub Page`\n*https://github.com/AstraaDev*
    > :robot: `SelfBot Project`\n*https://github.com/AstraaDev/Discord-SelfBot*"""

    await ctx.send(embed)

@bot.command()
async def geoip(ctx, ip: str=None):
    await ctx.message.delete()

    if not ip:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `geoip <ip>`", delete_after=5)
        return

    try:
        r = requests.get(f'http://ip-api.com/json/{ip}')
        geo = r.json()
        embed = f"""**GEOLOCATE IP | Prefix: `{prefix}`**\n
        > :pushpin: `IP`\n*{geo['query']}*
        > :globe_with_meridians: `Country-Region`\n*{geo['country']} - {geo['regionName']}*
        > :department_store: `City`\n*{geo['city']} ({geo['zip']})*
        > :map: `Latitute-Longitude`\n*{geo['lat']} - {geo['lon']}*
        > :satellite: `ISP`\n*{geo['isp']}*
        > :robot: `Org`\n*{geo['org']}*
        > :alarm_clock: `Timezone`\n*{geo['timezone']}*
        > :electric_plug: `As`\n*{geo['as']}*"""
        await ctx.send(embed, file=discord.File("img/astraa.gif"))
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to geolocate ip\n> __Error__: `{str(e)}`', delete_after=5)

@bot.command()
async def tts(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `tts <message>`", delete_after=5)
        return

    content = content.strip()

    tts = gTTS(text=content, lang="en")

    f = io.BytesIO()
    tts.write_to_fp(f)
    f.seek(0)

    await ctx.send(file=discord.File(f, f"{content[:10]}.wav"))

@bot.command(aliases=['qrcode'])
async def qr(ctx, *, text: str="https://discord.gg/PKR7nM9j9U"):
    qr = qrcode.make(text)

    img_byte_arr = io.BytesIO()
    qr.save(img_byte_arr)
    img_byte_arr.seek(0)

    await ctx.send(file=discord.File(img_byte_arr, "qr_code.png"))

@bot.command()
async def pingweb(ctx, website_url: str=None):
    await ctx.message.delete()

    if not website_url:
        await ctx.send("> **[ERROR]**: Invalid command.\n> __Command__: `pingweb <url>`", delete_after=5)
        return

    try:
        r = requests.get(website_url).status_code
        if r == 404:
            await ctx.send(f'> Website **down** *({r})*')
        else:
            await ctx.send(f'> Website **operational** *({r})*')
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to ping website\n> __Error__: `{str(e)}`', delete_after=5)

@bot.command()
async def gentoken(ctx, user: str=None):
    await ctx.message.delete()

    code = "ODA"+random.choice(string.ascii_letters)+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(20))+"."+random.choice(string.ascii_letters).upper()+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))+"."+''.join(random.choice(string.ascii_letters + string.digits) for _ in range(27))

    if not user:
        await ctx.send(''.join(code))
    else:
        await ctx.send(f"> {user}'s token is: ||{''.join(code)}||")

@bot.command()
async def quickdelete(ctx, *, message: str=None):
    await ctx.message.delete()

    if not message:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `quickdelete <message>`', delete_after=2)
        return

    await ctx.send(message, delete_after=2)

@bot.command(aliases=['uicon'])
async def usericon(ctx, user: discord.User = None):
    await ctx.message.delete()

    if not user:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `usericon <@user>`', delete_after=5)
        return

    avatar_url = user.avatar.url if user.avatar else user.default_avatar.url

    await ctx.send(f"> {user.mention}'s avatar:\n{avatar_url}")

@bot.command(aliases=['tinfo'])
async def tokeninfo(ctx, usertoken: str=None):
    await ctx.message.delete()

    if not usertoken:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `tokeninfo <token>`', delete_after=5)
        return

    headers = {'Authorization': usertoken, 'Content-Type': 'application/json'}
    languages = {
        'da': 'Danish, Denmark',
        'de': 'German, Germany',
        'en-GB': 'English, United Kingdom',
        'en-US': 'English, United States',
        'es-ES': 'Spanish, Spain',
        'fr': 'French, France',
        'hr': 'Croatian, Croatia',
        'lt': 'Lithuanian, Lithuania',
        'hu': 'Hungarian, Hungary',
        'nl': 'Dutch, Netherlands',
        'no': 'Norwegian, Norway',
        'pl': 'Polish, Poland',
        'pt-BR': 'Portuguese, Brazilian, Brazil',
        'ro': 'Romanian, Romania',
        'fi': 'Finnish, Finland',
        'sv-SE': 'Swedish, Sweden',
        'vi': 'Vietnamese, Vietnam',
        'tr': 'Turkish, Turkey',
        'cs': 'Czech, Czechia, Czech Republic',
        'el': 'Greek, Greece',
        'bg': 'Bulgarian, Bulgaria',
        'ru': 'Russian, Russia',
        'uk': 'Ukrainian, Ukraine',
        'th': 'Thai, Thailand',
        'zh-CN': 'Chinese, China',
        'ja': 'Japanese',
        'zh-TW': 'Chinese, Taiwan',
        'ko': 'Korean, Korea'
    }

    try:
        res = requests.get('https://discordapp.com/api/v6/users/@me', headers=headers)
        res.raise_for_status()
    except requests.exceptions.RequestException as e:
        await ctx.send(f'> **[**ERROR**]**: An error occurred while sending request\n> __Error__: `{str(e)}`', delete_after=5)
        return

    if res.status_code == 200:
        res_json = res.json()
        user_name = f'{res_json["username"]}#{res_json["discriminator"]}'
        user_id = res_json['id']
        avatar_id = res_json['avatar']
        avatar_url = f'https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}.gif'
        phone_number = res_json['phone']
        email = res_json['email']
        mfa_enabled = res_json['mfa_enabled']
        flags = res_json['flags']
        locale = res_json['locale']
        verified = res_json['verified']
        days_left = ""
        language = languages.get(locale)
        creation_date = datetime.datetime.fromtimestamp(((int(user_id) >> 22) + 1420070400000) / 1000).strftime('%d-%m-%Y %H:%M:%S UTC')
        has_nitro = False

        try:
            nitro_res = requests.get('https://discordapp.com/api/v6/users/@me/billing/subscriptions', headers=headers)
            nitro_res.raise_for_status()
            nitro_data = nitro_res.json()
            has_nitro = bool(len(nitro_data) > 0)
            if has_nitro:
                d1 = datetime.datetime.strptime(nitro_data[0]["current_period_end"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                d2 = datetime.datetime.strptime(nitro_data[0]["current_period_start"].split('.')[0], "%Y-%m-%dT%H:%M:%S")
                days_left = abs((d2 - d1).days)
        except requests.exceptions.RequestException as e:
            pass

        try:
            embed = f"""**TOKEN INFORMATIONS | Prefix: `{prefix}`**\n
        > :dividers: __Basic Information__\n\tUsername: `{user_name}`\n\tUser ID: `{user_id}`\n\tCreation Date: `{creation_date}`\n\tAvatar URL: `{avatar_url if avatar_id else "None"}`
        > :crystal_ball: __Nitro Information__\n\tNitro Status: `{has_nitro}`\n\tExpires in: `{days_left if days_left else "None"} day(s)`
        > :incoming_envelope: __Contact Information__\n\tPhone Number: `{phone_number if phone_number else "None"}`\n\tEmail: `{email if email else "None"}`
        > :shield: __Account Security__\n\t2FA/MFA Enabled: `{mfa_enabled}`\n\tFlags: `{flags}`
        > :paperclip: __Other__\n\tLocale: `{locale} ({language})`\n\tEmail Verified: `{verified}`"""

            await ctx.send(embed, file=discord.File("img/astraa.gif"))
        except Exception as e:
            await ctx.send(f'> **[**ERROR**]**: Unable to recover token infos\n> __Error__: `{str(e)}`', delete_after=5)
    else:
        await ctx.send(f'> **[**ERROR**]**: Unable to recover token infos\n> __Error__: Invalid token', delete_after=5)

@bot.command()
async def cleardm(ctx, amount: str="1"):
    await ctx.message.delete()

    if not amount.isdigit():
        await ctx.send(f'> **[**ERROR**]**: Invalid amount specified. It must be a number.\n> __Command__: `{config["prefix"]}cleardm <amount>`', delete_after=5)
        return

    amount = int(amount)

    if amount <= 0 or amount > 100:
        await ctx.send(f'> **[**ERROR**]**: Amount must be between 1 and 100.', delete_after=5)
        return

    if not isinstance(ctx.channel, discord.DMChannel):
        await ctx.send(f'> **[**ERROR**]**: This command can only be used in DMs.', delete_after=5)
        return

    deleted_count = 0
    async for message in ctx.channel.history(limit=amount):
        if message.author == bot.user:
            try:
                await message.delete()
                deleted_count += 1
            except discord.Forbidden:
                await ctx.send(f'> **[**ERROR**]**: Missing permissions to delete messages.', delete_after=5)
                return
            except discord.HTTPException as e:
                await ctx.send(f'> **[**ERROR**]**: An error occurred while deleting messages: {str(e)}', delete_after=5)
                return

    await ctx.send(f'> **Cleared {deleted_count} messages in DMs.**', delete_after=5)


@bot.command(aliases=['hs'])
async def hypesquad(ctx, house: str=None):
    await ctx.message.delete()

    if not house:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `hypesquad <house>`', delete_after=5)
        return

    headers = {'Authorization': token, 'Content-Type': 'application/json'}

    try:
        r = requests.get('https://discord.com/api/v8/users/@me', headers=headers)
        r.raise_for_status()
    except requests.exceptions.RequestException as e:
        await ctx.send(f'> **[**ERROR**]**: Invalid status code\n> __Error__: `{str(e)}`', delete_after=5)
        return

    headers = {'Authorization': token, 'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) discord/0.0.305 Chrome/69.0.3497.128 Electron/4.0.8 Safari/537.36'}
    payload = {}
    if house == "bravery":
        payload = {'house_id': 1}
    elif house == "brilliance":
        payload = {'house_id': 2}
    elif house == "balance":
        payload = {'house_id': 3}
    else:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Error__: Hypesquad house must be one of the following: `bravery`, `brilliance`, `balance`', delete_after=5)
        return

    try:
        r = requests.post('https://discordapp.com/api/v6/hypesquad/online', headers=headers, json=payload, timeout=10)
        r.raise_for_status()

        if r.status_code == 204:
            await ctx.send(f'> Hypesquad House changed to `{house}`!')

    except requests.exceptions.RequestException as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to change Hypesquad house\n> __Error__: `{str(e)}`', delete_after=5)

@bot.command(aliases=['ginfo'])
async def guildinfo(ctx):
    await ctx.message.delete()

    if not ctx.guild:
        await ctx.send("> **[**ERROR**]**: This command can only be used in a server", delete_after=5)
        return

    date_format = "%a, %d %b %Y %I:%M %p"
    embed = f"""> **GUILD INFORMATIONS | Prefix: `{prefix}`**
:dividers: __Basic Information__
Server Name: `{ctx.guild.name}`\nServer ID: `{ctx.guild.id}`\nCreation Date: `{ctx.guild.created_at.strftime(date_format)}`\nServer Icon: `{ctx.guild.icon.url if ctx.guild.icon.url else 'None'}`\nServer Owner: `{ctx.guild.owner}`
:page_facing_up: __Other Information__
`{len(ctx.guild.members)}` Members\n`{len(ctx.guild.roles)}` Roles\n`{len(ctx.guild.text_channels) if ctx.guild.text_channels else 'None'}` Text-Channels\n`{len(ctx.guild.voice_channels) if ctx.guild.voice_channels else 'None'}` Voice-Channels\n`{len(ctx.guild.categories) if ctx.guild.categories else 'None'}` Categories"""

    await ctx.send(embed)

@bot.command()
async def nitro(ctx):
    await ctx.message.delete()

    await ctx.send(f"https://discord.gift/{''.join(random.choices(string.ascii_letters + string.digits, k=16))}")

@bot.command()
async def whremove(ctx, webhook: str=None):
    await ctx.message.delete()

    if not webhook:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `{prefix}whremove <webhook>`', delete_after=5)
        return

    try:
        requests.delete(webhook.rstrip())
    except Exception as e:
        await ctx.send(f'> **[**ERROR**]**: Unable to delete webhook\n> __Error__: `{str(e)}`', delete_after=5)
        return

    await ctx.send(f'> Webhook has been deleted!')

@bot.command(aliases=['hide'])
async def hidemention(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `{prefix}hidemention <message>`', delete_after=5)
        return

    await ctx.send(content + ('||\u200b||' * 200) + '@everyone')

@bot.command()
async def edit(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `edit <message>`', delete_after=5)
        return

    msg = await ctx.send(content)
    await msg.edit(content=f"{content} **(edited)**")

@bot.command()
async def reverse(ctx, *, content: str=None):
    await ctx.message.delete()

    if not content:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `reverse <message>`', delete_after=5)
        return

    await ctx.send(content[::-1])

@bot.command()
async def spam(ctx, amount: int=None, *, message: str=None):
    await ctx.message.delete()

    if not amount or not message:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `spam <amount> <message>`', delete_after=5)
        return

    if amount > 50:
        await ctx.send(f'> **[**ERROR**]**: Amount cannot exceed 50', delete_after=5)
        return

    for _ in range(amount):
        await ctx.send(message)

@bot.command()
async def copycat(ctx, toggle: str=None, user: discord.User=None):
    await ctx.message.delete()

    if not toggle or not user:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `copycat <ON|OFF> <@user>`', delete_after=5)
        return

    if toggle.upper() == "ON":
        if user.id not in config['copycat']['users']:
            config['copycat']['users'].append(user.id)
            save_config(config)
            await ctx.send(f"> Now copying `{str(user)}` (text + voice)", delete_after=5)
        else:
            await ctx.send(f"> `{str(user)}` is already being copied.", delete_after=5)
    elif toggle.upper() == "OFF":
        if user.id in config['copycat']['users']:
            config['copycat']['users'].remove(user.id)
            save_config(config)
            await ctx.send(f"> No longer copying `{str(user)}`", delete_after=5)
        else:
            await ctx.send(f"> `{str(user)}` was not being copied.", delete_after=5)

@bot.command()
async def firstmessage(ctx):
    await ctx.message.delete()

    messages = [msg async for msg in ctx.channel.history(limit=1, oldest_first=True)]
    if messages:
        await ctx.send(f"> First message: {messages[0].jump_url}")
    else:
        await ctx.send("> No messages found in this channel", delete_after=5)

@bot.command()
async def shutdown(ctx):
    await ctx.message.delete()
    await ctx.send("> Shutting down selfbot...", delete_after=3)
    await bot.close()

@bot.command()
async def changeprefix(ctx, new_prefix: str=None):
    await ctx.message.delete()

    if not new_prefix:
        await ctx.send(f'> **[**ERROR**]**: Invalid input\n> __Command__: `changeprefix <prefix>`', delete_after=5)
        return

    config['prefix'] = new_prefix
    save_config(config)
    bot.command_prefix = new_prefix
    await ctx.send(f"> Prefix changed to `{new_prefix}`", delete_after=5)

bot.run(token)