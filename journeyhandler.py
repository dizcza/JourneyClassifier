# -*- coding: utf-8 -*-

"""
 Contains all necessary methods to classify journey check-ins into the set of travellings.
 Can:
    1) figure out a home localization, which is considered to be a place (centroid)
            with more than 70% stay-ins in the same place on the world map;
    2) visualize data (check-ins) over the map;
    3) correlate each check-in (GPS: latitude and longitude) with a country;
"""

__author__ = 'dizcza'

from traceback import extract_stack
import numpy as np
from sklearn.cluster import KMeans
from matplotlib import pyplot as plt
import read_shapefile
from mpl_toolkits.basemap import Basemap

# Use read_shapefile.py to open the country.shp file from the current directory.
# 'country.shp' is downloaded from an open source http://www.diva-gis.org/Data
# See a documentation (in the read_shapefile.py) for more details.
COUNTRY_BOUNDARIES = read_shapefile.get_country_boundaries()


# Set a func to get info in case of throwing an error
def get_func_name():
    """ Returns called function name. """
    stack = extract_stack()
    called_func = stack[0][-1]
    func_name = called_func
    return func_name


is_a_number = lambda item: type(item).__name__ == 'float' or type(item).__name__ == 'int'
is_iterable = lambda item: type(item).__name__ == 'list' or type(item).__name__ == 'tuple'


def max_with_index(data):
    """
	 Returns a maximum item with the corresponding index in the data.
	"""
    try:
        if is_a_number(data):
            return data
        elif is_iterable(data):
            largest_val = max(data)
        else:
            raise Exception

        for item in range(len(data)):
            if data[item] == largest_val:
                return largest_val, item
    except:
        print "\n\tError in calling %s." % get_func_name()
        return 0, 0


def get_data_length(data):
    """
	 Returns a length of data and checks whether their lengths matches.
	 data is considered to be a list/tuple of EXACTLY 2 lists/tuples/numbers:
	 It means, that data must be as [vectorX, vectorY].
	"""
    if not is_iterable(data) or len(data) != 2:
        return 0

    data_length = 0

    if is_a_number(data[0]) and is_a_number(data[1]):
        data_length = 1
    elif is_iterable(data[0]) and is_iterable(data[1]):
        data_length = len(data[0])
        if len(data[0]) != len(data[1]):
            print "\tLength mismatch in %s. Took a minimum." % get_func_name()
            data_length = min([len(data[0]), len(data[1])])
    return data_length


def dist(point, boundary):
    """ Returns a distance between the point and a boundary. """
    distances = set([])
    for boundary_point in boundary:
        delta_sq = 0
        for i in range(2):
            delta_sq += (point[i] - boundary_point[i]) ** 2
        distances.add(delta_sq ** 0.5)
    return distances


def inside_polygon(x, y, poly):
    """ Checks whether point (x,y) lies inside the polygon or not. """
    num_of_sides = len(poly)

    inside = False

    if num_of_sides < 3:
        print "\nError in processing %s: input data must be a list/tuple with 2 lists/tuples inside. " \
              "Each of them must contain at least 3 items (points) to create a polygon." % get_func_name()
        return False

    try:
        p1x, p1y = poly[0]
        for i in range(num_of_sides + 1):
            p2x, p2y = poly[i % num_of_sides]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
    except:
        print "\n\t(!)%s: Invalid data input." % get_func_name()
    finally:
        return inside


def find_country(lat, lon, dispersion=0):
    """
        Classify a country by check-in coord (lat, lon).
        dispersion - how far is (lat, lon) from the country boundary (in minutes).
    """
    for country_name, country in COUNTRY_BOUNDARIES.iteritems():    # Loop over all country box boundaries
        if inside_polygon(lat, lon, country["polybox"]):            # if it is in the country box border
            for each_part in country["boundary"]:                   # Loop through each adm territory boundary
                # if we turn on the dispersion around the map:
                if dispersion and min(dist([lat,lon], zip(each_part[0], each_part[1]))) < dispersion:
                    return country_name
                # otherwise, do an accurate search and check whether it is in a current country boundary
                elif inside_polygon(lat, lon, zip(each_part[0], each_part[1])):
                    # we found it!
                    return country_name


