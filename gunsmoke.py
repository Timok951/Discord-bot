import os
import json
import datetime
from bson import json_util
from answerslist import gunsmokereturn


class Gunsmokecheck:
    # file for checks duration between two gunsmokes

    @staticmethod
    def writejson(datelastgunsmoke, gunsmokeduration, update_lastlaunch=False):
        """Сохраняет JSON с данными Gunsmoke. update_lastlaunch = True только при новом запуске"""
        if update_lastlaunch:
            lastlaunch = datetime.datetime.utcnow()
        else:
            # Если файл уже есть, подгружаем существующее значение lastlaunch
            if os.path.exists("scheldue.json"):
                with open("scheldue.json", "r") as f:
                    try:
                        data = json.loads(f.read(), object_hook=json_util.object_hook)
                        lastlaunch = data.get("lastlaunch", datetime.datetime.utcnow())
                    except:
                        lastlaunch = datetime.datetime.utcnow()
            else:
                lastlaunch = datetime.datetime.utcnow()

        scheldue = {
            "lastgunsmoke": datelastgunsmoke,
            "gunsmokeduration": int(gunsmokeduration),
            "lastlaunch": lastlaunch
        }

        with open("scheldue.json", "w") as outfile:
            json.dump(scheldue, outfile, default=json_util.default)

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
            except Exception:
                year = int(input('Enter a year'))
                month = int(input('Enter a month'))
                day = int(input('Enter a day'))
                date1 = datetime.datetime(year, month, day)
                gusmokeduration = input()
                return Gunsmokecheck.writejson(date1, gusmokeduration)
        else:
            year = int(input('Enter a year'))
            month = int(input('Enter a month'))
            day = int(input('Enter a day'))
            date1 = datetime.datetime(year, month, day)
            print("input gunsmoke duration")
            gusmokeduration = input()
            return Gunsmokecheck.writejson(date1, gusmokeduration)

    @staticmethod
    def checkgunsmoke():
        datenow = datetime.datetime.now()
        date = Gunsmokecheck.readjson()

        lastgunsmoke = date["lastgunsmoke"]
        gunsmokeduration = int(date["gunsmokeduration"])
        lastlaunch = date["lastlaunch"]


        print(f"LastGunsmoke day: {lastgunsmoke}")
        print(f"Gunsmoke duration, if 0 gunsmoke end {gunsmokeduration}")
        days_since_lastgunsmoke = (datenow.date() - lastgunsmoke.date()).days
        days_since_lastlaunch = (datenow.date() - lastlaunch.date()).days
        print(f"Days since last Gunsmoke: {days_since_lastgunsmoke}")
        print(f"Days since last check launch: {days_since_lastlaunch}")



@staticmethod
def checkgunsmoke():
    datenow = datetime.datetime.now()
    date = Gunsmokecheck.readjson()

    lastgunsmoke = date["lastgunsmoke"]
    gunsmokeduration = int(date["gunsmokeduration"])
    lastlaunch = date["lastlaunch"]

    days_since_lastgunsmoke = (datenow.date() - lastgunsmoke.date()).days
    days_since_lastlaunch = (datenow.date() - lastlaunch.date()).days

    print(f"LastGunsmoke day: {lastgunsmoke}")
    print(f"Gunsmoke duration: {gunsmokeduration}")
    print(f"Days since last Gunsmoke: {days_since_lastgunsmoke}")
    print(f"Days since last check launch: {days_since_lastlaunch}")

    if gunsmokeduration == 0 and days_since_lastgunsmoke >= 7:
        print("Gunsmoke duration — new cycle")
        gunsmokeduration = 7
        lastgunsmoke = datenow
        Gunsmokecheck.writejson(lastgunsmoke, gunsmokeduration, update_lastlaunch=True)
        return str(gunsmokereturn[0])

    if gunsmokeduration > 0:
        print("Gunsmoke has started")
        gunsmokeduration -= 1
        Gunsmokecheck.writejson(lastgunsmoke, gunsmokeduration, update_lastlaunch=False)
        return str(gunsmokereturn[0])

    if lastlaunch.date() == datenow.date():
        print("Gunsmoke checking was already launched today")
        return None

    print("No gunsmoke for today")
    Gunsmokecheck.writejson(lastgunsmoke, gunsmokeduration, update_lastlaunch=False)
    return None

