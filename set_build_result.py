#!/usr/bin/env python

# Copyright (c) 2012 - 2014 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

"""
Change result of a Jenkins Job. Must be run from within the job!

Usage:
%(file)s [--result <result>] [--java <java>] [--direct-url <direct_url>] [(--username <user_name> --password <password>)]

-r, --result <result>      The result to set. Should probably be 'unstable' [default: unstable]
--java <java>              Alternative 'java' executable [default: java]
--direct-url <direct_url>  Jenkins URL. Default is JENKINS_URL env var value. Use this argument if JENKINS_URL is a proxy [default: None]
--username <user_name>     Name of jenkins user with access to the job
--password <password>     Password of jenkins user with access to the job. *** Warning Insecure, will show up in process listing! ***
"""
# TODO: insecure password

from __future__ import print_function
import sys, os, tempfile
from docopt import docopt

jenkins_cli_jar = 'jenkins-cli.jar'
hudson_cli_jar = 'hudson-cli.jar'


def cli_jar_info():
    base_url = os.environ.get('JENKINS_URL')
    cli_jar = jenkins_cli_jar

    if base_url is None:
        base_url = os.environ.get('HUDSON_URL')
        cli_jar = hudson_cli_jar

    if base_url is None:
        raise Exception("Could not get env variable JENKINS_URL or HUDSON_URL. Don't know whether to use " +
                        jenkins_cli_jar + " or " + hudson_cli_jar + " for setting result! " +
                        "You must set 'Jenkins Location' in Jenkins setup for JENKINS_URL to be exported. " +
                        "You must set 'Hudson URL' in Hudson setup for HUDSON_URL to be exported.")

    return cli_jar, base_url.rstrip('/')


def download_cli(cli_jar, direct_base_url, public_base_url):
    import urllib2
    
    path = '/jnlpJars/' + cli_jar
    if direct_base_url and direct_base_url != public_base_url:
        download_cli_url = direct_base_url + path
        print("INFO: Downloading cli:", repr(public_base_url + path), "(using direct url:", download_cli_url + ')')
    else:
        download_cli_url = public_base_url + path
        print("INFO: Downloading cli:", repr(download_cli_url))

    response = urllib2.urlopen(download_cli_url)
    with open(cli_jar, 'w') as ff:
        ff.write(response.read())
    print("INFO: Download finished:", repr(cli_jar))


def set_build_result(username, password, result, direct_url=None, java='java'):
    """Change the result of a Jenkins job.

    Note: set_build_result can only be done from within the job, not after the job has finished.

    Note: Only available if URL is set in `Jenkins <http://jenkins-ci.org/>`_ system configuration.

    This command uses the Jenkins `cli` to change the result. It requires a java executable to run the cli.

    Args:
        username (str): Name of jenkins user with access to the job
        password (str): Password of jenkins user with access to the job
        result (str): The result to set. Should probably be 'unstable'
        direct-url (str): Jenkins URL. Default is JENKINS_URL env var value. Use this argument if JENKINS_URL is a proxy.
        java (str): Alternative `java` executable. Use this if you don't wish to use the java in the PATH.
    """

    print("INFO: Setting job result to", repr(result))

    cli_jar, public_base_url = cli_jar_info()

    if not public_base_url.startswith('http:'):
        # Using script_api
        from . import script_api
        script_api.set_build_result(result)
        return

    import subprocess32 as subprocess

    def set_res():
        command = [java, '-jar', cli_jar, '-s', direct_url if direct_url else public_base_url, 'set-build-result', result]
        if username or password:
            assert password and username, "You must specify both username and password if any"
            fname = None
            try:
                fhandle, fname = tempfile.mkstemp()
                fhandle = os.fdopen(fhandle, 'w')
                fhandle.write(password)
                fhandle.close()
                subprocess.check_call(command + ['--username', username, '--password-file', fname])
            finally:
                try:
                    os.remove(fname)
                    fhandle.close()
                except IOError:  # pragma: no cover
                    pass
        else:
            subprocess.check_call(command)

    try:
        # If cli_jar is already present attempt to use it
        set_res()
    except subprocess.CalledProcessError:
        # We failed for some reason, try again with updated cli_jar
        download_cli(cli_jar, direct_url, public_base_url)
        set_res()


def main(arguments):
    here = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(1, os.path.dirname(here))
    import jenkinsflow
    __package__ = "jenkinsflow"

    doc = __doc__ % dict(file=__file__)
    args = docopt(doc, argv=arguments, help=True, version=None, options_first=False)
    direct_url = args['--direct-url']
    direct_url = direct_url + '/' if direct_url is not None and direct_url[-1] != '/' else direct_url
    result = args['--result']
    username = args['--username']
    password = args['--password']
    java = args['--java']

    set_build_result(username, password, result, direct_url, java)


# Allow relative imports while running as script
if __name__ == "__main__" and __package__ is None:
    main(sys.argv[1:])
