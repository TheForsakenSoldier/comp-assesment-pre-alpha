from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np


columnheading = [
    "gross-profit",
    "pe-ratio",
    "total-assets",
    "total-liabilities",
    "eps-earnings-per-share-diluted",
    "long-term-debt",
    "net-income",
    "total-share-holder-equity"
]

# calculating the growth rate of a column


def calcGrowthRateCol(column):
    column = column.apply(cleanPsik)
    column = pd.to_numeric(column)
    first_num = column.iloc[0]
    last_num = column.iloc[-1]
    total_years = len(column)
    total_growth = (last_num-first_num)/first_num
    avrage_growth = total_growth/(total_years-1)
    avrage_growth = avrage_growth*100
    return str(avrage_growth)+"%"


# cleaning dates with specified months
def cleanMultDate(datecolumn_val):
    head, sep, tail = datecolumn_val.partition('-')
    return head


# exports data to excel file
def exportExcel(company_name, company_data):
    company_data = company_data.apply(pd.to_numeric, axis=1)
    company_data.to_excel('./companies_data/'+company_name +
                          '.xlsx', sheet_name=company_name, index=False)
    print("Data saved successfullty")


# imports data from excel
def importExcel(company_name):
    df = pd.read_excel('./companies_data/'+company_name+'.xlsx')
    return df

# doing an avrage to pe from quarter results to make it yearly


def avrMultVals(df, column_head, temp_year):
    # piking drop value for the dataframe
    drop_value = np.nan
    # making the values to numaric values and not strs
    df[column_head] = pd.to_numeric(
        df[column_head], errors='coerce').fillna(0, downcast='infer')
    df[temp_year] = pd.to_numeric(
        df[temp_year], errors='coerce').fillna(0, downcast='infer')
    df = sortByYear(df, temp_year)
    # finding the first year
    first_year = df[temp_year].iat[0]
    # assigning current year
    previous_year = first_year
    # saving index of previous value
    current_year_index = 0
    # creating a year counter
    year_counter = 1
    # adding the first year PE
    sum = df[column_head].iat[current_year_index]
    for i in range(1, df[column_head].index[-1]+1):
      # creating the next value parameters
        current_year = df[temp_year].iat[i]
        current_pe = df[column_head].iat[i]
      # if previous year is equal to the current year
        if (previous_year == current_year):
            # add PE to sum
            sum += current_pe
            # adding 1 to year counter for avrage
            year_counter += 1
            # changing the previous year to the current one
            previous_year = current_year
            # saving the index of the current year
            current_year_index = i
            # changing the pe value to drop value
            df.loc[(current_year_index-1), [column_head]] = drop_value
            # handling the last value
        if (i == df[column_head].index[-1]):
            PE_avrage = sum/year_counter
            df.at[current_year_index, column_head] = PE_avrage
        # if the current year is different than the previous year
        elif (current_year != previous_year):
            # do an avrage of the pe of all the previous years
            PE_avrage = sum/year_counter
            # place that avrage into the last year location
            df.at[current_year_index, column_head] = PE_avrage
            # change the sum to the current year pe
            sum = current_pe
            # reset the year counter
            year_counter = 1
            # change the previous year into the current year
            previous_year = current_year
    # dropping NaN values
    df.dropna(subset=[column_head], inplace=True)
    # resetting index
    df.reset_index(inplace=True)
    # dropping old index
    df.drop(["index"], axis=1, inplace=True)
    return df


# reversing the dataframe
def reverseDataFrame(dataframe):
    df = dataframe[::-1].reset_index(drop=True)
    return df


# sorting data frame by year
def sortByYear(df, year_column):
    # finding the years that need to be dropped
    drop_vals = df[df[year_column] == 0].index
    # dropping the correct indexes
    df.drop(drop_vals, inplace=True)
    # sorting the data frame by year
    df.sort_values(by=year_column, ascending=True, inplace=True)
    # resetting index
    df.reset_index(inplace=True)
    # dropping old index
    df.drop(["index"], axis=1, inplace=True)
    return df


# cleaning dollar sign from a str (requires the apply command from a data frame)
def cleanDollar(str):
    y = str.replace('$', '')
    return y


# cleaning , sign from a str(requires apply command)
def cleanPsik(string):
    if (type(string) is not str):
        return string
    else:
        y = string.replace(',', '')
        return y

# main code


