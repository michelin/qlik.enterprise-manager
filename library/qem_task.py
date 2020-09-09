#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}
DOCUMENTATION = '''
---
module: qem_task
short_description: Manage Qlik Replicate/Compose task via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Manage Qlik Replicate/Compose task using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the task, if set will override the name present the task definition
        type: str
        required: False
        aliases:
            - task_name
    state:
        description:
            - If I(state=present), task will be added
            - If I(state=absent), task will be deleted
        default: present
        choices:
            - present
            - absent
    server:
        description:
            - The server to import the task
        type: str
        required: True
        aliases:
            - replicate_server
            - compose_server
    definition:
        description:
            - The task definition in JSON
        required: False
    delete_task_logs:
        description:
            - Wether or not the logs should be deleted when the task is deleted
        type: bool
        default: True
    force_task_stop:
        description:
            - Force to stop the task before deletion
        type: bool
        default: False
    force_task_timeout:
        description:
            - A timeout in seconds before raising an issue during the task stopping
        type: int
        default: 60
        required: False

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Removing a task
- name: Delete sample task
    qem_task:
        name: "My Sample Task"
        server: "My Sample Server"
        state: absent
        force_task_stop: yes

# Importing a task based on a local JSON file
- name: Import sample task
    qem_task:
        name: "My Sample Task"
        server: "My Sample Server"
        state: present
        definition: |
        {
            "name": "MyTask",
            "cmd.replication_definition": {
                "tasks":    [{
                        "task": {
                            "name": "daniel",
                            "source_name": "MyDB",
                            "target_names": ["MyKafka"]
                        },
                        "source": {
                            "rep_source": {
                                "source_name": "MyDB",
                                "database_name": "MyDB"
                            },
                            "source_tables": {
                                "name": "MyDB"
                            }
                        },
                        "targets":    [{
                                "rep_target": {
                                    "target_name": "MyKafka",
                                    "target_state": "DISABLED",
                                    "database_name": "MyKafka"
                                }
                            }],
                        "task_settings": {
                            "source_settings": {
                            },
                            "target_settings": {
                                "queue_settings": {
                                    "message_shape": {
                                    },
                                    "key_shape": {
                                    }
                                },
                                "ftm_settings": {
                                }
                            },
                            "sorter_settings": {
                                "local_transactions_storage": {
                                }
                            },
                            "common_settings": {
                                "change_table_settings": {
                                    "header_columns_settings": {
                                    }
                                },
                                "audit_table_settings": {
                                },
                                "dr_settings": {
                                },
                                "statistics_table_settings": {
                                },
                                "bidi_table_settings": {
                                },
                                "task_uuid": "87b841df-7b9a-8041-9666-fa4454d79023",
                                "status_table_settings": {
                                },
                                "suspended_tables_table_settings": {
                                },
                                "history_table_settings": {
                                },
                                "exception_table_settings": {
                                },
                                "recovery_table_settings": {
                                },
                                "data_batching_settings": {
                                },
                                "data_batching_table_settings": {
                                },
                                "log_stream_settings_depricated": {
                                },
                                "ddl_history_table_settings": {
                                },
                                "customized_charset_settings": {
                                    "validation": {
                                        "sub_char": 0
                                    }
                                }
                            }
                        }
                    }],
                "databases": []
            }    
        }
'''

import json
import ast
from collections import OrderedDict
from ansible.module_utils.aem_client import AemTaskState
from ansible.module_utils.qem_common import QemModuleBase


class QemTaskManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=False, aliases=['task_name']),
            state=dict(default='present', choices=['present', 'absent', 'started', 'stopped']),
            server=dict(required=True, aliases=['replicate_server', 'compose_server']),
            definition=dict(required=False),
            delete_task_logs=dict(required=False, type='bool', default=True),
            force_task_stop=dict(required=False, type='bool', default=False),
            force_task_timeout=dict(required=False, type='int', default=60),
        )

        self.state = None
        self.server = None
        self.name = None
        self.definition = None
        self.delete_task_logs = None
        self.force_task_stop = None
        self.force_task_timeout = None

        super(QemTaskManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        if self.definition:
            self.task_object = json.loads(self.definition, object_pairs_hook=OrderedDict)
            if not self.name:
                self.name = self.task_object['cmd.replication_definition']['tasks'][0]['task']['name']
            else:
                self.task_object['cmd.replication_definition']['tasks'][0]['task']['name'] = self.name

        states = {
            "present": self.import_task,
            "absent": self.delete_task,
        }
        self.results = dict(
            task=dict(
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

    def import_task(self):
        if not self.get_task_info():
            try:
                self.aem_client.import_task(
                    payload=json.dumps(self.task_object, indent=None),
                    server=self.server,
                    task=self.name
                )
                self.results['changed'] = True
                self.results['msg'] = 'task imported'
            except Exception as ex:
                self.fail(msg=str(ex))

    def delete_task(self):
        task_info = self.get_task_info()
        if task_info:
            try:
                if task_info.state != AemTaskState.STOPPED and self.force_task_stop:
                    result = self.aem_client.stop_task(
                        server=self.server,
                        task=self.name,
                        timeout=self.force_task_timeout
                    )

                self.aem_client.delete_task(
                    server=self.server,
                    task=self.name,
                    deletetasklogs=self.delete_task_logs
                )

                self.results['changed'] = True
                self.results['msg'] = 'task deleted'
            except Exception as ex:
                self.fail(msg=str(ex))


def main():
    QemTaskManager()


if __name__ == '__main__':
    main()
