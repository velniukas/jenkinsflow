#!/usr/bin/python

from bottle import route, run, static_file, post, response
from jenkinsapi.jenkins import Jenkins
from os.path import join as jp
import json
import requests
import argparse

jenkins_url = 'http://localhost:8080/'


@route('/jenkinsflow/graph')
def index():
    return static_file('flow_vis.html', root='./')


@route('/jenkinsflow/js/<filename>')
def js(filename):
    return static_file(filename, root='./js/')


@post('/jenkinsflow/builds')
def builds():
    # TODO: change this to jenkinsapi call because this url
    # returns html table, and we only need job names and state of the build
    # api = Jenkins(jenkins_url)
    # simple_queue = []
    # if len(api.get_queue()):
    #     for item in api.get_queue().values():
    #         print 'queue item: %s %s' % (type(item), item)
    #         job = api[item.task['name']]
    #         print 'job: %s %s' % (type(job), job)
    #         build = job.get_last_build_or_none()
    #         simple_queue.append({'job': job.name,
    #                              'running': job.is_running(),
    #                              'job_id': build.get_number()
    #                              if build is not None else '???'})

    # print 'DEBUG: simple_queue=', simple_queue
    rsp = requests.get(jenkins_url + 'queue/api/json')
    response.content_type = 'application/json'
    return json.dumps(rsp.json())


@post('/jenkinsflow/build/<name>')
def job(name):
    rsp = requests.get(jenkins_url + 'job/' + name + '/api/json')
    response.content_type = 'application/json'
    return json.dumps(rsp.json())


@route('/jenkinsflow/flow_graph.json')
def graph_json():
    response.content_type = 'text'
    return open('flow_graph.json', 'r')
    # return static_file('flow_graph.json', root=./)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serve flow grap')
    parser.add_argument('--hostname', default='localhost', help='hostname to listen on')
    parser.add_argument('--port', default=9090, help='port to listen on')
    parser.add_argument('--document_dir', default='/var/www/jenkinsflow/', help='Where to find json flow graph')
    args = parser.parse_args()

    run(host=args.hostname, port=args.port, debug=True)