def analyze(company_ticker, company, heading):
    # getting the website
    url2scrape = 'https://www.macrotrends.net/stocks/charts/' + \
        company_ticker+'/'+company+'/'+heading
    r = requests.get(url2scrape)
    # transforming to text
    cleanhead = heading.replace("-", '')
    html = r.text
    # cleaning the html data to list
    pre_clean_data = [[cell.text for cell in row("td")]
                      for row in BeautifulSoup(html, features="lxml")("tr")]
    # cleaning null values
    pre_clean_data = list(filter(None, pre_clean_data))
    # choosing chunk size
    chunk_size = 13
    if (heading == "pe-ratio"):
        chunk_size = 53
    # splitting the data into chuncks
    pre_clean_list = [pre_clean_data[i:i+chunk_size]
                      for i in range(0, len(pre_clean_data), chunk_size)]
    # choosing the needed chunk
    listdat = pre_clean_list[0]
    if (heading == "gross-profit"):
        df = pd.DataFrame(listdat, columns=['year', "dirty"+cleanhead])
        # dropping rows with null values
        df = reverseDataFrame(df)
        # turning the data to int
        df[cleanhead] = df["dirty"+cleanhead].apply(cleanDollar)
        df[cleanhead] = df[cleanhead].apply(cleanPsik)
        df.drop("dirty"+cleanhead, axis=1, inplace=True)
        return (df)
    if (heading == "pe-ratio"):
        df = pd.DataFrame(listdat, columns=[
                          'year', 'garbage2', "garbage3", "PE"])
        # dropping rows with null values
        df = df.dropna(how='any', axis=0)
        # removing unneccery data
        df.drop(['garbage2', 'garbage3'], axis=1, inplace=True)
        # cleaning dollar sign
        df['PE'] = df['PE'].apply(cleanDollar)
        # making the dates work in the format
        df['year'] = df['year'].apply(cleanMultDate)
        df = reverseDataFrame(df)
        df = avrMultVals(df, "PE", 'year')
        df['PE'] = df['PE'].apply(cleanPsik)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df
    if (heading == "total-assets"):
        df = pd.DataFrame(listdat, columns=["year", "annual assets"])
        # cleaning dollar sign
        df["annual assets"] = df["annual assets"].apply(cleanDollar)
        df["annual assets"] = df["annual assets"].apply(cleanPsik)
        # reversing the data
        df = reverseDataFrame(df)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df
    if (heading == "total-liabilities"):
        df = pd.DataFrame(listdat, columns=["year", "annual liabilities"])
        # cleaning dollar sign
        df["annual liabilities"] = df["annual liabilities"].apply(cleanDollar)
        df["annual liabilities"] = df["annual liabilities"].apply(cleanPsik)
        # reversing the data
        df = reverseDataFrame(df)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df
    if (heading == "eps-earnings-per-share-diluted"):
        df = pd.DataFrame(listdat, columns=["year", "eps"])
        # cleaning dollar sign
        df["eps"] = df["eps"].apply(cleanDollar)
        df["eps"] = df["eps"].apply(cleanPsik)
        # reversing the data
        df = reverseDataFrame(df)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df
    if (heading == "long-term-debt"):
        df = pd.DataFrame(listdat, columns=["year", "long term debt"])
        # cleaning dollar sign
        df["long term debt"] = df["long term debt"].apply(cleanDollar)
        df["long term debt"] = df["long term debt"].apply(cleanPsik)
        # reversing the data
        df = reverseDataFrame(df)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df
    if (heading == "net-income"):
        df = pd.DataFrame(listdat, columns=["year", "net income"])
        # cleaning dollar sign
        df["net income"] = df["net income"].apply(cleanDollar)
        df["net income"] = df["net income"].apply(cleanPsik)
        # reversing the data
        df = reverseDataFrame(df)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df
    if (heading == "total-share-holder-equity"):
        df = pd.DataFrame(listdat, columns=["year", "equity"])
        # cleaning dollar sign
        df["equity"] = df["equity"].apply(cleanDollar)
        df["equity"] = df["equity"].apply(cleanPsik)
        # reversing the data
        df = reverseDataFrame(df)
        # dropping the year
        df.drop(['year'], axis=1, inplace=True)
        return df

# starting the program


def progStart(companyTicker, company):
    if (company == "-1"):
        return
    for subject in columnheading:
        if (subject == "gross-profit"):
            gpdf = analyze(companyTicker, company, subject)
        if (subject == 'pe-ratio'):
            prdf = analyze(companyTicker, company, subject)
        if (subject == "total-assets"):
            tadf = analyze(companyTicker, company, subject)
        if (subject == "total-liabilities"):
            tldf = analyze(companyTicker, company, subject)
        if (subject == "total-share-holder-equity"):
            tshe = analyze(companyTicker, company, subject)
        if (subject == "eps-earnings-per-share-diluted"):
            epsdf = analyze(companyTicker, company, subject)
        if (subject == "long-term-debt"):
            ltddf = analyze(companyTicker, company, subject)
        if (subject == "net-income"):
            nidf = analyze(companyTicker, company, subject)
    super_table = pd.concat(
        [gpdf, prdf, tadf, tldf, tshe, epsdf, ltddf, nidf], axis=1, join="inner")
    return super_table
