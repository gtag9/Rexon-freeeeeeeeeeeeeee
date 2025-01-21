import aiohttp, asyncio, random, time
from datetime import datetime
from discord_webhook import AsyncDiscordWebhook, DiscordEmbed

#-------------------------------------------[GLOBAL VARS]--------------------------------------------
SPEED = 1

global_blacklisted = []
global_concats = {}

global_session_tickets = []
global_dead_session_tickets = []


tracker_notification_urls = []
public_webhook_urls = []
private_webhook_urls = []
player_left_webhook_urls = []

found_codes= {}

green = "00FF00"
red = "FF0000"
grey = "808080"

admin_badge_image = "https://media.discordapp.net/attachments/1295505731612835871/1315154306680225874/60ESRBGW2KgAAAAASUVORK5CYII.png?ex=67682ca5&is=6766db25&hm=7a3a7b045970b603b37ddf7023fc531807da4b00343c62d7d9f4245806833547&=&format=webp&quality=lossless&width=498&height=498"
stick_image = "https://media.discordapp.net/attachments/1245897958013145230/1259632101129457764/image_2023-07-29_092344244-Photoroom.png?ex=67688dcf&is=67673c4f&hm=93f3accede4542d4866372e25ff616d30dae014dcdab6416c12c7dd7cd7b49ba&=&format=webp&quality=lossless&width=450&height=450"
illustrator_badge_image = "https://media.discordapp.net/attachments/1245897958013145230/1259632896851837042/IllustratorbadgeTransparent.webp?ex=67688e8d&is=67673d0d&hm=c34007ba50f8791233e0a0a9d80d1ffbcf9ca770beaf80aace320870a9d51379&=&format=webp&width=1000&height=1000"
finger_painter_image = "https://images-ext-1.discordapp.net/external/Pat_dhjj2Tm8yZLNmTQRTP2kEoLQdQeKic6iXi9DrSI/https/tr.rbxcdn.com/5acad38fc4922e8240f2f3bc596da009/420/420/Hat/Webp?format=webp&width=840&height=840"
unreleased_sweater_image = "https://media.discordapp.net/attachments/1245897958013145230/1259632742342066237/sweater-removebg-preview.png?ex=67688e68&is=67673ce8&hm=1f5395dc7c06e85c5d89e3e7ed42830758f933adfd43bd86d21b879f5dad19aa&=&format=webp&quality=lossless&width=394&height=528"

test_image = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQgdC4mMlvGJqyYg87iDUCir4RnbJ2bAqG_LQ&s"

#--------------------------------------------[NICE LOGS]---------------------------------------------
BOLD = "\033[1m"
RED = "\033[0;31m"
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
BLUE = "\033[0;34m"
ITALIC = "\033[3m"
END = "\033[0m"

class Logger:
    PASS = 1
    DEBUG = 2
    INFO = 3
    ERROR = 4
    INIT = 5

    PASS_ENABLED = True
    DEBUG_ENABLED = True
    INFO_ENABLED = True
    ERROR_ENABLED = True

    @staticmethod
    def generate_timestamp():
        return datetime.now().strftime("%H:%M:%S")

    @staticmethod
    def log(message, log_type):
        if log_type == Logger.PASS and Logger.PASS_ENABLED:
            print(f"{END}[{BOLD}{ITALIC}{YELLOW}{Logger.generate_timestamp()}{END}] {END}[{GREEN}{BOLD}{ITALIC}PASS{END}] {message}")

        elif log_type == Logger.DEBUG and Logger.DEBUG_ENABLED:
            print(f"{END}[{BOLD}{ITALIC}{YELLOW}{Logger.generate_timestamp()}{END}] {END}[{YELLOW}{BOLD}{ITALIC}DEBUG{END}] {message}")

        elif log_type == Logger.INFO and Logger.INFO_ENABLED:
            print(f"{END}[{BOLD}{ITALIC}{YELLOW}{Logger.generate_timestamp()}{END}] {END}[{GREEN}{BOLD}{ITALIC}INFO{END}] {message}")

        elif log_type == Logger.ERROR and Logger.ERROR_ENABLED:
            print(f"{END}[{BOLD}{ITALIC}{YELLOW}{Logger.generate_timestamp()}{END}] {END}[{RED}{BOLD}{ITALIC}ERROR{END}] {message}")

        elif log_type == Logger.INIT:
            print(f"{END}[{BOLD}{ITALIC}{YELLOW}{Logger.generate_timestamp()}{END}] {END}[{BLUE}{BOLD}{ITALIC}INIT{END}] {message}")

