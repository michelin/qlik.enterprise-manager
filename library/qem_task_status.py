#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_task_status
short_description: Manage Qlik Replicate/Compose task status via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Manage Qlik Replicate/Compose task status using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the task you wan to start/stop
        type: str
        required: True
        aliases:
            - task_name
    state:
        description:
            - If I(state=started), task will be started
            - If I(state=stopped), task will be stopped
        default: present
        choices:
            - started
            - stopped
    server:
        description:
            - The server on which the task is defined
        type: str            
        required: True
        aliases:
            - replicate_server
            - compose_server
    timeout:
        description:
            - A timeout in seconds before raising an issue during the task starting/stopping
        type: int
        default: 60
        required: False
    option:
        description:
            - If I(option=resume_processing), resumes task execution from the point that it was stopped.
            - If I(option=reload_target), re-starts the full-load replication process if the task was previously run.
            - If I(option=resume_processing_from_timestamp), starts the CDC replication task from a specific point.
            - If I(option=metadata_only_recreate_all_tables), recovers a task using the recovery state stored locally in the task folder (located under the Data folder).
            - If I(option=metadata_only_create_missing_tables), recovers a task using the CHECKPOINT value from the attrep_txn_state table (created in the target database).
            - If I(option=recover_using_locally_stored_checkpoint), recovers a task using the CHECKPOINT value from the attrep_txn_state table (created in the target database).
            - If I(option=recover_using_checkpoint_stored_on_target), creates missing target tables, including Change Tables.

        default: 'resume_processing'
        choices:
            - resume_processing
            - reload_target
            - resume_processing_from_timestamp
            - metadata_only_recreate_all_tables
            - metadata_only_create_missing_tables
            - recover_using_locally_stored_checkpoint
            - recover_using_checkpoint_stored_on_target

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Starting a task with a extended timeout and restart the full load replication process
- name: Started sample task
    qem_task_status:
        name: "My Sample Task"
        server: "My Sample Server"
        timeout: 120
        state: started
        option: reload_target

# Stopping a task
- name: Stop sample task
    qem_task_status:
        name: "My Sample Task"
        server: "My Sample Server"
        state: stopped
'''

import json
from collections import OrderedDict
from ansible.module_utils.aem_client import AemTaskState, AemRunTaskReq, AemRunTaskOptions
from ansible.module_utils.qem_common import QemModuleBase

class QemTaskStatusManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=False, aliases=['task_name']),
            state=dict(default='present', choices=['present', 'absent', 'started', 'stopped']),
            server=dict(required=True, aliases=['replicate_server', 'compose_server']),
            timeout=dict(required=False, type='int', default=60),
            option=dict(required=False, choices=[e.name.lower() for e in AemRunTaskOptions], default=AemRunTaskOptions.RESUME_PROCESSING.name.lower())
        )

        self.state = None
        self.server = None
        self.name = None
        self.timeout = None
        self.option = None

        super(QemTaskStatusManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        states = {
            "started": self.start_task,
            "stopped": self.stop_task
        }
        self.results = dict(
            task_status=dict(
                name=self.name,
                server=self.server
            ),
            changed=False,
            msg=""
        )

        states.get(self.state)()

        return self.results


    def get_task_info(self):
        response = self.aem_client.get_task_list(self.server)
        if not response:
            return None
        matches = [task for task in response.taskList if task.name == self.name]
        if len(matches) > 0:
            return matches[0]
        return None


    def start_task(self):
        task_info = self.get_task_info()
        if not task_info:
            self.fail(msg="Task \"{0}\" not found on server \"{1}\"".format(self.name, self.server))
        if task_info.state != AemTaskState.RUNNING:
            try:
                result = self.aem_client.run_task(
                    payload=AemRunTaskReq(),
                    server=self.server,
                    task=self.name,
                    option=AemRunTaskOptions[self.option.upper()],
                    timeout=self.timeout)
                if result.state == AemTaskState.RUNNING:
                    self.results['changed'] = True
                    self.results['msg'] = 'task started'
            except Exception as ex:
                self.fail(msg=str(ex))


    def stop_task(self):
        task_info = self.get_task_info()
        if not task_info:
            self.fail(msg="Task \"{0}\" not found on server \"{1}\"".format(self.name, self.server))
        if task_info.state != AemTaskState.STOPPED:
            try:
                result = self.aem_client.stop_task(
                    server=self.server,
                    task=self.name,
                    timeout=self.timeout
                )
                self.results['changed'] = True
                self.results['msg'] = 'task started'
            except Exception as ex:
                self.fail(msg=str(ex))


def main():
    QemTaskStatusManager()


if __name__ == '__main__':
    main()
