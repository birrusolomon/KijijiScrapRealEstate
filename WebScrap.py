import requests
import csv
from bs4 import BeautifulSoup
from datetime import date
import time 
import mysql.connector
from SqlQuery import *
from sendEmail import *


global scrappedID 
global NotFoundURL
global PreviouslyScrapped
global mycursor
global newAds

scrappedID = 0 
newAds = 0
NotFoundURL = []
newScrapped = []


today = date.today()

#Create File 1: All scraped Ads
scarpe_data = today.strftime(" %B %d, %Y Raw Scrapped Data") + ".csv"
kijijiFile = open(scarpe_data, 'w')
raw_data = csv.writer(kijijiFile)
raw_data.writerow(["scrappedID","URL", "Address","Full Address", "Price","Uploaded Date","New Uploaded"])

#Get previously Scraped Ads to compare with new scraped ads. 
PreviouslyScrapped = []
with open('ScrappedAddess.txt', 'r') as filehandle:
    filecontents = filehandle.readlines()
    for line in filecontents:
        current_place = line[:-1]
        PreviouslyScrapped.append(current_place)


main_url = 'https://www.kijiji.ca/b-house-for-sale/winnipeg/c35l1700192?ll=49.894256%2C-97.138774&for-sale-by=ownr&address=Downtown%2C+Winnipeg%2C+MB&ad=offering&radius=30.0'
urlPages = "https://www.kijiji.ca/b-house-for-sale/winnipeg/page-{}/c35l1700192?radius=30.0&ad=offering&address=Downtown%2C+Winnipeg%2C+MB&ll=49.894256,-97.138774&for-sale-by=ownr"

# Clears content from previously scraped Data. 
# SQL QUERY:  Delete From Scrapped;
clearContent()

def getURLlinks(UrlPage):

	r = requests.get(UrlPage)
	soup = BeautifulSoup(r.text, 'html.parser')

	URL_Ads = []
	for link in soup.find_all('a'):
	    if link.has_attr('href'):

	    	ad_URL = link.attrs['href']
	    	if (ad_URL[0:2] == "/v"):
	    		
	    		URL_Ads.append("https://www.kijiji.ca"+ad_URL)
	    	
	return URL_Ads

def getAddress(address):
	global newScrapped
	try: 
		fullAddress = str(address.text) 
		token = fullAddress.split(',' )
		token2 = token[0]
		if '0' <= token2[0] <= '9':
			streetAddress = token2

		else:
			streetAddress = fullAddress
		#Saves all the scrapped Data
		newScrapped.append(fullAddress)
		return streetAddress, fullAddress
	
	except:
		return "Not Found", "Not Found"

def getPrice(price):
	if price != None:
		askingPrice = price.text.replace("$","").replace(",","")
	else:
		askingPrice = "0"

	if askingPrice == "Please Contact" or askingPrice == "Swap/Trade":
		return "0"
 
	return askingPrice

def getDate(uploadDate):
	try :
		token = (str(uploadDate).split('"'))
		if " title=" in token:
			postedDate = token[5]
		else:
			postedDate = token[3]
	except:
		postedDate = "Not Found"
	
	return postedDate

def getData(links,doublCheck):
	
	for URL in links:
		global scrappedID 
		global newAds


		r2 = requests.get(URL)
		soup2 = BeautifulSoup(r2.text, 'html.parser')
		address = soup2.find('span', itemprop='address')
		price = soup2.find('span', class_="currentPrice-2842943473")
		UploadedDate = soup2.find('div', class_="datePosted-383942873" )

		if (getAddress(address)[0]) != "Not Found":

			print (URL)
			print(getPrice(price))
			print(getDate(UploadedDate))
			fullAddress = (getAddress(address)[1])

			if fullAddress not in PreviouslyScrapped:
				newUpload = "**NEW UPLOAD**"
				newAds += 1
				print (newUpload)

			else:
				newUpload = ""


			scrappedID += 1

			mycursor.execute("INSERT INTO scrapped (HouseID, Address, FullAddress, price, DateUploaded, NewUpload, URL) VALUES (%s,%s,%s,%s,%s,%s,%s)",
				(scrappedID, getAddress(address)[0],getAddress(address)[1],getPrice(price),getDate(UploadedDate),newUpload,URL))
			db.commit()

			raw_data.writerow([scrappedID, getAddress(address)[0],getAddress(address)[1],getPrice(price),getDate(UploadedDate),newUpload,URL])
		elif not doublCheck:
			NotFoundURL.append(URL)
			
#Saves the new Scrapped data to compare for new Ads for the next time 
def saveSrappedHouses():
	with open('ScrappedAddess.txt', 'w') as filehandle:
	    for listitem in newScrapped:
	        filehandle.write('%s\n' % listitem)

def writeCvs(file,compared_CVS, rows):
	for colum in rows:
		compared_CVS.writerow([colum[0],colum[1],colum[2],colum[3],colum[4],colum[5],colum[6],
		colum[7],colum[8],colum[9],colum[10],colum[11],colum[12],colum[13],colum[14],colum[15]])
	file.close()

#My computer needs time laps 
getData(getURLlinks(main_url),False)
print ("Main Page is done: \n")
time.sleep(120)

for i in range (2,7):
	pages =  (urlPages.format(i))
	print(pages)
	getData(getURLlinks(pages),False)
	print ("*****************Page %s is done:*****************", i)
	time.sleep(120)

time.sleep(120)
getData(NotFoundURL,True)
print ("Finish Scrapping: ")

kijijiFile.close()



compared_date = today.strftime("%B %d, %Y Scrapped_and_Compared") + ".csv"
comparedfile = open(compared_date ,'w')
compared_CVS = csv.writer(comparedfile)
columTitle =  ["Address", "Asking Price","Assessed Price", "Diff", "Uploaded Date","New Upload", "Neighbourhood", 
	"Sq Foot", "Building Type","Basement","Basement Finish","Garage", "Year","zoning","Full Address", "URL"]


compared_CVS.writerow(columTitle)

saveSrappedHouses()
query()
rows = mycursor.fetchall()
compared_count = len(rows)
writeCvs(comparedfile,compared_CVS,rows)


filenames = [scarpe_data, compared_date]

if newAds:
	newAdsFile = today.strftime("%B %d, %Y New Ad ") + ".csv"
	newlyUploadedfile = open(newAdsFile,'w')
	newlyUploaded_CVS = csv.writer(newlyUploadedfile)
	newlyUploaded_CVS.writerow(columTitle)

	newlyUploadedQuery()
	rows2 = mycursor.fetchall()
	writeCvs(newlyUploadedfile,newlyUploaded_CVS,rows2)
	filenames.append(newAdsFile)


sendEmail(filenames, scrappedID,newAds,compared_count, main_url)




