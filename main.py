import asyncio
from collections import Counter

import requests
from bs4 import BeautifulSoup

# Initialization
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/123.0.0.0 Safari/537.36'}
url_dou = 'https://jobs.dou.ua/vacancies/?category=Python'
words = []
amount_of_ads = []
count_pct = {}


def get_blacklist():
    """
    Reads a list of words that should be excluded from the count.
    """
    with open('blacklist.txt', 'r', encoding="utf-8") as file:
        return [line.strip() for line in file]


async def get_text(ad_link):
    # try:
        r = requests.get(ad_link, headers=headers)
        print(f'Reading {r.url}')
        # print(r.url)
        soup = BeautifulSoup(r.text, "lxml")
        ad_text = soup.find('div', class_="text b-typo vacancy-section").getText()
        ad_words = [w for w in ad_text.split() if w.lower() not in blacklist]
        words.extend(ad_words)
    # except requests.exceptions.ConnectionError:
    #     print(f'Seems like {ad_link} lookup failed..')
    #     amount_of_ads.append(-1)
    #     # continue


async def read_dou():

    r = requests.get(url_dou, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    links_dou = [link.get('href') for link in soup('a', class_="vt")]
    amount_of_ads.append(len(links_dou))

    try:
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(get_text(link)) for link in links_dou]
            # print(f'Reading {r.url}')
    except Exception as err:
        print(err.args)
    # async with asyncio.TaskGroup() as tg:
    #
    #     for link in links_dou:
    #         task = tg.create_task(get_text(link))

    # tasks = [asyncio.create_task(get_text(link)) for link in links_dou]
    # await asyncio.gather(*tasks)

blacklist = get_blacklist()

asyncio.run(read_dou())

# Calculate
cnt = Counter(words)
sum_words = sum(cnt.values())
for k, v in cnt.items():
    pct = v * 100.0 / sum_words
    count_pct[k] = round(pct, 1)

# Sort
sorted_cnt = dict(sorted(count_pct.items(), key=lambda x: x[1]))

# Show
for k, v in sorted_cnt.items():
    print(k, v)
print(f'\nTotal amount of ads: {sum(amount_of_ads)}')
print(f'Total amount of keywords: {sum_words}')

# TODO: add jinny
# TODO get the full list of advertises
# TODO make async
# TODO add readme
# TODO connection error


# requests.exceptions.ConnectionError: ('Connection aborted.', ConnectionResetError(10054, 'Удаленный хост
# принудительно разорвал существующее подключение', None, 10054, None))
