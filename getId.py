import requests
from bs4 import BeautifulSoup
import json
import re
# genre
# authors
# actors
# statuses
# channels
flag = 0
try:
    ID = []
    genre = json.load(open("Result/genre.json", encoding='utf-8'))
    authors = json.load(open("Result/authors.json", encoding='utf-8'))
    actors = json.load(open("Result/actors.json", encoding='utf-8'))
    statuses = json.load(open("Result/statuses.json", encoding='utf-8'))
    channels = json.load(open("Result/channels.json", encoding='utf-8'))
    ID.append(genre.get("genre"))
    ID.append(authors.get("authors"))
    ID.append(actors.get("actors"))
    ID.append(statuses.get("statuses"))
    ID.append(channels.get("channels"))
    flag = 1
except:
    ID = [{}, {}, {}, {}, {}]


def get_html(url):
    r = requests.get(url)
    return r.text


# Находим id последнего сериала
def get_link_last_serial(url_last_page):
    soup = BeautifulSoup(get_html(url_last_page), "lxml")
    last_serial_id = soup.find("table", id="schedule-list").find_all("a", class_="title")[-1].get("href").split("=")[1]
    return int(last_serial_id)


# Записывает соответствующие id
# Статус - 3
# Каналы - 4
def write_id(string, arg):
    global ID
    index = len(ID[arg])
    if string not in ID[arg].values():
        dict = {index: string}
        ID[arg].update(dict)
    return 0


# Возвращает разделенные каналы, если их несколько
def get_valid_channel(channels):
    channels = channels.replace(" | ", "|").replace(" / ", "|").replace(", ", "|")
    channels = channels.replace("/", "|").replace(",", "|")
    channels = channels.split("|")
    return channels


# Записывает существующие статусы и каналы
def get_status_channel(url):
    soup = BeautifulSoup(get_html(url), "lxml")
    try:
        info = soup.find("div", class_="content-widget-1").find_all("div", class_="block_list")
    except:
        print("Serial not found: ", end=" ")
        print(url)
        return 0
    try:
        add_info = soup.find("div", class_="content-widget-1").find_all("div", class_="block_bold")
    except:
        return 0

    # if add_info[0].text.lower() == "статус":
    #     statuses = info[0].text
    #     write_id(statuses, 3)
    # elif add_info[1].text.lower() == "статус":
    #     statuses = info[1].text
    #     write_id(statuses, 3)
    # else:
    #     print("Status not found: ", end=" ")
    #     print(url)
    #
    # if add_info[1].text.lower() == "канал":
    #     channels = info[1].text
    #     channels = get_valid_channel(channels)
    #     for channel in channels:
    #         write_id(channel, 4)
    # elif add_info[0].text.lower() == "канал":
    #     channels = info[0].text
    #     channels = get_valid_channel(channels)
    #     for channel in channels:
    #         write_id(channel, 4)
    # else:
    #     print("Channel not found: ", end=" ")
    #     print(url)
    print(url)
    if add_info[0].text.lower() == "статус":
        statuses = info[0].text
        write_id(statuses, 3)
    elif add_info[0].text.lower() == "канал":
        channels = info[0].text
        channels = get_valid_channel(channels)
        for channel in channels:
            write_id(channel, 4)
    if len(add_info) > 1:
        if add_info[1].text.lower() == "канал":
            channels = info[1].text
            channels = get_valid_channel(channels)
            for channel in channels:
                write_id(channel, 4)

    return 0


# Возвращает ссылку с доп. информацией, есть она есть
def get_page_a(url):
    soup = BeautifulSoup(get_html(url), "lxml")
    pattern = "https://www.toramp.com/"
    a = soup.find("div", class_="content-widget-1").find("a").get("href")

    if a.find("www.toramp.com") >= 0:                                                   # Если ссылка уже содержит паттерн
        return a                                                                # выводим ее сразу
    link_info = pattern + a
    return link_info


# Записывает id:
# Авторы - 1
# Актеры - 2
def write_id_info(array, arg):
    global ID
    length = len(array)
    array[0] = array[0][1:]
    array[-1] = array[-1][:-1]
    for i in range(length):
        index = str(len(ID[arg]))
        if array[i] not in ID[arg].values():
            dict = {index: array[i]}
            ID[arg].update(dict)
    return 0


# Возвращает дополнительную информацию, если она есть
# Актеры, авторы
def get_persons(url):
    try:
        link = get_page_a(url)
    except:
        return 0
    soup = BeautifulSoup(get_html(link), 'lxml')
    info = soup.find("div", class_="block_right_index").find_all("div", class_="block_list")
    authores = info[1].text.split("\r\n")
    actors = info[2].text.split("\r\n")
    write_id_info(authores, 1)
    write_id_info(actors, 2)
    return 0


# Возвращает жанры
def get_genre(url):
    soup = BeautifulSoup(get_html(url), "lxml")
    try:
        genre = soup.find("div", class_="second-part-info").find_all("a")
    except:
        return 0

    for i in range(len(genre)):
        write_id(genre[i].text, 0)
    return 0


# Запись в файл в формате json
def w_file(array, name):
    dict = {name : array}
    name += ".json"
    way = "Result/" + name
    with open(way, "w", encoding='utf-8') as file:
        json.dump(dict, file, indent=2, ensure_ascii=False)
        file.close()


def get_id_info(total_pages):
    if flag:
        return ID
    last_serial_id = get_link_last_serial("https://www.toramp.com/schedule.php?page=" + str(total_pages - 1))

    base_url = "https://www.toramp.com/schedule.php?id="
    for id in range(1, last_serial_id):
        url = base_url + str(id)
        get_status_channel(url)
        get_persons(url)
        get_genre(url)

    w_file(ID[0], "genre")
    w_file(ID[1], "authors")
    w_file(ID[2], "actors")
    w_file(ID[3], "statuses")
    w_file(ID[4], "channels")
    return ID


def main():
    num = get_link_last_serial("https://www.toramp.com/schedule.php?page=0")
    return 0


if __name__ == "__main__":
    main()