from func import *


# This Checks if Processed Data is Present or not.
# If data is present, it continues
# Else, It Processes crime data. (If that file is not present It asks to download it)
if not isFile("crime_processed.csv"):
    if not isFile("crime.csv"):
        print("Download 'crime.csv' to continue.")
        quit()
    else:
        processCrimeCSV()


# This Checks if Starbucks data file is present or not
# If it is missing, It scrapes the given url and writes on file
if not isFile("starBucks.txt"):
    getStarbucksData()


# This Checks if Rapid Transit Stations shape file is present or not
# If it is missing, It asks to download it
if not isFile("rapid-transit-stations.shp"):
    print("Download 'rapid-transit-stations.shp' file to continue.")
    quit()


# This Checks if All Crimes Image file is present or not
# If it is missing, It plots the graph
if not isFile("All Crimes.jpg", True):
    crimeDataGraph()


# This Checks if Transit Station Locations Image file is present or not
# If it is missing, It plots the graph
if not isFile("Transit Locations.jpg", True):
    rapidTransitGraph()


# This Checks if Located Crime Coordinates file is present or not
# If it is missing, It Calculates and saves it
if not isFile("crime_located.csv"):
    getCrimeNearTransit()


# This Checks if Crime Near Transit Image file is present or not
# If it is missing, It plots the graph
if not isFile("Crimes Near Transit.jpg", True):
    crimeNearTransitGraph()


# This Checks if Star Bucks Locations Near Transit Locations Image file is present or not
# If it is missing, It plots the graph
if not isFile("Starbucks Near Transit.jpg", True):
    starbucksTransitGraph()


# This Checks if Star Bucks Locations Near Transit Locations Image file is present or not
# If it is missing, It plots the graph
if not isFile("Transit with no Starbucks Near.jpg", True):
    transitWithoutStarbuckGraph()


# This is a complex algorithm that predicts list of best possible location to open a coffee shop
# It is based on Transit Locations, Crime Near Transit Location, and Starbucks Near Transit Location
if not isFile("Coffee Shop Location.jpg", True):
    predictBestLocations()

