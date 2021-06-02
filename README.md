# Coffee-Shop-Location-Predictor
How can one predict a location for a coffee shop in Vancouver that is near a transit station, and has no Starbucks near it? The crime concentration should also be low in this area, and this program should be implemented in Python. We explore through this article
# Steps Required
1. Get all crime history of past two years
2. Get locations of all transit stations and starbucks in Vancouver
3. Check all the transit stations that do not have any starbucks near them
4. Get all crimes near the filtered transit stations
5. Create a grid of all possible coordinates around the transit station
6. Check crime around each created coordinate and display the top 5 locations.
# Data Sources
We can get crime history for the past 14 years in Vancouver from [https://www.kaggle.com/wosaku/crime-in-vancouver]. This data is in raw crime.csv format, so we have to process it and filter out useless data. We then write this processed information on the crime_processed.csv file.
Note: There are 530,653 records of crime in this file
In this program, we will just use the type and coordinate of the crime. There are many crime types, but we have classified them into three major categories namely;
Theft, Break and Enter and Mischief. 
These all crimes can be plotted on Graph as displayed below.
# Data Analysis
All the data accumulated is divided on the basis of the following parameters: 
1. Getting crime history
2. Getting Locations of all Rapid Transit Stations
3. Getting Locations of all Starbucks
4. Transit Stations with no Starbucks
5. Crime near Transit Stations
6. Crime near located Transit Stations
# Conclusion
After analyzing the data, we found six coordinates of best locations that have passed through all the constraints. 
# How Can MindTrades help? 
MindTrades Consulting Services, a leading marketing agency provides in-depth analysis and insights for the global IT sector including leading data integration brands such as Diyotta. From Cloud Migration, Big Data, Digital Transformation, Agile Deliver, Cyber Security, to Analytics- Mind trades provides published breakthrough ideas, and prompt content delivery. For more information, check [mindtrades.com].

