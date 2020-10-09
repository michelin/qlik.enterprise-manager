# Ansible Qlik Enterprise Manager

Ansible role to automate [Qlik](https://www.qlik.com/us/products/data-integration-products) (former Attunity) resource management.

## Introduction
This Ansible role provides a way to automate the interactions with Qlik Enterprise Manager API to manage the servers, endpoints and tasks.

The ansible module requires Python 3.

## Installation

You can use ansible galaxy to install the role in the `$ANSIBLE_ROLES_PATH` or use the `--roles-path` flag to change the destination.
```
ansible-galaxy install qlik.enterprise-manager
```

Otherwise you can use git submodule system to install locally the role.
Given `./lib` a folder in your Ansible project containing 3rd-party roles, you can run the following command:
```
git submodule add <url> ./lib/qlik.enterprise-manager
```

Be sure you configured properly the [`role search path`](https://docs.ansible.com/ansible/latest/user_guide/playbooks_reuse_roles.html#role-search-path).
Here you have an example for the mentionned `./lib`
```
[defaults]
roles_path = roles:lib
```

## Usage
You need to import the role

```
---
- hosts: localhost[0]
  connection: local
  gather_facts: False
  roles:
  - role: qlik.enterprise-manager # load the Ansible Qlik Enterprise
```
## Documentation

See the bundled [Modules Documentation](MODULES.md)

### Generating documentation
To generate the documentation you need to install `jinja2` (`pip install jinja2`).
Use the following command line to generate `MODULES.md`
```
python3 ./doc/generate-modules-doc.py
```
It generates the [Modules.md](MODULES.md) file.

## Workflow

This is a workflow that suits our needs and organization, feel free to adapt it.

1. As a developer I use a dev environment to define endpoints and then a task.
2. Once done, the developer exports the task with endpoints to generate a JSON file
3. In the task's JSON file, we extract the endpoint definition (located in the `databases` structure) and we create 1 file per endpoint.
4. We setup/complete an Ansible playbook to automate the task/endpoint creation/deletion.
5. The 3 files (task, source and endpoint) are updated to use on Ansible templating (ie `{{ myVar }}`).
6. When running Ansible, the standard variable injection system will be build the endpoint/task definition.
7. Everything is tracked into our Source Code Management System (Git) and 

Note: To work nicely, the endpoint names must match the task endpoint definition

## Contributing

Contributions are welcome!
If you see an issue or think about a new feature, please create an issue.
The best way to make it happen is to help out by submitting a pull request implementing it.

Feel free to ask for clarifications or guidance on how to prepare your pull request directly in Github issues.

## License

Ansible Qlik Enterprise Manager module is Open Source and available under the MIT Licence.
See the bundled [LICENSE](LICENSE) file for details.
In addition, some parts of this project have their own licenses attached (either in the source files or in a `LICENSE` file next to them).
