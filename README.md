# docker-zabbix-script-sender

## Description 

This docker container is a zabbix agent that send zabbix trap to a zabbix server.
It allows you to develop your own script to monitor whatever you want to monitor.
The python docker API is already provided.
With this container you will be able to send zabbix traps thanks to scripts developped in the language you like.

## Settings the Working Directory

* The docker container needs at least a settings JSON file called "Default.ini" and a log directory called "logs"

The minimum settings :
mkdir logs
touch Default.ini

## Launch the docker

The minimum settings : 
docker run -e ZABBIX_SERVER=172.29.215.230 --name=zabbix-client -it -v /PATH/TO/VOLUME:/usr/src/app -v /var/run/docker.sock:/var/run/docker.sock troptop/docker-zabbix-script-sender

## Configuration File


## As a Docker container itself!

The monitoring tool can also run inside a Docker container. An [automated build](https://hub.docker.com/r/troptop/docker-zabbix-script-sender/) always provides the latest stable version.

    docker pull troptop/docker-zabbix-script-sender

## Source File 

You can find the source file : 
https://github.com/troptop/docker-zabbix-script-sender

# Documentation

## Setup the installation :


