# encoding: utf-8

import logging
import os
import subprocess
import signal
import sys
import tempfile
import traceback


class TrapSender(subprocess.Popen):
    def __init__(self, **kwargs):
	# Config Logs
	self._logger=logging.getLogger("TRAPSENDER")
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
	self.kwargs=kwargs

    # Don't forward signals
    def preexec(self):
	os.setpgrp()

    @classmethod
    def cmdline(cls,
            input_file,
            config_file=None,
            zabbix_server=None,
            host=None,
            port=None,
            with_timestamps=False,
            real_time=False,
            verbose=2):
        cmdline = ['zabbix_sender', '--input-file', input_file]
        if config_file:
            cmdline.extend(['--config', config_file])
        if zabbix_server:
            cmdline.extend(['--zabbix-server', zabbix_server])
        if host:
            cmdline.extend(['--host', host])
        if port:
            cmdline.extend(['--port', port])
        if with_timestamps:
            cmdline.append('--with-timestamps')
        if real_time:
            cmdline.append('--real-time')
        if verbose != 0:
            cmdline.append('-' + 'v' * verbose)
        return cmdline

    # Send the request to zabbix sender
    def emit(self, events):
        if not any(events):
            return
        fmt = "{hostname} {key} {value}\n"
        if events[0].has_key('timestamp'):
            fmt = "{hostname} {key} {timestamp} {value}\n"
        for event in events:
		try:
			# Exec zabbix-sender
			proc=subprocess.Popen(TrapSender.cmdline(input_file='-',with_timestamps=True,**self.kwargs), stderr=subprocess.PIPE, stdout=subprocess.PIPE, stdin=subprocess.PIPE,preexec_fn=self.preexec)
			self._logger.info("Sending to Zabbix : %s ", fmt.format(**event))
			# Send the Request
			stdout=proc.communicate(input=fmt.format(**event))
			self._logger.info("Sent to Zabbix : %s ", fmt.format(**event))
			self._logger.info("Zabbix Response : %s ", stdout)
			
		except:
			traceback.print_exc()
			self._logger.info("FAILED : Sending Proccess zabbix-sender has crashed")




