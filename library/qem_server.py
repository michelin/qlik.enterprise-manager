#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_server
short_description: Create or delete Qlik Replicate/Compose servers in Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Create or remove Qlik Replicate/Compose servers using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the server
        type: str
        required: True
        aliases:
            - server
    state:
        description:
            - If I(state=present), server will be created
            - If I(state=absent), server will be deleted
        default: present
        choices:
            - present
            - absent
    description:
        description:
            - The description of the server
        type: str
        required: False
    host:
        description:
            - The host of the server
        type: str
        required: False
    port:
        description:
            - The connection port of the server
        type: int
        required: False
    verify_server_certificate:
        description:
            - Wether or not the server certificate should be verified
        type: bool
        default: False
    username:
        description:
            - The user to connect to the server in a Windows format (ie. <DOMAIN>\<Username>)
        type: str
        required: False
    password:
        description:
            - The user's password to connect to the server
        type: str
        required: False
    monitored:
        description:
            - Wether or not the server should be monitored by Qlik Enterprise Manager
        type: bool
        default: False
    type:
        description:
            - If I(type=replicate), create a Replicate server
            - If I(type=compose), create a Compose server
        default: replicate
        choices:
            - replicate
            - compose

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Delete the server named "My Sample Server"
- name: Delete Server
    qem_server:
        name: "My Sample Server"
        state: absent

# Create a Replicate server named "My Sample Server"
- name: Create Server
    qem_server:
        name: "My Sample Server"
        description: "Created By Ansible"
        host: "localhost"
        port: "443"
        username: "CONTOSO\\John"
        password: "p4ssw0rd"
        monitored: True
        verify_server_certificate: False
        state: present
'''

import json
from ansible.module_utils.aem_client import AemReplicateServer, AemComposeServer
from ansible.module_utils.qem_common import QemModuleBase

class QemServerManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=True, aliases=['server']),
            state=dict(default='present', choices=['present', 'absent']),
            description=dict(required=False, default=""),
            host=dict(required=False),
            port=dict(required=False, type='int', default=443),
            verify_server_certificate=dict(required=False, type='bool', default=True),
            username=dict(required=False),
            password=dict(required=False, no_log=True),
            monitored=dict(required=False, type='bool', default=True),
            type=dict(default='replicate', choices=['replicate', 'compose'])
        )

        self.state = None
        self.name = None
        self.description = None
        self.host = None
        self.port = None
        self.verify_server_certificate = None
        self.username = None
        self.password = None
        self.monitored = None
        self.type = None

        super(QemServerManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        states = {
            "present": self.create_server,
            "absent": self.delete_server,
        }
        self.results = dict(
            name=self.name,
            changed=False,
            msg=""
        )

        states.get(self.state)()

        return self.results

    def is_server_present(self):
        try:
            server = self.aem_client.get_server(self.name)
            return server
        except Exception as e:
            return None

    def create_server(self):
        if not self.is_server_present():
            server = AemReplicateServer() if self.type == 'replicate' else AemComposeServer()
            server.name=self.name
            server.description=self.description
            server.host=self.host
            server.port=self.port
            server.username=self.username
            server.password=self.password
            server.monitored=self.monitored
            server.verify_server_certificate=self.verify_server_certificate
            try:
                self.aem_client.put_server(
                    payload=server,
                    server=server.name
                )
                self.results['changed'] = True
                self.results['msg'] = 'server created'
            except Exception as ex:
                self.fail(msg=str(ex))

    def delete_server(self):
        if self.is_server_present():
            try:
                self.aem_client.delete_server(
                    server=self.name,
                )
                self.results['changed'] = True
                self.results['msg'] = 'server deleted'
            except Exception as ex:
                self.fail(msg=str(ex))


def main():
    QemServerManager()


if __name__ == '__main__':
    main()
