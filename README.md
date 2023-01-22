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

## Notes

- Tested and proven to work on `DSM 7.1`;
- ⚠️ Package names for `synopkg` are case-sensitive (so `Docker` is an existing package name, though `docker` is not);
- `make test` for tests;
- The role's package is not idiomatic and this is _mostly_ intentional. You're welcome to contribute back.

## Disclaimer

Since the role is a part of my homelab, it has never been prepared for public distribution and further public support. Though the role suits the needs well, there is no guarantee that it will work for you or will work ever properly. You apply it on your own responsibility.

