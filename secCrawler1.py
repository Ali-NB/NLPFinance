# This script will download the 10-K filing and extract text only out of it
# provided that list of companies symbols and their CIK codes.

from bs4 import BeautifulSoup
import re
import requests
import os
import pandas as pd


class SecCrawler():

    def __init__(self):
        self.hello = "Welcome to Sec Crawler!"

    def make_directory(self, companyCode, cik, priorto, filing_type):
        # Making the directory to save comapny filings
        if not os.path.exists("SEC-Edgar-data/"):
            os.makedirs("SEC-Edgar-data/")
        if not os.path.exists("SEC-Edgar-data/" + str(companyCode)):
            os.makedirs("SEC-Edgar-data/" + str(companyCode))
        if not os.path.exists("SEC-Edgar-data/" + str(companyCode) + "/" + str(cik)):
            os.makedirs("SEC-Edgar-data/" + str(companyCode) + "/" + str(cik))
        if not os.path.exists("SEC-Edgar-data/" + str(companyCode) + "/" + str(cik) + "/" + str(filing_type)):
            os.makedirs("SEC-Edgar-data/" + str(companyCode) + "/" + str(cik) + "/" + str(filing_type))

    def save_in_directory(self, companyCode, cik, priorto, docList, docNameList, filing_type):
        # Save every text document into its respective folder
        for j in range(len(docList)):
            base_url = docList[j]
            r = requests.get(base_url)
            html = r.text
            #soup = BeautifulSoup(html)
            #text = soup.get_text()
            path = "SEC-Edgar-data/" + str(companyCode) + "/" + str(cik) + "/" + str(filing_type) + "/" + str(
                docNameList[j])
            filename = open(path, "a",encoding='utf-8')
            #filename.write(data.encode('ascii', 'ignore'))
            filename.write(html)

    def remove_html(self, companyCode, cik, docList, docNameList, filing_type):
        # Extract text from 10-k
        for j in range(len(docList)):
                        
            path = "SEC-Edgar-data/" + str(companyCode) + "/" + str(cik) + "/" + str(filing_type) + "/" + str(
                docNameList[j])
            filename = open(path, "r")
            lines = filename.readlines()
            
            with open(path + "Clean" + ".txt", 'w') as f1:
                for line in lines:
                    if re.search('<XBRL>.*', line):
                        break
                    f1.write(line)

            soup = BeautifulSoup(open(path + "Clean" + ".txt", "r").read(), 'lxml')

            for tables in soup.find_all('table'):
                soup.table.extract()

            text = soup.get_text()
            file2 = open(path + "Clean" + ".txt", "w", encoding='utf-8')
            file2.write(text)

            #print("Number of files to clean %s", len(linkListFinal))
            
    def filing_10K(self, companyCode, cik, priorto, count):
        try:
            self.make_directory(companyCode, cik, priorto, '10-K')
        except:
            print("Not able to create directory")

        if 10<count<20:
            count1=20
        elif 20<count<40:
            count1=40
        elif 40 < count < 80:
            count1 = 80
        elif 80 < count < 100:
            count1 = 100
        else: count1= count

        # generate the url to crawl
        base_url = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=" + str(
            cik) + "&type=10-K&dateb=" + str(priorto) + "&owner=exclude&output=xml&count=" + str(count1)
        print("started !0-K" + str(companyCode))
        r = requests.get(base_url)
        data = r.text
        soup = BeautifulSoup(data, "lxml")  # Initializing to crawl again
        linkList = []  # List of all links from the CIK page

        # If the link is .htm convert it to .html
        for link in soup.find_all('filinghref'):
            URL = link.string
            if link.string.split(".")[len(link.string.split(".")) - 1] == "htm":
                URL += "l"
            linkList.append(URL)
        linkListFinal = linkList[0:count]

        print("Number of files to download %s", len(linkListFinal))
        print("Starting download....")

        docList = []  # List of URL to the text documents
        docNameList = []  # List of document names

        for k in range(len(linkListFinal)):
            requiredURL = str(linkListFinal[k])[0:len(linkListFinal[k]) - 11]
            txtdoc = requiredURL + ".txt"
            docname = txtdoc.split("/")[len(txtdoc.split("/")) - 1]
            docList.append(txtdoc)
            docNameList.append(docname)

        try:
            self.save_in_directory(companyCode, cik, priorto, docList, docNameList, '10-K')
        except:
            print("Not able to save the file :( ")

        print("Successfully downloaded all the files")

        try:
            self.remove_html(companyCode, cik, docList, docNameList, '10-K')
        except:
            print("Not able to clean the file :( ")

        print("Successfully cleaned all the files")

file_tic_list = 'cik_ticker.2.txt'
data_tic_list = pd.read_csv(file_tic_list, error_bad_lines=False, encoding="utf-16" ,sep= "\t")
CIK = data_tic_list['CIK']
Tic = data_tic_list['Ticker']
date = '20180101'

secCrawler = SecCrawler()
for x in range(0,len(Tic)):
    secCrawler.filing_10K(Tic[x], CIK[x], date, 2)
