import os
import stat
import shutil
import filecmp

from dvc.main import main
from dvc.command.imp import CmdImport

from tests.basic_env import TestDvc


class TestCmdImport(TestDvc):
    def test(self):
        ret = main(['import',
                    self.FOO, 'import'])
        self.assertEqual(ret, 0)

        ret = main(['import',
                    'non-existing-file', 'import'])
        self.assertNotEqual(ret, 0)