#----------------------------------------[GET MAIN VARIABLES]----------------------------------------

async def get_blacklisted() -> None:
    with open("blacklisted.txt") as local_blacklisted:
        for blacklisted in local_blacklisted:
            global_blacklisted.append(blacklisted)

async def get_concats() -> None:
    with open("concats.txt", "r") as local_concats:
        for local_concat in local_concats:
            concat_data = local_concat.split(";")

            concat_str = concat_data[0]
            concat_name = concat_data[1]
            concat_image = concat_data[2]

            global_concats[concat_str]["name"] = concat_name
            global_concats[concat_str]["image"] = concat_image

async def get_steam_tickets() -> None:
    with open("steam_tickets.txt", "r") as local_steam_tickets:
        for local_steam_ticket in local_steam_tickets:
                async with aiohttp.ClientSession() as session:
                    headers = {"Content-Type":"application/json"}
                    json = {
                        "SteamTicket": local_steam_ticket,
                        "CreateAccount": True,
                        "TitleId": "63FDD",
                    }
                    async with session.post(url="https://63fdd.playfabapi.com/Client/GetSharedGroupData",json=json, headers=headers) as response:
                        responsejson = await response.json()
                        local_session_ticket = responsejson["data"]["SessionTicket"]

                        if not local_session_ticket in global_session_tickets:
                            global_session_tickets.append(local_session_ticket)

async def get_sessions() -> None:
    with open("sessions.txt", "r") as local_session_tickets:
        for local_session_ticket in local_session_tickets:
            if local_session_ticket not in global_dead_session_tickets:
                global_session_tickets.append(local_session_ticket)

    Logger.log(f"{len(global_session_tickets)} session ticket(s) have been retrieved", Logger.INIT)


        Logger.log(f"The auth key has been retrieved", Logger.INIT)

async def get_private_codes() -> list[str]:
    with open("private_codes.txt", "r") as local_private_codes:
        codes = local_private_codes.readlines()
        Logger.log(f"{len(codes)} private codes have been retrieved", Logger.INIT)
        return codes

async def get_public_codes() -> list[str]:
    async with aiohttp.ClientSession() as session:

        async with session.post(url="http://api.lucid-tracker.com:5000/get_rooms", headers=headers) as response:
            raw_public_codes = await response.json()

            codes_string = raw_public_codes[0].get("Codes")

            formatted_codes = codes_string.split(":")

            for i, public_code in enumerate(formatted_codes):
                room_code = public_code[:4]
                room_region = public_code[4:]
                formatted_codes[i] = room_code + ";" + room_region

            Logger.log(f"{len(formatted_codes)} public codes have been retrieved", Logger.INIT)
            return formatted_codes

async def get_tracker_notification_urls() -> None:
    with open("tracker_notification_urls.txt", "r") as local_tracker_notification_urls:
        for local_tracker_notification_url in local_tracker_notification_urls:
            tracker_notification_urls.append(local_tracker_notification_url)

async def get_public_webhook_urls() -> None:
    with open("public_webhook_urls.txt", "r") as local_public_webhook_urls:
        for local_public_webhook_url in local_public_webhook_urls:
            public_webhook_urls.append(local_public_webhook_url)

async def get_private_webhook_urls() -> None:
    with open("private_webhook_urls.txt", "r") as local_private_webhook_urls:
        for local_private_webhook_url in local_private_webhook_urls:
            private_webhook_urls.append(local_private_webhook_url)

async def get_player_left_webhook_urls() -> None:
    with open("player_left_webhook_urls.txt", "r") as local_player_left_webhook_urls:
        for local_player_left_webhook_url in local_player_left_webhook_urls:
            player_left_webhook_urls.append(local_player_left_webhook_url)

#--------------------------------[PUBLIC WEBHOOKS + PRIVATE WEBHOOKS]--------------------------------

