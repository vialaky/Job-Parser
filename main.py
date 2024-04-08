# import lxml
import requests
from bs4 import BeautifulSoup


url = 'https://jobs.dou.ua/vacancies/?category=Python'

header = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0',}
page = requests.get(url, headers=header)

soup = BeautifulSoup(page.text, "lxml")


print(soup)