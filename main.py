import asyncio
from collections import Counter

import aiohttp
import re
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

# Initialization
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/123.0.0.0 Safari/537.36'}
url_dou = 'https://jobs.dou.ua/vacancies/?category=Python'
url_djinni = 'https://djinni.co/jobs/?primary_keyword=Python&exp_level=no_exp&exp_level=1y&exp_level=2y'
words = []
total_ads = []
count_pct = {}


def get_my_skills():
    """
    Reads a list of words from my skills list that should be excluded from the count.
    """
    print('Reading My skills')
    with open('my_skills.txt', 'r', encoding="utf-8") as file:
        skills = list(set([x.lower() for y in [line.strip().split() for line in file] for x in y]))
    return skills


def get_blacklist():
    """
    Reads a list of words that should be excluded from the count.
    """
    print('Reading Blacklist')
    with open('blacklist.txt', 'r', encoding="utf-8") as file:
        ls = list(set([x.lower() for y in [line.strip().split() for line in file] for x in y]))
        ls.sort()
    return ls


def update_blacklist(ls):
    with open('blacklist.txt', 'w', encoding="utf-8") as file:
        file.writelines(f'{line.lower()}\n' for line in ls if line.isalpha())


async def get_text_dou(dou_session, ad_link):
    r = await dou_session.get(ad_link, headers=headers)
    print(f'Reading {r.url}')
    soup = BeautifulSoup(await r.text(), "lxml")

    ad_text_with_punctuation = soup.find('div', class_="b-typo vacancy-section").prettify()

    ad_text = re.sub(r"[.,:;()/%]", " ", ad_text_with_punctuation)

    ad_words_dou = list(set([w.strip() for w in ad_text.split()
                             if w.lower() not in blacklist
                             and w.lower() not in my_skills]))
    ad_words_dou = [w.lower() for w in ad_words_dou if w.isascii() and w.isalpha() and len(w) > 1]

    words.extend(ad_words_dou)
    total_ads.append(1)


async def get_text_djinni(djinni_session, ad_link):
    r = await djinni_session.get(ad_link, headers=headers)
    print(f'Reading {r.url}')
    soup = BeautifulSoup(await r.text(), "lxml")

    ad_text_with_punctuation = soup.find('div', class_="mb-4 job-post__description").prettify()

    ad_text = re.sub(r"[.,:;()/%]", " ", ad_text_with_punctuation)

    ad_words_djinni = list(set([w.strip() for w in ad_text.split()
                                if w.lower() not in blacklist
                                and w.lower() not in my_skills]))
    ad_words_djinni = [w.lower() for w in ad_words_djinni if w.isascii() and w.isalpha() and len(w) > 1]

    words.extend(ad_words_djinni)
    total_ads.append(1)


async def read_dou():
    print('Start reading DOU')
    print(url_dou)

    driver = webdriver.Firefox()
    print(url_dou)
    driver.get(url_dou)
    time.sleep(3)

    for _ in range(3):
        more_button = driver.find_element(By.LINK_TEXT, "Більше вакансій")
        more_button.click()
        time.sleep(2)

    soup = BeautifulSoup(driver.page_source, "lxml")
    target = soup('a', class_="vt")

    links_dou = [link.get('href') for link in target if
                 "Senior" not in link.getText() and
                 "Lead" not in link.getText() and
                 "Mentor" not in link.getText() and
                 "QA" not in link.getText()]

    driver.quit()

    async with aiohttp.ClientSession() as session_dou:

        try:
            async with asyncio.TaskGroup() as tg:
                [tg.create_task(get_text_dou(session_dou, link)) for link in links_dou]
        except Exception as err:
            print(err.args)


async def read_djinni():
    print('Start reading DJINNI')

    page = requests.get(url_djinni, headers=headers)
    soup = BeautifulSoup(page.text, "lxml")

    target = soup('a', class_="job-item__title-link")

    links_djinni = ['https://djinni.co' + link.get('href') for link in target if
                    "Senior" not in link.getText() and
                    "Lead" not in link.getText() and
                    "Mentor" not in link.getText() and
                    "QA" not in link.getText()]

    async with aiohttp.ClientSession() as session_djinni:

        try:
            async with asyncio.TaskGroup() as tg:
                [tg.create_task(get_text_djinni(session_djinni, link)) for link in links_djinni]
        except Exception as err:
            print(err.args)


async def main():
    async with asyncio.TaskGroup() as tg:
        tg.create_task(read_djinni())
        tg.create_task(read_dou())


start_timestamp = time.time()

my_skills = get_my_skills()
blacklist = get_blacklist()
update_blacklist(blacklist)
# asyncio.run(main())
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
    if v >= 10:
        print(k, v)
print(f'\nTotal amount of ads: {sum(total_ads)}')
print(f'Total amount of keywords: {total_words}')

task_time = round(time.time() - start_timestamp, 2)
rps = round(N / task_time, 1)
print(f"| Requests: {N}; Total time: {task_time} s; RPS: {rps}. |\n")

# TODO add readme
# TODO connection error


# requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'Удаленный хост
# принудительно разорвал существующее подключение', None, 10054, None))
