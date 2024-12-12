# This program is meant to iterate throught a json file and scrape web links dynamically using selenium.

import json
from subprocess import Popen, CREATE_NEW_CONSOLE
import argparse
import pandas as pd
import numpy as np
import os

# input for the number of workers you choose
parser = argparse.ArgumentParser()
parser.add_argument("--num_workers", type=int, help='Number of workers that will scrape data', default=1)
parsarg = vars(parser.parse_args())

numWorkers = parsarg.get('num_workers')

# Specify the relative file path for the JSON file
json_file_path = './IronManData/races.json'
# Read the JSON file
df = pd.read_json(json_file_path, orient='records', lines=True)

#create a dataframe of just link and id
race_df = df[['link', 'id']]


#initialize counts and df to track which 
count = 0
races_to_scrape = pd.DataFrame(columns=race_df.columns)  # Ensure it has the same columns as race_df

#iterate through race_df and check if race csv exists. If not, add to races to scrape
for race in race_df.itertuples(index=True, name='Pandas'):
    if os.path.exists(f'./IronManData/raceResultsData/{race.id}.csv'):
        count += 1
    else:
        # Convert the tuple back to a DataFrame before concatenating
        race_to_add = pd.DataFrame([[race.link, race.id]], columns=['link', 'id'])
        races_to_scrape = pd.concat([races_to_scrape, race_to_add], ignore_index=True)

print(f'{count} races already scraped. {len(races_to_scrape)} races to scrape.')
print('Exporting List to races_to_scrape.json')

# Save the JSON string to a file
json_str = races_to_scrape.to_json(orient='records', lines=True)
json_file_path = './IronManData/races_to_scrape.json'
with open(json_file_path, 'w') as file:
    file.write(json_str)

print("JSON file created successfully!")


def split_indexes(a, n):
  k, m = divmod(len(a), n)
  splitted_data = list((a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in list(range(n))))
  count = 0
  indexes = []
  for split in splitted_data:
      indexes.append(str(count) + '-' + str(len(split)+count-1))
      count += len(split)

  # output will be like: ["0-99", "100-199", "200-299", ...]
  return indexes


# get the array of indexes
# e.g: [“0-99”, “100-199”, “200-299”, ...]
indexes = split_indexes(races_to_scrape, numWorkers)

# for each string in our indexes list, 
# we open a new console that will launch the worker process

for index in indexes:
    Popen(('python worker.py ' + index), creationflags=CREATE_NEW_CONSOLE)