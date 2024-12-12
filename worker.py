from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import pandas as pd
import numpy as np
import time
import sys
import os

# optional
from tqdm import tqdm

# Specify the relative file path for the JSON file
json_file_path = './IronManData/races_to_scrape.json'
# Read the JSON file
df = pd.read_json(json_file_path, orient='records', lines=True)

#create an array of links and arrays from the json file
race_array = df[['link', 'id']].values


# from the "indexes" parameter (which has been passed as a console parameter as secondargument
# we get 
# the index_start and index_end
index_start = int(sys.argv[1].split('-')[0])
index_end = int(sys.argv[1].split('-')[1])

if len(race_array) == 1:
    index_start=0
    index_end=1

#code to strip athlete ID from URL
def extract_number(url):
    try:
        return url.rstrip('/').split('/')[-1]
    except AttributeError:
        return None

#Scraping function
def scrape_race_results(url,raceID):
    
    driver = webdriver.Chrome()
    driver.get(url)
    
    print(f"Processing race {raceID}")
    # Find all rows in the table
    rows = driver.find_elements(By.XPATH, '//table/tbody/tr')
    
    # Prepare to collect data
    all_rows_data = []
    
    # Iterate over each row of data with a progress bar
    for row in tqdm(rows, desc="Processing rows"):
        columns = row.find_elements(By.TAG_NAME, 'td')
        row_data = []
        # Iterate over each element
        for i, column in enumerate(columns):
            row_data.append(column.text)
            # Check the second (Athlete) and fifth (Division) columns for links
            if i in [1, 4]:
                links = column.find_elements(By.TAG_NAME, 'a')
                if links:
                    href = links[0].get_attribute('href')
                    row_data.append(href)
                else:
                    row_data.append(pd.NA)
        
        # Ensure the row has the expected number of columns before adding it to all_rows_data
        if len(row_data) >= 15:
            all_rows_data.append(row_data)
    
    driver.quit()
    
    # Convert the list of lists into a DataFrame
    df = pd.DataFrame(all_rows_data)
    df.columns = ['bib','Name','athleteLink','Country','Gender','Division','divLink','divisionRank','overallTime','overallRank','swimTime','swimRank','bikeTime','bikeRank','runTime','runRank','finishStatus']
    df['raceID'] = raceID
    df['athleteID'] = df['athleteLink'].apply(extract_number)
    return df


for race in tqdm(race_array[index_start:index_end]):
    #check if csv already exists. Start next loop if it does
    if os.path.exists(f'./IronManData/raceResultsData/{race[1]}.csv'):
        print(f"Race {race[1]} already exists. Skipping...")
        continue

    scrape_race_results(race[0], race[1]).to_csv(f'./IronManData/raceResultsData/{race[1]}.csv', index=False)
    print(f"Finished race {race[1]}")



