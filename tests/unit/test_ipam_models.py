# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2011 OpenStack LLC.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest

from melange.ipam.models import IpBlock
from melange.ipam.models import IpAddress
from melange.ipam import models
from melange.db import session
from melange.db import api as db_api

class TestIpBlock(unittest.TestCase):

    def test_create_ip_block(self):
        IpBlock.create({"cidr":"10.0.0.1\8","network_id":10})

        saved_block = IpBlock.find_by_network_id(10)
        self.assertEqual(saved_block.cidr, "10.0.0.1\8")

    def test_find_by_network_id(self):
        IpBlock.create({"cidr":"10.0.0.1\8","network_id":10})
        IpBlock.create({"cidr":"10.1.1.1\2","network_id":11})

        block = IpBlock.find_by_network_id(11)

        self.assertEqual(block.cidr,"10.1.1.1\2")

    def test_find_ip_block(self):
        block_1 = IpBlock.create({"cidr":"10.0.0.1\8","network_id":10})
        block_2 = IpBlock.create({"cidr":"10.1.1.1\8","network_id":11})

        found_block = IpBlock.find(block_1.id)

        self.assertEqual(found_block.cidr, block_1.cidr)

    def test_allocate_ip(self):
        block= IpBlock.create({"cidr":"10.0.0.0/31"})
        block = IpBlock.find(block.id)
        ip = block.allocate_ip(port_id = "1234")

        saved_ip = IpAddress.find(ip.id)
        self.assertEqual(ip.address, saved_ip.address)
        self.assertTrue(saved_ip.allocated)
        self.assertEqual(ip.port_id,"1234")

    def test_allocate_ip_is_not_duplicated(self):
        block= IpBlock.create({"cidr":"10.0.0.0/30"})
        self.assertEqual(block.allocate_ip().address,"10.0.0.0")
        self.assertEqual(IpAddress.find_all_by_ip_block(block.id).first().address,
                         "10.0.0.0")
        self.assertEqual(block.allocate_ip().address,"10.0.0.1")
        