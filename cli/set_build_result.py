# Copyright (c) 2012 - 2015 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

from __future__ import print_function

import click

from ..utils import set_build_result as usbr


@click.command()
@click.option('--result', help="The result to set. Should probably be 'unstable'", default='unstable')
@click.option('--username', help="Name of jenkins user with access to the job")
@click.option('--password', help="Password of jenkins user with access to the job.")
@click.option('--java', help="Alternative 'java' executable", default='java')
@click.option('--direct-url', help="Jenkins URL. Default is JENKINS_URL/HUDSON_URL env var value. Use this argument if JENKINS_URL is a proxy [default: None]")
def set_build_result(result, username, password, direct_url=None, java='java'):
    """Change the result of a Jenkins job.

    Note: set_build_result can only be done from within the job, not after the job has finished.
    Note: Only available if URL is set in `Jenkins <http://jenkins-ci.org/>`_ system configuration.

    This command uses the Jenkins `cli` to change the result. It requires a java executable to run the Jenkins `cli`.
    Please note that in some versions of jenkins the cli is broken, it has no manifest file!
    """
    # %(file)s [--result <result>] [--java <java>] [--direct-url <direct_url>] [(--username <user_name> --password <password>)]

    usbr.set_build_result(result, username, password, direct_url, java)
