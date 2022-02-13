import pytest
import json
from netmikolab import *

devices = json.load(open("devices.json"))

def test_ip():
    for device in devices:
        for interface in device["interfaces"]:
            assert get_ip(device["device_params"], interface["interface_name"]) == interface["ip_address"]
    print("test ip complete")

def test_subnetmask():
    for device in devices:
        for interface in device["interfaces"]:
            assert get_subnetmask(device["device_params"], interface["interface_name"], interface["vrf"]) == interface["subnet_mask"]
    print("test subnetmask complete")

def test_description():
    device = devices[2]
    for device in devices:
        for interface in device["interfaces"]:
            assert get_description(device["device_params"], interface["interface_name"]) == interface["description"]
        print("test description complete")

def test_status():
    for device in devices:
        for interface in device["interfaces"]:
            assert get_status(device["device_params"], interface["interface_name"]) == interface["status"]
    print("test status complete")

