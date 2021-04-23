import requests
import csv
from bs4 import BeautifulSoup
from datetime import date
import time 
import mysql.connector

db = mysql.connector.connect(
	host = "localhost",
	user = "root",
	passwd = "********",
	database = "Real Estate"
) 


mycursor = db.cursor()


def clearContent():
	mycursor.execute("Delete From Scrapped;")


def query():
	mycursor.execute("SET SQL_SAFE_UPDATES = 0;")
	mycursor.execute('''delete t1 FROM Scrapped t1 INNER  JOIN Scrapped t2 WHERE t1.Houseid < t2.Houseid AND t1.address = t2.Address;''')
	db.commit()
	mycursor.execute(''' 
			Select 
    scr.address address,
    scr.price 'asking price',
    as1.assessedPrice 'Assessed Price',
    scr.price - as1.assessedPrice AS diff,
    scr.DateUploaded AS 'Uploaded Date',
    scr.NewUpload,
    as1.Neighbourhood,
    as1.SqFoot,
    as1.BuildingType,
    as1.Basement,
    as1.BasementFinish,
    as1.Garage,
    as1.Year,
    as1.zoning,
    scr.fulladdress 'Full Address',
    scr.URL
	FROM
    scrapped AS scr
        INNER JOIN
    assessement_parcels_v2 as1 ON scr.address = as1.Full_Address
        OR scr.address = as1.AbvAddress
	ORDER BY diff ASC; ''')


def newlyUploadedQuery():
	mycursor.execute(''' 
			Select 
    scr.address address,
    scr.price 'asking price',
    as1.assessedPrice 'Assessed Price',
    scr.price - as1.assessedPrice AS diff,
    scr.DateUploaded AS 'Uploaded Date',
    scr.NewUpload,
    as1.Neighbourhood,
    as1.SqFoot,
    as1.BuildingType,
    as1.Basement,
    as1.BasementFinish,
    as1.Garage,
    as1.Year,
    as1.zoning,
    scr.fulladdress 'Full Address',
    scr.URL
	FROM
    scrapped AS scr
        INNER JOIN
    assessement_parcels_v2 as1 ON (scr.address = as1.Full_Address
        OR scr.address = as1.AbvAddress) 
        and scr.NewUpload = "**NEW UPLOAD**"
	ORDER BY diff ASC; ''')
	#db.commit()
