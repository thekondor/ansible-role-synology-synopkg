# Ansible+Synopkg

Basic adapter over `synopkg` to (un)install packages. Installation is with `install_from_server` only (= remote packages from a built-in list).

## Usage:

``` yaml
tasks:
    - name: Import synopkg role
      import_role: name=ansible-role-synology-synopkg
      
    - name: Uninstall bloatware ActiveInsight
      synopkg:
        name: ActiveInsight
        installed: no

    - name: Install Docker
      synopkg:
        name: Docker
        installed: yes
```

