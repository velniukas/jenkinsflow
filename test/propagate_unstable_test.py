#!/usr/bin/python

# Copyright (c) 2012 - 2014 Lars Hupfeldt Nielsen, Hupfeldt IT
# All rights reserved. This work is under a BSD license, see LICENSE.TXT.

from pytest import raises

from jenkinsflow.flow import parallel, serial, BuildResult, FailedChildJobException
from jenkinsflow.test.framework import mock_api

from demo_security import username, password

def test_propagate_unstable_serial_toplevel(env_base_url, fake_java, capfd):
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('j11', 0.01, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('j12_unstable', 0.01, max_fails=0, expect_invocations=1, expect_order=2, final_result='unstable')
        api.job('j13', 0.01, max_fails=0, expect_invocations=1, expect_order=3)

        with serial(api, timeout=70, username=username, password=password, job_name_prefix=api.job_name_prefix) as ctrl1:
            ctrl1.invoke('j11')
            ctrl1.invoke('j12_unstable')
            ctrl1.invoke('j13')

        assert ctrl1.result == BuildResult.UNSTABLE


def test_propagate_unstable_parallel_toplevel(env_base_url, fake_java, capfd):
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('j11', 0.01, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('j12_unstable', 0.01, max_fails=0, expect_invocations=1, expect_order=1, final_result='unstable')
        api.job('j13', 0.01, max_fails=0, expect_invocations=1, expect_order=1)

        with parallel(api, timeout=70, username=username, password=password, job_name_prefix=api.job_name_prefix) as ctrl1:
            ctrl1.invoke('j11')
            ctrl1.invoke('j12_unstable')
            ctrl1.invoke('j13')

        assert ctrl1.result == BuildResult.UNSTABLE


def test_propagate_unstable_serial_inner(env_base_url, fake_java, capfd):
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('j11', 0.01, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('j21', 0.01, max_fails=0, expect_invocations=1, expect_order=2)
        api.job('j22_unstable', 0.01, max_fails=0, expect_invocations=1, expect_order=3, final_result='unstable')
        api.job('j23', 0.01, max_fails=0, expect_invocations=1, expect_order=4)

        with serial(api, timeout=70, username=username, password=password, job_name_prefix=api.job_name_prefix) as ctrl1:
            ctrl1.invoke('j11')
            with ctrl1.serial() as ctrl2:
                ctrl2.invoke('j21')
                ctrl2.invoke('j22_unstable')
                ctrl2.invoke('j23')

        assert ctrl2.result == BuildResult.UNSTABLE
        assert ctrl1.result == BuildResult.UNSTABLE


def test_propagate_unstable_parallel_inner(env_base_url, fake_java, capfd):
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('j11', 0.01, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('j21', 0.01, max_fails=0, expect_invocations=1, expect_order=2)
        api.job('j22_unstable', 0.01, max_fails=0, expect_invocations=1, expect_order=2, final_result='unstable')
        api.job('j23', 0.01, max_fails=0, expect_invocations=1, expect_order=2)

        with serial(api, timeout=70, username=username, password=password, job_name_prefix=api.job_name_prefix) as ctrl1:
            ctrl1.invoke('j11')
            with ctrl1.parallel(max_tries=2) as ctrl2:
                ctrl2.invoke('j21')
                ctrl2.invoke('j22_unstable')
                ctrl2.invoke('j23')

        assert ctrl2.result == BuildResult.UNSTABLE
        assert ctrl1.result == BuildResult.UNSTABLE


def test_propagate_unstable_serial_inner_fail_after(env_base_url, fake_java, capfd):
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('j11', 0.01, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('j21', 0.01, max_fails=0, expect_invocations=1, expect_order=2)
        api.job('j22_unstable', 0.01, max_fails=0, expect_invocations=1, expect_order=3, final_result='unstable')
        api.job('j23_fail', 0.01, max_fails=1, expect_invocations=1, expect_order=4)

        with raises(FailedChildJobException):
            with serial(api, timeout=70, username=username, password=password, job_name_prefix=api.job_name_prefix) as ctrl1:
                ctrl1.invoke('j11')
                with ctrl1.serial() as ctrl2:
                    ctrl2.invoke('j21')
                    ctrl2.invoke('j22_unstable')
                    ctrl2.invoke('j23_fail')


def test_propagate_unstable_parallel_inner_fail_before(env_base_url, fake_java, capfd):
    with mock_api.api(__file__) as api:
        api.flow_job()
        api.job('j11', 0.01, max_fails=0, expect_invocations=1, expect_order=1)
        api.job('j21_fail', 0.01, max_fails=1, expect_invocations=1, expect_order=2)
        api.job('j22_unstable', 0.01, max_fails=0, expect_invocations=1, expect_order=2, final_result='unstable')
        api.job('j23', 0.01, max_fails=0, expect_invocations=1, expect_order=2)

        with raises(FailedChildJobException):
            with serial(api, timeout=70, username=username, password=password, job_name_prefix=api.job_name_prefix) as ctrl1:
                ctrl1.invoke('j11')
                with ctrl1.parallel() as ctrl2:
                    ctrl2.invoke('j21_fail')
                    ctrl2.invoke('j22_unstable')
                    ctrl2.invoke('j23')