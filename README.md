# README

## Installing

First setup the ElasticSearch index and load data:

Make sure ElasticSearch is running:
    $ sudo service elasticsearch start
    
Then set up the index and data:

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


## If you want to mirror "production"
- Copy the nginx config to /etc/nginx/sites-enabled/radar
- Copy the gunicorn upstart job to /etc/init/radar.conf
- Copy the nginx upstart job to /etc/init/radar
- Copy the elasticsearch upstart job to /etc/init/elasticsearch.conf
 
## Running

If you are using the Upstart jobs, log in and start the services with `sudo
start`.

Otherwise log in and run the development server.
