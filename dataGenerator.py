
import sys
import os
import pandas as pd
import json
import geopandas as gpd
import re
import os
import sys

# Extracting the year of a string and output the string
def extract_year(input_string):
    # Define a regular expression pattern for a year (four digits)
    pattern = re.compile(r'(\d{4})')

    # Search for the pattern in the input string
    match = re.search(pattern, input_string)

    # If a match is found, return the matched year; otherwise, return None
    if match:
        return match.group(1)
    else:
        return None

root_path = sys.path[0]

def generate_data():
    '''Loads the data form csv files and returns a dataframe with the information needed'''

    # List of files that need to be loaded
    fichiers=['app_2018.csv','app_2022_3.csv','app_2022_12.csv','app_2022.csv','maison_2018.csv','maison_2022.csv']

    frames=[]
    # Transform each file into a partial dataframe
    csvFolderPath = os.path.join(root_path,"datacsv")
    listOfFilesInFolderCSV = os.listdir(csvFolderPath)
    filteredListOfFilesInFolderCSV = {}
    # Filter the files get a list of the names of the csv input in the folder "datacsv"
    for file in listOfFilesInFolderCSV:
        if file.endswith('.csv'):
            # extracting the date of the string and it to a dictionnary
            year = extract_year(file)
            if year:
                if year not in filteredListOfFilesInFolderCSV:
                    filteredListOfFilesInFolderCSV[year] = []
                filteredListOfFilesInFolderCSV[year].append(file)
    sorted(filteredListOfFilesInFolderCSV)
    
    # Getting the path of the csv files and filter the data to get only with the right TYPE and YEAR and append it to frames
    for folder in filteredListOfFilesInFolderCSV:
        for file in filteredListOfFilesInFolderCSV[folder]:
            partial_df=pd.read_csv(os.path.join(root_path,"datacsv",file),encoding='latin1',delimiter=';',decimal=',')
            partial_df['TYPE']=file[0:file.index('_')]
            partial_df['YEAR']=file[file.index('_')+1:file.index('_')+5]
            frames.append(partial_df)

    # Build a dataframe taking into account all the partial dataframes loaded
    loyers_df=pd.concat(frames,ignore_index=True)

    # Load the name of regions
    regions_df=pd.read_csv(os.path.join(root_path,"filecsv","region.csv"),encoding='latin1',delimiter=',')
    regions_df=regions_df.rename(columns={'REGION,C,2':'REG','NCC,C,70':'NOM_REGION'})

    loyers_df=loyers_df.merge(regions_df,on=['REG'])

    # Select the columns that I need to build the dashboard with
    loyers_df=loyers_df.rename(columns={'loypredm2':'LOYER_EUROM2','LIBGEO':'NOM'})
    loyers_df=loyers_df[['NOM','INSEE','DEP','REG','LOYER_EUROM2','TYPE','YEAR','NOM_REGION']]
    # Transform the INSEE code for each row to a string in order to make the relation with a geojsonfile
    loyers_df['INSEE']=loyers_df['INSEE'].astype(str)
    loyers_df['DEP']=loyers_df['DEP'].astype(str)
    loyers_df['INSEE']=loyers_df['INSEE'].str.zfill(5)
    loyers_df['DEP']=loyers_df['DEP'].str.zfill(2)
    return loyers_df

def load_geojson(df):
    '''Loads the geojson file to get the geometry of each commune'''

    # Read the geojson file
    #with open(os.path.join(root_path,"geojsonfiles",'correspondance-code-insee-code-postal.geojson')) as f:
    with open(os.path.join(root_path,"geojsonfiles",'departements-avec-outre-mer.geojson')) as f:
        geojsondata = json.load(f)

    return geojsondata

def load_geojsoncommune(df):
    '''Loads the geojson file to get the geometry of each commune'''

    # Read the geojson file
    with open(os.path.join(root_path,"geojsonfiles",'correspondance-code-insee-code-postal.geojson')) as f:
        geojsondata = json.load(f)

    return geojsondata

def load_school_data():
    return pd.read_csv('datacsv/adresses_ecoles.csv')