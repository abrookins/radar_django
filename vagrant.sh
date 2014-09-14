#!/bin/sh

sudo apt-get update

# Install ElasticSearch
cd ~
sudo apt-get install openjdk-7-jre-headless -y

wget https://download.elasticsearch.org/elasticsearch/elasticsearch/elasticsearch-1.3.2.deb
sudo dpkg -i elasticsearch-1.3.2.deb

sudo service elasticsearch start

# Install python3
sudo apt-get install python-software-properties -y
sudo add-apt-repository ppa:fkrull/deadsnakes -y
sudo apt-get update -y
sudo apt-get install libreadline6 libreadline6-dev libncurses5-dev -y
sudo apt-get install python3.4-dev -y
sudo apt-get install python3.4 -y
sudo apt-get install g++ -y
sudo apt-get install vim -y
sudo apt-get install nginx -y

# Install setuptools (easy_install, pip)
wget https://bitbucket.org/pypa/setuptools/raw/bootstrap/ez_setup.py -O /tmp/ez_setup.py
sudo python3.4 /tmp/ez_setup.py
sudo easy_install-3.4 pip

# Install Django/app
pyvenv-3.4 ~/radar
source ~/radar/bin/activate

# Install setuptools into the venv (not done automatically)
python /tmp/ez_setup.py
easy_install pip

cd /vagrant

pip install -r requirements.txt
pip install gunicorn

sudo ln -s /vagrant/conf/nginx/radar /etc/nginx/sites-enabled/radar
sudo cp /vagrant/conf/init/radar.conf /etc/init/radar.conf
sudo cp /vagrant/conf/init/nginx.conf /etc/init/nginx.conf
sudo cp /vagrant/conf/init/elasticsearch.conf /etc/init/elasticsearch.conf
