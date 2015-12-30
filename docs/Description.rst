Docker Zabbix Script Sender (DZSS)
==================================

Description 
###########

The DZSS docker container is a zabbix agent that send zabbix trap to a zabbix server.
It is a script based monitoring, that allows you to develop your own scripts to monitor whatever you want in docker containers.
The python docker API is already provided to be able to get any information about docker.
With this container you will be able to send zabbix traps thanks to scripts developped in the language you like (bash,python,perl).

Overview
########

This Tool contains 3 components :
	- Docker Monitoring Manager (DMM)
	- The Trap Sender Component (TPC)
	- The Configuration Parser Component (CPC)

Each components has a specific usage.

* **Docker Monitoring Manager (DMM) :**

This component is a thread that take care of every docker containers in the host. Every "time interval" in second (By default every 30min), this component check if a running container is in the configuration file and if the component has to monitor it.

At the start, the Component identify every containers on the host.
Then check in the Default.ini Configuration file if there is a section related to the container (if container's name is a section in the file)

If it does exist, a new thread "Trap Sender" is created to send statistic to the zabbix server.
Otherwise, it checks with the next docker container.

This Component manage the Trap Sender component. Every time there is a new statistic to send to the server, The DMM create a TPC thread according to the settings in the configuration file (provided by CPC Component).

Then TPC will get the information and send it to the server.
Also, It is checking periodically if the configuration file has been change and change the TPC thread settings if needed.
And finally, DMM shutdown the TPC thread when you don't need it anymore (if the docker container is shutdown or if the statitic in the configuration file has been deleted).

In the log file, everything related to this component will get the Logger Name "MAIN"

* **Trap Sender Component (TPC) :**

This component is a thread that take care of the Trap that will be send to zabbix server.
As I said, the TPC thread is created, setup and launch by the DMM Component. And can be periodically modify if you change the settings in the configuration file, the TPC Component will change its settings on the fly.
The role of the TPC Component is to get the information from the different docker container´s and send the results to the ZABBIX SERVER to monitor them.

One TPC Thread is created for each stat we want to get. One stat is corresponding to one script.
When the DMM create the TPC, it gets from the configuration file parameters that will allow us to get the stat we need about a docker container. 

The parameter of the TPC Thread are :
	- **script/command** to get the information from the monitored docker container
	- **delay** corresponding to the delay that the process is waiting periodically before to execute it again
	- **Key** corresponding to the key setup on the ZABBIX SERVER in the ITEM settings with a AGENT ZABBIX (ACTIVE) type of trap

In the log file, everything related to this component will get the Logger Name "TRAPSENDER" or "COMMAND"

* **Configuration Parser Component (CPC) :**

This Component manages the Configuration File.

By Default there is only one Default.ini configuration file, where you can setup everything about the configuration.
But for more flexibility the Default.ini file can reference other files and you can order your scripts, config file and docker container as you want. You can create a complex configuration file hierarchy with nested config file. More explanation in the section dedicated to the CPC.

This Component parse every config files and send the information to the DMM, that will use it to monitor
CPC parse only JSON files. 

These files contain different sections, subsections and attributs :
	- **CONFIG** (section) link a DZSS Container with a configuration file. Indeed you can have one file per monitoring DZSS Container
	- **Container's name** (section) contains information as reference and script subsection. the section name has to be the same as the container name that you want to monitor.
	- **reference** (subSection) contains file references to be able to get more script to monitor, permit to sort the config files by type of scripts (see the CPC dedicated section)
	- **script** (subSection) contains the script that will be executed by the TPC thread to get the stat and send it to ZABBIX SERVER

In the log file, everything related to this component will get the Logger Name "CONFPARSER"
	

The Log File logs every action, such as thread creation/change/shutdown, error of config file, traps sent, result of the trap...
Moreover you have the thread id that allow you to recognize quickly what TPC thread has an issue.


As a Docker container itself
############################

The monitoring tool is running inside a Docker container. An [automated build](https://hub.docker.com/r/troptop/docker-zabbix-script-sender/) always provides the latest stable version :
::
        docker pull troptop/docker-zabbix-script-sender

Source File & Contribution
##########################

Source Code : https://github.com/troptop/docker-zabbix-script-sender

Issue Tracker : https://github.com/troptop/docker-zabbix-script-sender/issues

