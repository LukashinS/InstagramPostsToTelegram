from telethon import TelegramClient, errors
import os, json
import asyncio
import time
import datetime

api_id = int("api_id")
api_hash = 'api_hash'

client = TelegramClient('session_name', api_id, api_hash)
chat_name = "chat name"

dir_name = 'folder path'
dir_folders = os.listdir(dir_name)

full_paths = list(map(lambda name: os.path.join(dir_name, name), dir_folders))

dirs = []
files = []
jpg = "jpg"
mp4 = "mp4"
txt = "txt"

# Блок для создания файла с данными result.json
result = {}
for index, folder in enumerate(full_paths):
    result[index + 1] = {jpg: [], mp4: [], txt: ""}
    if os.path.isdir(folder):
        dir_files = os.listdir(folder)
        for file in dir_files:
            if f".{jpg}" in file:
                result[index + 1][jpg].append(os.path.join(folder, file))
            if f".{mp4}" in file:
                result[index + 1][mp4].append(os.path.join(folder, file))
            if f".{txt}" in file:
                with open(os.path.join(folder, file), encoding="utf-8") as f:
                    read_txt = f.read()
                result[index + 1][txt] = read_txt
result_json = json.dumps(result, ensure_ascii=False)
with open('result.json', 'w', encoding="utf-8") as f:
    f.write(result_json)

result = json.load(open(os.path.join('result.json'), 'r', encoding='utf-8'))
client.start()


def get_time(delay):
    time_now = datetime.datetime.now()
    time_delta = time_now + datetime.timedelta(seconds=delay)
    fmt = "%H:%M:%S"
    print(f"{time_now.strftime(fmt)} - Have to sleep {delay} seconds. End to - {time_delta.strftime(fmt)}")


async def flood_waiter(action, result):
    try:
        await action()
    except errors.FloodWaitError as e:
        result_json = json.dumps(result, ensure_ascii=False)
        with open('result.json', 'w', encoding="utf-8") as f:
            f.write(result_json)
        get_time(e.seconds)
        time.sleep(e.seconds)
        await action()


async def main():
    async with client:
        await client.get_dialogs()
        for key, value in result.items():
            if result[key]:
                await flood_waiter(lambda: client.send_message(chat_name, f"#{str(key)}"), result)
                mp4_lst = value.get(mp4)
                jpg_lst = value.get(jpg)
                txt_value = value.get(txt)
                for elem in mp4_lst:
                    file_stats = os.stat(elem)
                    if file_stats.st_size / (1024 * 1024) > 50:
                        await flood_waiter(
                            lambda: client.send_message(chat_name, f"Большой видео файл - не буду грузить\n{elem}"),
                            result)
                    else:
                        await flood_waiter(lambda: client.send_file(chat_name, elem), result)
                    result[key][mp4] = []
                for elem in jpg_lst:
                    await flood_waiter(lambda: client.send_file(chat_name, elem), result)
                    result[key][jpg] = []
                if txt_value:
                    await flood_waiter(lambda: client.send_message(chat_name, txt_value), result)
                    result[key][txt] = ""


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
