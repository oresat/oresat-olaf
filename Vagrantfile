# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "debian/bullseye64"

  # add forwarded ports
  config.vm.network "forwarded_port", guest: 8000, host: 8000, host_ip: "127.0.0.1"

  # sync oresat-olaf directory
  config.vm.synced_folder "../oresat-olaf", "/home/vagrant/oresat-olaf"
 
  # install all dependencies and add a vcan bus
  config.vm.provision "shell", inline: <<-SHELL
    apt-get update
    apt-get install -y \
      can-utils \
      git \
      libusb-1.0-0 \
      libusb-1.0-0-dev \
      linux-modules-extra-$(uname -r) \
      python3 \
      python3-pip \
      usbutils \
      vim
    pip3 install -r requirements.txt
    modprobe vcan
    ip link add dev vcan0 type vcan
    ip link set up vcan0
  SHELL

  # enable USB Controller on VirtualBox and filter for any CANables
  config.vm.provider "virtualbox" do |vb|
    vb.customize ["modifyvm", :id, "--usb", "on"]
    vb.customize ["modifyvm", :id, "--usbehci", "on"]
    vb.customize ["usbfilter", "add", "0", "--target", :id,
      "--name", "Any CANable",
      "--manufacturer", "Protofusion Labs",
      "--remote", "no"
    ]
  end
end
