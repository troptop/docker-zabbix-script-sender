# Docker Zabbix Script Sender
## Description

The DZSS docker container is a zabbix agent that send zabbix trap to a zabbix server.
It is a script based monitoring, that allows you to develop your own scripts to monitor whatever you want in docker containers.
The python docker API is already provided to be able to get any information about docker.
With this container you will be able to send zabbix traps thanks to scripts developped in the language you like (bash,python,perl).

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

#### Sections Explanation

- **CONFIG Section** :
This section allow you to setup another specific file for a specific DZSS Container.
This section contains a source subSection. This subSection contains a list of parameter corresponding to the DZSS Container's name and the specific configuration file apply to it.
For exemple, you have 2 DZSS containers running on the same host (zabbix-client1 and zabbix-client2). The container called zabbix-client1 will use the configration file source_zabbix1.json and the container called zabbix-client2 will use the configuration file source_zabbix2.json

**The CONFIG Section can only be declared in the Default.ini file**

- **Container's Name Section** :
This Section allows you to setup specific scripts for the container you want to monitor.
The name of the section has to have the exact same name of the container.
This section has 2 subSections :
	1. **reference** : This subSection references other files you want to use to monitor this container in more of the scripts you already have in this section. Useful if you want to have a specific file for a certain type of servers (exemple : a generic configuration file for all the apache servers)
A reference has 2 parameters corresponding to the **"Configuration File"** you want to use to monitor the server and **"The Section"** in this file you have to use to monitor it

In the example above, the subSection mypostgres contains one reference. In more of using the scripts in the scripts subSection to monitor the mypostgres container, DZSS will get the scripts in the "/usr/src/app/storage/database.json" configuration file at the "postgresql" section

In the same way, in the subSection myapache, it has 2 references. This section will monitor the container called myapache. In this case these two references are identicals. The parameter "section" is empty or does not exist. This means that DZSS will get every section in the "/usr/src/app/apache.json" configuration file to monitor the server

With the reference files, we can imagine that the apache.json file looks like :

2. **scripts** : This subSection list the scripts you will execute to monitor the containers. DZSS will execute this script and request the zabbix server send it the statistic.
A script has 5 parameters corresponding to the **"key"** you had setup on the zabbix server, **"interpreter"** is the interpreter used to execute the script, **"file"** is the script file, **"argument"** are the argument passed to the script, **"delay"** is the time interval where this script will be executed periodically.
If you do not setup up the delay or if it is empty, **the default value is 30s**
The output format of the script has to be only one value get by an echo ouput on stdout


## Source File & Contribution

Source Code : https://github.com/troptop/docker-zabbix-script-sender

Issue Tracker : https://github.com/troptop/docker-zabbix-script-sender/issues
