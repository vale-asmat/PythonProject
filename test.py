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
#print(filteredListOfFilesInFolderCSV)

for f in filteredListOfFilesInFolderCSV:
    for file in filteredListOfFilesInFolderCSV[f]:
        print(file)