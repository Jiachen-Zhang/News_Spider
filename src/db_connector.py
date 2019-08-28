import spider as my_spi
import sqlite3

DB_creator_sql = """
          CREATE TABLE "Article" (
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

class Connector:
    def __init__(self):
        # open database in memory
        self.mem_DB = sqlite3.connect(":memory:")
    
    def spider_data(self):
        dateRangeMin = 825
        dateRangeMax = 828
        mem_DB_cursor = self.mem_DB.cursor()
        mem_DB_cursor.execute(DB_creator_sql)
        spider = my_spi.spider(dateRangeMin,dateRangeMax, mem_DB_cursor)
        spider.get_CN_data()
        spider.get_EN_data()
        mem_DB_cursor.close()
        self.mem_DB.commit()

    def store_disk(self): 
        # https://blog.csdn.net/rongyongfeikai2/article/details/13628155
        from io import StringIO
        buffer = StringIO()
        for line in self.mem_DB.iterdump():
            buffer.write(line)
        self.mem_DB.close()

        print("-----------------Get buffer from mem_DB")
        # open database on disk
        disk_DB = sqlite3.connect("./src/data/data.db")
        print("-----------------Open disk_DB")
        cursor = disk_DB.cursor()
        cursor.executescript(buffer.getvalue())
        print("-----------------Write buffer into disk_DB")
        cursor.close()
        disk_DB.close()

connector = Connector()
connector.spider_data()
connector.store_disk()



