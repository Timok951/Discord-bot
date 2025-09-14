import os
import json
import datetime
import json
from bson import json_util
from answerslist import gunsmokereturn


class Gunsmokecheck:
    #file for checks duration between two gunsmokes
    #dump

    @staticmethod
    def writejson(datelastgunsmoke,gunsmokeduration ):
        
        lastlaunch = datetime.datetime.today()
        scheldue={       
        "lastgunsmoke": datelastgunsmoke,
        "gunsmokeduration": int(gunsmokeduration),
        "lastlaunch": lastlaunch
        
    }
        jsonObject = json.dumps(scheldue, default=json_util.default)
        with open("scheldue.json", "w") as outfile:
            outfile.write(jsonObject)
                
        with open("scheldue.json", "r") as file:
            data = json.loads(file.read(), object_hook=json_util.object_hook)
        return data

    @staticmethod
    def readjson():
        if os.path.exists("scheldue.json"):
            try:
                with open("scheldue.json", "r") as file:
                    data = json.loads(file.read(), object_hook=json_util.object_hook)
                return data
            except Exception as e:
                year = int(input('Enter a year'))
                month = int(input('Enter a month'))
                day = int(input('Enter a day'))
                date1 = datetime.datetime(year, month, day)
                gusmokeduration = input()
                return Gunsmokecheck.writejson(date1,gusmokeduration)
                
        else:
                year = int(input('Enter a year'))
                month = int(input('Enter a month'))
                day = int(input('Enter a day'))
                date1 = datetime.datetime(year, month, day)
                print("input gunsmoke duration")
                gusmokeduration = input()
                return Gunsmokecheck.writejson(date1,gusmokeduration)
                                 
    @staticmethod
    def checkgunsmoke(): 
        
        datenow = datetime.datetime.now()

        date = Gunsmokecheck.readjson()
       
        lastgunsmoke = date["lastgunsmoke"]
        gunsmokeduration = int(date["gunsmokeduration"])
        lastlaunch = date["lastlaunch"]
        
        daysincelastlaunch = (datenow.date() - lastgunsmoke.date()).days
        
        print(f"LastGunsmoke day: {lastgunsmoke}")
        print(f"Gunsmoke duration, if 0 gunsmoke end {gunsmokeduration}")
        print(f"Time between last gunsmoke and now, if 7, Gunsmoke will start {daysincelastlaunch}")
        
        if lastlaunch == datenow:
            print("today date = last date")
        else:
            print(f"lastlaunch {lastlaunch}")
        
        #if gunsmoke ended and has 7 days lasted     
        if gunsmokeduration > 0:
            #Gunsmoke continue
            print("Gunsmoke has started")
            gunsmokeduration -=1
            Gunsmokecheck.writejson(lastgunsmoke, gunsmokeduration)
            return str (gunsmokereturn[0])
        
        #gunsmoke ended     
        if gunsmokeduration == 0 and daysincelastlaunch >= 7:
            print("Gunsmoke duration")
            if lastlaunch.date() != datenow.date():
                gunsmokeduration = 7
                lastgunsmoke = datenow
                Gunsmokecheck.writejson(lastgunsmoke, gunsmokeduration)
                return str(gunsmokereturn[0])
        return None
        
        