async def tracker_notification():
    random.shuffle(tracker_notification_urls)
    tracker_notification_url = random.choice(tracker_notification_urls)

    webhook = AsyncDiscordWebhook(url=tracker_notification_url)
    embed = DiscordEmbed(title="Tracker Started", color=grey)

    embed.add_embed_field(name="**Session Tickets:**", value=f"\n{len(global_session_tickets)}", inline=False)
    embed.add_embed_field(name="**Public Codes:**", value=f"\n{len(await get_public_codes())}", inline=False)
    embed.add_embed_field(name="**Private Codes:**", value=f"\n{len(await get_private_codes())}", inline=False)

    embed.set_footer(text="discord.gg/lucidtracker")

    webhook.add_embed(embed=embed)

    await webhook.execute()

async def public_webhook(found_name: str, code: str, region: str, player_count: str, leaderboard_position: str, role: str, image: str) -> AsyncDiscordWebhook:
    random.shuffle(public_webhook_urls)
    public_webhook_url = random.choice(public_webhook_urls)

    webhook = AsyncDiscordWebhook(url=public_webhook_url, content=role)

    webhook.avatar_url = ""
    embed = DiscordEmbed(title="Player Found", color=green)

    embed.set_thumbnail(url=image)

    embed.add_embed_field(name="**Tracked:**", value=f"\n{found_name}", inline=False)
    embed.add_embed_field(name="**Room:**", value=f"\n{code}", inline=False)
    embed.add_embed_field(name="**Region:**", value=f"\n{region}", inline=False)
    embed.add_embed_field(name="**Player Count:**", value=f"\n{player_count}", inline=False)
    embed.add_embed_field(name="**Leaderboard Pos:**", value=f"\n{leaderboard_position}", inline=False)

    embed.set_footer(text="Don't forget to vouch! | discord.gg/lucidtracker")

    webhook.add_embed(embed=embed)
    
    await webhook.execute()

    return webhook

async def private_webhook(found_name: str, code: str, region: str, player_count: str, leaderboard_position: str, role: str, image: str) -> AsyncDiscordWebhook:
    random.shuffle(private_webhook_urls)
    private_webhook_url = random.choice(private_webhook_urls)

    webhook = AsyncDiscordWebhook(url=private_webhook_url, content=role)
    embed = DiscordEmbed(title="Player Found", color=green)

    embed.set_thumbnail(url=image)

    embed.add_embed_field(name="**Tracked:**", value=f"\n{found_name}", inline=False)
    embed.add_embed_field(name="**Room:**", value=f"\n{code}", inline=False)
    embed.add_embed_field(name="**Region:**", value=f"\n{region}", inline=False)
    embed.add_embed_field(name="**Player Count:**", value=f"\n{player_count}", inline=False)
    embed.add_embed_field(name="**Leaderboard Pos:**", value=f"\n{leaderboard_position}", inline=False)

    embed.set_footer(text="Don't forget to vouch! | discord.gg/lucidtracker")

    webhook.add_embed(embed=embed)

    await webhook.execute()

    return webhook

async def player_left_webhook(found_name: str, code: str, region: str, role: str, image: str) -> None:
    random.shuffle(player_left_webhook_urls)
    player_left_webhook_url = random.choice(player_left_webhook_urls)

    webhook = AsyncDiscordWebhook(url=player_left_webhook_url, content=role)
    embed = DiscordEmbed(title="Player Left", color=red)

    embed.set_thumbnail(url=image)

    embed.add_embed_field(name="**Tracked:**", value=f"\n{found_name}", inline=False)
    embed.add_embed_field(name="**Room:**", value=f"\n{code}", inline=False)
    embed.add_embed_field(name="**Region:**", value=f"\n{region}", inline=False)


    embed.set_footer(text="Don't forget to vouch! | discord.gg/lucidtracker")

    webhook.add_embed(embed=embed)

    await webhook.execute()

#-------------------------------------------[PROCESS ROOM]-------------------------------------------

async def get_shared_group_data(headers, json):

    async with aiohttp.ClientSession() as session:
        async with session.post(
                url="https://63fdd.playfabapi.com/Client/GetSharedGroupData",
                json=json,
                headers=headers
        ) as response:
            return await response.json(), response.status

