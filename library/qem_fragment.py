class ModuleDocFragment(object):

    # QEM doc fragment
    DOCUMENTATION = r'''
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

notes:
    - For authentication with Qlik Enterprise Manager you can pass parameters, set environment variables,
      use a profile stored in ~/.qem/credentials.
    - To authenticate via module parameters qem_hostname, qem_domain, qem_username, qem_password,
      qem_verify_certificate or set environment variables QEM_HOSTNAME, QEM_DOMAIN, QEM_USERNAME, QEM_PASSWORD,
      QEM_VERIFY_CERTIFICATE.
    - "Alternatively, credentials can be stored in ~/.qem/credentials. This is an ini file containing
      a [default] section and the following keys: qem_hostname, qem_domain, qem_username, qem_password,
      qem_verify_certificate. It is also possible to add additional profiles. Specify the profile by passing profile or
      setting QEM_PROFILE in the environment."
'''