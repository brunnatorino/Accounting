import pandas as pd
import numpy as np
import matplotlib as mlt
import math
import datetime as dt
from datetime import datetime, date
from datetime import datetime, timedelta
import time
from datetime import date

print('ATTENTION: For the assets file, make sure the columns correctly correspond to the ones described in the names section in the next cell. The names do not need to match')
print('but the number of cells and content must match exactly')

## adds user input to enable non-python users to use the code directly from the command line 

file_countries = input('Please enter the file name for the country mapping with .xlsx extension. If using standard, just enter standard.xlsx:')
file_assets = input('Please enter the file name for the assets you wish to calculate depreciation for with .xlsx extension:')

## this function imports the excel files, change names within read_excel("") to import different files
countries = pd.read_excel('countries-table.xlsx')
assets = pd.read_excel('assets2018.xlsx', names = ['Asset_Account','Acquisition Date','Asset Description','Asset Class','Initial_Value','Acquisition','Retirement',
                                                 'Transfer','Current_apc','Dep_FY_START','DEP_FOR_YEAR','DEP_RETIR','dep-transfer','ACCUM_DEP','BK_FY_START',
                                                   'CURR_BK','Beginning','Closing'])
## prints the data set


assets = assets.query('Initial_Value > 0')
assets['Value'] = assets['Initial_Value'].add(assets['Acquisition'])
assets['Value'] =assets['Value'].add(assets['Retirement'])
assets['Value'] =assets['Value'].add(assets['Transfer'])

countries_map = countries[['Asset Class','Germany']]
countries_map = countries_map.set_index('Asset Class').to_dict()['Germany']
assets['Asset Class'] = assets['Asset Class'].map(countries_map)

## creates three new dataframes to separate countries
dfA = assets.copy()

## fills last column country with A,B or C --> replace with country abbreviations
dfA['Threshold'] = 250

## drop values smaller than threshold 
dfA = dfA.query('Value >= Threshold')

## setting up for dictionary
useful_life1 = countries[['Germany','Useful Life Germany']]

## dictionary for mapping of useful life
useful_life1 = useful_life1.set_index('Germany').to_dict()['Useful Life Germany']

## life = type column for mapping
dfA['Life'] = dfA['Asset Class']

## mapping for useful life
dfA['Life'] = dfA['Life'].map(useful_life1)

##rounding values with truncate funcion

dfA = dfA.dropna(subset=['Acquisition Date'])

today = datetime.today()
month = today.month
year = today.year
dfA['Life_In_Months'] = dfA['Life'].mul(12)

## CALCULATING DEPRECIATION TIME FOR COUNTRY A
dfA['Acquisition Date'] = pd.to_datetime(dfA['Acquisition Date'],format='%d%m%Y')
dfA['year'], dfA['month'], dfA['day'] = dfA['Acquisition Date'].dt.year, dfA['Acquisition Date'].dt.month,dfA['Acquisition Date'].dt.day
dfA['Closing'] = pd.to_datetime(dfA['Closing'] ,format='%d%m%Y')
dfA['Beginning'] = pd.to_datetime(dfA['Beginning'] ,format='%d%m%Y')

## adds a month if the day is bigger than 1, also works for december --> adds a year 
## begins new month in the first day

dfA.loc[dfA["day"] != 1,'First_Date_Month'] = dfA['Acquisition Date'] + pd.offsets.MonthBegin(1)
dfA.loc[dfA["day"] == 1,'First_Date_Month'] = dfA['Acquisition Date']

## calculates how many months it has been since the start of the current financial year
## using closing date as same as beginning date for simplicity, but if using exact closing date, make sure to add +1 after astype(int)
dfA['Months_Past'] = ((dfA['Beginning'] - dfA['First_Date_Month'])/np.timedelta64(1, 'M')).astype(int) 

## sets to zero all the assets bought this year// they haven't been depreciated yet 
dfA.loc[dfA["Months_Past"] < 0,'Months_Past'] = 0

