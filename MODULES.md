# Ansible Attunity Enterprise Manager documentation

## Authenticating with Attunity Enterprise Manager

### Passing parameters
If you wish to pass credentials as parameters to a task, use the following parameters:
* `qem_hostname`
* `qem_domain`
* `qem_username`
* `qem_password`
* `qem_verify_certificate`

Example:
```
- name: Single Task facts
    qem_info:
        qem_hostname: "qem.consto.com"
        qem_domain: "CONTOSO"
        qem_username: "John"
        qem_password: "Passw0rd!"
        qem_verify_certificate: yes
        name: "My Task"
        server: "My Sample Server"
    register: output
```

### Using Environment variables

To pass credentials via the environment, define the following variables:
* `QEM_HOSTNAME`
* `QEM_DOMAIN`
* `QEM_USERNAME`
* `QEM_PASSWORD`
* `QEM_VERIFY_CERTIFICATE`

### Storing in a file
When working in a development environment, it may be desirable to store credentials in a file.
The modules will look for credentials in `$HOME/.qem/credentials`. This file is an ini style file. It will look as follows:

```
[default]
qem_hostname=qem.contoso.com
qem_domain=CONTOSO
qem_username=John
qem_password=Passw0rd!
qem_verify_certificate=True
```

It is also possible to add additional profiles. Specify the profile by passing defining the `profile` parameter or setting `QEM_PROFILE` in the environment.

Example:
```
[default]
qem_hostname=qem.contoso.com
qem_domain=CONTOSO
qem_username=John
qem_password=Passw0rd!
qem_verify_certificate=False

[dev]
qem_hostname=qem.dev.contoso.com
qem_domain=CONTOSO
qem_username=John
qem_password=Passw0rd!
qem_verify_certificate=False
```

```
- name: Single Task facts
    qem_task_info:
        profile: "dev"
        name: "My Task"
        server: "My Sample Server"
    register: output
```

## Modules

