import spider as my_spi

# set the time range
month = 8
dateRangeMin = str(month) + "01"
dateRangeMax = str(month+1) + "01"
# spider the data and store into database
db_path = "./src/data/news_data.db"
spider = my_spi.spider(dateRangeMin, dateRangeMax, db_path)
spider.connect_DB()
spider.get_CN_data()
spider.get_EN_data()
spider.disconnect_DB()

# generate markdown format and convert into html format


# generate outline and convert into doc format
