import requests
from bs4 import BeautifulSoup
import json


# Возвращает информацию о сезонах сериала
def get_episodes(url):
    result = []
    months = {
        "января": "01", "февраля": "02", "марта": "03", "апреля": "04", "мая": "05", "июня": "06",
        "июля": "07", "августа": "08", "сентября": "09", "октября": "10", "ноября": "11", "декабря": "12",
    }
    r = requests.get(url).text
    soup = BeautifulSoup(r, "lxml")
    seasons = soup.find_all("table", id="num-season")
    # Нужен цикл по сезонам
    length = len(seasons)
    for index in range(length - 1, -1, -1):
        episodes = seasons[index].find_all("tr")
        season = []
        # Нужен цикл по эпизодам
        num = len(episodes)
        for jndex in range(num):
            info = episodes[jndex].find_all("td")

            try:
                name = info[1].find("b").text.strip()
            except:
                name = ''
            try:
                original = info[1].find("span").text.strip()
            except:
                original = ''
            try:
                data = info[3].text.split()
                data[1] = months.get(data[1])
                data = data[0] + "." + data[1] + "." + data[2]
            except:
                data = ''

            number = jndex + 1
            dict = {
                "number": number,
                "name": name,
                "original": original,
                "data": data,
            }
            season.append(dict)
        result.append(season)

    return result


def main():
    # url = "https://www.toramp.com/schedule.php?id=1"
    # ss = get_episodes(url)
    # for s in ss:
    #     print(s)
    pass


if __name__ == "__main__":
    main()