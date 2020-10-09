#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_endpoint
short_description: Manage Qlik Replicate/Compose endpoint via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Manage Qlik Replicate/Compose endpoint using the Qlik Enterprise Manager API Python client. If the endpoint already exists on the target server, the import will override its configuration.
    - The endpoint will be created according to the target QEM version.
    - There are no backward compatibility guarantees if you try to import an endpoint definition (eg. 6.6) on a old QEM instance (eg. 6.4).
options:
    name:
        description:
            - The name of the endpoint, if set will override the name present of the first endpoint definition
        type: str
        required: False
        aliases:
            - endpoint_name
    state:
        description:
            - If I(state=present), endpoint will be added/updated
            - If I(state=absent), endpoint will be deleted
        default: present
        choices:
            - present
            - absent
    server:
        description:
            - The server to import the endpoint
        type: str
        required: True
        aliases:
            - replicate_server
            - compose_server
    definition:
        description:
            - The endpoint definition in JSON
        type: str
        required: False

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Removing an endpoint
- name: Delete sample endpoint
    qem_endpoint:
        name: "My Sample Endpoint"
        server: "My Sample Server"
        state: absent

# Importing a endpoint base on a local JSON file
- name: Import sample endpoint
    qem_endpoint:
        name: "My Sample Endpoint"
        server: "My Sample Server"
        state: present
        definition: |
        {
            "name": "MyDB",
            "role": "SOURCE",
            "is_licensed": true,
            "type_id": "ORACLE_COMPONENT_TYPE",
            "db_settings": {
                "$type": "OracleSettings",
                "syntax": "Oracle",
                "username": "Scott",
                "password": "{{ Qlik_db_password }}",
                "server": "//db.contoso.com:1521",
                "useLogminerReader": false,
                "accessAlternateDirectly": false,
                "emptyStringValue": " "
            },
            "override_properties": {
                "name": "default"
            }
        }
