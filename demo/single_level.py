#!/usr/bin/python

# Copyright (c) 2012 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

# NOTE: To run the demo you must have the following jobs defined in jenkins/hudson
# quick(password, s1, c1) # Requires parameters
# wait10
# wait5

import sys
import os.path
from os.path import join as jp
here = os.path.dirname(__file__)
sys.path.append(jp(here, '../..'))

import logging

from jenkinsapi import jenkins

from jenkinsflow.jobcontrol import parallel, serial, FailedJobsException, FlowTimeoutException
from jenkinsflow.unbuffered import UnBuffered
sys.stdout = UnBuffered(sys.stdout)

jenkinsurl = "http://localhost:8080"

def main():
    logging.basicConfig()
    logging.getLogger("").setLevel(logging.WARNING)
    api = jenkins.Jenkins(jenkinsurl)

    with serial(api, timeout=30, report_interval=3) as ctrl:
        ctrl.invoke('quick', password='X', s1='HELLO', c1='true')
        ctrl.invoke('wait10')
        ctrl.invoke('wait5')

    with parallel(api, timeout=20, report_interval=3) as ctrl:
        ctrl.invoke('quick', password='Y', s1='WORLD', c1='maybe')
        ctrl.invoke('wait10')
        ctrl.invoke('wait5')

if __name__ == '__main__':
    main()