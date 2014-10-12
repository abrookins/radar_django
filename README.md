# README

This is a Django version of "radar," a site and API that I am continually
tinkering with to provide crime statistics for locations in Portland, Oregon.

This version uses ElasticSearch, geohash grids and median averages to compare
crime at the user's location to average crime across the city.

The comparison is done by aggregating city crime data by geohash cell, summing
by crime type for each cell (a bounding box), finding the median values for all
crime types across cells, and then later finding the cell the user's location
is in and comparing crime sums in that cell to the city averages.

## Installing

First, set up the Vagrant instance:

    $ vagrant up

Then, log in and make sure ElasticSearch is running:

    $ vagrant ssh
    $ sudo service elasticsearch start
    
Set up the index and data (still assuming you're in the Vagrant machine):

    $ source ~/radar/bin/activate
    $ cd /vagrant
    $ cd crime_stats
    $ python create_index.py
    $ python load_crimes.py ../data/crimes_2013.json
    
Next, set up the Django database:

    $ cd /vagrant
    $ ./manage.py syncdb
    $ ./manage.py migrate
    
And get your static files collected:

    $ ./manage.py collectstatic


## Running

Log into the Vagrant machine in and run the development server.

    $ vagrant ssh
    $ source ~/radar/bin/activate
    $ cd /vagrant
    $ ./manage.py runserver 0.0.0.0:8000

The Vagrant file sets a static IP for the machine, so browse to
http://192.168.50.4:8000/ to see the site.
