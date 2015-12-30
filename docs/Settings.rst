DZSS Settings
=============

Settings the Working Directory
##############################

The Working directory into the DZSS container is **/usr/src/app**.

So if you want to interact directly with the DZSS container you have to share this directory with a local directory on the docker host.

The minimum Working Directory Settings 
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The docker container needs at least a settings JSON file called \"Default.ini\" and a log directory called "logs".
::
	mkdir WorkDir && cd WorkDir
	mkdir logs
	touch Default.ini

You can make a try to see if you get any errors to create the DZSS container :
::
        docker run --name=zabbix-client -it -v /PATH/TO/VOLUME:/usr/src/app -v /var/run/docker.sock:/var/run/docker.sock troptop/docker-zabbix-script-sender
        
When starting the container the log file **docker-zabbix-sender.log** will be created in the logs directory.

A rotation setting is setup on the log. The container create a log file every day during 7 days.

Docker Command Line Settings
############################

The DZSS command line need only a few parameter :
	- Environment variable :
		- **ZABBIX_SERVER** : the Zabbix Server IP or HOSTNAME
		- **INTERVAL** : The Time Interval for DMM component to check if the configuration has been change
	- Sharing Volume : 
		- **docker.sock** : the docker.sock file need to be shared to be able to communicate with docker with the docker API
		- **Working Directory** : you have to share the working directory (/usr/src/app)if you want to Configure the container
Example :
::
        docker run -e ZABBIX_SERVER=IP_SERVER/HOSTNAME -e INTERVAL=30 --name=zabbix-client -it -v /PATH/TO/VOLUME:/usr/src/app -v /var/run/docker.sock:/var/run/docker.sock troptop/docker-zabbix-script-sender

File Configuration
##################

All the configuration files are **JSON files**.

The Default configuration file is called **Default.ini**.

Example
^^^^^^^

The File can look like :
::
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

Sections Explanation 
^^^^^^^^^^^^^^^^^^^^
	- **CONFIG Section** :
                This section allow you to setup another specific file for a specific DZSS Container.

                This section contains a source subSection. This subSection contains a list of parameter corresponding to **the DZSS Container's name** and **the specific configuration file** apply to it.

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
::
        {
                "apache2.0": {
        			....
                },
                "apache2.2": {
        			....
                },
                "apache2.5": {
        			....
                }
        }

The database.json file looks like :
::
        {
                "mysql": {
        			....
                },
                "postgresql": {
        			....
                },
                "sqlite": {
        			....
                }
        }

The reference section allows you to be flexible in your monitoring configuration.


                2. **scripts** : This subSection list the scripts you will execute to monitor the containers. DZSS will execute this script and request the zabbix server send it the statistic.

                  A script has 5 parameters corresponding to the **"key"** you had setup on the zabbix server, **"interpreter"** is the interpreter used to execute the script, **"file"** is the script file, **"argument"** are the argument passed to the script, **"delay"** is the time interval where this script will be executed periodically.

                  If you do not setup up the delay or if it is empty, **the default value is 30s**
                
                  The output format of the script has to be only one value get by an echo ouput on stdout

                  Then DZSS format the result to be able to send the request to the zabbix server 
The format :
::
        [{'hostname' : CONTAINER_NAME, 'key' : KEY_IN_CONFIG_FILE, 'timestamp' : str(int(time.time())), 'value' : STDOUT_OF_THE_SCRIPT}]

For example the script below for the container "mypostgresql" is a bash script called "mypostgres_check.sh" and will be called every 60s: 
::
        "scripts" : [
                        {"key" : "postgreskey", "interpreter" : "bash", "file" : "mypostgres_check.sh", "argument" : ""}
                ]

The script "mypostgres_check.sh" contains : 
::
	#!/bin/bash

	echo -n 2

So DZSS will format the result such as :
::
        [{'hostname' : 'mypostgresql', 'key' : 'postgreskey', 'timestamp' : '1451370349', 'value' : '2'}]



	
Specific rules
^^^^^^^^^^^^^^
- The configuration files are **case sensitive**
- Be careful with the keys you are using. if 1 monitored container has 2 scripts with the same key, just one of these script will be used
- **Nested references** configuration files, be aware of a possible infinite loop with the references configuration file, it would crash the DZSS
- Error of json files parsing. does not have a big impact, only shutdown the TPC thread contained in the json configuration file failing, when you will correct the error in the json config file, the TPC thread will start again.
