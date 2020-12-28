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
  def __init__(self, _dateRangeMin, _dateRangeMax):
    # ## Build the headers
    # Ignore SSL certificate errors
    self.ctx = ssl.create_default_context()
    self.ctx.check_hostname = False
    self.ctx.verify_mode = ssl.CERT_NONE
    self.dateRangeMin = _dateRangeMin
    self.dateRangeMax = _dateRangeMax
  
  def connect_DB(self, db_path):
    self.DB = sqlite3.connect(db_path)
    self.cursor = self.DB.cursor()
    self.insert_sql = """INSERT OR IGNORE INTO Article 
                            (title, year, month, day, abstract, pic_url, url, isChinese) 
                            VALUES 
                            (?, ?, ?, ?, ?, ?, ?, ?)
                      """
    DB_creator_sql = """
          CREATE TABLE IF NOT EXISTS "Article" (
            "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            "title"	TEXT NOT NULL UNIQUE,
            "year"	INTEGER NOT NULL,
            "month"	INTEGER NOT NULL,
            "day"	INTEGER NOT NULL,
            "abstract"	BLOB NOT NULL,
            "pic_url"	INTEGER NOT NULL,
            "url"	TEXT NOT NULL,
            "isChinese"	INTEGER NOT NULL
          );
          """
    self.cursor.execute(DB_creator_sql)

  def disconnect_DB(self):
    self.DB.commit()
    self.cursor.close()
    self.DB.close()
    

  def get_CN_data(self):
    # ## Open the file
    # self.handle = open("./src/data/dataCN.txt", "w")
    origin_url = "https://newshub.sustech.edu.cn/zh/?cat=3&paged="
    for i in range(1, 20):
      result = self.__parse_page_CN(origin_url + str(i))
      if result is False:
          print("Finish")
          break
    self.DB.commit()
    # self.handle.close()


  def get_EN_data(self):
    # self.handle = open("./src/data/dataEN.txt", "w")
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
      result = self.__parse_page_EN(origin_url + str(i))
      if result is False:
        print("Finish")
        break
    # self.handle.close()

  def __parse_page_CN(self, url):
    html = urlopen(url, context=self.ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    
    for news in soup.select(".m-newslist > ul > li"):
      date = news.find(class_="u-date").get_text().strip().replace("\n", "/")
      temp = date.split("/")
      date_num = int(temp[0] + temp[1])
      print(date_num)
      if date_num < self.dateRangeMin:
        print("finish")
        return False
      if date_num > self.dateRangeMax:
        print("ignore")
        continue
      
      s = str()
      title = news.find(class_="title f-clamp").get_text().strip()
      pic_url = news.find( class_="u-pic").attrs['style'].split("(")[1].split(")")[0]
      abstract = news.find(class_="details f-clamp4").get_text().replace("\n", "")
      url = news.a.attrs.get("href")

      # s += "Date: " + date + "\r\n"
      # s += "Title: " + title  + "\r\n"
      # s += "PicURL: " + pic_url + "\r\n"
      # s += "Abstract: "+ abstract + "\r\n"
      # s += "URL: " + url + "\r\n"
      # print(s)
      # self.handle.write(s.replace("\u2022", "").replace("\xa0", "").replace("\u200b", ""))
      # (title, year, month, day, abstract, pic_url, url, isChinese)
      data = (title, 2019, int(temp[0]), int(temp[1]), abstract, pic_url, url, 1)
      self.cursor.execute(self.insert_sql, data)
    return True
                  
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
      if date_num < self.dateRangeMin:
        print("finish")
        return False
      if date_num > self.dateRangeMax:
        print("ignore")
        continue
      url_article = news.find("a").attrs['href']
      title = news.find("img").attrs["alt"]
      abstract = get_abstract(url_article)
      pic_url = news.find("img").attrs["src"]
      # str = ""
      # str += "Date: " + date + "\r\n"
      # str += "Title: " + title + "\r\n"
      # str += "PicURL: " + pic_url + "\r\n"
      # str += "Abstract: " + abstract + "\r\n"
      # str += "URL: " + url_article + "\r\n"
      # print(str)
      # self.handle.write(str.replace("\xa0", ""))
      data = (title, 2019, int(dates[0]), int(dates[1]), abstract, pic_url, url_article, 0)
      # (title, year, month, day, abstract, pic_url, url, isChinese)
      self.cursor.execute(self.insert_sql, data)      
    return True



class TitleSpider(spider):
  def __init__(self, _dateRangeMin, _dateRangeMax):
    super().__init__(_dateRangeMin, _dateRangeMax)
  def get_CN_data(self):
    print("START get_CN_data")
    # ## Open the file
    # self.handle = open("./src/data/dataCN.txt", "w")
    origin_url = "https://newshub.sustech.edu.cn/zh/news?page="
    for i in range(0, 10):
      result = self.__parse_page_CN(origin_url + str(i))
      if result is False:
          print("Finish")
          break
    self.DB.commit()
    print("END get_CN_data")
  def __parse_page_CN(self, url):
    html = urlopen(url, context=self.ctx).read()
    soup = BeautifulSoup(html, "html.parser")
    
    for news in soup.select(".m-newslist > ul > li"):
      date = news.find(class_="u-date").get_text().strip().replace("\n", "/")
      temp = date.split("/")
      date_num = int(temp[0] + temp[1])
      print(date_num)
      if date_num < self.dateRangeMin:
        print("finish")
        return False
      if date_num > self.dateRangeMax:
        print("ignore")
        continue
      
      s = str()
      title = news.find(class_="title f-clamp").get_text().strip()
      print(title)
      pic_url = news.find( class_="u-pic").attrs['style'].split("(")[1].split(")")[0]
      if pic_url.startswith('/'):
        pic_url = 'https://newshub.sustech.edu.cn' + pic_url
      abstract = news.find(class_="details f-clamp4").get_text().replace("\n", "")
      url = news.a.attrs.get("href")
      if url.startswith('/'):
        url = 'https://newshub.sustech.edu.cn' + url

      # s += "Date: " + date + "\r\n"
      # s += "Title: " + title  + "\r\n"
      # s += "PicURL: " + pic_url + "\r\n"
      # s += "Abstract: "+ abstract + "\r\n"
      # s += "URL: " + url + "\r\n"
      # print(s)
      # self.handle.write(s.replace("\u2022", "").replace("\xa0", "").replace("\u200b", ""))
      # (title, year, month, day, abstract, pic_url, url, isChinese)
      if ('2019' in url):
        return False
      data = (title, 2020, int(temp[0]), int(temp[1]), abstract, pic_url, url, 1)
      self.cursor.execute(self.insert_sql, data)
      print("write ", data)
    return True
  


if __name__ == '__main__':
  db_path = "./data/news_data.db"
  spider = TitleSpider(1121, 1231)
  # spider.connect_DB(db_path)
  # spider.get_CN_data()
  # spider.disconnect_DB()
  DB = sqlite3.connect(db_path)
  cursor = DB.cursor()


  def md_format_outline(file):
    sql_html_select = """
        SELECT (month || '/' || day) AS date, title, url
        FROM Article
        WHERE year = 2020
        AND (title LIKE '%获%' OR title LIKE '%当选%')
        ORDER BY month DESC, day DESC"""
    cursor.execute(sql_html_select)
    for t in cursor.fetchall():
      date = t[0]
      title = t[1]
      url = t[2]
      # write into file 
      file.write(date + " [" + title + "](" + url + ")\r\n\r\n")
  md_format_outline(file = open("./data/output.md", "w"))
  cursor.close()
  DB.close()
