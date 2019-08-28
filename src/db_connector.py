import spider_CN as my_spi
import sqlite3

# connect to the database
# database in memory
db = sqlite3.connect(":memory:")
cu = db.cursor()
cu.execute("""
          CREATE TABLE "Article" (
            "id"	INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
            "title"	TEXT NOT NULL UNIQUE,
            "year"	INTEGER NOT NULL,
            "month"	INTEGER NOT NULL,
            "day"	INTEGER NOT NULL,
            "abstract"	BLOB NOT NULL,
            "main_pic"	INTEGER NOT NULL,
            "link"	TEXT NOT NULL
          );
          """)
dateRangeMin = 825
dateRangeMax = 828
my_spi.spider(dateRangeMin,dateRangeMax, db)
db.close()

