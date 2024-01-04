
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
    '''extracting the date of the string and it to a dictionnary'''
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

    # Transform the INSEE code for each row to a string in order to make the relation with a geojsonfile
    loyers_df['INSEE']=loyers_df['INSEE'].astype(str)
    loyers_df['DEP']=loyers_df['DEP'].astype(str)
    loyers_df['INSEE']=loyers_df['INSEE'].str.zfill(5)
    loyers_df['DEP']=loyers_df['DEP'].str.zfill(2)

    # Load the name of regions
    regions_df=pd.read_csv(os.path.join(root_path,"filecsv","region.csv"),encoding='latin1',delimiter=',')
    regions_df=regions_df.rename(columns={'REGION,C,2':'REG','NCC,C,70':'NOM_REGION'})
    loyers_df=loyers_df.merge(regions_df,on=['REG'])

    # Load the name of departments
    deps_df=pd.read_csv(os.path.join(root_path,"filecsv","departements-france.csv"),encoding='utf-8',delimiter=',')
    deps_df=deps_df.rename(columns={'code_departement':'DEP','nom_departement':'NOM_DEP'})
    loyers_df=loyers_df.merge(deps_df,on=['DEP'])

    # Select the columns that I need to build the dashboard with
    loyers_df=loyers_df.rename(columns={'loypredm2':'LOYER_EUROM2','LIBGEO':'NOM'})
    loyers_df=loyers_df[['NOM','INSEE','DEP','REG','LOYER_EUROM2','TYPE','YEAR','NOM_DEP','NOM_REGION']]

    # Load the geographical center of departments
    geo_df=pd.read_csv(os.path.join(root_path,"filecsv","georef-france-region@public.csv"),encoding='utf-8',delimiter=';')
    geo_df[['LAT_CENTRE', 'LON_CENTRE']] = geo_df['Geo Point'].str.split(', ', expand=True)
    geo_df=geo_df[['Code Officiel Courant Région','LAT_CENTRE', 'LON_CENTRE']]
    geo_df=geo_df.rename(columns={'Code Officiel Courant Région':'REG'})
    geo_df['LAT_CENTRE']=geo_df['LAT_CENTRE'].astype(float)
    geo_df['LON_CENTRE']=geo_df['LON_CENTRE'].astype(float)
    loyers_df=loyers_df.merge(geo_df,on=['REG'])


    return loyers_df

def load_geojson(df):
    '''Loads the geojson file to get the geometry of each deparment'''

    # Read the geojson file
    with open(os.path.join(root_path,"geojsonfiles",'departements-avec-outre-mer.geojson')) as f:
        geojsondata = json.load(f)

    return geojsondata

def load_geojsoncommune(df):
    '''Loads the geojson file to get the geometry of each commune'''

    # Read the geojson file
    with open(os.path.join(root_path,"geojsonfiles",'correspondance-code-insee-code-postal.geojson')) as f:
        geojsondata = json.load(f)
        
    return geojsondata

def load_wellbeing_data():
    '''Well-being data frame construction'''
    #Well-being data frame construction
    wellbeing_df=pd.read_csv(os.path.join(root_path,"filecsv","oecd_wellbeing.csv"),encoding='utf-8',delimiter=';',decimal=',')
    wellbeing_df=wellbeing_df[wellbeing_df['Country']=='France']
    wellbeing_df=wellbeing_df[['Region','Code','Education','Jobs','Income','Safety','Health','Environment','Civic engagement','Accessiblity to services','Housing','Community','Life satisfaction']]
    #Because the data is in english we need to make the relationships for each region to its name in french
    eng_french=[['Île-de-France','ILE-DE-FRANCE'],
                ['Centre - Val de Loire','CENTRE-VAL DE LOIRE'],
                ['Bourgogne-Franche-Comté','BOURGOGNE-FRANCHE-COMTE'],
                ['Normandy','NORMANDIE'],
                ['Hauts-de-France','HAUTS-DE-FRANCE'],
                ['Grand Est','GRAND EST'],
                ['Pays de la Loire','PAYS DE LA LOIRE'],
                ['Brittany','BRETAGNE'],
                ['Nouvelle-Aquitaine','NOUVELLE-AQUITAINE'],
                ['Auvergne-Rhône-Alpes','AUVERGNE-RHONE-ALPES'],
                ['Provence-Alpes-Côte d’Azur',"PROVENCE-ALPES-COTE D'AZUR"],
                ['Guadeloupe','GUADELOUPE'],
                ['Martinique','MARTINIQUE'],
                ['French Guiana','GUYANE'],
                ['La Réunion','LA REUNION'],
                ['Corsica','CORSE'],
                ['Occitanie','OCCITANIE']]
    eng_french=pd.DataFrame(eng_french,columns=['NOM_ENG','NOM_REGION'])
    eng_french=eng_french.rename(columns={'NOM_ENG':'Region'})
    wellbeing_df=wellbeing_df.merge(eng_french,on=['Region'])
    wellbeing_df=wellbeing_df.rename(columns={'Education':'EDUCATION','Jobs':'TRAVAIL','Income':'REVENUS','Safety':'SECURITE','Health':'SANTE','Community':'COMMUNAUTE','Life satisfaction':'QUALITE DE VIE'})
    wellbeing_df=wellbeing_df[['NOM_REGION','EDUCATION','TRAVAIL','REVENUS','SECURITE','SANTE','COMMUNAUTE','QUALITE DE VIE']]
    
    wellbeing_df=wellbeing_df.replace(',', '.', regex=True)
    wellbeing_df=wellbeing_df.replace('..', 0)
    # Convert each note in a float type
    for col in wellbeing_df:
        if col != 'NOM_REGION':
            wellbeing_df[col]= wellbeing_df[col].astype(float)
    return wellbeing_df