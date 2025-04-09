import os 
from dotenv import load_dotenv
import discord 
import cv2
import json
import numpy as np
import random
import datetime
import re
import logging
from gunsmoke import checkgunsmoke
from answerslist import answers, work, workreminder
from discord.ext import tasks
from bson import json_util


handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

discord.utils.setup_logging(level=logging.INFO, root=False)

with open('reminderimage.png', 'rb') as f:
    picture = discord.File(f)

content  = []


if os.path.exists("imagehash.json"):
    try:
        with open('imagehash.json','r') as file:
            exsisting_images=json.load(file)
    except Exception as e:
        new_data =[{
            
            "hash": 0,
            "message": 0,
            "server": 0
                }]
        json_object = json.dumps(new_data, indent=4)
        with open('imagehash.json','w') as outfile:
            outfile.write(json_object) 
        with open('imagehash.json','r') as file:
            exsisting_images=json.load(file)


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
    resized = cv2.resize(image, (32,32), interpolation = cv2.INTER_AREA)#make image small
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


datenow = datetime.datetime.now()

#dump
datelastgunsmoke = datetime.datetime(2025, 3, 14)

def writejson(datelastgunsmoke,gunsmokeduration ):
    scheldue={       
    "lastgunsmoke": datelastgunsmoke,
    "gunsmokeduration": gunsmokeduration
}
    jsonObject = json.dumps(scheldue, default=json_util.default)
    with open("scheldue.json", "w") as outfile:
        outfile.write(jsonObject)
            
    with open("scheldue.json", "r") as file:
        data = json.loads(file.read(), object_hook=json_util.object_hook)
    return data

def readjson():
    with open("scheldue.json", "r") as file:
        data = json.loads(file.read(), object_hook=json_util.object_hook)
        return data
#using read to get string

    
if os.path.exists("scheldue.json"):
    date = readjson()
    print(date)
else:
    f = open("scheldue.json", "x")
    date = writejson(datelastgunsmoke, 7)
    print(date)


lastgunsmoke = date["lastgunsmoke"]
gunsmokeduration = date["gunsmokeduration"]

timebetween = datenow - lastgunsmoke


@tasks.loop(time=timereminder)
async def platoon_timer():
    global event_start, event_end
    ran = random.randint(0, 7)
    now = datetime.datetime.now(utc)

    channel = client.get_channel(1321747276129112064)
    print("reminder for current day was send")
    
    await channel.send(returnworkanswereminder1())
    if checkgunsmoke(timebetween, gunsmokeduration,lastgunsmoke,datenow ) != None:
        await channel.send(str(checkgunsmoke(timebetween, gunsmokeduration,lastgunsmoke,datenow)))

    if ran == 0:
        await channel.send(file=picture)
    

@tasks.loop(time=timereminder2)
async def platoon_timer2():
    channel = client.get_channel(1321747276129112064)
    print("reminder for previous task was send")
    await channel.send(returnworkanswerreminder2())       

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')
    if not platoon_timer.is_running():
        platoon_timer.start()
    if not platoon_timer2.is_running():
        platoon_timer2.start()
    
    if checkgunsmoke(timebetween, gunsmokeduration,lastgunsmoke,datenow ) != None:
        channel = client.get_channel(1304149985712930889)
        gunsmokeanswers = checkgunsmoke(timebetween, gunsmokeduration,lastgunsmoke,datenow)
        await channel.send(str(gunsmokeanswers))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('Helian') :
        await message.reply('At your service', mention_author=True)

    if message.content.startswith('!reminder') :
        channel = client.get_channel(1321747276129112064)
        print("message was send")
        await channel.send(returnworkanswereminder1())

    if  message.attachments:
        for att in message.attachments:
            if (att.content_type.startswith("image") and (str(message.channel) == "sfw-arts" or  str(message.channel)=="nsfw-art")):
                idmsg = message.jump_url
                server = message.guild.id
                await att.save("images/savedimage.png")
                if CompareImages(idmsg, server) != None:
                    idmsgsent  = CompareImages(idmsg, server)
                    try:
                        await message.reply(f"" + returnanswers() + str(idmsgsent) , mention_author=True)

                    except:
                       await message.channel.send("I saw the image, but it disappeared..... anyway.")            
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
            else: 
                break   


 


def main():
    client.run(TOKEN, log_handler=handler)


if __name__ == '__main__':
    main()
    
