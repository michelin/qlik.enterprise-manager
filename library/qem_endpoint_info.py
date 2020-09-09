#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_endpoint_info
short_description: Qlik Replicate endpoints info via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Return Qlik Replicate endpoint info using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the endpoint
        type: str
        required: False
        aliases:
            - endpoint_name
    server:
        description:
            - The server where the endpoint is defined
        type: str
        required: True
        aliases:
            - replicate_server

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Single endpoint info
- name: Single Endpoint info
    qem_endpoint_info:
        name: "My Endpoint"
        server: "My Sample Server"
    register: output

- name: Display info
    var: output.qem_endpoints[0]

# All endpoint info
- name: All endpoint info
    qem_endpoint_info:
        server: "My Sample Server"
    register: output

- name: Display info
    var: output.qem_endpoints
'''

import json
from collections import OrderedDict
from ansible.module_utils.aem_client import AemTaskState, AemRunTaskReq, AemRunTaskOptions
from ansible.module_utils.qem import QemModuleBase

class QemEndpointInfoManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=False, aliases=['endpoint_name']),
            server=dict(required=True, aliases=['replicate_server']),
        )

        self.server = None
        self.name = None

        super(QemEndpointInfoManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        self.results = dict(
            endpoint=dict(
                name=self.name,
                server=self.server
            ),
            changed=False,
            msg=""
        )
        self.results['qem_endpoints'] = self.get_endpoints_info()
        return self.results

    def get_endpoints_info(self):
        response = self.aem_client.get_endpoint_list(self.server)
        if not response:
            return None
        endpoints = []
        if self.name:
            endpoints = [endpoint for endpoint in response.endpointList if endpoint.name == self.name]
        else:
            endpoints = response.endpointList
        return map(self.endpoint_mapper, endpoints)

    def endpoint_mapper(self, endpoint):
        return {
            'name': endpoint.name,
            'description': endpoint.description,
            'role':  endpoint.role.name,
            'type':  endpoint.type,
            'is_licensed': endpoint.is_licensed
        }

def main():
    QemEndpointInfoManager()


if __name__ == '__main__':
    main()
