#!../venv python
# coding: utf-8

# ## Import the library

from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import xml.etree.ElementTree as ET
import requests
import sqlite3


# Method for parse page
class spider:
  def __init__(self, _dateRangeMin, _dateRangeMax, _cursor):
    # ## Build the headers
    # Ignore SSL certificate errors
    self.ctx = ssl.create_default_context()
    self.ctx.check_hostname = False
    self.ctx.verify_mode = ssl.CERT_NONE
    self.dateRangeMin = _dateRangeMin
    self.dateRangeMax = _dateRangeMax
    self.cursor = _cursor

  def get_CN_data(self):
    # ## Open the file
    self.handle = open("./src/data/dataCN.txt", "w")
    origin_url = "https://newshub.sustech.edu.cn/zh/?cat=3&paged="
    for i in range(1, 20):
      result, data = self.__parse_page_CN(origin_url + str(i))
      if result is False:
          print("Finish")
          break
      self.cursor.execute(
        "INSERT OR IGNORE INTO Article (title, year, month, day, abstract, pic_url, url, isChinese) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    self.handle.close()


  def get_EN_data(self):
    self.handle = open("./src/data/dataEN.txt", "w")
    self.headers = {
      'path': '/?tag=arts-culture&tagall=1&paged=4',
      "authority": 'newshub.sustech.edu.cn,',
      "accept": 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
      "accept-encoding": 'gzip, deflate, br',
      "accept-language": 'zh-CN,zh;q=0.9,en;q=0.8',
      "cache-control": 'max-age=0',
      "upgrade-insecure-requests": '1',
      "user-agent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    }
    origin_url = "https://newshub.sustech.edu.cn//?tag=arts-culture&tagall=1&paged="
    for i in range(1, 20):
      print(origin_url + str(i))
      result, date = self.__parse_page_EN(origin_url + str(i))
      if result is False:
        print("Finish")
        break
      self.cursor.execute(
        "INSERT OR IGNORE INTO Article (title, year, month, day, abstract, pic_url, url, isChinese) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", data)
    self.handle.close()

  def __parse_page_CN(self, url):
    html = urlopen(url, context=self.ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    for news in soup.select(".m-newslist > ul > li"):
      date = news.find(class_="u-date").get_text().strip().replace("\n", "/")
      temp = date.split("/")
      date_num =int(temp[0] + temp[1])
      print(date_num)
      if date_num < self.dateRangeMin:
        return False, None
      if date_num > self.dateRangeMax:
        continue
      s = str()
      title = news.find(class_="title f-clamp").get_text().strip()
      pic_url = news.find( class_="u-pic").attrs['style'].split("(")[1].split(")")[0]
      abstract = news.find(class_="details f-clamp4").get_text().replace("\n", "")
      url = news.a.attrs.get("href")

      s += "Date: " + date + "\r\n"
      s += "Title: " + title  + "\r\n"
      s += "PicURL: " + pic_url + "\r\n"
      s += "Abstract: "+ abstract + "\r\n"
      s += "URL: " + url + "\r\n"
      print(s)
      self.handle.write(s.replace("\u2022", "").replace("\xa0", "").replace("\u200b", ""))
    return True, (title, 2019, int(temp[0]), int(temp[1]), abstract, pic_url, url, 1)
                # (title, year, month, day, abstract, pic_url, url, isChinese)
  
          
  def __parse_page_EN(self, url):
    def get_abstract(url_article):
      html = urlopen(url_article).read()
      soup = BeautifulSoup(html, "html.parser")
      page = soup.find(class_="u-content col-sm-8 col-xs-12")
      abstract = page.find("p").get_text().split(".")[0] + "."
      return abstract
    print("parsing: " + repr(url))
    html = requests.get(url, headers=self.headers).text
    soup = BeautifulSoup(html, "html.parser")

    aim = soup.select("body")[0]
    for news in aim.find_all(class_="u-view"):
      date = news.find(class_="date").get_text().strip()
      dates = date.split("/")
      date_num = int(dates[0] + dates[1])
      if date_num > self.dateRangeMax:
        continue
      if date_num < self.dateRangeMin:
        return False, None
      url_article = news.find("a").attrs['href']
      title = news.find("img").attrs["alt"]
      abstract = get_abstract(url_article)
      pic_url = news.find("img").attrs["src"]
      str = ""
      str += "Date: " + date + "\r\n"
      str += "Title: " + title + "\r\n"
      str += "PicURL: " + pic_url + "\r\n"
      str += "Abstract: " + abstract + "\r\n"
      str += "URL: " + url_article + "\r\n"
      print(str)
      self.handle.write(str.replace("\xa0", ""))
    return True, (title, 2019, int(dates[0]), int(dates[1]), abstract, pic_url, url_article, 0)
    # (title, year, month, day, abstract, pic_url, url, isChinese)

