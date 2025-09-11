import logging.handlers
import os 
import sys
from dotenv import load_dotenv
import discord 
import cv2
import json
import numpy as np
import random
import datetime
import re
import logging
import ping3  #for pinging discord servers because with RKN it has some problems
import gunsmoke
from answerslist import answers, work, workreminder
from discord.ext import tasks
import asyncio

from bson import json_util #if I remember correctly it for time managment

data = None



# file logging
logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter('[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)

#logging console
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

logger.addHandler(handler)
logger.addHandler(console_handler)


with open('reminderimage.png', 'rb') as f:
    picture = discord.File(f)

content  = []

new_data =[{
    "hash": 0,
    "message": 0,
    "server": 0
        }]

#checking if it has json file with imagehashes
if os.path.isfile("imagehash.json") and os.access("imagehash.json", os.R_OK):
    #check if file exists
    logger.info("Imagehash exists")
    try:
        with open('imagehash.json','r') as file:
            exsisting_images=json.load(file)
    except Exception as e:
        json_object = json.dumps(new_data, indent=4)
        with open('imagehash.json','w') as outfile:
            outfile.write(json_object) 
        with open('imagehash.json','r') as file:
            exsisting_images=json.load(file)
else:
    logger.info("Imagehas does not exists. Creating imagehash file")
    #otherwise creating file with json dump
    with open("imagehash.json", 'w') as outfile:
        json_object = json.dumps(new_data, indent=4)
        outfile.write(json_object)
        exsisting_images = new_data

def returnanswers():
    ran = random.randint(0, 7)
    return answers[ran]
def returnworkanswereminder1():
    ran = random.randint(0, 7)
    return work[ran]
def returnworkanswerreminder2():
    ran = random.randint(0, 1)
    return workreminder[ran]

def CompareLinks(message, server, link):
    try:
        for links in exsisting_images:
            if links["link"] == link:
                return links["message"]
            else:
                return None
    except Exception as e:
        new_data ={
            "message": message,
            "server": server,
            "link": link,
            }
        exsisting_images.append(new_data)
        with open('imagehash.json','w') as file:
            json.dump(exsisting_images, file, indent=4)  
        return None

def CompareImages(message, server):
    newimagehash = CalcImageHash("images/savedimage.png")
    try:
        for img in exsisting_images:
            hashscompare = CompareHash(img["hash"], newimagehash)
            if hashscompare > 0.99999 and img["server"] == server:
                return img["message"]
        new_data ={
            "hash": newimagehash,
            "message": message,
            "server": server
            }
        exsisting_images.append(new_data)
        with open('imagehash.json','w') as file:
            json.dump(exsisting_images, file, indent=4)  
        return None
    except Exception as e:
        logging.error(f"Problem with calculating imagehash.{e}")
        new_data ={
            "hash": newimagehash,
            "message": message,
            "server": server
            }
        exsisting_images.append(new_data)
        with open('imagehash.json','w') as file:
            json.dump(exsisting_images, file, indent=4)  
        return None

#function calculateHash
def CalcImageHash(FileName):
    image = cv2.imread(FileName)
    resized = cv2.resize(image, (16,16), interpolation = cv2.INTER_AREA)#make image small
    gray_image=cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)#Make Image Black and white

    dct = cv2.dct(np.float32(gray_image))

    dct_flattened = dct.flatten()
    
    hash_value = (dct_flattened).tolist()

    return hash_value

def CompareHash(hash1,hash2):
    dot_product = np.dot(hash1, hash2)
    norm_a = np.linalg.norm(hash1)
    norm_b = np.linalg.norm(hash2)
    
    if norm_a == 0 or norm_b == 0:
        return 0.0
    
    similarity = dot_product / (norm_a * norm_b)
    logging.info(f"Simularity between images is {similarity}")
    return similarity

#Load token
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') #by os getting our token

# Setup Bot
intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
utc = datetime.timezone.utc
timereminder = datetime.time(hour=9, minute=0, tzinfo=utc)
timereminder2 = datetime.time(hour=8, minute=0, tzinfo=utc)

@tasks.loop(time=timereminder)
async def platoon_timer():
    global event_start, event_end
    ran = random.randint(0, 7)

    try:
        channel = client.get_channel(1321747276129112064)
        await channel.send(returnworkanswereminder1())
        logger.info("reminder for current day was send")
    except Exception as e:
        logger.error("problem with getting channel and sending the message for first daily reminder")
        logger.info(ping3.ping("discord.com"))
        
    gunsmokeanswers = gunsmoke.Gunsmokecheck.checkgunsmoke()

    if gunsmokeanswers != None:
        await channel.send(str(gunsmokeanswers))

    if ran == 0:
        try:
            await channel.send(file=picture)
        except Exception as e:
            logger.error("problem with sending picture reminder")
            logger.info(ping3.ping("discord.com"))


