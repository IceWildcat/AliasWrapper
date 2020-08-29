import unittest
from io import StringIO
from unittest import TestCase
from unittest.mock import patch
from extras.ls import do_ls
from main import wShell as sh
import re


class TestShell(unittest.TestCase):
    def test_ls(self):
        with patch('sys.stdout', new = StringIO()) as ls_out:
            sh.do_ls("")
            self.assertEqual(ls_out.getvalue(), '\t\t'.join(['__pychache__', 'built_in', 'extras', 'LICENSE', 'main.py', 'README.md', 'test.py']))


if __name__ == '__main__':
    sh().cmdloop()
    unittest.main()
