import ast
import base64
import json
import os
from os.path import expanduser
from ansible.module_utils.aem_client import *
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six.moves import configparser

try:
    from ansible.module_utils.basic import missing_required_lib
except Exception:
    def missing_required_lib(msg, reason=None, url=None):
        return msg


QEM_COMMON_ARGS = dict(
    qem_hostname=dict(required=False),
    qem_domain=dict(required=False),
    qem_username=dict(required=False),
    qem_password=dict(required=False, no_log=True),
    qem_verify_certificate=dict(required=False, type='bool', default=True),
    profile=dict(required=False)
)

QEM_ENV_MAPPING = dict(
    qem_hostname='QEM_HOSTNAME',
    qem_domain='QEM_DOMAIN',
    qem_username='QEM_USERNAME',
    qem_password='QEM_PASSWORD',
    qem_verify_certificate='QEM_VERIFY_CERTIFICATE',
    profile='QEM_PROFILE'
)

class QemModuleBase(object):
    def __init__(self, derived_arg_spec):

        merged_arg_spec = dict()
        merged_arg_spec.update(QEM_COMMON_ARGS)

        if derived_arg_spec:
            merged_arg_spec.update(derived_arg_spec)

        self.module = AnsibleModule(argument_spec=merged_arg_spec)
        credentials = self._get_credentials(self.module.params)
        if not credentials:
            self.fail(msg="Impossible to retrieve credentials from (in order) the module parameters, env vars or ~/.qem/credentials profile file")
        try:
            self.aem_client = self.get_qem_client(**credentials)
        except Exception as e:
            self.fail(msg=str(e))

        result = self.exec_module(**self.module.params)
        self.module.exit_json(**result)

    def exec_module(self, **kwargs):
        self.fail("Error: {0} failed to implement exec_module method.".format(self.__class__.__name__))


    def get_qem_client(self, qem_hostname=None, qem_domain=None, qem_username=None, qem_password=None, qem_verify_certificate=None, **kwargs):
        if type(qem_verify_certificate) is str:
            qem_verify_certificate = ast.literal_eval(qem_verify_certificate)
        try:
            b64_username_password = base64.b64encode(
                '{0}\\{1}:{2}'.format(qem_domain, qem_username, qem_password)
            ).decode('ascii')
            return AemClient(
                b64_username_password=b64_username_password,
                machine_name=qem_hostname,
                verify_certificate=qem_verify_certificate
            )
        except Exception as e:
            raise


    def _get_credentials(self, params):
        arg_credentials = dict()
        for attribute, env_variable in QEM_ENV_MAPPING.items():
            arg_credentials[attribute] = params.get(attribute, None)

        # precedence: module parameters -> environment variables -> default profile in ~/.qem/credentials
        # try module params
        if arg_credentials['profile'] is not None:
            self.log('Retrieving credentials with profile parameter.')
            credentials = self._get_profile(arg_credentials['profile'])
            return credentials

        if arg_credentials['qem_hostname']:
            self.log('Received credentials from parameters.')
            return arg_credentials

        # try environment
        env_credentials = self._get_env_credentials()
        if env_credentials:
            self.log('Received credentials from env.')
            return env_credentials

        # try default profile from ~./qem/credentials
        default_credentials = self._get_profile()
        if default_credentials:
            self.log('Retrieved default profile credentials from ~/.qem/credentials.')
            return default_credentials

    def _get_profile(self, profile="default"):
        path = expanduser("~/.qem/credentials")
        try:
            config = configparser.ConfigParser()
            config.read(path)
        except Exception as exc:
            self.fail("Failed to access {0}. Check that the file exists and you have read "
                        "access. {1}".format(path, str(exc)))
        credentials = dict()
        for key in QEM_ENV_MAPPING:
            try:
                credentials[key] = config.get(profile, key, raw=True)
            except Exception:
                pass

        if credentials.get('qem_hostname'):
            return credentials

        return None

    def _get_env_credentials(self):
        env_credentials = dict()
        for attribute, env_variable in QEM_ENV_MAPPING.items():
            env_credentials[attribute] = os.environ.get(env_variable, None)

        if env_credentials['profile']:
            credentials = self._get_profile(env_credentials['profile'])
            return credentials

        if env_credentials.get('qem_hostname') is not None:
            return env_credentials

        return None


    def fail(self, msg, **kwargs):
        self.module.fail_json(msg=msg, **kwargs)

    def log(self, msg, pretty_print=False):
        if pretty_print:
            self.module.debug(json.dumps(msg, indent=4, sort_keys=True))
        else:
            self.module.debug(msg)