def figure_out_home(degrees_data):
    """
	 Returns a home location in degrees.
	 Home is considered as a localization with >70.0% that pertains
		to the same place during taken observations.
	 'BOUNDARIES' contains information about world countries BOUNDARIES.
	"""
    print "Finding a home location..."
    data_length = get_data_length(degrees_data)
    if data_length == 0:
        print "\n\t(!)%s: Invalid data input: not enough size of data." % get_func_name()
        return [0, 0], ""

    data_array = np.array([0., ] * 2 * data_length).reshape(data_length, 2)
    data_array[:, 0] = np.array(degrees_data[0])
    data_array[:, 1] = np.array(degrees_data[1])

    threshold = 0.7
    num_of_clusters = 2
    near_home = 1.0

    # return [37.24, -122.01], 'USA'

    # (!) The loop below is executed at least one times.
    while near_home > threshold:
        # Use k-means algorithm with more numbers of clusters.
        km_deep = KMeans(n_clusters=num_of_clusters)
        km_deep.fit(data_array)

        # Set clusters' labels each sample in data_array belongs to.
        labels = km_deep.predict(data_array)

        # Compute size for each clustering data.
        clsize = [sum(labels == label) for label in range(num_of_clusters)]

        # Compute stay-ins as near_home and corresponding home label.
        stayins, home_label = max_with_index(clsize)
        near_home = stayins / float(data_length)

        # Find home location.
        homeloc = np.around(km_deep.cluster_centers_[home_label], decimals=2)

        # Specify home localization by increasing numbers of clusters.
        num_of_clusters += 1

    homeloc = homeloc.tolist()

    # Find a native country... and return it
    return homeloc, find_country(homeloc[0], homeloc[1])


def setzones(data):
    """
	 Get a country name for each check-in in data.
	 Returns the result as a list of countries names.
	"""
    data_length = get_data_length(data)
    journey_zones = ['' for dummy_checkin in range(data_length)]

    if data_length == 0:
        print "\n\t(!) %s: Invalid data input: not enough size of data." % get_func_name()
        return journey_zones

    for checkin in range(data_length):
        latitude = data[0][checkin]
        longitude = data[1][checkin]

        dispersion = 0      # Firstly, we try to classify data without any dispersion on it.
        while True:         # do it unless we classify the check-in
            country_name = find_country(latitude, longitude, dispersion)
            if country_name:                                # if we found
                journey_zones[checkin] = country_name       # Store it in journey_zones
                if dispersion:          # if we used dispersion to classify the current check-in
                    print "#%d: (%g, %g) is out from %s with dispersion = %g'" % \
                          (checkin, latitude, longitude, country_name, dispersion)
                else:
                    # if we found a country for the (lat, lon) with no dispersion (accurate search)
                    print "#%d: (%g, %g) %s " % (checkin, latitude, longitude, country_name)
                break
            else:
                # if some GPS-point failed to classify itself, sprawl each country boundary by 1 minute
                dispersion += 1

    # Verify the results.
    mismatches = journey_zones.count('') + journey_zones.count(None)
    if mismatches:
        print "# of classifier mismatches in journey zones after all: %d" % mismatches
    else:
        print "All check-ins have found their geographical country."

    return journey_zones


def visualize_data(lat, lon, home=None, quality='l'):
    """
        Visualize the data all over the world.
        home: home localization (if it's turned on)
        quality: map resolution of boundary database.
                 Can be c (crude), l (low), i (intermediate), h (high), f (full) or None.
                 Set to low ('l').
    """
    # Custom adjust of the subplots
    plt.subplots_adjust(left=0.05,right=0.95,top=0.90,bottom=0.05,wspace=0.15,hspace=0.05)

    # Make a map for the whole world
    m = Basemap(resolution=quality,projection='merc', llcrnrlat=-65.0,urcrnrlat=85.0,llcrnrlon=-170.0,urcrnrlon=170.0)
    m.drawcountries(linewidth=0.7)
    m.drawcoastlines(linewidth=0.7)
    m.fillcontinents(color='coral',lake_color='aqua')

    m.drawparallels(np.arange(-90.0, 91.0, 30.), labels=[False, True, True, False])
    m.drawmeridians(np.arange(0.0, 361.0, 60.), labels=[True, False, False, True])
    m.drawmapboundary(fill_color='aqua')

    xpt, ypt = m(lon, lat)      # convert to map projection coords.
    m.plot(xpt, ypt, 'bo')      # plot a blue dot for each check-in

    if home:
        xpt_home, ypt_home = m(home[1], home[0])
        plt.plot(xpt_home, ypt_home, 'ro', color='yellow', alpha=1.0, marker='$\star$', markersize=20, label="home")
        plt.text(0, 0, 'Home location (plotted as a star): (%.2f,%.2f)'%(home[0],home[1]), size=16, color=(0.8,0.8,0))
    plt.title("Check-ins visualization")

    plt.show()
