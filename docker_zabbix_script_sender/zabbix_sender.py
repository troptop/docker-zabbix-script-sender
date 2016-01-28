# encoding: utf-8

import argparse
import logging
from .version import version
import logging.handlers
import os
import signal
import sys
import tempfile
import threading
import time
from docker import Client
from docker.utils import kwargs_from_env
from Command import Command
from TrapSender import TrapSender
from ConfParser import ConfParser
import copy

class zabbixSender(threading.Thread):
	def openConfigFile(self,configFile):
		## Init the WorkDirectory
                fd = ConfParser(configFile)
		return fd

	def __init__(self,args=None):
		## Init Thread 
		threading.Thread.__init__(self)
		self.wait=threading.Event()
		## Init Logs
		self._logger = logging.getLogger("MAIN")
		FORMAT = '%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s'
		LOGFILE='logs/docker-zabbix-sender.log'
		logFormatter = logging.Formatter(FORMAT)
		console = logging.StreamHandler(sys.stdout)
		console.setFormatter(logFormatter)
		fileHandler = logging.handlers.TimedRotatingFileHandler(LOGFILE, when='D', interval=1, backupCount=7)
		fileHandler.setFormatter(logFormatter)
		self._logger.addHandler(fileHandler)
		self._logger.setLevel(logging.INFO)
		self._logger.addHandler(console)
		
		## Parse the command line
		parser = argparse.ArgumentParser(
			description="""Provides Zabbix Docker containers statistics running on a Docker daemon."""
		)
		parser.add_argument('-V', '--version',
    	        	action='version',
	    	        version='%(prog)s ' + version
    		)
		parser.add_argument('-v', '--verbose',
	    	        action='count',
    		        help='Verbose mode, -vv for more details'
		)
		parser.add_argument("--tlsverify",
			action='store',
	    	        choices=["true", "false"],
    		        default='true',
	    	        help="Use TLS and verify the remote Docker daemon. Default is %(default)s"
    		)
	    	parser.add_argument('-c', '--config',
    		        metavar="<file>",
	    	        help="Absolute path to the zabbix agent configuration file"
    		)
		parser.add_argument('-z', '--zabbix-server',
    	        	metavar='<server>',
	    	        help='Hostname or IP address of Zabbix server'
    		)
	    	parser.add_argument('-p', '--port',
    		        metavar='<server port>',
    	        	help='Specify port number of server trapper running on the server. Default is 10051'
		)
	    	parser.add_argument('-i', '--interval',
    		        metavar='<sec>',
    	        	default=1800,
	    	        type=int,
    		        help='Specify Zabbix update interval (in sec). Default is %(default)s'
    	    	)
	    	parser.add_argument('-r', '--real-time',
    		        action='store_true',
    	        	help="zabbix_sender push metrics to Zabbix one by one as soon as they are sent."
		)
	    	parser.add_argument('-s', '--host',
    		        metavar='<hostname>',
	    	        help='Specify host name. Host IP address and DNS name will not work'
    		)
	   	self.args = parser.parse_args(args)
    		kwargs  = kwargs_from_env()
	    	if not self.args.tlsverify.lower() in ("yes", "true", "t", "1"):
    		        kwargs['tls'].assert_hostname = False
	    	kwargs['version'] = '1.17'
	    	if self.args.zabbix_server is None:
    		        self.args.zabbix_server = os.environ['ZABBIX_SERVER']
	    	if self.args.host is None:
    		        self.args.host = os.environ['ZABBIX_HOST']
		if "INTERVAL" in os.environ :
			self.args.interval = os.environ['INTERVAL']
		## Hostame in environment varaiable
		if "HOSTNAME" in os.environ :
			self.hostname=os.environ['HOSTNAME']
		## The configuration file
		self.configFilename = "Default.ini"
		## Open the Config File
		self.json = self.openConfigFile(self.configFilename)
		if self.json.cp == None :
	                self._logger.info("PARSE ERROR : Please Check the Configuration File %s", self.configFilename )

			
			
		## Init de l'API docker && Param to stop the thread && the zabbix_sender subProcess && Thread Array
    		self.docker_client = Client(**kwargs)
	    	self.running = True
    		self.zabbixPipe = TrapSender(
          		config_file = self.args.config,
	    		zabbix_server = self.args.zabbix_server,
    			host = self.args.host,
    	       		port = self.args.port,
	    		real_time = self.args.real_time,
    			verbose = self.args.verbose if self.args.verbose is not None else 0
		);
		self.emitter={}


	## Main Thread ##
	def run(self):
		keys={}
		oldKeys={}
		prev_running_containers=set()
		## Get all the Docker Containers on the Host ##
	        all_containers = self.docker_client.containers(all=True)
		for container in all_containers:
                	self._logger.info("All containers on this Host : %s - > %s", container['Names'][0],container['Id'])
		## Get Only the Docker Containers Running
		running_containers = self.docker_client.containers()
		running_containers_id=set()
                running_containers_info={}

		FILENAME=self.configFilename
		## Get the ID and NAME of each Container
		for container in running_containers:
			self._logger.info("Container are already running : %s - > %s", container['Names'][0],container['Id'])
			running_containers_id.add(container['Id'])
                        running_containers_info[container['Id']]=[container['Id'],container['Names'][0]]
		## Start the Thread Loop ##
		while self.isRunning():
                	self._logger.info("Main Thread is still RUNNING")

			## Check if the section CONFIG exist
			self.json = self.openConfigFile(self.configFilename)
			if self.json.cp != None :
				## Extract the file corresponding to the hostname
				if self.json.has_section("CONFIG"):
					myName=""
					for i in running_containers_id:
						if running_containers_info[i][0][:12] == self.hostname :
							myName=running_containers_info[i][1][1:]
							
					if myName == "" :
						self._logger.info("ERROR : Can not find my own Container name : Hostname : %s" , self.hostname)
					sources = self.json.getSource()
					FILENAME=self.configFilename
					for server in sources: 
						if server == myName : 
							FILENAME = sources[server]
							break
						



			## Compare The running Container at the T-1 time to the T time (previous loop) to know if Containers have been stopped
			## If started, start the threads that monitor the servers
			stopped_containers = prev_running_containers - running_containers_id
                        for container in stopped_containers:
                                if container in self.emitter:
                                        self._logger.info("Container has been stopped : %s - > %s", prev_running_containers_info[container][1],container)
                                        for keyCommand in self.emitter[container]:
                                                self.emitter[container][keyCommand].shutdown()
                                        for keyCommand in self.emitter[container]:
                                                self.emitter[container][keyCommand].join()
                                                delkey.append(keyCommand)
                                        for keyCommand in delkey:
                                                del self.emitter[container][keyCommand]
                                        del self.emitter[container]
                                        self._logger.info("Full Deletion of Monitored Container Done : %s - > %s", prev_running
_containers_info[container][1], container)

	                ## Compare The running Container at the T time to the T-1 time (previous loop) to know if Containers have been stopped
                        ## If stopped, kill the threads that monitor the servers
			started_containers = running_containers_id - prev_running_containers
			for container in started_containers:
				nameContainer = running_containers_info[container][1][1:]
				## Get the filename and section in the references section of the default.ini config file
				config=self.recursiveConfParse(nameContainer,container,nameContainer,self.configFilename)
				keys[container]=[]
				## Start new thread or change the thread setting with the default.ini file
				keys[container].extend(self.changeThreadSetting(nameContainer,container,nameContainer,self.configFilename))
				if (FILENAME != self.configFilename ) :
					## Get the filename and section in the source section of the default.ini config file
					config.extend(self.recursiveConfParse(nameContainer,container,nameContainer,FILENAME))
					keys[container].extend(self.changeThreadSetting(nameContainer,container,nameContainer,FILENAME))
				for param in config:
					for filename in param:
						keys[container].extend(self.changeThreadSetting(nameContainer,container,param[filename],filename))
				oldKeys=copy.deepcopy(keys)
			
			delContainer=[]
			## Change the Thread Variable if The Config File has been Changed
			if self.emitter:
				containerMonitored=self.emitter
			else:
				containerMonitored=running_containers_id
			for container in containerMonitored:
				nameContainer = running_containers_info[container][1][1:]
				config=self.recursiveConfParse(nameContainer,container,nameContainer,self.configFilename)
				keys[container]=[]
				keys[container].extend(self.changeThreadSetting(nameContainer,container,nameContainer,self.configFilename))
				if (FILENAME != self.configFilename ) :
					config.extend(self.recursiveConfParse(nameContainer,container,nameContainer,FILENAME))
					keys[container].extend(self.changeThreadSetting(nameContainer,container,nameContainer,FILENAME))
				for param in config:
					for filename in param:
						keys[container].extend(self.changeThreadSetting(nameContainer,container,param[filename],filename))
				## Delete keys in the container and stop the Thread
				deleteKeys = list(set(oldKeys[container]) - set(keys[container]))
				self.deleteThread(deleteKeys,nameContainer,container)
				oldKeys=copy.deepcopy(keys)
				if container in self.emitter:
					if not self.emitter[container]:
						delContainer.append(container)
			for container in delContainer:
				del self.emitter[container]
			        self._logger.info("Full Deletion of Monitored Container Done : %s - > %s", nameContainer, container)



                        if self.json.cp != None :
				## Affect T to T-1 For the containers comparaison
				## Reinit T For the containers comparaison
		                prev_running_containers = running_containers_id
                	        prev_running_containers_info=running_containers_info
				running_containers = self.docker_client.containers()
				running_containers_id=set()
		                running_containers_info={}
	        	        for container in running_containers:
	                	        running_containers_id.add(container['Id'])
                        		running_containers_info[container['Id']]=[container['Id'],container['Names'][0]]
			else:
	                	self._logger.info("PARSE ERROR : Please Check the Configuration File %s", self.configFilename )
				
			## Sleep Delay Time Giving in Param to the command