async def player_found(room_data, actor_number, player_count, leaderboard_pos, registered_concat, concat, role_ping, cosmetic="", cosmetic_image="", name="", image=""):
    webhook = None

    code = room_data[0]
    region = room_data[1]
    is_public = room_data[2]

    is_found = False

    found_information = (concat, cosmetic)

    for i in found_codes[code + region]:
        if not found_codes[code + region][i][actor_number]:
            print(f"{cosmetic} found for the first time in code {code, region}")
            found_codes[code + region].append({actor_number:found_information})

    if not is_found:
        if is_public:
            if registered_concat:
                webhook = await public_webhook(found_name=name, code=code, region=region,
                                     player_count=player_count,
                                     leaderboard_position=leaderboard_pos, role=role_ping,
                                     image=image)
            else:
                webhook = await public_webhook(found_name=cosmetic, code=code, region=region,
                                     player_count=player_count,
                                     leaderboard_position=leaderboard_pos, role=role_ping,
                                     image=cosmetic_image)
        else:
            if registered_concat:
                webhook = await private_webhook(found_name=name, code=code, region=region,
                                      player_count=player_count,
                                      leaderboard_position=leaderboard_pos, role=role_ping,
                                      image=image)
            else:
                webhook = await private_webhook(found_name=cosmetic, code=code, region=region,
                                      player_count=player_count,
                                      leaderboard_position=leaderboard_pos, role=role_ping,
                                      image=cosmetic_image)

    while is_found:
        for i in found_codes[code + region]:
            if not found_codes[code + region][i][actor_number]:
                print(f"{cosmetic} left the code {code, region}")
                is_found = False
                webhook.delete()
                if registered_concat:
                    await player_left_webhook(name, code, region, role_ping, image)
                else:
                    await player_left_webhook(cosmetic, code, region, role_ping, cosmetic_image)

async def process_shared_group_data(responsejson, room_data):
    code = room_data[0]
    region = room_data[1]

    leaderboard_pos = 0
    player_count = len(responsejson["data"]["Data"])
    for actor, concat in responsejson["data"]["Data"].items():
        Logger.log(f"Checking actor {actor} for code {code} region {region}", Logger.DEBUG)

        leaderboard_pos += 1
        registered_concat = False
        name = ""
        image = ""

        if concat in global_blacklisted:
            return

        for logged_concat in global_concats:
            if concat in logged_concat:
                registered_concat = True

                name = concat["name"]
                image = concat["image"]

        Logger.log(f"Checking if the actor {actor} in code {code}{region} has the Admin Badge", Logger.DEBUG)
        if "LBAAD." in concat:  # admin badge
            print(f"Admin Badge identified in code {code, region}")

            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="", cosmetic="", cosmetic_image="")
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="<@1320181649777889343>", cosmetic="Admin Badge", cosmetic_image=admin_badge_image)

        Logger.log(f"Checking if the actor {actor} in code {code}{region} has the Stick", Logger.DEBUG)
        if "LBAAK." in concat:  # stick
            Logger.log(f"Stick identified in code {code, region}", Logger.PASS)
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="<@1320181784943656970>", cosmetic="Stick", cosmetic_image=stick_image)

        Logger.log(f"Checking if the actor {actor} in code {code}{region} has the Illustrator Badge", Logger.DEBUG)
        if "LBAGS." in concat:  # illustrator
            Logger.log(f"Illustrator identified in code {code, region}", Logger.PASS)
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="<@1320182142730502154>", cosmetic="Illustrator", cosmetic_image="illustrator_badge_image")

        Logger.log(f"Checking if the actor {actor} in code {code}{region} has the Finger Painter", Logger.DEBUG)
        if "LBADE." in concat:  # finger painter
            Logger.log(f"Finger Painter identified in code {code, region}", Logger.PASS)
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="<@1320181915294367774>", cosmetic="Finger Painter", cosmetic_image=finger_painter_image)

        Logger.log(f"Checking if the actor {actor} in code {code}{region} has the Unreleased Sweater", Logger.DEBUG)
        if "LBACP." in concat:  # unreleased sweater
            Logger.log(f"Unreleased Sweater identified in code {code, region}", Logger.PASS)
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="<@1282213756222443530>", cosmetic="Unreleased Sweater", cosmetic_image=unreleased_sweater_image)

        Logger.log(f"Checking if the actor {actor} in code {code}{region} has the Test Cosmetic", Logger.PASS)
        if "." in concat:  # test
            Logger.log(f"Test person identified in code {code, region}", Logger.DEBUG)
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="No Ping", cosmetic="Test", cosmetic_image=test_image)

        if registered_concat:
            await player_found(room_data, actor, player_count, leaderboard_pos, registered_concat, concat, role_ping="", name=name, image=image)

