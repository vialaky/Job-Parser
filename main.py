import re
import sys

import requests
from bs4 import BeautifulSoup

url = 'https://jobs.dou.ua/vacancies/?category=Python'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/123.0.0.0 Safari/537.36'}

r = requests.get(url, headers=headers)

soup = BeautifulSoup(r.text, "lxml")
ad_links = [link.get('href') for link in soup('a', class_="vt")]

# for ad in ad_links:
#     print(ad)
#

link = ad_links[0]
r = requests.get(link, headers=headers)
# print(r.url)
soup = BeautifulSoup(r.text, "lxml")

ad_text = soup.find('div', class_="text b-typo vacancy-section").getText()


words = set([w for w in ad_text.split()])
print(words)
print(len(words))



# mystr = re.sub(r"[<>/]", "", ad)
#

print(f'Total amount of ads: {len(ad_links)}')
