#!/usr/bin/python

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: qem_acl
short_description: Manage Qlik Replicate/Compose license registration via Qlik Enterprise Manager (QEM)
version_added: "1.0"
description:
    - Manage Qlik Replicate/Compose license registration using the Qlik Enterprise Manager API Python client
options:
    qem_hostname:
        description:
            - Qlik Enterprise manager host name.
        type: str
        required: False
    qem_domain:
        description:
            - Active Directory domain where to find the user.
        type: str
        required: False
    qem_username:
        description:
            - Active Directory user to connect to Qlik Enterprise Manager.
        type: str
        required: False
    qem_password:
        description:
            - Active Directory user password.
        type: str
        required: False
    qem_verify_certificate:
        description:
            - Wether or not the server certificate should be verifies.
        type: bool
        default: True
    profile:
        description:
            - Security profile found in ~/.qem/credentials file.
        type: str
        required: False
    name:
        description:
            - The server to register the license
        type: str
        required: True
        aliases:
            - replicate_server
            - compose_server
    license:
        description:
            - The license information
        type: str
        required: True
    force:
        description:
            - Wether or not we force the license registration
        type: bool
        default: 'no'

author:
    - Daniel Petisme (daniel.petisme@michelin.com)
'''
EXAMPLES = '''
# Register a license
    - name: Add Replicate Server temporal license
        qem_license:
            name: "My Sample Server"
            license: |
                #
                # Qlik  License
                # Generated on 01-Oct-2019 12:00:00.0000+03:00
                # License Comment:
                #
                license_type=EVALUATION_LICENSE
                licensed_to=CONTOSO
                licensed_by=Qlik EMEA
                serial_no=70016519
                expiration_date=2019-11-01
                hosts=
                source_types=Oracle
                target_types=Kafka,ADLS,SQLServer,AzureSQLServer,Oracle,LogStream
                features=
                version=6.3
                issue_date=2019-10-02
                checksum=9537H-2QRQ5-CF289-C3JRE
'''

import json
from ansible.module_utils.qem import QemModuleBase
from ansible.module_utils.aem_client import AemLicenseState

class QemLicenseManager(QemModuleBase):

    def __init__(self):

        self.module_arg_spec = dict(
            name=dict(required=True, aliases=['server', 'replicat_server', 'compose_server']),
            license=dict(required=False),
            force=dict(required=False, type='bool', default=False)
        )

        self.force = None
        self.name = None
        self.license = None

        super(QemLicenseManager, self).__init__(derived_arg_spec=self.module_arg_spec)

    def exec_module(self, **kwargs):

        for key in list(self.module_arg_spec.keys()):
            setattr(self, key, kwargs[key])

        self.results = dict(
            name=self.name,
            changed=False,
            msg=""
        )

        self.import_license()

        return self.results

    def get_server_details(self):
        try:
            response = self.aem_client.get_server_details(self.name)
            return response.server_details if response else None
        except Exception:
            return None


    def import_license(self):
        server_details = self.get_server_details()
        if not server_details:
            self.fail(msg="Server \"{0}\" not found".format(self.name))
        license = server_details.license
        is_valid_license = license.state == AemLicenseState.VALID_LICENSE
        if not is_valid_license or self.force:
            try:
                self.aem_client.put_server_license(
                    payload=self.license,
                    server=self.name
                )
                self.results['changed'] = True
                self.results['msg'] = 'license added'
            except Exception as ex:
                self.fail(msg=str(ex))


def main():
    QemLicenseManager()


if __name__ == '__main__':
    main()
