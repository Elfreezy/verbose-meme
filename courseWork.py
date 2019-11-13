import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
from multiprocessing import Pool

from getId import *
from seasons import *
from episodes import *
from images import *
#   06.11.19
#


# Возвращает кол-во страниц
def get_total_pages(html):
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find("div", class_="schedule-ddd").find_all("a")[-1].text
    return int(pages)


# Возвращает ссылку каждого сериала
def get_page_link(html):
    soup = BeautifulSoup(html, 'lxml')
    series = soup.find("table", id="schedule-list").find_all("a", class_="title")
    links = []
    for serial in series:
        a = serial.get("href")
        link = "https://www.toramp.com/" + a
        links.append(link)
    return links


# Возвращает строку полного описания
def get_description(url):
    link = get_page_a(url)

    soup = BeautifulSoup(get_html(link), "lxml")
    result = ''
    description = soup.find_all("p", class_="body")
    for index in range(len(description) - 1):
        result += description[index].text + " "
    return result


# Записывает id:
# Авторы - 1
# Актеры - 2
def write_info_id(array, arg):
    length = len(array)
    array[0] = array[0][1:]
    array[-1] = array[-1][:-1]
    id = []
    for i in range(length):
        if array[i] in ID[arg].values():
            for key, value in ID[arg].items():
                if value == array[i]:
                    id.append(key)
                    break
    return id


# Возвращает дополнительную информацию, если она есть
# Актеры, авторы
def get_more_info(url):
    link = get_page_a(url)
    soup = BeautifulSoup(get_html(link), 'lxml')
    info = soup.find("div", class_="block_right_index").find_all("div", class_="block_list")

    authores = info[1].text.split("\r\n")
    actors = info[2].text.split("\r\n")

    idAuthores = write_info_id(authores, 1)
    idActors = write_info_id(actors, 2)

    data = {
        "author_id": idAuthores,
        "role_id": idActors,
    }

    return data


# Записывает соответствующие id
# Жанры - 0
# Статус - 3
# Каналы - 4
def get_status_id(string, arg):
    global ID
    if string in ID[arg].values():
        for key, value in ID[arg].items():
            if value == string:
                id = key
                break
    return id


# Возвращает информацию со страницы
def get_page_data(url, id):
    soup = BeautifulSoup(get_html(url), 'lxml')
    try:
        name = soup.find("h1", class_="title-basic").find("span", itemprop="name").text.strip()
    except:
        name = ''
    try:
        original = soup.find("h1", class_="title-basic").find("span", itemprop="alternativeHeadline").text.strip()
    except:
        original = ''
    try:
        timing = soup.find("div", class_="second-part-info").text.strip().split(" - ")
        timing = timing[1]
    except:
        timing = ''
    try:
        shortDescription = soup.find("p", class_="summary").text.strip()
    except:
        shortDescription = ''
    try:
        description = get_description(url)
    except:
        description = ''

    #Error
    # try:
    #     info = soup.find("div", class_="content-widget-1").find_all("div", class_="block_list")
    #     statuses = info[0].text
    #     status_id = get_status_id(statuses, 3)
    # except:
    #     status_id = ''
    # try:
    #     info = soup.find("div", class_="content-widget-1").find_all("div", class_="block_list")
    #     statuses = info[1].text
    #     channel_id = get_status_id(statuses, 4)
    # except:
    #     channel_id = ''

    try:
        info = soup.find("div", class_="content-widget-1").find_all("div", class_="block_list")
        try:
            add_info = soup.find("div", class_="content-widget-1").find_all("div", class_="block_bold")
        except:
            add_info = ''
        channel_id = []
        if add_info[0].text.lower() == "статус":
            statuses = info[0].text
            status_id = get_status_id(statuses, 3)
        elif add_info[0].text.lower() == "канал":
            channels = info[0].text
            channels = get_valid_channel(channels)
            for channel in channels:
                channel_id.append(get_status_id(channel, 4))
            status_id = ''
        if len(add_info) > 1:
            if add_info[1].text.lower() == "канал":
                channels = info[1].text
                channels = get_valid_channel(channels)
                for channel in channels:
                    channel_id.append(get_status_id(channel, 4))
    except:
        info = ''

    try:
        genres = soup.find("div", class_="second-part-info").find_all("a")
        genre_id = []
        for genre in genres:
            genre_id.append(get_status_id(genre.text, 0))
    except:
        genre_id = ''
    try:
        more_info = get_more_info(url)
    except:
        more_info = ''

    try:
        thumb_url = get_url_image(url)
    except:
        thumb_url = ''
    try:
        thumb = get_name(thumb_url)
    except:
        thumb = ''

    data = {
        # "id": id,
        "url": url,
        "name": name,
        "original": original,
        "timing": timing,
        "shortDescription": shortDescription,
        "description": description,
        "thumb_url": thumb_url,
        "thumb": thumb,
    }
    # data = {}
    if genre_id:
        data.update({"genre_id": genre_id})
    if more_info:
        data.update(more_info)
    if info:
        if status_id:
            data.update({"status_id": status_id})
        if channel_id:
            data.update({"channel_id": channel_id})
    return data


# Создание мультипроцесса
def make_multi_proc(url):
    result = [[], [], []]
    html = get_html(url)
    links = get_page_link(html)
    for link in links:
        # print(link)
        page_id = int(link.split("=")[1])
        result[0].append(get_page_data(link, page_id))
        result[1].append(get_seasons(link))
        result[2].append(get_episodes(link))
        save_image(link)

    return result


# Запись в файл в формате json
def write_file(array, name):
    name += ".json"
    way = "Result/" + name
    with open(way, "a", encoding='utf-8') as file:
        json.dump(array, file, indent=2, ensure_ascii=False)
        file.close()


def main():
    start = datetime.now()
    global ID

    url = "https://www.toramp.com/schedule.php"
    base_url = "https://www.toramp.com/schedule.php?page="
    all_pages = []
    total_pages = get_total_pages(get_html(url))                     # Самая последняя страница соотв. total pages
    for i in range(total_pages):                                              # Кол-во страниц для парсинга
        all_pages.append(str(base_url + str(i)))

    get_id_info(total_pages)                                              # Создает ID файл для 5 страниц. Кол-во должно
    for id in ID:                                                   # соответствовать макс. кол-ву страниц для парсинга
        print(id)
    with Pool(25) as p:
        pages = p.map(make_multi_proc, all_pages)

    serials_array = []
    episodes_array = []

    # Индексация
    serial_id = 1
    season_id = 1
    episode_id = 1
    for page in pages:
        info = page[0]
        serials = page[1]
        episodes = page[2]
        for index_serial in range(len(serials)):
            info[index_serial].update({"id": serial_id})
            for index_season in range(len(serials[index_serial])):
                serials[index_serial][index_season].update({"id": season_id})
                serials[index_serial][index_season].update({"serial_id": serial_id})
                serials_array.append(serials[index_serial][index_season])                                       # Убираем вложенность

                for index_episode in range(len(episodes[index_serial][index_season])):
                    episodes[index_serial][index_season][index_episode].update({"id": episode_id})
                    episodes[index_serial][index_season][index_episode].update({"season_id": season_id})
                    episodes_array.append(episodes[index_serial][index_season][index_episode])                  # Убираем вложенность
                    episode_id += 1
                season_id += 1

            serial_id += 1
        write_file(info, "serials")

    write_file(serials_array, "seasons")
    write_file(episodes_array, "episodes")
    end = datetime.now()
    print(str(end - start))


if __name__ == "__main__":
    main()