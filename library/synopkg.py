#!/usr/bin/python
# -*- coding: utf-8 -*-


# (c) 2023, Andrew Sichevoi https://thekondor.net
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.


DOCUMENTATION = """
---
module: synopkg
short_description: Basic package management for Synology
author: Andrew Sichevoi (@thekondor)
notes:
  - Packages are installed using `install_from_server`
  - Tested and proven to work on DSM 7.1
"""

EXAMPLES = """
- name: Uninstall bloatware ActiveInsight
  synopkg:
    name: ActiveInsight
    installed: no

- name: Install Docker
  synopkg:
    name: Docker
    installed: yes
"""


from ansible.module_utils.basic import AnsibleModule

import typing as t
import subprocess


class Synopkg(object):
    def is_installed(self, package_name) -> bool:
        installed = self._get_installed_packages()
        try:
            _ = installed.index(package_name)
            return True
        except ValueError:
            return False

    def install(self, package_name) -> bytes:
        return self._cmd("install_from_server", package_name)

    def uninstall(self, package_name) -> bytes:
        return self._cmd("uninstall", package_name)

    def _get_installed_packages(self) -> t.List[str]:
        out = self._cmd("list", "--name")
        return out.decode("ascii").split("\n")

    def _cmd(self, *args) -> bytes:
        ### `synopkg` depends on other commands which are looked through ${PATH}
        ### So w/o sourcing correct ${PATH}, there're weird and meaningless errors occur
        cmd_args = " ".join(["source /etc/profile;", "synopkg", *args])

        process = subprocess.Popen(
            cmd_args,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd="/tmp",
        )
        rc = process.wait()

        if not process.stdout:
            raise subprocess.CalledProcessError(
                rc, f"{cmd_args}: missing stdout stream"
            )
        stdout = process.stdout.read()

        if rc:
            if not process.stderr:
                raise subprocess.CalledProcessError(
                    rc, f"{cmd_args}: missing stderr stream"
                )
            stderr = process.stderr.read()

            raise subprocess.CalledProcessError(rc, f"{cmd_args}", stdout, stderr)

        return stdout


def run_module():
    module_args = dict(
        name=dict(type="str", required=True),
        installed=dict(type="bool", required=True),
    )

    module = AnsibleModule(argument_spec=module_args, supports_check_mode=False)

    try:
        result = _manage_package_presence(
            module.params["name"], module.params["installed"]
        )
        module.exit_json(**result)
    except PackageManageError as e:
        module.fail_json(msg=str(e))


class PackageManageError(Exception):
    pass


def _manage_package_presence(package_name, package_installed) -> t.Dict[str, t.Any]:
    spkg = Synopkg()

    is_installed = spkg.is_installed(package_name)
    if package_installed:
        if is_installed:
            return dict(name=package_name, changed=False)

        try:
            spkg.install(package_name)
        except subprocess.CalledProcessError as e:
            raise PackageManageError(str(e.stdout) + " :: STDERR: " + str(e.stderr))

        return dict(name=package_name, changed=True)

    if not is_installed:
        return dict(name=package_name, changed=False)

    spkg.uninstall(package_name)
    return dict(name=package_name, changed=True)


def main():
    run_module()


if "__main__" == __name__:
    main()
