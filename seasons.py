import requests
from bs4 import BeautifulSoup


def get_html(url):
    r = requests.get(url)
    return r.text


# Возвращает названия сериалов
def get_seasons(url):
    soup = BeautifulSoup(get_html(url), 'lxml')
    seasons = soup.find_all("h2")
    result = []

    length = len(seasons)
    for i in range(length - 1, - 1, -1):
        dict = {
            "title": seasons[i].text.strip(),
        }
        result.append(dict)
    return result


def main():
    # result = [[], [], []]
    # result[1].append(get_seasons("https://www.toramp.com/schedule.php?id=6"))
    # print(result)
    pass


if __name__ == "__main__":
    main()