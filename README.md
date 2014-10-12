# README

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
