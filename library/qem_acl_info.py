#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_acl_info
short_description: Qlik Replicate ACLs info via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Return Attunity Replicate acl info using the Qlik Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the acl
        type: str
        required: False
        aliases:
            - acl_name
    server:
        description:
            - The server where the acl is defined
        type: str
        required: True
        aliases:
            - replicate_server

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Single acl info
- name: Single ACL info
    qem_acl_info:
        name: "CONTOSO\\User2"
        server: "My Sample Server"
    register: output

- name: Display inheritance info
    var: output.qem_acls.disable_inheritance

# All acl info
- name: All acl info
    qem_acl_info:
        server: "My Sample Server"
    register: output

- name: Display info
    var: output.qem_acls.acl
'''

import json
from collections import OrderedDict
from ansible.module_utils.aem_client import AemAuthorizationAcl, AemRoleDef, AemUserRef, AemGroupRef
from ansible.module_utils.qem_common import QemModuleBase

class QemACLInfoManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=False, aliases=['acl_name']),
            server=dict(required=True, aliases=['replicate_server']),
        )

        self.server = None
        self.name = None

        super(QemACLInfoManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        self.results = dict(
            acl=dict(
                name=self.name,
                server=self.server
            ),
            changed=False,
            msg=""
        )
        self.results['qem_acls'] = self.get_acls_info()
        return self.results


    def init_acl(self):
        acl = AemAuthorizationAcl()
        acl.disable_inheritance = False
        acl.admin_role = AemRoleDef()
        acl.designer_role = AemRoleDef()
        acl.operator_role = AemRoleDef()
        acl.viewer_role = AemRoleDef()
        return acl


    def get_server_acl(self):
        try:
            return self.aem_client.get_server_acl(self.server)
        except Exception as e:
            if e.error_code == "AEM_SERVER_HAS_NO_ACL":
                return self.init_acl()
        return None


    def get_acls_info(self):
        acl = self.get_server_acl()
        acl_list = []
        acl_list.extend(self.to_acl_list("admin", acl.admin_role))
        acl_list.extend(self.to_acl_list("designer", acl.designer_role))
        acl_list.extend(self.to_acl_list("operator", acl.operator_role))
        acl_list.extend(self.to_acl_list("viewer", acl.viewer_role))
        if self.name:
            acl_list =  [item for item in acl_list if item['name'] == self.name]
        return { 'disable_inheritance': acl.disable_inheritance, 'acl': acl_list}


    def to_acl_list(self, role, role_def):
        acl_list = []
        acl_list.extend(map(lambda acl: { 'name': acl.name, 'type': 'user', 'role': role}, role_def.users))
        acl_list.extend(map(lambda acl: { 'name': acl.name, 'type': 'group', 'role': role}, role_def.groups))
        return acl_list


def main():
    QemACLInfoManager()


if __name__ == '__main__':
    main()
