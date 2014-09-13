# README

## Installing

First setup the ElasticSearch index and load data:

    $ cd /vagrant
    $ cd radar
    $ python create_index.py
    $ python load_crimes.py ../data/crimes_2013.json
    
Then set up the Django database:

    $ cd /vagrant
    $ ./manage.py syncdb
    $ ./manage.py migrate
