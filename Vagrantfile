# -*- mode: ruby -*-
# vi: set ft=ruby :

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  config.vm.provision "shell", path: "vagrant.sh"

  config.vm.network "private_network", ip: "192.168.50.4"
  config.vm.network :forwarded_port, host: 8011, guest: 9200
end
