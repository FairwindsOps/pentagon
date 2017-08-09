
import unittest
import pentagon
import os
import logging


class TestPentagonProject(unittest.TestCase):
    name = "test-pentagon-base"

    def setUp(self):
        self.p = pentagon.PentagonProject(self.name)

    def tearDown(self):
        self.p = None

    def test_instance(self):
        self.assertIsInstance(self.p, pentagon.PentagonProject)

    def test_name(self):
        print ('test')
        self.assertEqual(self.p._name, self.name)

    def test_repository_name(self):
        self.assertEqual(self.p._repository_name, '{}-infrastructure'.format(self.name))

    def test_repository_directory(self):
        self.assertEqual(self.p._repository_directory, "{}/{}".format(self.p._workspace_directory, self.p._repository_name))

    def test_workspace_directory(self):
        self.assertEqual(self.p._workspace_directory, os.path.expanduser('.'))

    def test_private_path(self):
        self.assertEqual(self.p._private_path, "{}/config/private/".format(self.p._repository_directory))
