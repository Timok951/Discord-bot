import os 
from dotenv import load_dotenv
import discord 
import cv2
import json
import numpy as np
import random
from answerslist import answers

content  = []

if os.path.exists("imagehash.json"):
    with open('imagehash.json','r') as file:
        exsisting_images=json.load(file)
else:
    existing_images= []

def returnanswers():
    ran = random.randint(1, 8)
    return answers[ran]


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
    resized = cv2.resize(image, (8,8), interpolation = cv2.INTER_AREA)#make image small
    gray_image=cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)#Make Image Black and white
    dct = cv2.dct(np.float32(gray_image))

    # Преобразуем эти коэффициенты в одномерный вектор
    dct_flattened = dct.flatten()
    
    # Нормализуем коэффициенты (по желанию)
    norm_dct = np.linalg.norm(dct_flattened)
    
    # Преобразуем в вектор с плавающей запятой (не бинарный)
    hash_value = (dct_flattened / norm_dct).tolist()

    return hash_value




def CompareHash(hash1,hash2):
    # Вычисляем косинусную схожесть между двумя хэшами (векторами)
    dot_product = np.dot(hash1, hash2)
    norm_a = np.linalg.norm(hash1)
    norm_b = np.linalg.norm(hash2)
    
    # Избегаем деления на 0
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


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('Helian') :
        await message.reply('at your service', mention_author=True)
    
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
                       await message.channel.send("I saw image but it has dessapeared...anyway")            
                else:
                   break
    
    if len(content) > 3:
       content.pop(0)

    if content.count(message.content) >= 2 :
        await message.reply(message.content)

    if  len(content)==0:
        content.append(message.content)

    if message.content != content[0]:
        content.append(message.content)


def main():
    client.run(TOKEN)


if __name__ == '__main__':
    main()
    
