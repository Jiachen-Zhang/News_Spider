#!../venv python
# coding: utf-8

# ## Import the library

from urllib.request import urlopen
from bs4 import BeautifulSoup
import ssl
import xml.etree.ElementTree as ET
import sqlite3

# Method for parse page
class spider:
  def __init__(self, _dateRangeMin, _dateRangeMax, _db):
    # ## Build the headers
    # Ignore SSL certificate errors
    self.ctx = ssl.create_default_context()
    self.ctx.check_hostname = False
    self.ctx.verify_mode = ssl.CERT_NONE

    self.dateRangeMin = _dateRangeMin
    self.dateRangeMax = _dateRangeMax
    self.db = _db
    self.get_CN_Date()

  def get_CN_Date(self):
    # ## Open the file
    self.handle = open("dataCN.txt", "w")
    origin_url = "https://newshub.sustech.edu.cn/zh/?cat=3&paged="
    for i in range(1, 20):
      result = self.parse_page_CN(origin_url + str(i))
      if result is False:
          print("Finish")
          break
    self.handle.close()
    

  def parse_page_CN(self, url):
    html = urlopen(url, context=self.ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    for news in soup.select(".m-newslist > ul > li"):
      date = news.find(class_="u-date").get_text().strip().replace("\n", "/")
      temp = date.split("/")
      date_num =int(temp[0] + temp[1])
      print(date_num)
      if date_num < self.dateRangeMin:
        return False
      if date_num > self.dateRangeMax:
        continue
      s = str()
      s += "Date: " + date + "\r\n"
      title = news.find(class_="title f-clamp").get_text().strip()
      s += "Title: " + title  + "\r\n"
      pic_url = news.find( class_="u-pic").attrs['style'].split("(")[1].split(")")[0]
      s += "PicURL: " + pic_url + "\r\n"
      abstract = news.find(class_="details f-clamp4").get_text().replace("\n", "")
      s += "Abstract: "+ abstract + "\r\n"
      url = news.a.attrs.get("href")
      s += "URL: " + url + "\r\n"
      print(s)
      self.handle.write(s.replace("\u2022", "").replace("\xa0", "").replace("\u200b", ""))
    return True, 
          # (title, year, month, day, abstract, pic_url, url)
          (title, 2019, int(temp[0]), int(temp[1]), abstract, pic_url, url)