## calculates the initial balance of the asset in the start of the year 
dfA['Depreciation_Per_Month'] = dfA['Value'].div(dfA['Life_In_Months'])
dfA['Depreciated_Amount'] = dfA['Depreciation_Per_Month'].mul(dfA['Months_Past'])
dfA['Balance_Start'] = dfA['Value'].sub(dfA['Depreciated_Amount'])
dfA = dfA.query('Balance_Start >= 0')

## depreciation for this year --> coded like this to fit a financial year ending in OCTOBER. If your financial year ends
## in another year, make sure to adjust the code below! It is better to code it this way to make sure you are making
## the correct calculations, but another option would be (if your years ends Dec. 31st):
## dfA['Depreciation_This_Year_In_Months'] = dfA['Closing'].dt.month - dfA['First_Date_Month'].dt.month + 1

dfA.loc[dfA['First_Date_Month'].dt.month == 1,'Depreciation_This_Year_In_Months'] = 9
dfA.loc[dfA['First_Date_Month'].dt.month == 2,'Depreciation_This_Year_In_Months'] = 8
dfA.loc[dfA['First_Date_Month'].dt.month == 3,'Depreciation_This_Year_In_Months'] = 7
dfA.loc[dfA['First_Date_Month'].dt.month == 4,'Depreciation_This_Year_In_Months'] = 6
dfA.loc[dfA['First_Date_Month'].dt.month == 5,'Depreciation_This_Year_In_Months'] = 5
dfA.loc[dfA['First_Date_Month'].dt.month == 6,'Depreciation_This_Year_In_Months'] = 4
dfA.loc[dfA['First_Date_Month'].dt.month == 7,'Depreciation_This_Year_In_Months'] = 3
dfA.loc[dfA['First_Date_Month'].dt.month == 8,'Depreciation_This_Year_In_Months'] = 2
dfA.loc[dfA['First_Date_Month'].dt.month == 9,'Depreciation_This_Year_In_Months'] = 1
dfA.loc[dfA['First_Date_Month'].dt.month == 10,'Depreciation_This_Year_In_Months'] = 12
dfA.loc[dfA['First_Date_Month'].dt.month == 11,'Depreciation_This_Year_In_Months'] = 11
dfA.loc[dfA['First_Date_Month'].dt.month == 12,'Depreciation_This_Year_In_Months'] = 10

## calculates amount to depreciate and book value at the end of fiscal year
dfA['Amount_To_Depreciate'] = dfA['Depreciation_This_Year_In_Months'].mul(dfA['Depreciation_Per_Month'])
dfA['End of FY19 - Book Value'] = dfA['Balance_Start'] - dfA['Amount_To_Depreciate']

## calculates months until asset is completely depreciated
dfA['Months_To_Zero'] = dfA['Life_In_Months']- dfA['Months_Past']
## returns correct amount to depreciate if asset's life ends this year
dfA.loc[dfA["Balance_Start"] < dfA['Amount_To_Depreciate'],'Amount_To_Depreciate'] = dfA['Balance_Start']
dfA.loc[dfA["Months_To_Zero"] <= dfA["Depreciation_This_Year_In_Months"],'Note'] = 'End of Life in Current fiscal Year'

## takes care of rounding 
dfA.loc[dfA["End of FY19 - Book Value"] < 0,'End of FY19 - Book Value'] = 0
dfA.loc[dfA["End of FY19 - Book Value"] < 0.1,'End of FY19 - Book Value'] = 0

## output as excel file for outside users

writer = pd.ExcelWriter("output-sample.xlsx",
                        engine='xlsxwriter',
                        datetime_format='yyyymmdd',
                        date_format='yyyymmdd')

dfA.to_excel(writer, sheet_name = ('Germany'))


workbook  = writer.book
worksheet = writer.sheets['Germany']
worksheet.set_column('B:C', 20)
writer.save()