#Time reminder for previous task
@tasks.loop(time=timereminder2)
async def platoon_timer2():
    try:
        channel = client.get_channel(1321747276129112064)
        logger.info("reminder for previous task was send")
        await channel.send(returnworkanswerreminder2())
    except Exception as e:
        logger.error("problem with getting to channel and sending workanswereminder for previous task")
        logger.info(ping3.ping("discord.com"))


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    logger.info(f"We have logged as {client.user}")
    logger.info(ping3.ping("discord.com"))
    if not platoon_timer.is_running():
        platoon_timer.start()
    if not platoon_timer2.is_running():
        platoon_timer2.start()

    gunsmokeanswers = gunsmoke.Gunsmokecheck.checkgunsmoke()
    logger.info(gunsmokeanswers)

previous = {
}
previous_lock = asyncio.Lock()  
cooldown = {} 

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('Helian') :
        await message.reply('At your service', mention_author=True)

    if message.content.startswith('!reminder') :
        print("message was send")
        await message.reply(returnworkanswereminder1())
        try:
            await message.reply(file=picture)
        except Exception as e:
            logger.error("problem with sending picture reminder")



    content = message.content
    channel_id = message.channel.id
    cooldown = {}
    
    if content.startswith('Helian'):
        await message.reply('At your service', mention_author=True)
        return
    if content.startswith('!reminder'):
        await message.reply(returnworkanswereminder1())
        try:
            await message.reply(file=picture)
        except Exception as e:
            logger.error("problem with sending picture reminder")
        return

    async with previous_lock:
        if channel_id not in previous:
            previous[channel_id] = {"content": None, "count": 0, "replied": False}

        if channel_id not in cooldown:
            cooldown[channel_id] = False

        state = previous[channel_id]

        if state["content"] == content:
            state["count"] +=1
            logger.info(f"Message content = previous. Adding count {state["count"]}")
        else:
            state["content"] = content
            state["count"] = 0
            state["replied"] = False
            logger.info("New message detected reseting count")


        if state["count"] >= 3 and not state["replied"] and not cooldown[channel_id]:
            await message.reply(content, mention_author=False)
            state["replied"] = True
            state["count"] = 0
            cooldown[channel_id] = True  #enable blocking
            logger.info(f"Enabling cooldown message was answered")

            asyncio.create_task(reset_cooldown(channel_id))

async def reset_cooldown(channel_id):
    await asyncio.sleep(1)
    cooldown[channel_id] = False
    #cooldown


        

    if  message.attachments:
        for att in message.attachments:
            if (att.content_type.startswith("image") and (str(message.channel) == "sfw-arts" or  str(message.channel)=="nsfw-art")):
                idmsg = message.jump_url
                server = message.guild.id
                try:
                    await att.save("images/savedimage.png")
                except Exception as e:
                    logger.error("problem with saving image")
                    pinglog = ping3.ping("discord.com")
                    logger.info(f"discord ping {pinglog}")

                if CompareImages(idmsg, server) != None:
                    idmsgsent  = CompareImages(idmsg, server)
                    try:
                        await message.reply(f"" + returnanswers() + str(idmsgsent) , mention_author=True)

                    except:
                       await message.channel.send("I saw the image, but it disappeared..... anyway.")
                       logger.warning("Message was already deleted or error occured")            
                else:
                   break
    if (("https://x.com" in message.content) and (str(message.channel) == "sfw-arts" or str(message.channel) == "nsfw-art")):
        urlpattern = r'https?://x\.com[^\s]+'
        urls = re.findall(urlpattern,message.content)
        idmsg = message.jump_url
        server = message.guild.id
        for url in urls:
            if CompareLinks(idmsg, server, url) != None:
                idmsgsent = CompareLinks(idmsg, server, url)
                try:
                    await message.reply(f"" + returnanswers() + str(idmsgsent), mention_author=True)

                except:
                    await message.channel.send("I saw the image, but it disappeared..... anyway.")
                    logger.warning("Message was already deleted or error occured")            
            else: 
                break   



def main():
    client.run(TOKEN, log_handler=handler)
    logger.info("Bot has started")


if __name__ == '__main__':
    main()
    