'''

import json
import time
import uuid
from collections import OrderedDict
from ansible.module_utils.qem_common import QemModuleBase

DUMMY_TASK_TEMPLATE = '''
{
    "name":    "New Task__2020-02-12--23-11-16-297171",
    "cmd.replication_definition": {
        "tasks":    [{
                "task": {
                    "name":    "TASK_NAME",
                    "source_name":    "DUMMY_SOURCE",
                    "target_names":    ["DUMMY_TARGET"]
                },
                "source": {
                    "rep_source": {
                        "source_name":    "DUMMY_SOURCE",
                        "database_name":    "DUMMY_SOURCE"
                    },
                    "source_tables": {
                        "name":    "DUMMY_SOURCE"
                    }
                },
                "targets":    [{
                        "rep_target": {
                            "target_name":    "DUMMY_TARGET",
                            "target_state":    "DISABLED",
                            "database_name":    "DUMMY_TARGET"
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
                        "apply_changes_enabled":    false,
                        "dr_settings": {
                        },
                        "statistics_table_settings": {
                        },
                        "bidi_table_settings": {
                        },
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
                                "sub_char":    0
                            }
                        }
                    }
                }
            }],
        "databases":    []
    }
}
'''

DUMMY_SOURCE = '''
{
    "name": "DUMMY_SOURCE",
    "role": "SOURCE",
    "is_licensed": true,
    "type_id": "FILE_COMPONENT_TYPE",
    "db_settings": {
        "$type": "FileSettings"
    },
    "override_properties": {
    }
}
'''

DUMMY_TARGET = '''
{
    "name": "DUMMY_TARGET",
    "role": "TARGET",
    "is_licensed": true,
    "type_id": "NULL_TARGET_COMPONENT_TYPE",
    "db_settings": {
        "$type": "NulltargetSettings"
    },
    "override_properties": {
    }
}
'''


class QemEndpointManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=False, aliases=['endpoint_name']),
            state=dict(default='present', choices=['present', 'absent']),
            server=dict(required=True, aliases=['replicate_server', 'compose_server']),
            definition=dict(required=False),
        )

        self.state = None
        self.server = None
        self.name = None
        self.definition = None

        super(QemEndpointManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        if self.definition:
            self.endpoint_object = json.loads(self.definition, object_pairs_hook=OrderedDict)
            if not self.name:
                self.name = self.endpoint_object['name']
            else:
                self.endpoint_object['name'] = self.name

        states = {
            "present": self.import_endpoint,
            "absent": self.delete_endpoint,
        }
        self.results = dict(
            endpoint=dict(
                name=self.name,
                server=self.server
            ),
            changed=False,
            msg=""
        )

        states.get(self.state)()

        return self.results

    def get_endpoint_info(self):
        response = self.aem_client.get_endpoint_list(self.server)
        if not response:
            return None
        matches = [endpoint for endpoint in response.endpointList if endpoint.name == self.name]
        if len(matches) > 0:
            return matches[0]
        return None

    def get_server_version(self):
        response = self.aem_client.get_server_details(server=self.server)
        version = response.server_details.version
        version_parts = version.split('.')
        return dict(
            version=version,
            version_major=version_parts[0],
            version_minor=version_parts[1],
            version_revision=version_parts[3]
        )

    def import_endpoint(self):
        # QEM does not provide a direct API to create endpoints. Nevertheless, the endpoints are created if a task is imported.
        # The "trick" is to generate a dummy task which will piggyback the endpoint to create.
        # Since Task is a composed by a source and a target, depenending of what the user want to import we need to generate the dual:
        # - If we try to import a source, we generate a dummy target based on the handly NullTarget
        # - If we try to import a target, we generate a dummy source based on the FileSource
        # Once imported, we wait a couple of seconds, it look like the task/endpoint creation is asyn thus we need to be sure everything exists before movin on
        # Once we are sure the creation succeed, we delete the dummy task and endpoint (source of target) to let on the server only the endpoint the user wants to import.
        import_task = json.loads(DUMMY_TASK_TEMPLATE, object_pairs_hook=OrderedDict)
        transaction_id = uuid.uuid1()
        task_name = 'ansible-import-endpoint-{0}'.format(transaction_id)
        import_task['cmd.replication_definition']['tasks'][0]['task']['name'] = task_name
        dummy_endpoint_name = 'ansible-import-endpoint-dummy-{0}'.format(transaction_id)
        # Qlik Replicate backward compatibility consists in fallbacking to the default options if no explicit version set
        # We use the one from the target cluster, this means you need consistency accross your environments
        import_task["_version"] = self.get_server_version()
        if self.endpoint_object['role'] != 'SOURCE' and self.endpoint_object['role'] != 'TARGET':
            self.fail(msg='Import a endpoint with Role=BOTH or ROLE=ALL is not yet implemented.')

        if self.endpoint_object['role'] == 'SOURCE':
            dummy_target = json.loads(DUMMY_TARGET, object_pairs_hook=OrderedDict)
            dummy_target['name'] = dummy_endpoint_name
            import_task['cmd.replication_definition']['tasks'][0]['task']['source_name'] = self.endpoint_object['name']
            import_task['cmd.replication_definition']['tasks'][0]['task']['target_names'] = [dummy_target['name']]

            import_task['cmd.replication_definition']['tasks'][0]['source']['rep_source']['source_name'] = self.endpoint_object['name']
            import_task['cmd.replication_definition']['tasks'][0]['source']['rep_source']['database_name'] = self.endpoint_object['name']
            import_task['cmd.replication_definition']['tasks'][0]['source']['source_tables']['name'] = self.endpoint_object['name']

            import_task['cmd.replication_definition']['tasks'][0]['targets'][0]['rep_target']['target_name'] = dummy_target['name']
            import_task['cmd.replication_definition']['tasks'][0]['targets'][0]['rep_target']['database_name'] = dummy_target['name']

            import_task['cmd.replication_definition']['databases'].insert(0, self.endpoint_object)
            import_task['cmd.replication_definition']['databases'].insert(1, dummy_target)

        if self.endpoint_object['role'] == 'TARGET':
            dummy_source = json.loads(DUMMY_SOURCE, object_pairs_hook=OrderedDict)
            dummy_source['name'] = dummy_endpoint_name

            import_task['cmd.replication_definition']['tasks'][0]['task']['source_name'] = dummy_source['name']
            import_task['cmd.replication_definition']['tasks'][0]['task']['target_names'] = [self.endpoint_object['name']]

            import_task['cmd.replication_definition']['tasks'][0]['source']['rep_source']['source_name'] = dummy_source['name']
            import_task['cmd.replication_definition']['tasks'][0]['source']['rep_source']['database_name'] = dummy_source['name']
            import_task['cmd.replication_definition']['tasks'][0]['source']['source_tables']['name'] = dummy_source['name']

            import_task['cmd.replication_definition']['tasks'][0]['targets'][0]['rep_target']['target_name'] = self.endpoint_object['name']
            import_task['cmd.replication_definition']['tasks'][0]['targets'][0]['rep_target']['database_name'] = self.endpoint_object['name']

            import_task['cmd.replication_definition']['databases'].insert(0, dummy_source)
            import_task['cmd.replication_definition']['databases'].insert(1, self.endpoint_object)

        try:
            self.aem_client.import_task(
                payload=json.dumps(import_task, indent=None),
                server=self.server,
                task=task_name
            )
            time.sleep(5) # Wait for task to be created... could be improved by an loop checking if aem_client.get_task_details returns actually the task
            self.aem_client.delete_task(
                server=self.server,
                task=task_name,
                deletetasklogs=True
            )
            self.aem_client.delete_endpoint(
                server=self.server,
                endpoint=dummy_endpoint_name
            )
            self.results['changed'] = True
            self.results['msg'] = 'endpoint imported'
        except Exception as ex:
            self.fail(msg=str(ex))

    def delete_endpoint(self):
        if self.get_endpoint_info():
            try:
                self.aem_client.delete_endpoint(
                    server=self.server,
                    endpoint=self.name
                )
                self.results['changed'] = True
                self.results['msg'] = 'endpoint deleted'
            except Exception as ex:
                self.fail(msg=str(ex))


def main():
    QemEndpointManager()


if __name__ == '__main__':
    main()
