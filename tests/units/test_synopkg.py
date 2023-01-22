import unittest
from unittest.mock import patch, MagicMock
import os
import json
import contextlib
import collections

from ansible.module_utils._text import to_bytes
from ansible.module_utils import basic

from library.synopkg import main, Synopkg


def set_module_args(args):
    args = json.dumps({'ANSIBLE_MODULE_ARGS': args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class SynopkgTest(unittest.TestCase):
    def test_underlying_calls(self):
        expected = collections.namedtuple('expected', ('args',))

        calls = {
            'is_installed': expected(
                args=("source /etc/profile; synopkg list --name",)
            ),
            'install': expected(
                args=("source /etc/profile; synopkg install_from_server docker",)
            ),
            'uninstall': expected(
                args=("source /etc/profile; synopkg uninstall docker",)
            ),
        }

        for call_name, exp in calls.items():
            with self.subTest(msg=f"call={call_name}"):
                with patch('subprocess.Popen') as Popen:
                    sut = Synopkg()

                    pipe = Popen.return_value
                    pipe.wait.return_value = 0

                    _ = getattr(sut, call_name)('docker')

                    Popen.assert_called_once()

                    all_args = Popen.call_args
                    self.assertEqual(exp.args, all_args.args)
                    self.assertDictEqual({
                        'shell': True, 'stdout': -1, 'stderr': -1, 'cwd': '/tmp'
                    }, all_args.kwargs)


class ModuleTest(unittest.TestCase):
    @patch('ansible.module_utils.basic.AnsibleModule.fail_json')
    @patch('ansible.module_utils.basic.AnsibleModule.exit_json')
    @patch('library.synopkg.Synopkg')
    def setUp(self, Synopkg, exit_json, fail_json):
        self.spkg = MagicMock()
        Synopkg.return_value = self.spkg


    @contextlib.contextmanager
    def patched(self):
        yld = collections.namedtuple('Patched', 'sut, exit_json fail_json, spkg')

        with patch('ansible.module_utils.basic.AnsibleModule.fail_json') as fail_json,\
            patch('ansible.module_utils.basic.AnsibleModule.exit_json') as exit_json,\
            patch('library.synopkg.Synopkg') as Synopkg:

            ### We do not expect any negative scenarios
            fail_json.side_effect = Exception('SUT failed')

            spkg = Synopkg.return_value
            yield yld(sut=main, exit_json=exit_json, fail_json=fail_json, spkg=spkg)


    def test_package_not_installed_expected_is_not_installed(self):
        set_module_args({
            'name': 'docker',
            'installed': False,
        })

        with self.patched() as p:
            p.spkg.is_installed.return_value = False

            p.sut()
            p.spkg.is_installed.assert_called_once_with('docker')
            p.spkg.install.assert_not_called()

    def test_package_not_installed_expected_is_uninstalled(self):
        set_module_args({
            'name': 'docker',
            'installed': False,
        })

        with self.patched() as p:
            p.spkg.is_installed.return_value = True

            p.sut()
            p.spkg.is_installed.assert_called_once_with('docker')
            p.spkg.uninstall.assert_called_once_with('docker')

    def test_package_installed_expected_is_not_installed(self):
        set_module_args({
            'name': 'docker',
            'installed': True,
        })

        with self.patched() as p:
            p.spkg.is_installed.return_value = False

            p.sut()
            p.spkg.is_installed.assert_called_once_with('docker')
            p.spkg.install.assert_called_once_with('docker')


    def test_package_installed_expected_is_installed(self):
        set_module_args({
            'name': 'docker',
            'installed': True,
        })

        with self.patched() as p:
            p.spkg.is_installed.return_value = True

            p.sut()
            p.spkg.is_installed.assert_called_once_with('docker')
            p.exit_json.assert_called_once_with(name='docker', changed=False)

