# Docker Zabbix Script Sender
## Description

The DZSS docker container is a zabbix agent that send zabbix trap to a zabbix server.
The python docker API is provided 
you will be able to send zabbix traps thanks to scripts developped in the language you like (bash,python,perl).

## Documentation

For the complete documentation and example :
http://docker-zabbix-script-sender.readthedocs.org/en/latest/index.html

## Settings the Working Directory

The Working directory into the DZSS container is **/usr/src/app**.

So if you want to interact directly with the DZSS container you have to share this directory with a local directory on the docker host.

#### The minimum Working Directory Settings

The docker container needs at least a settings JSON file called \"Default.ini\" and a log directory called "logs".
```
        mkdir WorkDir && cd WorkDir
        mkdir logs
        touch Default.ini
```
## Docker Command Line Settings

The DZSS command line need only a few parameter :
- Environment variable :
	1. **ZABBIX_SERVER** : the Zabbix Server IP or HOSTNAME
	2. **INTERVAL** : The Time Interval for DMM component to check if the configuration has been change
- Sharing Volume :
	1. **docker.sock** : the docker.sock file need to be shared to be able to communicate with docker with the docker API
	2. **Working Directory** : you have to share the working directory (/usr/src/app)if you want to Configure the container
Example :
```
        docker run -e ZABBIX_SERVER=IP_SERVER/HOSTNAME -e INTERVAL=30 --name=zabbix-client -it -v /PATH/TO/VOLUME:/usr/src/app -v /var/run/docker.sock:/var/run/docker.sock troptop/docker-zabbix-script-sender
```

## File Configuration

All the configuration files are **JSON files**.

The Default configuration file is called **Default.ini**.

The File looks like :
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

#### Sections Explanation

- **CONFIG Section** :
This section contains a source subSection. This subSection contains a list of parameter corresponding to the DZSS Container's name and the specific configuration file apply to it.
For exemple, you have 2 DZSS containers running on the same host (zabbix-client1 and zabbix-client2). The container called zabbix-client1 will use the configration file source_zabbix1.json and the container called zabbix-client2 will use the configuration file source_zabbix2.json

**The CONFIG Section can only be declared in the Default.ini file**

- **Container's Name Section** :
The name of the section has to have the exact same name of the container.
This section has 2 subSections :
1. **reference** : This subSection references other files you want to use to monitor this container in more of the scripts you already have in this section. A reference has 2 parameters corresponding to the **"Configuration File"** you want to use to monitor the server and **"The Section"** in this file you have to use to monitor it

2. **scripts** : This subSection list the scripts you will execute to monitor the containers. DZSS will execute this script and request the zabbix server send it the statistic.
A script has 5 parameters corresponding to the **"key"** you had setup on the zabbix server, **"interpreter"** is the interpreter used to execute the script, **"file"** is the script file, **"argument"** are the argument passed to the script, **"delay"** is the time interval where this script will be executed periodically.


## Source File & Contribution

Source Code : https://github.com/troptop/docker-zabbix-script-sender

Issue Tracker : https://github.com/troptop/docker-zabbix-script-sender/issues
