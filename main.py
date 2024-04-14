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
    with open('blacklist.txt', 'r') as file:
        return [line.strip() for line in file]


def reading_dou():
    words_dou = []

    r = requests.get(url_dou, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")

    links_dou = [link.get('href') for link in soup('a', class_="vt")]
    amount_of_ads.append(len(links_dou))

    for link in links_dou:
        r = requests.get(link, headers=headers)
        print(f'Reading {r.url}')
        soup = BeautifulSoup(r.text, "lxml")
        ad_text = soup.find('div', class_="text b-typo vacancy-section").getText()
        ad_words = [w for w in ad_text.split() if w.lower() not in blacklist]
        words_dou.extend(ad_words)

    return words_dou


blacklist = get_blacklist()

words.extend(reading_dou())

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
