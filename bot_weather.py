# war bot

import asyncio
import logging
import sys
import requests
from datetime import datetime, timedelta
from config import token_weather_bot, open_weather_token
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.utils.markdown import hbold


dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f"Привет, {hbold(message.from_user.full_name)}! Напиши мне название города и я пришлю тебе сводку погоды!")


@dp.message()
async def process_language(message: Message) -> None:

    try:
        txt = message.text.casefold().split(" ")
        word1 = txt[0]
        word2 = txt[1]
        if word1 == "сейчас":
            city = word2
            r = requests.get(
                    f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={open_weather_token}&units=metric&lang=ru"
                )
            data = r.json()
            city = data["name"]
            cur_weather = data["main"]["temp"]
            humidity = data["main"]["humidity"]
            pressure = data["main"]["pressure"]
            wind = data["wind"]["speed"]
            sunrise_timestamp = datetime.fromtimestamp(data["sys"]["sunrise"])
            sunset_timestamp = datetime.fromtimestamp(data["sys"]["sunset"])
            length_of_the_day = datetime.fromtimestamp(data["sys"]["sunset"]) - datetime.fromtimestamp(
                data["sys"]["sunrise"])

            await message.reply(f"***{datetime.now().strftime('%Y-%m-%d %H:%M')}***\n"
                                f"Погода в городе: {city}\nТемпература: {cur_weather}C \n"
                                f"Влажность: {humidity}%\nДавление: {pressure} мм.рт.ст\nВетер: {wind} м/с\n"
                                f"Восход солнца: {sunrise_timestamp}\n"
                                f"Закат солнца: {sunset_timestamp}\n"
                                f"Продолжительность дня: {length_of_the_day}\n"
                                f"Хорошего дня!"
                                )
        elif word1 == "прогноз":
            city = word2
            r = requests.get(
                f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={open_weather_token}&units=metric&lang=ru"

            )
            data = r.json()
            winddirections = (
                "северный", "северо-восточный", "восточный", "юго-восточный", "южный", "юго-западный", "западный",
                "северо-западный")
            answer = f"Прогноз погоды для города {data['city']['name']}\n"
            count = 1
            for item in data['list']:
                data_time = item['dt_txt']
                timezone = data['city']['timezone']
                time_str = data_time
                time_format = "%Y-%m-%d %H:%M:%S"
                time = datetime.strptime(time_str, time_format)
                timezone_offset_seconds = timezone
                time_with_timezone = time + timedelta(seconds=timezone_offset_seconds)
                time_with_timezone_str = time_with_timezone.strftime(time_format)

                temp = item['main']['temp']
                weather_d = item['weather'][0]['description']
                wind_speed = item['wind']['speed']
                wind_deg = item['wind']['deg']
                direction = int((wind_deg + 22.5) // 45 % 8)
                pop = item['pop'] * 100
                answer += f"{hbold(time_with_timezone_str)}, Температура воздуха {temp}C, {weather_d}, Ветер {wind_speed}м/с {winddirections[direction]} , Вероятность осадков {pop}% \n"
                count += 1
                if count == 21:
                    break
            await message.reply(answer)
        else:
            await message.send_copy(chat_id=message.chat.id)
    except IndexError:
        await message.send_copy(chat_id=message.chat.id)

        
async def main() -> None:
    bot = Bot(token_weather_bot, parse_mode=ParseMode.HTML)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
    