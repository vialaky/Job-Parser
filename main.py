import asyncio
from collections import Counter

import aiohttp
import re
import time
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialization
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/123.0.0.0 Safari/537.36'}
url_dou = 'https://jobs.dou.ua/vacancies/?category=Python'
words = []
total_ads = []
count_pct = {}


def get_blacklist():
    """
    Reads a list of words that should be excluded from the count.
    """
    with open('blacklist.txt', 'r', encoding="utf-8") as file:
        ls = list(set([x.lower() for y in [line.strip().split() for line in file] for x in y]))
        ls.sort()
    return ls


def update_blacklist(ls):
    with open('blacklist.txt', 'w', encoding="utf-8") as file:
        file.writelines(f'{line.lower()}\n' for line in ls if line.isalpha())


async def get_text(dou_session, ad_link):
    r = await dou_session.get(ad_link, headers=headers)
    print(f'Reading {r.url}')
    soup = BeautifulSoup(await r.text(), "lxml")
    ad_text_with_punctuation = soup.find('div', class_="text b-typo vacancy-section").getText()

    ad_text = re.sub(r"[.,:;()/%]", " ", ad_text_with_punctuation)

    # ad_text = ad_text.replace(',', ' ').replace('.', ' ').replace(
    #     '(', ' ').replace(':', ' ').replace(')', ' ').replace(
    #     ';', ' ').replace('●', ' ').replace('*', ' ')

    ad_words = list(set([w.strip() for w in ad_text.split() if w.lower() not in blacklist]))
    ad_words = [w for w in ad_words if w.isascii() and w.isalpha() and len(w) > 1]

    words.extend(ad_words)
    total_ads.append(1)


async def read_dou():
    driver = webdriver.Chrome()
    driver.get(url_dou)
    time.sleep(3)

    for _ in range(3):
        more_button = driver.find_element(By.LINK_TEXT, "Більше вакансій")
        more_button.click()
        time.sleep(2)

    # r = requests.get(url_dou, headers=headers)
    soup = BeautifulSoup(driver.page_source, "lxml")

    links_dou = [link.get('href') for link in soup('a', class_="vt")]

    driver.quit()

    async with aiohttp.ClientSession() as session:

        try:
            async with asyncio.TaskGroup() as tg:
                [tg.create_task(get_text(session, link)) for link in links_dou]
        except Exception as err:
            print(err.args)


start_timestamp = time.time()

blacklist = get_blacklist()

update_blacklist(blacklist)

asyncio.run(read_dou())

# Calculate
N = sum(total_ads)
cnt = Counter(words)
# total_words = sum(cnt.values())
total_words = len(set(words))
for k, v in cnt.items():
    pct = v * 100.0 / N

    count_pct[k] = round(pct)

# Sort
sorted_cnt = dict(sorted(count_pct.items(), key=lambda x: x[1]))

# Show
for k, v in sorted_cnt.items():
    print(k, v)
print(f'\nTotal amount of ads: {sum(total_ads)}')
print(f'Total amount of keywords: {total_words}')

task_time = round(time.time() - start_timestamp, 2)
rps = round(N / task_time, 1)
print(f"| Requests: {N}; Total time: {task_time} s; RPS: {rps}. |\n")

# TODO: add jinny
# TODO get the full list of advertises
# TODO add readme
# TODO connection error


# requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'Удаленный хост
# принудительно разорвал существующее подключение', None, 10054, None))
