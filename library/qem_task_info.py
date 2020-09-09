#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_task_info
short_description: Qlik Replicate/Compose task facts via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Return Qlik Replicate/Compose task facts using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the task
        type: str
        required: False
    aliases:
        - task_name
    server:
        description:
            - The server where the task is defined
        type: str
        required: True
        aliases:
            - replicate_server
            - compose_server

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Single task facts
- name: Single Task facts
    qem_task_info:
        name: "My Task"
        server: "My Sample Server"
    register: output

- name: Display facts
    var: output.qem_tasks[0]

# All task facts
- name: All task facts
    qem_task_info:
        server: "My Sample Server"
    register: output

- name: Display facts
    var: output.qem_tasks
'''

import json
from collections import OrderedDict
from ansible.module_utils.aem_client import AemTaskState, AemRunTaskReq, AemRunTaskOptions
from ansible.module_utils.qem_common import QemModuleBase

class QemTaskInfoManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=False, aliases=['task_name']),
            server=dict(required=True, aliases=['task_server']),
        )

        self.server = None
        self.task = None

        super(QemTaskInfoManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        self.results = dict(
            task=dict(
                name=self.name,
                server=self.server
            ),
            changed=False,
            msg=""
        )
        self.results['qem_tasks'] = self.get_tasks_info()
        return self.results

    def get_tasks_info(self):
        response = self.aem_client.get_task_list(self.server)
        if not response:
            return None
        tasks = []
        if self.name:
            tasks = [task for task in response.taskList if task.name == self.name]
        else:
            tasks = response.taskList
        return map(self.task_mapper, tasks)

    def task_mapper(self, task):
      return {
        'name': task.name,
        'state': task.state.name,
        'stop_reason':  task.stop_reason.name,
        'message':  task.message,
        'assigned_tags': task.assigned_tags
      }

def main():
    QemTaskInfoManager()


if __name__ == '__main__':
    main()