#			time.sleep(self.args.interval)
			self.wait.wait(float(self.args.interval))

		## End of Loop

		## Shutdown Every Thread
		for idContainer in self.emitter:
			self._logger.info("Shutdown the Monitoring for : %s - > %s", prev_running_containers_info[idContainer][1],idContainer)
			for keyCommand in self.emitter[idContainer]:
				self.emitter[idContainer][keyCommand].shutdown()	
		for idContainer in self.emitter:
			self._logger.info("Join Thread : %s - > %s", prev_running_containers_info[idContainer][1],idContainer)
			for keyCommand in self.emitter[idContainer]:
				self.emitter[idContainer][keyCommand].join()	
		self._logger.info("Process Zabbix_Docker_Sender is Shutdown")
	




	## Parse the config files to get every references recursively
	def recursiveConfParse(self,nameContainer,container,section,filename):
		result=[]
		referenceTab = self.getReferences(section,filename)
		if referenceTab != None :
			for myFile in referenceTab:
        			for section in referenceTab[myFile]:
					result.append({myFile:section})
	                	        result.extend(self.recursiveConfParse(nameContainer,container,section,myFile))
		return result                    


	## get the references
	def getReferences(self,section,filename):
        	reference = None 
		## Open ConfigFile
		self.json = self.openConfigFile(filename)
                if self.json.cp != None :
		        if self.json.has_section(section):
				## Get The Script in the Config File Section
	                	for ref in self.json.getReferences(section):
					## Parse the Config File Reference
					reference = self.json.getReference(ref)
					## If Reference is not well parse in the Config File
					if not reference:
                        		        self._logger.info("Please Check the References in the Configuration File %s, Section %s ", filename,section)
						reference = None
		return reference



	def changeThreadSetting(self,nameContainer,container,section,filename):
		newKeys=[]
		## Open ConfigFile
		self.json = self.openConfigFile(filename)
                if self.json.cp != None :
			## Check if the section Exists
	                if self.json.has_section(section):
				if not container in self.emitter:
					self.emitter[container]={}
        		        command = ""
				## Get The Script in the Config File Section
	                        for scriptParam in self.json.getScripts(section):
        	        	        ## Parse the Script in the Config File to Get the Command
                	                command = self.json.getCommand(scriptParam)
                        	        if command == None:
                        		        self._logger.info("Please Check the Scripts in the Configuration File %s, Section %s ", filename,section)
	                                else:
						## If Command is well parsed in The Config File
                	                        if (command['command'] != ""):
							## If The Key in the ConfigFile Does not have a Thread Related, Create the Command Thread that will check the server
                                	                if not command['key'] in  self.emitter[container] :
                                        	        	self._logger.info("New Monitored Key Container %s : %s - > %s", command['key'], nameContainer, container)
                                                	        self.emitter[container][command['key']] = Command(nameContainer,command,self.zabbixPipe)
                                                        	self.emitter[container][command['key']].start()
								newKeys.append(command['key'])
								
							## If The Key in the ConfigFile Have a Thread Related, Change the Command Parameter of the Thread that is checking the server
        	                                        else :
                	                                	self._logger.info("Check to Change Monitored Key Container %s : %s - > %s", command['key'], nameContainer, container)
                        	                                self.emitter[container][command['key']].change(command)
								newKeys.append(command['key'])

		return newKeys




	def deleteThread(self,keys,nameContainer,container):
			## If a Thread exists and does not have a Related Key in the Config File -> Shutdown the Thread && Delete the Array Element
			for key in keys :
				self.emitter[container][key].shutdown()
				## Delete the Key in the Emiiter Tab After stopping the process
			for key in keys:
	                	self.emitter[container][key].join()
				del self.emitter[container][key]
       		                self._logger.info("Delete Monitored Key Container %s : %s - > %s", key, nameContainer, container)



	## Check if the Thread is Running
	def isRunning(self):
		return self.running

	## Shutdown the Thread
	def shutdown(self,signum,frame):
		self.running=False
		self.wait.set()
		self._logger.info("Main Thread ShutDown in Progress...")
	
## Function used by setuptool module (entryPoint) - Duplicated Main Function
def run():
	zabbix=zabbixSender()
	signal.signal(signal.SIGTERM, zabbix.shutdown)
	signal.signal(signal.SIGINT, zabbix.shutdown)
	zabbix.start()
	signal.pause()

## Main Function
if __name__ == '__main__':
	zabbix=zabbixSender()
	signal.signal(signal.SIGTERM, zabbix.shutdown)
	signal.signal(signal.SIGINT, zabbix.shutdown)
	zabbix.start()
	signal.pause()
