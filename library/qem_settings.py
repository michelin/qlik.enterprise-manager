#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_settings
short_description: Apply Qlik Replicate/Compose settings in Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Apply Qlik Replicate/Compose settings using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the server
        type: str
        required: True
        aliases:
            - server
    settings:
        description:
            - The settings to apply
        type: str
        required: true

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Apply settings to the server named "My Sample Server"
- name: Delete Server
    qem_settings:
        name: "My Sample Server"
        settings: "{{ lookup('file', 'my-settings.json')}}"
'''

import json
from ansible.module_utils.aem_client import AemReplicateServer, AemComposeServer
from ansible.module_utils.qem_common import QemModuleBase

class QemSettingsManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=True, aliases=['server']),
            settings=dict(required=False, default="")
        )

        self.name = None
        self.settings = None

        super(QemSettingsManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        self.results = dict(
            name=self.name,
            changed=False,
            msg=""
        )

        self.import_settings()

        return self.results

    def is_server_present(self):
        try:
            server = self.aem_client.get_server(self.name)
            return server
        except Exception as e:
            return None

    def import_settings(self):
        if self.is_server_present():
            try:
                self.aem_client.import_all(
                    payload=self.settings,
                    server=self.name
                )
                self.results['changed'] = True
                self.results['msg'] = 'Settings imported'
            except Exception as ex:
                self.fail(msg=str(ex))

def main():
    QemSettingsManager()


if __name__ == '__main__':
    main()