async def process_private(session_ticket: str, private_codes: list[str]) -> None:
    Logger.log("process_private is running", Logger.INIT)
    random.shuffle(private_codes)
    for private_code in private_codes:
        for region in ["EU", "US", "USW"]:
            room_data = (private_code, region, False)

            json = {"SharedGroupId": private_code.strip() + region.strip()}

            responsejson, status_code = await get_shared_group_data(headers=headers, json=json)

            if status_code == 200:
                Logger.log(f"Checking code {private_code.strip()} region {region.strip()}", Logger.INFO)
                await process_shared_group_data(responsejson, room_data)

            elif status_code == 429:
                Logger.log(f"Attempted to check code {private_code.strip()} region {region.strip()} but was met with status code {status_code}", Logger.ERROR)
                ratelimit = responsejson['retryAfterSeconds']
                await asyncio.sleep(int(ratelimit))

            else:
                Logger.log(f"Attempted to check code {private_code.strip()} region {region.strip()} but was met with status code {status_code}", Logger.ERROR)
                try:
                    global_session_tickets.remove(session_ticket)
                    global_dead_session_tickets.append(session_ticket)
                except Exception:
                    pass

async def process_public(session_ticket: str, public_codes: list[str]) -> None:
    random.shuffle(public_codes)
    for public_code in public_codes:

        raw_room_data = public_code.split(";")
        room_code = raw_room_data[0]
        region = raw_room_data[1]

        room_data = (room_code, region, True)

        json = {"SharedGroupId": public_code + region}

        responsejson, status_code = await get_shared_group_data(headers=headers, json=json)

        if status_code == 200:
            Logger.log(f"Checking code {room_code.strip()} region {region.strip()}", Logger.INFO)
            await process_shared_group_data(responsejson, room_data)

        elif status_code == 429:
            Logger.log(f"Attempted to check code {room_code.strip()} region {region.strip()} but was met with status code {status_code}", Logger.ERROR)
            ratelimit = responsejson['retryAfterSeconds']
            await asyncio.sleep(int(ratelimit))

        else:
            Logger.log(f"Attempted to check code {room_code.strip()} region {region.strip()} but was met with status code {status_code}", Logger.ERROR)
            try:
                global_session_tickets.remove(session_ticket)
                global_dead_session_tickets.append(session_ticket)
            except Exception:
                pass

#-----------------------------------------------[MAIN]-----------------------------------------------
async def main() -> None:
    enabled_loggers = []

    if Logger.PASS_ENABLED:
        enabled_loggers.append("PASS")
    if Logger.DEBUG_ENABLED:
        enabled_loggers.append("DEBUG")
    if Logger.INFO_ENABLED:
        enabled_loggers.append("INFO")
    if Logger.ERROR_ENABLED:
        enabled_loggers.append("ERROR")

    Logger.log(f"The following log types are enabled: {enabled_loggers}", Logger.INIT)
    await get_tracker_notification_urls()
    await get_public_webhook_urls()
    await get_private_webhook_urls()
    await get_player_left_webhook_urls()

    while True:
        await get_sessions()
        await get_steam_tickets()
        await get_concats()
        await get_blacklisted()

        public_codes = await get_public_codes()
        private_codes = await get_private_codes()
        print("\n")

        tasks = []
        for _ in range(SPEED):
            for session_ticket in global_session_tickets:
                process_private_task = asyncio.create_task(process_private(session_ticket, private_codes))
                process_public_task = asyncio.create_task(process_public(session_ticket, public_codes))
                tasks.append(process_public_task)
                tasks.append(process_private_task)
                time.sleep(10)

        await asyncio.gather(*tasks)

#-------------------------------------------[RUNNING MAIN]-------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())