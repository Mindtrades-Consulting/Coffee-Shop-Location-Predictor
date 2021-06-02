import os.path
import csv
from math import sqrt

import geopandas as gpd
import matplotlib.pyplot as plt
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from shapely.geometry import Point, Polygon
import time


# Function to Check whether a file exists in data subdirectory or not.
# Parameter : String, Name of file : Boolean, Is in source directory or not
# Return : Boolean, True/False
def isFile(name, source=False):
    if source:
        path = os.getcwd() + "\\" + name
    else:
        path = os.getcwd() + "\data\\" + name
    return os.path.isfile(path)


# Function to Read from Crime.csv file, process (Filter) it and write on Crime_processed.csv file
# Parameter : None
# Return : None
def processCrimeCSV():
    path = os.getcwd() + "\data\\crime.csv"
    with open(path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        line_count = 0
        with open("data\crime_processed.csv", 'w') as file:
            writer = csv.writer(file)
            for row in csv_reader:
                if line_count == 0:
                    writer.writerow(["TYPE", "TIME", "HUNDRED_BLOCK", "NEIGHBOURHOOD", "X", "Y", "Latitude", "Longitude"])
                line_count += 1
                if row["Latitude"] == "0" or row["Longitude"] == "0":
                    continue
                if row['TYPE'].startswith("Vehicle Collision"):
                    continue
                if float(row['Longitude']) < -123.21 or float(row['Longitude']) > -123:
                    continue
                if float(row['Latitude']) < 49 or float(row['Latitude']) > 50:
                    continue
                time = row["HOUR"] + ":" + row["MINUTE"]
                processed_row = [f'{row["TYPE"]}', f'{time}', f'{row["HUNDRED_BLOCK"]}', f'{row["NEIGHBOURHOOD"]}', f'{row["X"]}', f'{row["Y"]}', f'{row["Latitude"]}', f'{row["Longitude"]}']
                writer.writerow(processed_row)
        print(f'Processed {line_count} lines.')


# Function to Parse Starbucks data location wise from given url and store in a text file
# Parameter : None
# Return : None
def getStarbucksData():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.set_page_load_timeout(20)
    driver.get("https://www.starbucks.ca/store-locator?map=49.281601,-123.110406,12z&place=vancouver,%20bc")
    time.sleep(5)
    parsed_raw_data = driver.find_elements_by_css_selector("section[data-e2e='locationCardList']")
    parsed_data = str(parsed_raw_data[0].text).split("\n")
    data = "stores: " + str(parsed_data[0])
    path = os.getcwd() + "\data\\starBucks.txt"
    i = 1
    while True:
        if i > len(parsed_data) - 1:
            break
        closing_time = parsed_data[i + 2].split("·")
        data += "\nname : " + str(parsed_data[i])
        data += "\naddress : " + str(parsed_data[i + 1])
        data += "\nclosing time : " + str(closing_time[1])
        if parsed_data[i + 3].startswith("Mobile"):
            data += "\nmobile order : " + str(parsed_data[i + 3])
            i += 5
        elif parsed_data[i + 3].startswith("In"):
            data += "\nmobile order : NaN"
            i += 4
        elif parsed_data[i + 3] == "Store closed":
            print("Some Stores are Closed! Using Default Values (Parsed).")
            # The purpose of this is that because some stores are closed
            # the further processes depending on them will not be precise
            data = '''49.232458314238364 -123.02407272314883
                49.23227574158398 -123.03308345969475
                49.23107782308495 -123.00368204688475
                49.22616917166424 -123.00363326822566
                49.219575765881146 -123.04033890706297
                49.22497791757441 -123.05275724554062
                49.257805586361016 -123.03101811248608
                49.2334792377984 -123.06610281341919
                49.205980666411776 -123.02991634624101
                49.25947353644168 -123.04426901244054
                49.26241116241549 -123.06838508963239
                49.22477179635515 -123.09022096827186
                49.27962806708104 -123.04596762071007
                49.270485800458744 -123.08743356655712
                49.26305703714515 -123.10028534876245
                49.20967021647956 -123.10694569155054
                49.23375787402132 -123.11571919062663
                49.25303642066152 -123.11591575811961
                49.2686230594611 -123.10267836661832
                49.20883819416455 -123.11656949158993
                49.26336767536111 -123.11379344408262
                49.243845501808536 -123.1256413357224
                49.279164928180755 -123.10690296622467
                49.27369303388979 -123.12170940286242
                '''
            with open(path, "w") as file:
                file.write(data)
            return
        data += "\nin store" + str(parsed_data[i + 4])

    with open(path, "w") as file:
        file.write(data)


# Function to Plot a graph based on coordinates of crime data
# Displays Different Colors for Different Graphs
# Parameter : None
# Return : None
def crimeDataGraph():
    geometry = crimeDataAnalysis()
    geo_df_other_theft = gpd.GeoDataFrame(geometry=geometry[0])
    geo_df_enter_residential = gpd.GeoDataFrame(geometry=geometry[1])
    geo_df_mischief = gpd.GeoDataFrame(geometry=geometry[2])
    boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
    street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
    fig, ax = plt.subplots(1, figsize=(20, 11))
    boundary_map.plot(ax=ax, color='black')
    street_map.plot(ax=ax, color='white', alpha=0.4)
    geo_df_other_theft.plot(ax=ax, markersize=0.1, color='red', marker="o", label="Other Theft")
    geo_df_enter_residential.plot(ax=ax, markersize=0.1, color='orange', marker="o", label="Break&Enter Residential")
    geo_df_mischief.plot(ax=ax, markersize=0.1, color='green', marker="o", label="Mischief")
    plt.title('Vancouver - BC\nAll Crime Locations', loc='left', fontsize=20)
    ax.axis('off')
    plt.savefig('All Crimes.jpg', dpi=1000)
    plt.show()


# Function to Analyze the crime data create a list of lists of all points based on Longitudes and Latitudes
# Parameter : None
# Return : List of lists, List of Points (for plotting on graphs)
# Return Format : [[OtherTheft], [BreakandEnterResidentialOther], [Mischief], ...]
def crimeDataAnalysis():
    geometry = []
    OtherTheft = []
    BreakandEnterResidentialOther = []
    Mischief = []
    path = os.getcwd() + "\data\\crime_processed.csv"
    with open(path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            xy = (float(row['Longitude']), float(row['Latitude']))
            if row['TYPE'] == "Other Theft":
                OtherTheft.append(Point(xy))
            if row['TYPE'] == "Break and Enter Residential/Other":
                BreakandEnterResidentialOther.append(Point(xy))
            if row['TYPE'] == "Mischief":
                Mischief.append(Point(xy))
            if row['TYPE'] == "Break and Enter Commercial":
                BreakandEnterResidentialOther.append(Point(xy))
            if row['TYPE'] == "Theft from Vehicle":
                OtherTheft.append(Point(xy))
            if row['TYPE'] == "Theft of Vehicle":
                OtherTheft.append(Point(xy))
            if row['TYPE'] == "Theft of Bicycle":
                OtherTheft.append(Point(xy))
        geometry.append(OtherTheft)
        geometry.append(BreakandEnterResidentialOther)
        geometry.append(Mischief)
    return geometry


# Function to Plot a graph based on Transit data shape file
# Parameter : None
# Return : None
def rapidTransitGraph():
    boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
    street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
    points_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\rapid-transit-stations.shp')  # Transit Data
    fig, ax = plt.subplots(1, figsize=(20, 11))
    boundary_map.plot(ax=ax, color='black')
    street_map.plot(ax=ax, color='white', alpha=0.4)
    points_map.plot(ax=ax, color='red')
    plt.title('Vancouver - BC\nTransit Station Locations', loc='left', fontsize=20)
    ax.axis('off')
    plt.savefig('Transit Locations.jpg', dpi=1000)
    plt.show()


# Gets Transit Stations Coordinates from 'rapid-transit-stations.csv'
# Creates a Polygon around each coordinate and checks if location of processed_crime is near Transit Station
# Writes these crimes in 'crime_located.csv' file
# Parameter : None
# Return : None
def getCrimeNearTransit():
    print("Checking Crime Locations against Transit Location areas\n'Note: This may take some time (approx. 5 minutes)")
    # Getting Coordinates of all Transit Stations
    coordinates = []
    path = os.getcwd() + "\data\\rapid-transit-stations.csv"
    with open(path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            line = str(row).split("[")
            line = line[2].split("]")
            line = line[0].split("'")
            longitude = float(line[0])
            latitude = float(line[2])
            data = {
                "longitude": longitude,
                "latitude": latitude
            }
            coordinates.append(data)
    OtherTheft = []
    BreakandEnterResidentialOther = []
    Mischief = []
    # Checking Crimes that are in those coordinates
    path = os.getcwd() + "\data\\crime_processed.csv"
    # 100 m = 0.00090 deg (Adjust radius accordingly)
    radius = 0.00360
    with open(path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            for coordinate in coordinates:
                coords = [(coordinate['longitude'] + radius, coordinate['latitude'] + radius),
                          (coordinate['longitude'] - radius, coordinate['latitude'] + radius),
                          (coordinate['longitude'] - radius, coordinate['latitude'] - radius),
                          (coordinate['longitude'] + radius, coordinate['latitude'] - radius)]
                point = Point(float(row['Longitude']), float(row['Latitude']))
                poly = Polygon(coords)
                if point.within(poly):
                    xy = (float(row['Longitude']), float(row['Latitude']))
                    if row['TYPE'] == "Other Theft":
                        OtherTheft.append(xy)   # Use point for Points instead of xy
                    elif row['TYPE'] == "Break and Enter Residential/Other":
                        BreakandEnterResidentialOther.append(xy)
                    elif row['TYPE'] == "Mischief":
                        Mischief.append(xy)
                    elif Point(xy) in OtherTheft or Point(xy) in BreakandEnterResidentialOther or Point(xy) in Mischief:
                        continue
    path = os.getcwd() + "\data\\crime_located.csv"
    with open(path, "w") as csv_file:
        csv_file.write('Other Theft\n')
        for item in OtherTheft:
            csv_file.write(str(item[0]) + "," + str(item[1]) + "\n")
        csv_file.write('Break and Enter Residential/Other\n')
        for item in BreakandEnterResidentialOther:
            csv_file.write(str(item[0]) + "," + str(item[1]) + "\n")
        csv_file.write('Mischief\n')
        for item in Mischief:
            csv_file.write(str(item[0]) + "," + str(item[1]) + "\n")
    print("Found Cases : ", (len(OtherTheft)+len(BreakandEnterResidentialOther)+len(Mischief)))


# Gets Located Crimes near Transit stations data from 'crime_located.csv' and Plots Graph
# Different Crimes are identified with different Colors
# Parameter : None
# Return : None
def crimeNearTransitGraph():
    OtherTheft = []
    BreakandEnterResidentialOther = []
    Mischief = []
    path = os.getcwd() + "\data\\crime_located.csv"
    current = ""
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if str(row[0]).startswith("Other Theft"):
                current = "OtherTheft"
                continue
            elif str(row[0]) == "Break and Enter Residential/Other":
                current = "BreakandEnterResidentialOther"
                continue
            elif str(row[0]) == "Mischief":
                current = "Mischief"
                continue
            xy = (float(row[0]), float(row[1]))
            if current == "OtherTheft":
                OtherTheft.append(Point(xy))
            elif current == "BreakandEnterResidentialOther":
                BreakandEnterResidentialOther.append(Point(xy))
            elif current == "Mischief":
                Mischief.append(Point(xy))
    boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
    street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
    fig, ax = plt.subplots(1, figsize=(20, 11))
    geo_df_other_theft = gpd.GeoDataFrame(geometry=OtherTheft)
    geo_df_enter_residential = gpd.GeoDataFrame(geometry=BreakandEnterResidentialOther)
    geo_df_mischief = gpd.GeoDataFrame(geometry=Mischief)
    boundary_map.plot(ax=ax, color='black')
    street_map.plot(ax=ax, color='white', alpha=0.4)
    geo_df_other_theft.plot(ax=ax, markersize=0.1, color='red', marker="o", label="Other Theft")
    geo_df_enter_residential.plot(ax=ax, markersize=0.1, color='orange', marker="o", label="Break & Enter Residential")
    geo_df_mischief.plot(ax=ax, markersize=0.1, color='green', marker="o", label="Mischief")
    plt.title('Vancouver - BC\nCrimes Near Transit Locations', loc='left', fontsize=20)
    ax.axis('off')
    plt.savefig('Crimes Near Transit.jpg', dpi=1000)
    plt.show()


# Gets Transit stations location data from 'rapid-transit-stations.csv' and creates an area of given radius around it
# Gets Starbucks Location from '' and checks if they are within that area. If they are, they are plotted on a Graph
# Parameter : None
# Return : None
def starbucksTransitGraph():
    if not isFile("starBucks_located.txt"):
        T_coordinates = []  # Transit Station Coordinates
        S_coordinates = []  # Starbucks Coordinates
        # 100 m = 0.00090 deg (Adjust radius accordingly)
        radius = 0.0090
        path = os.getcwd() + "\data\\rapid-transit-stations.csv"
        with open(path, 'r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                line = str(row).split("[")
                line = line[2].split("]")
                line = line[0].split("'")
                longitude = float(line[0])
                latitude = float(line[2])
                data = {
                    "longitude": longitude,
                    "latitude": latitude
                }
                T_coordinates.append(data)
        path = os.getcwd() + "\data\\transit-stations-locations.txt"
        with open(path, 'w') as file:
            for coords in T_coordinates:
                file.write(str(coords) + "\n")
        path = os.getcwd() + "\data\\starBucks.txt"
        with open(path, "r") as file:
            data = file.read()
            temp = data.split()
        i = 0
        while True:
            if i == len(temp):
                break
            temp2 = (float(temp[i]), float(temp[i + 1]))
            S_coordinates.append(temp2)
            i += 2
        temp = []
        coordinates = []
        for T_coor in T_coordinates:
            coords = [(T_coor['longitude'] + radius, T_coor['latitude'] + radius),
                      (T_coor['longitude'] - radius, T_coor['latitude'] + radius),
                      (T_coor['longitude'] - radius, T_coor['latitude'] - radius),
                      (T_coor['longitude'] + radius, T_coor['latitude'] - radius)]
            poly = Polygon(coords)
            for S_coor in S_coordinates:
                point = Point(float(S_coor[1]), float(S_coor[0]))
                if point.within(poly):
                    xy = (float(S_coor[1]), float(S_coor[0]))
                    temp.append(xy)
        path = os.getcwd() + "\data\\starBucks_located.txt"
        with open(path, "w") as file:
            for cords in temp:
                file.write(str(cords) + "\n")
        for tc in temp:
            coordinates.append(Point(tc))
    else:
        coordinates = []
        path = os.getcwd() + "\data\\starBucks_located.txt"
        with open(path, "r") as file:
            data = file.read().split()
            i = 0
            for cords in range(len(data)):
                if i%2 == 0:
                    temp = data[cords].split(",")
                    temp = temp[0].split("(")
                    x = float(temp[1])
                else:
                    temp = data[cords].split(")")
                    y = float(temp[0])
                    xy = (x, y)
                    coordinates.append(Point(xy))
                i += 1
    boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
    street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
    fig, ax = plt.subplots(1, figsize=(20, 11))
    geo_df_starbucks_location = gpd.GeoDataFrame(geometry=coordinates)
    boundary_map.plot(ax=ax, color='black')
    street_map.plot(ax=ax, color='white', alpha=0.4)
    geo_df_starbucks_location.plot(ax=ax, markersize=30, color='yellow', marker="o", label="StarBucks")
    plt.title('Vancouver - BC\nStarBucks Near Transit Locations', loc='left', fontsize=20)
    ax.axis('off')
    plt.savefig('Starbucks Near Transit.jpg', dpi=1000)
    plt.show()


# Get crime and starbuck locations near transit file checks all Transit locations where any starbuck is not within 2km.
# Parameter : None
# Return : None
def transitWithoutStarbuckGraph():
    starbucks_coordinates = []              # StarBucks Coordinates near to Transit Location
    path = os.getcwd() + "\data\\starBucks_located.txt"
    with open(path, "r") as file:
        data = file.read().split()
        i = 0
        x = ""
        for cords in range(len(data)):
            if i % 2 == 0:
                temp = data[cords].split(",")
                temp = temp[0].split("(")
                x = float(temp[1])
            else:
                temp = data[cords].split(")")
                y = float(temp[0])
                xy = (x, y)
                starbucks_coordinates.append(xy)
            i += 1
    crime_coordinates = []              # Crime cases Coordinates near to Transit Location
    path = os.getcwd() + "\data\\crime_located.csv"
    with open(path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        for row in csv_reader:
            if row[0] == "Other Theft":
                continue
            elif row[0] == "Break and Enter Residential/Other":
                continue
            elif row[0] == "Mischief":
                continue
            xy = (float(row[0]), float(row[1]))
            crime_coordinates.append(xy)
    path = os.getcwd() + "\data\\transit-stations-locations.txt"        # Transit Station Coordinates
    transit_coordinates = []
    with open(path, "r") as file:
        data = file.read()
        lines = data.split("\n")
        for line in lines:
            if not line == "":
                temp = line.split(",")
                temp2 = temp[0].split(":")
                temp3 = temp[1].split(":")
                xy = (float(temp2[1]), float(temp3[1][:(len(temp3[1]) - 1)]))
                transit_coordinates.append(xy)
    # 100 m = 0.00090 deg (Adjust radius accordingly)
    found_transit = []
    radius = 0.00900
    count = 0
    plg = []
    for s_coord in starbucks_coordinates:
        coords = [(s_coord[0] + radius, s_coord[1] + radius),
                  (s_coord[0] - radius, s_coord[1] + radius),
                  (s_coord[0] - radius, s_coord[1] - radius),
                  (s_coord[0] + radius, s_coord[1] - radius)]
        poly = Polygon(coords)
        plg.append(poly)
    for t_coord in transit_coordinates:
        point = Point(t_coord[0], t_coord[1])
        for poly in plg:
            if point.within(poly):
                count += 1
        if count == 0:
            found_transit.append(point)
        count = 0
    path = os.getcwd() + "\data\\transit-no-starbucks.txt"  # Transit Station Coordinates
    with open(path, "w") as file:
        for location in found_transit:
            file.write(str(location.x) + "," + str(location.y) + "\n")
    boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
    street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
    fig, ax = plt.subplots(1, figsize=(20, 11))
    geo_df_found = gpd.GeoDataFrame(geometry=found_transit)
    boundary_map.plot(ax=ax, color='black')
    street_map.plot(ax=ax, color='white', alpha=0.4)
    geo_df_found.plot(ax=ax, markersize=30, color='red', marker="o", label="StarBucks")
    plt.title('Vancouver - BC\nTransit Station with no Starbucks Near', loc='left', fontsize=20)
    ax.axis('off')
    plt.savefig('Transit with no Starbucks Near.jpg', dpi=1000)
    plt.show()


# Check crime data of 'transit-no-starbucks.txt' areas. Check with respect to located Transits
# Generate a grid of coordinates around each transit and check the crimes near each possible coordinate
# Predict the Best Possible Locations and append them in order of nearest to transit in a list and write on file
# Parameter : None
# Return : None
def predictBestLocations():
    transit_coordinates = []
    path = os.getcwd() + "\data\\transit-no-starbucks.txt"
    with open(path, "r") as file:
        all = file.read()
        data = all.split("\n")
        for line in data:
            if not line == "":
                l = line.split(",")
                transit_coordinates.append((float(l[0]), float(l[1])))
    if not isFile("crimes near located transits.txt"):
        theft = []
        breakingAndEntering = []
        mischief = []
        current = ""
        path = os.getcwd() + "\data\\crime_located.csv"
        with open(path, 'r') as csv_file:
            csv_reader = csv.reader(csv_file)
            for row in csv_reader:
                if str(row[0]).startswith("Other Theft"):
                    current = "theft"
                    continue
                elif str(row[0]) == "Break and Enter Residential/Other":
                    current = "breakenter"
                    continue
                elif str(row[0]) == "Mischief":
                    current = "mischief"
                    continue
                xy = (float(row[0]), float(row[1]))
                if current == "theft":
                    theft.append(xy)
                elif current == "breakenter":
                    breakingAndEntering.append(xy)
                elif current == "mischief":
                    mischief.append(xy)
        # 1 km = 0.0090 deg (Adjust radius accordingly)
        radius = 0.0090
        plg = []
        for coordinate in transit_coordinates:
            coords = [(coordinate[0] + radius, coordinate[1] + radius),
                      (coordinate[0] - radius, coordinate[1] + radius),
                      (coordinate[0] - radius, coordinate[1] - radius),
                      (coordinate[0] + radius, coordinate[1] - radius)]
            poly = Polygon(coords)
            plg.append(poly)
        p_theft = []
        for x in theft:
            if x not in p_theft:
                p_theft.append(x)
        p_mischief = []
        for x in mischief:
            if x not in p_theft:
                p_mischief.append(x)
        p_break = []
        for x in breakingAndEntering:
            if x not in p_theft:
                p_break.append(x)
        t = []
        m = []
        b = []
        for location in p_theft:
            for poly in plg:
                point = Point((location[0], location[1]))
                if point.within(poly):
                    if point not in t:
                        t.append((location[0], location[1]))
                    break
        for location in p_mischief:
            for poly in plg:
                point = Point(location[0], location[1])
                if point.within(poly):
                    if point not in m:
                        m.append((location[0], location[1]))
                    break
        for location in p_break:
            for poly in plg:
                point = Point(location[0], location[1])
                if point.within(poly):
                    if point not in b:
                        b.append((location[0], location[1]))
                    break
        theft = []
        breakingAndEntering = []
        mischief = []
        for xy in t:
            theft.append(Point(xy))
        for xy in b:
            breakingAndEntering.append(Point(xy))
        for xy in m:
            mischief.append(Point(xy))
        path = os.getcwd() + "\data\\crimes near located transits.txt"
        with open(path, "w") as file:
            file.write("Theft\n")
            for xy in t:
                file.write(str(xy) + "\n")
            file.write("Break\n")
            for xy in b:
                file.write(str(xy) + "\n")
            file.write("Mischief\n")
            for xy in m:
                file.write(str(xy) + "\n")
        quit()
    else:
        theft = []
        breakingAndEntering = []
        mischief = []
        t = []
        m = []
        b = []
        path = os.getcwd() + "\data\\crimes near located transits.txt"
        with open(path, "r") as file:
            data = file.read()
            lines = data.split("\n")
            for line in lines:
                if line == "Theft":
                    current = "Theft"
                elif line == "Break":
                    current = "Break"
                elif line == "Mischief":
                    current = "Mischief"
                else:
                    if current == "Theft":
                        if not line == " ":
                            li = line.split(",")
                            x = float(li[0][1:])
                            y = float(li[1][:(len(li[1]) -1)])
                            t.append((x, y))
                    if current == "Break":
                        if not line == " ":
                            li = line.split(",")
                            x = float(li[0][1:])
                            y = float(li[1][:(len(li[1]) - 1)])
                            b.append((x, y))
                    if current == "Mischief":
                        if not line == " ":
                            li = line.split(",")
                            if len(li) == 1:
                                continue
                            x = float(li[0][1:])
                            y = float(li[1][:(len(li[1]) - 1)])
                            m.append((x, y))
        for xy in t:
            theft.append(Point(xy))
        for xy in b:
            breakingAndEntering.append(Point(xy))
        for xy in m:
            mischief.append(Point(xy))
    if not isFile("Crime Near Located Transit.jpg", True):
        boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
        street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
        fig, ax = plt.subplots(1, figsize=(20, 11))
        geo_df_theft = gpd.GeoDataFrame(geometry=theft)
        geo_df_break = gpd.GeoDataFrame(geometry=breakingAndEntering)
        geo_df_mischief = gpd.GeoDataFrame(geometry=mischief)
        boundary_map.plot(ax=ax, color='black')
        street_map.plot(ax=ax, color='white', alpha=0.4)
        geo_df_theft.plot(ax=ax, markersize=0.1, color='red', marker="o", label="StarBucks")
        geo_df_break.plot(ax=ax, markersize=0.1, color='orange', marker="o", label="StarBucks")
        geo_df_mischief.plot(ax=ax, markersize=0.1, color='green', marker="o", label="StarBucks")
        plt.title('Vancouver - BC\nCrime Near Located Transit Stations', loc='left', fontsize=20)
        ax.axis('off')
        plt.savefig('Crime Near Located Transit.jpg', dpi=1000)
        plt.show()
    all_coordinates = []
    path = os.getcwd() + "\data\\all possible locations.txt"
    if not isFile("all possible locations.txt"):
        all_coordinates = []
        # 49.24827221040713
        grid = 10
        radius = 0.005
        for c in transit_coordinates:
            i = c[0] - radius
            j = c[1] - radius
            for x in range(grid):
                for y in range(grid):
                    if i <= 2 * radius:
                        i += 0.001
                        all_coordinates.append((i, j))
                i = c[0] - radius
                j += 0.001
        for the in t:
            coords = [(the[0] + 0.0090, the[1] + 0.0090),
                      (the[0] - 0.0090, the[1] + 0.0090),
                      (the[0] - 0.0090, the[1] - 0.0090),
                      (the[0] + 0.0090, the[1] - 0.0090)]
            poly = Polygon(coords)
            # Theft removes 1km
            for c in all_coordinates:
                xy = Point(c[0], c[1])
                if xy.within(poly):
                    all_coordinates.remove(c)

        for the in b:
            coords = [(the[0] + 0.00180, the[1] + 0.00180),
                      (the[0] - 0.00180, the[1] + 0.00180),
                      (the[0] - 0.00180, the[1] - 0.00180),
                      (the[0] + 0.00180, the[1] - 0.00180)]
            poly = Polygon(coords)
            # Break and Enter removes 200m
            for c in all_coordinates:
                xy = (c[0], c[1])
                if Point(xy).within(poly):
                    all_coordinates.remove(c)
                    break

        for c in all_coordinates:
            coords = [(c[0] + 0.00180, c[1] + 0.00180),
                      (c[0] - 0.00180, c[1] + 0.00180),
                      (c[0] - 0.00180, c[1] - 0.00180),
                      (c[0] + 0.00180, c[1] - 0.00180)]
            poly = Polygon(coords)
            # Mischief removes 200m
            for the in m:
                xy = (the[0], the[1])
                if Point(xy).within(poly):
                    all_coordinates.remove(c)
                    break
        temp = []
        locations = []
        for c in all_coordinates:
            for t in transit_coordinates:
                distance = sqrt((c[0] - t[0]) ** 2 + (c[1] - t[1]) ** 2)
                temp.append(distance)
            locations.append((min(temp), (c[0], c[1])))
        locations.sort(key=lambda x1: x1[0])
        all_coordinates = []
        for c in locations:
            xy = c[1]
            all_coordinates.append((xy[0], xy[1]))
        with open(path, "w") as file:
            for x in all_coordinates:
                file.write(str(x[0]) + ", " + str(x[1]) + "\n")
    else:
        with open(path, "r") as file:
            data = file.read()
            lines = data.split("\n")
            for line in lines:
                row = line.split(",")
                if line == "":
                    continue
                all_coordinates.append((float(row[0]), float(row[1])))

    predicted_location = []
    for c in all_coordinates:
        print(c)
        predicted_location.append(Point((c[0], c[1])))
    boundary_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\local-area-boundary.shp')
    street_map = gpd.read_file(r'D:\Projects\Python\Upwork Project\data\public-streets.shp')
    fig, ax = plt.subplots(1, figsize=(20, 11))
    geo_df_predicted = gpd.GeoDataFrame(geometry=predicted_location)
    boundary_map.plot(ax=ax, color='black')
    street_map.plot(ax=ax, color='white', alpha=0.4)
    geo_df_predicted.plot(ax=ax, markersize=20, color='red', marker="o", label="StarBucks")
    plt.title('Vancouver - BC\nBest Locations for Coffee Shop', loc='left', fontsize=20)
    ax.axis('off')
    plt.savefig('Coffee Shop Location.jpg', dpi=1000)
    plt.show()

















