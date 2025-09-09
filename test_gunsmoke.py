import datetime
import pytest
from Gunsmoke import Gunsmokecheck
from answerslist import gunsmokereturn

def test_daily_gunsmoke_progress():
    """Проверяем ежедневный прогресс гансмока"""
    today = datetime.datetime.today()
    lastgunsmoke = today - datetime.timedelta(days=1)  # последний гансмок был вчера
    duration = 3  # осталось 3 дня гансмока

    # Создаем состояние JSON
    Gunsmokecheck.writejson(lastgunsmoke, duration)

    # Первый вызов — уменьшает duration на 1
    result1 = Gunsmokecheck.checkgunsmoke()
    assert result1 == gunsmokereturn[0]

    # Считываем JSON и проверяем, что duration уменьшился
    data = Gunsmokecheck.readjson()
    assert data["gunsmokeduration"] == duration - 1

def test_no_double_launch_today():
    """Гансмок не запускается дважды за день"""
    today = datetime.datetime.today()
    lastgunsmoke = today - datetime.timedelta(days=1)
    duration = 2

    # Записываем состояние с lastlaunch = сегодня
    Gunsmokecheck.writejson(lastgunsmoke, duration)
    data = Gunsmokecheck.readjson()
    data["lastlaunch"] = today  # имитируем, что гансмок уже запускался сегодня
    with open("scheldue.json", "w") as f:
        import json, bson
        f.write(json.dumps(data, default=bson.json_util.default))

    result = Gunsmokecheck.checkgunsmoke()
    assert result is None

def test_new_cycle_after_7_days():
    """Проверяем новый цикл гансмока после 7 дней паузы"""
    today = datetime.datetime.today()
    lastgunsmoke = today - datetime.timedelta(days=8)  # прошло >7 дней
    duration = 0  # гансмок закончился

    Gunsmokecheck.writejson(lastgunsmoke, duration)

    result = Gunsmokecheck.checkgunsmoke()
    assert result == gunsmokereturn[0]

    data = Gunsmokecheck.readjson()
    assert data["gunsmokeduration"] == 7
    assert data["lastgunsmoke"].date() == today.date()
