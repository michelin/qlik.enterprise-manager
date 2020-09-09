#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_acl
short_description: Manage Qlik Replicate/Compose ACL via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Manage Attunity Replicate/Compose Access Control List (ACL) using the Attunity Enterprise Manager API Python client
options:
    name:
        description:
            - The name of the user/group in a Windows format (ie. <DOMAIN>\<Username or Groupname>)
        type: str
        required: True
    state:
        description:
            - If I(state=present), ACL will be added
            - If I(state=absent), ACL will be deleted
        default: present
        choices:
            - present
            - absent
    server:
        description:
            - The server to apply the ACL
        required: True
        aliases:
            - replicate_server
            - compose_server
    role:
        description:
            - The role impacted by the ACL
        choices:
            - admin
            - designer
            - operator
            - viewer
    type:
        description:
            - The ACL is applied on a User or a Group
        choices:
            - user
            - group

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Apply a simple ACL
- name: Apply ACL
    qem_acl:
        server: "My Sample Server"
        name: "CONTOSO\\User1"
        type: "user"
        role: "admin"
        state: "present"

# Apply multiple ACL in one task
- name: Apply ACL
    qem_acl:
        server: "My Sample Server"
        name: "{{ item.name }}"
        type: "{{ item.type }}"
        role: "{{ item.role }}"
        state: "{{ item.state }}"
    with_items:
        - { name: "CONTOSO\\User2", type: "user", role: "designer", state: "present"}
        - { name: "CONTOSO\\User3", type: "user", role: "operator", state: "absent"}
        - { name: "CONTOSO\\Group", type: "group", role: "viewer", state: "present"}
'''

import json
from collections import OrderedDict
from ansible.module_utils.aem_client import AemAuthorizationAcl, AemRoleDef, AemUserRef, AemGroupRef
from ansible.module_utils.qem_common import QemModuleBase

class QemAclManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=True),
            state=dict(default='present', choices=['present', 'absent']),
            server=dict(required=True, aliases=['replicate_server', 'compose_server']),
            role=dict(default='viewer', choices=['admin', 'designer', 'operator', 'viewer']),
            type=dict(default='user', choices=['user', 'group']),
        )

        self.state = None
        self.name = None
        self.server = None
        self.role = None
        self.type = None

        super(QemAclManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        states = {
            "present": self.create_acl,
            "absent": self.delete_acl,
        }

        roles = {
            "admin": "admin_role",
            "designer": "designer_role",
            "operator": "operator_role",
            "viewer": "viewer_role"
        }
        types = {
            "user": "users",
            "group": "groups",
        }

        self.ref = AemUserRef({"name": self.name}) if self.type == "user" else AemGroupRef({"name": self.name})
        self.acl_role = roles.get(self.role)
        self.acl_type = types.get(self.type)

        self.results = dict(
            acl=dict(
                name=self.name,
                role=self.role,
                server=self.server
            ),
            changed=False,
            msg=""
        )

        states.get(self.state)()

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


    def has_exact_acl(self, acl):
        roles = getattr(acl, self.acl_role)
        refs = getattr(roles, self.acl_type)
        return len([ref for ref in refs if ref.name == self.name]) > 0

    def update_acl(self, acl, func):
        roles = getattr(acl, self.acl_role)
        refs = getattr(roles, self.acl_type)
        refs = func(refs)
        setattr(roles, self.acl_type, refs)
        setattr(acl, self.acl_role, roles)
        return acl


    def add_acl(self, refs):
        refs.append(self.ref)
        return refs


    def create_acl(self):
        acl = self.get_server_acl()
        if not acl:
            self.fail(msg="Impossible to get ACL for server \"{0}\"".format(self.server))
        if not self.has_exact_acl(acl):
            acl = self.update_acl(acl, self.add_acl)

            try:
                self.aem_client.put_server_acl(
                    payload=acl,
                    server=self.server,
                )
                self.results['changed'] = True
                self.results['msg'] = 'ACL created'
            except Exception as ex:
                self.fail(msg=str(ex))



    def delete_acl(self):
        acl = self.get_server_acl()
        if not acl:
            self.fail(msg="Impossible to get ACL for server \"{0}\"".format(self.server))
        for role in ['admin_role', 'designer_role', 'operator_role', 'viewer_role']:
            for typ in ['users', 'groups']:
                role_def = getattr(acl, role)
                typ_def = getattr(role_def, typ)
                updated = filter(lambda it: it.name.upper() != self.name.upper(), typ_def)
                changed = len(updated) == len(typ_def)
                setattr(role_def, typ, updated)
                setattr(acl, role, role_def)
        if changed:
            try:
                self.aem_client.put_server_acl(
                    payload=acl,
                    server=self.server,
                )
                self.results['changed'] = True
                self.results['msg'] = 'ACL deleted'
            except Exception as ex:
                self.fail(msg=str(ex))


def main():
    QemAclManager()


if __name__ == '__main__':
    main()
