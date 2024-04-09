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

ad = str(soup('div', class_="text b-typo vacancy-section"))

print(ad)




# for link in soup.find_all('a', class_="vt"):
#     print(link.get('href'))
# #
#
# ads = [v for v in soup.find_all('a', class_='vt')]
# for link in ads:
#     print(link.get('href'))
#     #
# ad_page = requests.get(link.get('href'), headers=header)
# soup = BeautifulSoup(page.text, "lxml")
#
# ad = soup.find('div', class_="text b-typo vacancy-section")
# # ad = soup.find(class_="l-vacancy")
# print(ad)
#
# sys.exit()
# text = soup

# print(soup.get_text())

# for vac in vacancies:
#     print(vac)

print(f'Total amount of ads: {len(ad_links)}')
