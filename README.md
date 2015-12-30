# Docker Zabbix Script Sender
## Description

The DZSS docker container is a zabbix agent that send zabbix trap to a zabbix server.
It is a script based monitoring, that allows you to develop your own scripts to monitor whatever you want in docker containers.
The python docker API is already provided to be able to get any information about docker.
With this container you will be able to send zabbix traps thanks to scripts developped in the language you like (bash,python,perl).

## Overview

This Tool contains 3 components :
        - Docker Monitoring Manager (DMM)
        - The Trap Sender Component (TPC)
        - The Configuration Parser Component (CPC)

Each components has a specific usage.

## Settings the Working Directory

The Working directory into the DZSS container is **/usr/src/app**.

So if you want to interact directly with the DZSS container you have to share this directory with a local directory on the docker host.

### The minimum Working Directory Settings

The docker container needs at least a settings JSON file called \"Default.ini\" and a log directory called "logs".
```
        mkdir WorkDir && cd WorkDir
        mkdir logs
        touch Default.ini
```
## Docker Command Line Settings

The DZSS command line need only a few parameter :
        - Environment variable :
                - **ZABBIX_SERVER** : the Zabbix Server IP or HOSTNAME
                - **INTERVAL** : The Time Interval for DMM component to check if the configuration has been change
        - Sharing Volume :
                - **docker.sock** : the docker.sock file need to be shared to be able to communicate with docker with the docker API
                - **Working Directory** : you have to share the working directory (/usr/src/app)if you want to Configure the container
Example :
```
        docker run -e ZABBIX_SERVER=IP_SERVER/HOSTNAME -e INTERVAL=30 --name=zabbix-client -it -v /PATH/TO/VOLUME:/usr/src/app -v /var/run/docker.sock:/var/run/docker.sock troptop/docker-zabbix-script-sender
```

## File Configuration

All the configuration files are **JSON files**.

The Default configuration file is called **Default.ini**.

The File can look like :
```
        {
                "CONFIG": {
                        "source":[
                                {"server": "zabbix-client1", "file":"source_zabbix1.json"},
                                {"server": "zabbix-client2", "file":"source_zabbix2.json"}
                        ]
                },
                "mypostgres": {
                        "reference": [
                                {"file" : "storage/database.json","section" : "postgresql"}
                        ],
                        "scripts" : [
                                {"key" : "postgreskey", "interpreter" : "bash", "file" : "mypostgres_check.sh", "argument" : "", "delay" : 40"}
                        ]
                },
                "myapache": {
                        "reference": [
                                {"file" : "apache.json","section" : ""},
                                {"file" : "apache.json"}
                        ],
                        "scripts" : [
                                {"key" : "check_myapache","interpreter" : "bash","file" : "check_myapache.sh", "argument" : ""}
                        ]
                }
        }
```

## Source File & Contribution

Source Code : https://github.com/troptop/docker-zabbix-script-sender

Issue Tracker : https://github.com/troptop/docker-zabbix-script-sender/issues
