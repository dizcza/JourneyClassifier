# -*- coding: utf-8 -*-

"""
    This file is to read a shapefile from http://biogeo.ucdavis.edu/data/world/countries_shp.zip
    (see more on http://www.diva-gis.org/Data) and store its values into a nested dic, formatted as:
    country_data = {
        "country_name" : {
            "boundary"     : [[lat1, lon1], [lat2, lon2], ..., [lat_N, lon_N]],
            "bbox"         : (min_lat, max_lat, min_lon, max_lon),
            "polybox"      : <Polygon of a bbox: tuple of 4 points>
            "num_of_parts" : N
        },
        ...
    }
    There should be 264 different countries/territories in the COUNTRY_BOUNDARIES
    N (num_of_parts) is a quantity of administrative zones in the particular country.
    Each country/territory has at least 1 of those parts -- its boundary (f.e., small islands).
    For more info go to https://github.com/dizcza/JourneyClassifier
"""

import random
from matplotlib import pyplot as plt
from traceback import extract_stack
import fiona

unwrapped_boundary = []
country_data = {}


def get_func_name():
    """ Returns called function name. """
    stack = extract_stack()
    called_func = stack[0][-1]
    func_name = called_func
    return func_name


is_iterable = lambda item: type(item).__name__ == 'list' or type(item).__name__ == 'tuple'


def unwrap(mylist):
    """
	   Unwrap data (unless reach the list with tuples inside) into
	   the pairs [latitudes, longitudes]. Each pair represents
	   administrative territory pertain to the country or the whole its boundary.
	"""
    global unwrapped_boundary
    while is_iterable(mylist) and len(mylist) == 1:
        mylist = mylist[0]
    for list_item in range(len(mylist)):
        if type(mylist[list_item]).__name__ == 'list':
            # dive more deeply to reach the tuples
            unwrap(mylist[list_item])
        else:
            # we are in a boundary list with tuples
            # add me! zip me!
            lon, lat = zip(*mylist)
            unwrapped_boundary.append([lat, lon])
            break


def plot_the_country(country_name):
    """
        Plots the country by its name.
        It's an additional function, provided to you to see the country boundary.
    """
    boundary_data = country_data[country_name]["boundary"]
    boundary_color = []
    for rgb in range(3):
        boundary_color.append(random.randrange(100) / 100.0)

    for each_part in boundary_data:
        plt.plot(each_part[1], each_part[0], color=boundary_color)


def get_bbox(boundary_data):
    """ Evaluate a boundary box data for the current country. """
    lat = []
    lon = []
    for each_part in boundary_data:
        lat += each_part[0]
        lon += each_part[1]
    bbox = min(lat), max(lat), min(lon), max(lon)
    polybox = ((bbox[0], bbox[2]), (bbox[1], bbox[2]), (bbox[1], bbox[3]), (bbox[0], bbox[3]))

    return bbox, polybox


def open_shapefile(shpfile_name='countries.shp'):
    """ Reads a shapefile and store the data in country_data dic. """
    global unwrapped_boundary, country_data
    #initialize_data()

    shpfile = fiona.open(shpfile_name, mode='r')
    print "Shapefile %s is successfully opened." % shpfile_name

    for country in shpfile:
        # Clear the list of boundaries after previous calling the func unwrap(coordinates)
        unwrapped_boundary = []

        # Get some info from a shapefile
        country_name = country['properties']['NAME']
        coordinates = country['geometry']['coordinates']

        # fix some issues connected to Brunei (a bug)
        if country_name == "Baker Island" and country['properties']['COUNTRY'] == "Brunei":
            country_name = "Brunei"

        # Unwrap a tricky list of boundaries into a pretty one.
        unwrap(coordinates)

        # Evaluate boundary box in two ways (see the doc for this func)
        bbox, polybox = get_bbox(unwrapped_boundary)

        # Add the result in a dic
        country_data[country_name] = {
            "bbox": bbox,
            "polybox": polybox,
            "boundary": unwrapped_boundary,
            "num_of_parts": len(unwrapped_boundary)
        }

    shpfile.close()


def get_country_boundaries():
    """ Used in journeyhandler.py to read the data from the shapefile. """
    open_shapefile()
    return country_data

# Test data if you want to.
if __name__ == "__main__":
    open_shapefile()
    # Plots the boundary for Ukraine.
    plot_the_country("Ukraine")
    plt.show()
