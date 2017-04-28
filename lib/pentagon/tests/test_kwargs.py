import unittest
import pentagon
import os
import logging
from pentagon.tests.test_base import TestPentagonProject


class TestPentagonProjectWithoutKwargs(TestPentagonProject):
    name = 'test_pentagon_without_kwargs'

    def setUp(self):
        self.p = pentagon.PentagonProject(self.name)

    def tearDown(self):
        self.p = None


class TestPentagonProjectWithMinmalKwargs(TestPentagonProject):
    name = 'test_pentagon_with_minimal_kwargs'

    kwargs = {
        'configure': True,
        # need to test some of these without all of them
        'aws_access_key': 'test-aws-key',
        'aws_secret_key': 'test-aws-secret-key',
        'aws_default_region': 'test-aws-region',
        'aws_availability_zone_count': 5,
        }

    def setUp(self):
        self.p = pentagon.PentagonProject(self.name, self.kwargs)

    def tearDown(self):
        self.p = None

    def test_configure_project(self):
        self.assertEqual(self.p._configure_project, self.kwargs['configure'])

    def test_aws_availability_zones(self):
        azs = "test-aws-regiona, test-aws-regionb, test-aws-regionc, test-aws-regiond, test-aws-regione"
        self.assertIsInstance(self.p._aws_availability_zone_count, int)
        self.assertEqual(self.p._aws_default_region, self.kwargs['aws_default_region'])
        self.assertEqual(self.p._aws_availability_zones, azs)


class TestPentagonProjectWithAllKwargs(TestPentagonProject):
    name = 'test_pentagon_with_all_kwargs'
    kwargs = {
        'configure_project': True,

        # 'repository_name': 'test-repository-name',
        # 'workspace_directory': 'test-workspace-direcotry',

        # need to test some of these without all of them
        'aws_access_key': 'test-aws-key',
        'aws_secret_key': 'test-aws-secret-key',
        'aws_default_region': 'test-aws-region',
        'aws_availability_zone_count': 3,
        'aws_availability_zones': 'test-aws-regiona,test-aws-regionb,test-aws-regionc',
        'vpc_name': 'test_vpc_name',
        'vpc_cidr_base': 'test_vpc_cidr_base',
        'vpc_id': 'test_vpc_id',
        # KOPS:
        'state_store_bucket': 'test-statestore-bucket',
        # Working Kubernetes
        'working_kubernetes_cluster_name': 'test-working-cluster-name',
        'working_kubernetes_dns_zone': 'test-working-cluster-dns-zone',
        'working_kubernetes_node_count': 3,
        'working_kubernetes_master_aws_zone': 'test-working-aws-master-zone',
        'working_kubernetes_master_node_type': 'test-working-master-node-type',
        'working_kubernetes_worker_node_type': 'test-working-worker-node-type',
        'working_kubernetes_v_log_level': 'test-working-v-log-level',
        'working_kubernetes_network_cidr': 'test-working-netwwork-cidr',
        # Production Kubernetes
        'production_kubernetes_cluster_name': 'test-production-cluster-name',
        'production_kubernetes_dns_zone': 'test-production-cluster-dns-zone',
        'production_kubernetes_node_count': 3,
        'production_kubernetes_master_aws_zone': 'test-production-aws-master-zone',
        'production_kubernetes_master_node_type': 'test-production-master-node-type',
        'production_kubernetes_worker_node_type': 'test-production-worker-node-type',
        'production_kubernetes_v_log_level': 'test-production-v-log-level',
        'production_kubernetes_network_cidr': 'test-production-netwwork-cidr',
        # ssh keys
        'admin_vpn_key': 'test-admin-vpn-key',
        'working_kube_key': 'test-working-kube-key',
        'production_kube_key': 'test-production-kube-key',
        'working_private_key': 'test-working-private-key',
        'production_private_key': 'test-production-private-key',
        }

    def setUp(self):
        self.p = pentagon.PentagonProject(self.name, self.kwargs)

    def tearDown(self):
        self.p = None


