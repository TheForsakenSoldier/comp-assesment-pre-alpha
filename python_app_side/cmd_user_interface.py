from app import progStart,exportExcel,importExcel,calcGrowthRateCol
import os

while(True):
   ticker=input("Enter company ticker: (-1 to finish): \n")
   if(ticker==-1 or ticker =="-1"):
    break
   directory="companies_data"
   isExistDir=os.path.isdir('./'+directory)
   #if the directory to hold the excel data dosent exist
   if(isExistDir==False):
    path=os.path.join('./',directory)
    os.mkdir(path)
  #creating the path for the excel file and checking if it exists
   path="./companies_data/"+ticker+".xlsx"
   isExist=os.path.exists(path)
   if(isExist):
       company=importExcel(ticker)
       print(company)
       print(calcGrowthRateCol(company["grossprofit"]))
       print("--------------")
   else:
    #if the file dosent exist (meaning the company wasent analized before) add him and print it
       company=progStart(ticker,ticker)
       print(company)
       save_file=input("Do you wish to save company data as excel file ? (y/n):")
       if(save_file=="y"):
         exportExcel(ticker,company_data=company)
         save_file=""
         print("--------------")
       else:
         print("--------------")
   