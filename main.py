# -*- coding: utf-8 -*-
__author__ = 'dizcza'

# THIS IS A FILE TO TUN THE PROJECT JourneyClassifier
# For more info go to https://github.com/dizcza/JourneyClassifier
import time, csv
from datetime import datetime

# run a timer and import data from journeyhandler.py
time_start = time.time()
import journeyhandler
from journeyhandler import COUNTRY_BOUNDARIES as BOUNDARIES



def classify(years, journey_zones):
    """
	 Classify data into group of journeys with the same year and the same zone (country).
	 All countries borders must be stored in 'borders'.
	"""
    try:
        data_length = journeyhandler.get_data_length([years, journey_zones])
        if data_length == 0:
            raise Exception
    except:
        print "\n\t(!) %s: Invalid data input.\n" % journeyhandler.get_func_name()
        return

    group_list = [0 for dummy_checkin in range(data_length)]

    # Set first unique IDs for each set of journeys, taken during one year.
    ids = 1
    first_year = min(years)
    last_year = max(years)
    for year in range(last_year, first_year - 1, -1):
        for country_name in BOUNDARIES.iterkeys():
            # If data sample with current zone in current year is found, checker 'isfound' becomes True.
            isfound = False
            for checkin in range(data_length - 1, -1, -1):
                # Loop from the end to the beginning of data samples for each year and possible localization zone.
                if journey_zones[checkin] != 'usa' and journey_zones[checkin] == country_name and years[
                    checkin] == year:
                    group_list[checkin] = ids
                    isfound = True
            if isfound:
                # If matching is found on the last steps, look for another zone
                # in the current year. Thus, we must change the ID to the new
                # travelling group and reset found matches.
                ids += 1

    print "OUTPUT: Have found %d groups of travellings." % max(group_list)
    return group_list


print "\n" + "*" * 20 + " Begin to operate data. " + "*" * 20

csvfile = open('checkins.csv', 'r')
data = csv.reader(csvfile, delimiter=',')

ID = []
timeunix = []
years = []
latitude = []
longitude = []

for checkin, row in enumerate(data):
    ID.append(str(row[0]))
    timeunix.append(int(row[1]))
    year = int(datetime.fromtimestamp(timeunix[-1]).strftime('%Y'))
    years.append(year)
    latitude.append(float(row[2]))
    longitude.append(float(row[3]))
csvfile.close()

# Make data immutable.
latitude = tuple(latitude)
longitude = tuple(longitude)
NUM_OF_CHECKINS = len(ID)

# Finding home location.
homeloc, native_country_name = journeyhandler.figure_out_home([latitude, longitude])
print "Home location: %s \t" % native_country_name, homeloc

# Visualize the data, if you want.
journeyhandler.visualize_data(latitude, longitude, home=homeloc)

# Journey zones classifier.
journey_zones = journeyhandler.setzones([latitude, longitude])

# Classify data into set of journeys with unique IDs
group_list = classify(years, journey_zones)

# Wrap data into 'checkins_upd.csv'
try:
    csvfile = open('checkins_upd.csv', 'wb')
    outputfile = csv.writer(csvfile, delimiter=',')
    for checkin in range(NUM_OF_CHECKINS):
        outputfile.writerow(
            [ID[checkin], timeunix[checkin], latitude[checkin], longitude[checkin], group_list[checkin]])
except:
    print "\nOUTPUT ERROR: Cannot write the results into the output file.\n"
finally:
    csvfile.close()

time_end = time.time()
print "*" * 25 + " THE END. " + "*" * 25 + "\n"
print "Execution time: %g sec." % (time_end - time_start)
