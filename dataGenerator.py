
import sys
import os
import pandas as pd
import json

root_path = sys.path[0]
def generate_data():
    '''Loads the data form csv files and returns a dataframe with the information needed'''

    # List of files that need to be loaded
    fichiers=['app_2018.csv','app_2022_3.csv','app_2022_12.csv','app_2022.csv','maison_2018.csv','maison_2022.csv']

    frames=[]
    # Transform each file into a partial dataframe
    for f in fichiers:
        partial_df=pd.read_csv(os.path.join(root_path,"fichierscsv",f),encoding='latin1',delimiter=';',decimal=',')
        partial_df['TYPE']=f[0:f.index('_')]
        partial_df['YEAR']=f[f.index('_')+1:f.index('_')+5]
        frames.append(partial_df)

    # Build a dataframe taking into account all the partial dataframes loaded
    loyers_df=pd.concat(frames,ignore_index=True)

    # Load the name of regions
    regions_df=pd.read_csv(os.path.join(root_path,"fichierscsv","reg2018.csv"),encoding='latin1',delimiter=',')
    regions_df=regions_df.rename(columns={'REGION,C,2':'REG','NCC,C,70':'NOM_REGION'})

    loyers_df=loyers_df.merge(regions_df,on=['REG'])

    # Select the columns that I need to build the dashboard with
    loyers_df=loyers_df.rename(columns={'loypredm2':'LOYER_EUROM2','LIBGEO':'NOM'})
    loyers_df=loyers_df[['NOM','INSEE','DEP','REG','LOYER_EUROM2','TYPE','YEAR','NOM_REGION']]
    # Transform the INSEE code for each row to a string in order to make the relation with a geojsonfile
    loyers_df['INSEE']=loyers_df['INSEE'].astype(str)
    loyers_df['INSEE']=loyers_df['INSEE'].str.zfill(5)

    return loyers_df

def load_geojson():
    '''Loads the geojson file to get the geometry of each commune'''

    # Read the geojson file
    with open(os.path.join(root_path,"geojsonfiles",'correspondance-code-insee-code-postal.geojson')) as f:
        geojsondata = json.load(f)

    return geojsondata