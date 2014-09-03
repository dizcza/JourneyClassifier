JourneyClassifier
=================

    Visualize and classify your GPS shots

This project uses GPS points (check-ins) to classify them into groups by the same year and the same country. You can also visualize all your check-ins on the world map.
The input data from GPS should be formatted as 
    <p>UniqueID    UnixTime    Latitude    Longitude</p>
and stored in “checkins.csv”.

The output data (“checkins_upd.csv”) contains additional right column that represents group ID, classified by the same year and the same country in.
In case of being at home at least >70% of all time (the input observation should be taken during one or more years), more than half of GPS observations are found in the country, where the person live and work. Thus, you can figure out the home localization (shown as a yellow star on the map).
All country boundaries have been taken from the <a href="http://www.diva-gis.org/Data">Free Spatial Data</a>. You should <a href="http://biogeo.ucdavis.edu/data/world/countries_shp.zip">download global country boundaries</a> and unzip the “countries.shp” in the project directory or use provided one from here.

You must have Python2.7.x installed on your computer with the obligatory packages below to run the project. It was tested on Python2.7.8.
<p>Obligatory Python packages:</p>
<ul>
    <li>matplotlib (with pyparsing, dateutil, pytz and six)</li>
	<li>matplotlib basemap toolkit to visualize data</li>
	<li>numpy</li>
	<li>scipy</li>
	<li>fiona (with GDAL) to read a shapefile and get country boundaries.
</ul>
