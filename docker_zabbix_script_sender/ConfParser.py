import json
import os
import logging
import logging.handlers
import sys
class ConfParser():

	def __init__(self,configFile):
		## Init Logs
		self.cp = None
                self._logger = logging.getLogger("CONFPARSER")
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
		# Open ConfigFile
		self.openConfigFile(configFile)

	## Check if the file exist and Load the JSON data
	def openConfigFile(self,filename):
		filename= os.path.realpath(".") + "/" + filename
		self.cp = None
                if (os.access(filename, os.F_OK) and os.access(filename, os.R_OK)):
			with open(filename) as data_file:
				try:
					self.cp = json.load(data_file)
    				except :
					self._logger.info("Invalid JSON File, Please Check %s", filename)
			        	self.cp = None
		else:
			self._logger.info("The file %s is not accessible", filename)

	## Get every Keys
	def getSection(self):
		return self.cp.keys()

	# Get every References
	def getReferences(self,section):
		if self.has_option(self.cp[section],'reference'):
			return self.cp[section]['reference']
		else:
			return {}

	## Get the sources in the CONFIG section
	def getSource(self):
		dic={}
		if self.has_option(self.cp["CONFIG"],'source'):
			for source in self.cp["CONFIG"]['source']:
				if self.has_option(source,'server') and self.has_option(source,'file') and self.getOption(source,'server')!= "" and self.getOption(source,'file') != "" :
					if (os.access(self.getOption(source,'file'), os.F_OK)):
						dic[self.getOption(source,'server')] = self.getOption(source,'file')
					else: 
						self._logger.info("The file %s is not accessible", self.getOption(source,'file'))
				else:
					self._logger.info('Wrong Server or File Parameter in the CONFIG section in the "Default.ini" File ')
					
                        return dic
	

	def getOption(self,dic,option):
		return dic[option]


	def getScripts(self,section):
		if self.has_option(self.cp[section],'scripts'):
			return self.cp[section]['scripts']
		else:
			return {}
	
	
	def has_section(self,sectionName):
		return (sectionName in self.cp)

	def has_option(self,dic, optionName):
		return (optionName in dic) and (dic[optionName]!="")
	
	def getKeys(self,sectionName):
		result=[]
		for script in self.getScripts(sectionName):
			if self.has_option(script,'key'):
				result.append(script['key'])
		return result
	
	## Get References in the references section
	def getReference(self,references):
		referenceList={}
		# If the settings are OK
		if (self.has_option(references,'file')):
			# If no section parameter or empty then get every section in the File in parameter
			if (not self.has_option(references,'section') or (self.has_option(references,'section') and self.getOption(references,'section') == '')):
				# Check if the file is readable
				self.openConfigFile(self.getOption(references,'file'))
				if self.cp != None:
					# For every section
					for section in self.cp:
						## If  Empty
						if not self.getOption(references,'file') in  referenceList:
							referenceList[self.getOption(references,'file')]=[]
						# add every reference in the list
						referenceList[self.getOption(references,'file')].append(section)
			else: 
				# IF section has a value
				if not self.getOption(references,'file') in  referenceList:
					referenceList[self.getOption(references,'file')]=[]
				# add the reference to the list
				referenceList[self.getOption(references,'file')].append(self.getOption(references,'section'))
		
		return referenceList


	## Get the command line to execute the script
	def getCommand(self, scriptParam):
		command = ""
		# If the settings are OK
		if (self.has_option(scriptParam,'interpreter') and self.has_option(scriptParam,'file') and self.has_option(scriptParam,'key') and self.has_option(scriptParam,'delay')):
			if (not self.has_option(scriptParam,'delay')) or scriptParam['delay'] == "":
				delay = 60
			else:
				delay = scriptParam['delay'] 
#			# If The file can be read
			if (os.access(scriptParam['file'], os.F_OK)):
				command = scriptParam['interpreter'] + " " + scriptParam['file'] + " " + scriptParam['argument']	
				# Return The command and parameter
				return {'command':command, 'key':scriptParam['key'], 'delay':delay}
			else : 
				self._logger.info("The file %s is not accessible", scriptParam['file'])
		return None
