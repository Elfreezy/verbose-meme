import requests
from bs4 import BeautifulSoup
import json
import os


def get_url_image(url):
    r = requests.get(url).text
    soup = BeautifulSoup(r, "lxml")
    url_image = soup.find("td", id="img_basic").find("img").get("src")
    return url_image


def get_file(url_image):
    r = requests.get(url_image, stream=True)
    return r


def get_name(url_image):
    thumb = url_image.split("/")[-1]
    return thumb


def save_image(url):
    name = get_name(get_url_image(url))
    file_obj = get_file(get_url_image(url))

    # Если нет папки images, создаем ее
    pattern = "Images"
    if not os.path.exists(pattern):
        os.makedirs(pattern)
    path = os.path.abspath(pattern)
    way = path + "/" + name

    if not os.path.exists(pattern + "/" + name):
        with open(way, "bw") as f:
            for chunk in file_obj.iter_content(8192):
                f.write(chunk)
        print("NEW " + name)


def main():
    url = "https://www.toramp.com/schedule.php?id=1"
    pass


if __name__ == "__main__":
    main()