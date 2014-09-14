# README

## Installing

First setup the ElasticSearch index and load data:

Make sure ElasticSearch is running:
    $ sudo service elasticsearch start
    
Then set up the index and data:

    $ cd /vagrant
    $ cd radar
    $ python create_index.py
    $ python load_crimes.py ../data/crimes_2013.json
    
Next, set up the Django database:

    $ cd /vagrant
    $ ./manage.py syncdb
    $ ./manage.py migrate
    
And get your static files collected:

    $ ./manage.py collectstatic
    
Copy the nginx config to /etc/nginx/sites-enabled/radar:

    server {
        listen 0.0.0.0:8000;
    
        location / {
            proxy_pass http://127.0.0.1:8001;
        }
    
        location /static/ {
            autoindex on;
            alias /vagrant/static/;
        }
    }
    
Copy the gunicorn upstart job to /etc/init/radar.conf:
 
    description "radar"
    
    start on (filesystem)
    stop on runlevel [016]
    
    respawn
    setuid vagrant
    setgid vagrant
    chdir /vagrant
    
    script
       . /home/vagrant/radar/bin/activate
      exec /home/vagrant/radar/bin/gunicorn radar.wsgi --bind 0.0.0.0:8001
    end script
    
Copy the nginx upstart job to /etc/init/nginx.conf:

    description "nginx http daemon"
     
    start on runlevel [2]
    stop on runlevel [016]
     
    console owner
     
    exec /opt/nginx/sbin/nginx -c /opt/nginx/conf/nginx.conf -g "daemon off;"
     
    respawn
 
Copy the elasticsearch upstart job to /etc/init/elasticsearch.conf:

    # ElasticSearch Service
     
    description     "ElasticSearch"
     
    start on (net-device-up
              and local-filesystems
              and runlevel [2345])
     
    stop on runlevel [016]
     
    respawn limit 10 5
     
    env ES_HOME=/usr/share/elasticsearch/home
    env ES_MIN_MEM=256m
    env ES_MAX_MEM=2g
    env DAEMON="${ES_HOME}/bin/elasticsearch"
    env DATA_DIR=/data/elasticsearch/data
    env CONFIG_DIR=/etc/elasticsearch
     
    console output
     
    script
      if [ -f /etc/default/elasticsearch ]; then
        . /etc/default/elasticsearch
      fi
     
      su -s /bin/dash -c "/usr/bin/elasticsearch -f -Des.path.conf=$CONFIG_DIR -Des.path.home=$ES_HOME -Des.path.logs=$LOG_DIR -Des.path.data=$DATA_DIR -Des.path.work=$WORK_DIR" elasticsearch
    end script
 
## Running

If you installed the upstart jobs right, just log in! bwahaha
