# encoding: utf-8
import os
import json
import logging
import time
import threading
from docker import Client
import subprocess
from ConfParser import ConfParser
import sys

class Command(threading.Thread):
    def __init__(self,container,tabCommand, sender_subPro):
        ## thread initialization
	threading.Thread.__init__(self)
	self.wait=threading.Event()
	## Config Log
        self._logger = logging.getLogger("COMMAND")
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
	## zabbix-sender process 
        self.sender_subPro = sender_subPro
	self.container=container
	## zabbix-sender parameter
	self.tabCommand=tabCommand
	## Variable to shutdown the process
        self.stop = False


    def run(self):
        # emit to endpoint_func
	while self._should_run():
		# section est le nom du container
		if (self.tabCommand['command'] != ""):
			# Exec the zabbix-sender process
			proc=subprocess.Popen(self.tabCommand['command'],stderr=subprocess.PIPE, stdout=subprocess.PIPE,shell=True,preexec_fn=self.preexec)
			value = proc.communicate()
			stdout_value=value[0]
			stderr_value=value[1]
			# setup the request to send to zabbix-sender
			result= [{'hostname' : self.container, 'key' : self.tabCommand['key'], 'timestamp' : str(int(time.time())), 'value' : stdout_value}]
                        self._logger.info("Every %s second -> Exec :  %s ", self.tabCommand['delay'], result)
			# Emit the Request
       			self.sender_subPro.emit(result)
			self.wait.wait(float(self.tabCommand['delay']))
		else : 
			self.shutdown()

    # Don't forward signals
    def preexec(self): 
        os.setpgrp()	

    # Shutdown the Thread
    def shutdown(self):
        self._logger.info("Thread Shutdown - Key %s - Server %s ", self.tabCommand['key'],self.container)
        self.stop = True
	self.wait.set()
	
    # Check if the thread should run
    def _should_run(self):
        return not self.stop

    # Change the Delay
    def setDelay(self,delay):
	self.tabCommand['delay'] = delay

    # Change the Thread Setting
    def change(self,tabCommand):
	if self.tabCommand != tabCommand :
		self.tabCommand=tabCommand
		self._logger.info("Change done :  %s ", self.tabCommand)

