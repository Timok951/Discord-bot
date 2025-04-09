import os
import json
import datetime
from bson import json_util

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

gunsmokereturn = "Gunsmoke time! 🚨🚬 \nDo not forget go on boss-battle"

def checkgunsmoke(timebetween, gunsmokeduration,lastgunsmoke,datenow ):
    print(f"LastGunsmoke day: {lastgunsmoke}")
    print(f"Gunsmoke duration if gunsmoke has not started will be seven {gunsmokeduration}")
    print(f"Time between last gunsmoke and now, if 30, Gunsmoke will start-{timebetween}")
    if timebetween >= datetime.timedelta(days=30) and gunsmokeduration >= 7:
        print("Gunsmoke has started")
        gunsmokeduration = gunsmokeduration -1
        writejson(lastgunsmoke, gunsmokeduration)
        return(str(gunsmokereturn))
    elif timebetween >= datetime.timedelta(days=30) and gunsmokeduration > 0:
        print("Gunsmoke is continued")
        gunsmokeduration = gunsmokeduration -1
        writejson(lastgunsmoke, gunsmokeduration)
        return(str(gunsmokereturn))
    elif timebetween >= datetime.timedelta(days=30) and gunsmokeduration == 0:
        print("Gunsmoke has ended")
        gunsmokeduration = 7
        writejson(datenow, gunsmokeduration)
        return None
    
    else:
        return None



