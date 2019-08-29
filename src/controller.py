# In[1]: Get data from website
import spider as my_spi
import datetime

# set the time range
month = datetime.datetime.now().month
print("制作" + str(month-1) + "月电子报")
dateRangeMin = int(str(month-1) + "01")
dateRangeMax = int(str(month) + "00")

# spider the data and store into database
db_path = "./src/data/news_data.db"
def spider_data():
    spider = my_spi.spider(dateRangeMin, dateRangeMax)
    spider.connect_DB(db_path)
    spider.get_CN_data()
    spider.get_EN_data()
    spider.disconnect_DB()


spider_data()

# In[2]: Extract data and generate markdown files
import sqlite3
import os


DB = sqlite3.connect(db_path)
cursor = DB.cursor()

sql_html_select = """
        SELECT (month || '/' || day) AS date, title, abstract, url, pic_url 
        FROM Article
        WHERE Month == ? And isChinese == (?)"""
def md_format(isChinese, file):
    cursor.execute(sql_html_select, [month-1 ,isChinese])
    for t in cursor.fetchall():
        date = t[0]
        title = t[1]
        abstract = t[2]
        url = t[3]
        pic_url = t[4]
        # write into file 
        file.write(date + " **" + title + "**\r\n\r\n")
        file.write("<img src=\"" + pic_url + "\"  width=\"50%\">" + "\r\n\r\n")
        file.write(abstract + "\r\n\r\n")
        file.write("*" + url + "*\r\n\r\n\r\n\r\n")


# generate outline
def md_format_outline(file):
    sql_html_select = """
        SELECT (month || '/' || day) AS date, title, url 
        FROM Article
        WHERE Month == 8 And isChinese == 1"""
    cursor.execute(sql_html_select)
    for t in cursor.fetchall():
        date = t[0]
        title = t[1]
        url = t[2]
        # write into file 
        file.write(date + " [" + title + "](" + url + ")\r\n\r\n")


md_format(1, open("./src/data/电子报中文大纲.md", "w"))
md_format(0, open("./src/data/电子报英文大纲.md", "w"))
print("-------------------markdown files for html have been generated")

md_format_outline(file = open("./src/data/电子报分类大纲.md", "w"))
print("-------------------markdown files for content have been generated")

cursor.close()
DB.close()

# In[13]: Convert format and remove mid-files
import pypandoc


output = pypandoc.convert_file('./src/data/电子报中文大纲.md', 'html', 
                                outputfile='./src/data/电子报中文大纲.html')
assert output == ""
# output = pypandoc.convert_file('./src/data/电子报英文大纲.md', 'html', 
                                outputfile='./src/data/电子报英文大纲.html')
# assert output == ""
# output = pypandoc.convert_file('./src/data/电子报分类大纲.md', 'docx', 
                                outputfile='./src/data/电子报分类大纲.docx')
# assert output == ""
print("-------------------Finish format-converting")


os.remove('./src/data/电子报中文大纲.md')
os.remove('./src/data/电子报英文大纲.md')
os.remove('./src/data/电子报分类大纲.md')
print("-------------------Reduntant files removed")