* [qem_acl_info](#qem_acl_info) - Qlik Replicate ACLs info via Qlik Enterprise Manager (QEM)
* [qem_settings](#qem_settings) - Apply Qlik Replicate/Compose settings in Qlik Enterprise Manager (QEM)
* [qem_task_info](#qem_task_info) - Qlik Replicate/Compose task facts via Qlik Enterprise Manager (QEM)
* [qem_endpoint](#qem_endpoint) - Manage Qlik Replicate/Compose endpoint via Qlik Enterprise Manager (QEM)
* [qem_task_status](#qem_task_status) - Manage Qlik Replicate/Compose task status via Qlik Enterprise Manager (QEM)
* [qem_server](#qem_server) - Create or delete Qlik Replicate/Compose servers in Qlik Enterprise Manager (QEM)
* [qem_task](#qem_task) - Manage Qlik Replicate/Compose task via Qlik Enterprise Manager (QEM)
* [qem_acl](#qem_acl) - Manage Qlik Replicate/Compose license registration via Qlik Enterprise Manager (QEM)
* [qem_acl](#qem_acl) - Manage Qlik Replicate/Compose ACL via Qlik Enterprise Manager (QEM)
* [qem_endpoint_info](#qem_endpoint_info) - Qlik Replicate endpoints info via Qlik Enterprise Manager (QEM)


### qem_acl_info

#### Synopsis

Return Attunity Replicate acl info using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| name  |  |  The name of the acl  | |
| server<br> **required**  |  |  The server where the acl is defined  | |

#### Examples

```
# Single acl info
- name: Single ACL info
    qem_acl_info:
        name: "CONTOSO\User2"
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

```

### qem_settings

#### Synopsis

Apply Qlik Replicate/Compose settings using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| name<br> **required**  |  |  The name of the server  | |
| settings<br> **required**  |  |  The settings to apply  | |

#### Examples

```
# Apply settings to the server named "My Sample Server"
- name: Delete Server
    qem_settings:
        name: "My Sample Server"
        settings: "{{ lookup('file', 'my-settings.json')}}"

```

### qem_task_info

#### Synopsis

Return Qlik Replicate/Compose task facts using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| aliases  |  |  | |
| name  |  |  The name of the task  | |
| server<br> **required**  |  |  The server where the task is defined  | |

#### Examples

```
# Single task facts
- name: Single Task facts
    qem_task_info:
        name: "My Task"
        server: "My Sample Server"
    register: output

- name: Display facts
    var: output.qem_tasks[0]

# All task facts
- name: All task facts
    qem_task_info:
        server: "My Sample Server"
    register: output

- name: Display facts
    var: output.qem_tasks

```

### qem_endpoint

#### Synopsis

Manage Qlik Replicate/Compose endpoint using the Qlik Enterprise Manager API Python client. If the endpoint already exists on the target server, the import will override its configuration.
The endpoint will be created according to the target QEM version.
There are no backward compatibility guarantees if you try to import an endpoint definition (eg. 6.6) on a old QEM instance (eg. 6.4).


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| definition  |  |  The endpoint definition in JSON  | |
| name  |  |  The name of the endpoint, if set will override the name present of the first endpoint definition  | |
| server<br> **required**  |  |  The server to import the endpoint  | |
| state  | Choices<br><ul><li>**present**</li><li>absent</li></ul> |  If I(state=present), endpoint will be added/updated  If I(state=absent), endpoint will be deleted  | |

#### Examples

```
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

```

### qem_task_status

#### Synopsis

Manage Qlik Replicate/Compose task status using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| name<br> **required**  |  |  The name of the task you wan to start/stop  | |
| server<br> **required**  |  |  The server on which the task is defined  | |
| state  | Choices<br><ul><li>started</li><li>stopped</li></ul> |  If I(state=started), task will be started  If I(state=stopped), task will be stopped  | |
| timeout  | Default:<br>**60** |  A timeout in seconds before raising an issue during the task starting/stopping  | |

#### Examples

```
# Starting a task with a extended timeout
- name: Started sample task
    qem_task_status:
        name: "My Sample Task"
        server: "My Sample Server"
        timeout: 120
        state: started

# Stopping a task
- name: Stop sample task
    qem_task_status:
        name: "My Sample Task"
        server: "My Sample Server"
        state: stopped

```

### qem_server

#### Synopsis

Create or remove Qlik Replicate/Compose servers using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| description  |  |  The description of the server  | |
| host  |  |  The host of the server  | |
| monitored  | Default:<br>**no** |  Wether or not the server should be monitored by Qlik Enterprise Manager  | |
| name<br> **required**  |  |  The name of the server  | |
| password  |  |  The user's password to connect to the server  | |
| port  |  |  The connection port of the server  | |
| state  | Choices<br><ul><li>**present**</li><li>absent</li></ul> |  If I(state=present), server will be created  If I(state=absent), server will be deleted  | |
| type  | Choices<br><ul><li>**replicate**</li><li>compose</li></ul> |  If I(type=replicate), create a Replicate server  If I(type=compose), create a Compose server  | |
| username  |  |  The user to connect to the server in a Windows format (ie. <DOMAIN>\<Username>)  | |
| verify_server_certificate  | Default:<br>**no** |  Wether or not the server certificate should be verified  | |

#### Examples

```
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
        username: "CONTOSO\John"
        password: "p4ssw0rd"
        monitored: True
        verify_server_certificate: False
        state: present

```

### qem_task

#### Synopsis

Manage Qlik Replicate/Compose task using the Qlik Enterprise Manager API Python client
The task will be created according to the target QEM version.
There are no backward compatibility guarantees if you try to import a task definition (eg. 6.6) on a old QEM instance (eg. 6.4).


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| definition  |  |  The task definition in JSON  | |
| delete_task_logs  | Default:<br>**yes** |  Wether or not the logs should be deleted when the task is deleted  | |
| force_task_stop  | Default:<br>**no** |  Force to stop the task before deletion  | |
| force_task_timeout  | Default:<br>**60** |  A timeout in seconds before raising an issue during the task stopping  | |
| name  |  |  The name of the task, if set will override the name present the task definition  | |
| server<br> **required**  |  |  The server to import the task  | |
| state  | Choices<br><ul><li>**present**</li><li>absent</li></ul> |  If I(state=present), task will be added  If I(state=absent), task will be deleted  | |

#### Examples

```
# Removing a task
- name: Delete sample task
    qem_task:
        name: "My Sample Task"
        server: "My Sample Server"
        state: absent
        force_task_stop: yes

# Importing a task based on a local JSON file
- name: Import sample task
    qem_task:
        name: "My Sample Task"
        server: "My Sample Server"
        state: present
        definition: |
        {
            "name": "MyTask",
            "cmd.replication_definition": {
                "tasks":    [{
                        "task": {
                            "name": "daniel",
                            "source_name": "MyDB",
                            "target_names": ["MyKafka"]
                        },
                        "source": {
                            "rep_source": {
                                "source_name": "MyDB",
                                "database_name": "MyDB"
                            },
                            "source_tables": {
                                "name": "MyDB"
                            }
                        },
                        "targets":    [{
                                "rep_target": {
                                    "target_name": "MyKafka",
                                    "target_state": "DISABLED",
                                    "database_name": "MyKafka"
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
                                "dr_settings": {
                                },
                                "statistics_table_settings": {
                                },
                                "bidi_table_settings": {
                                },
                                "task_uuid": "87b841df-7b9a-8041-9666-fa4454d79023",
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
                                        "sub_char": 0
                                    }
                                }
                            }
                        }
                    }],
                "databases": []
            }    
        }

```

### qem_acl

#### Synopsis

Manage Qlik Replicate/Compose license registration using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| force  | Default:<br>**no** |  Wether or not we force the license registration  | |
| license<br> **required**  |  |  The license information  | |
| name<br> **required**  |  |  The server to register the license  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Qlik Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Qlik Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |

#### Examples

```
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

```

### qem_acl

#### Synopsis

Manage Attunity Replicate/Compose Access Control List (ACL) using the Attunity Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| name<br> **required**  |  |  The name of the user/group in a Windows format (ie. <DOMAIN>\<Username or Groupname>)  | |
| role  | Choices<br><ul><li>admin</li><li>designer</li><li>operator</li><li>viewer</li></ul> |  The role impacted by the ACL  | |
| server<br> **required**  |  |  The server to apply the ACL  | |
| state  | Choices<br><ul><li>**present**</li><li>absent</li></ul> |  If I(state=present), ACL will be added  If I(state=absent), ACL will be deleted  | |
| type  | Choices<br><ul><li>user</li><li>group</li></ul> |  The ACL is applied on a User or a Group  | |

#### Examples

```
# Apply a simple ACL
- name: Apply ACL
    qem_acl:
        server: "My Sample Server"
        name: "CONTOSO\User1"
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
        - { name: "CONTOSO\User2", type: "user", role: "designer", state: "present"}
        - { name: "CONTOSO\User3", type: "user", role: "operator", state: "absent"}
        - { name: "CONTOSO\Group", type: "group", role: "viewer", state: "present"}

```

### qem_endpoint_info

#### Synopsis

Return Qlik Replicate endpoint info using the Qlik Enterprise Manager API Python client


#### Parameters

| Parameter     | Choices/Defaults | Comments |
| ------------- | ---------------- |--------- |
| qem_domain  |  |  Active Directory domain where to find the user.  | |
| qem_hostname  |  |  Attunity Enterprise manager host name.  | |
| qem_password  |  |  Active Directory user password.  | |
| qem_username  |  |  Active Directory user to connect to Attunity Enterprise Manager.  | |
| qem_verify_certificate  | Default:<br>**yes** |  Wether or not the server certificate should be verifies.  | |
| profile  |  |  Security profile found in ~/.qem/credentials file.  | |
| name  |  |  The name of the endpoint  | |
| server<br> **required**  |  |  The server where the endpoint is defined  | |

#### Examples

```
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

```

