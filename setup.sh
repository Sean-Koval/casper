#! /usr/bin/bash

# Remove old installations
sudo apt-get purge -y nvidia-container* docker.io
sudo apt-get autoremove -y

# Fresh installation
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
&& curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add - \
&& curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update && sudo apt-get install -y \
    nvidia-container-toolkit-base \
    nvidia-docker2

sudo systemctl restart docker