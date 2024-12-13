import os 
from dotenv import load_dotenv
import discord 
import cv2
import json

images=[]

if os.path.exists("imagehash.json"):
    with open('imagehash.json','r') as file:
        exsisting_images=json.load(file)
else:
    existing_images= []



def CompareImages():
    newimagehash = CalcImageHash("images/savedimage.png")
    for img in exsisting_images:
        hashscompare = CompareHash(img["hash"],newimagehash)
        if int(hashscompare) <= 5:
            return True

    new_data ={
        "hash": newimagehash
        }
    exsisting_images.append(new_data)
    with open('imagehash.json','w') as file:
        json.dump(exsisting_images, file, indent=4)  
    return False

            




#function calculateHash
def CalcImageHash(FileName):
    image = cv2.imread(FileName)
    resized = cv2.resize(image, (8,8), interpolation = cv2.INTER_AREA)#make image small
    gray_image=cv2.cvtColor(resized,cv2.COLOR_BGR2GRAY)#Make Image Black and white
    avg=gray_image.mean()#average pixel value
    ret, threshold_image = cv2.threshold(gray_image,avg,255,0)#Binarization by threshold
    #calcute hash
    _hash=""
    for x in range(8):
        for y in range(8):
            val=threshold_image[x,y]
            if val==255:
                _hash=_hash+"1"
            else:
                _hash=_hash+"0"
    return _hash


def CompareHash(hash1,hash2):
    l = len(hash1)
    count=0
    for i in range(l):
        if hash1[i] != hash2[i]:
            count=count+1
    return count



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
            if (att.content_type.startswith("image") and str(message.channel) == "sfw-arts"  ):
                await att.save("images/savedimage.png")
                if CompareImages():
                    await message.reply(f'This image was already sent', mention_author=True)
                else:
                   break




def main():
    client.run(TOKEN)


if __name__ == '__main__':
    main()
    
