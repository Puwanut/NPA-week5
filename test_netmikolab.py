import pytest
import json
from netmikolab import *

devices = json.load(open("devices.json"))
device_params = {} #delete after

def test_ip():
    for device in devices:
        for interface in device["interfaces"]:
            assert get_ip(device["device_params"], interface["interface_name"]) == interface["ip_address"]
    print("test ip complete")

# def test_ip():
#     assert get_ip(device_params, "G0/0") == "172.31.106.4"
#     assert get_ip(device_params, "G0/1") == "172.31.106.17"
#     assert get_ip(device_params, "G0/2") == "172.31.106.34"
#     assert get_ip(device_params, "G0/3") == "unassigned"
#     print("test ip complete")

def test_subnetmask():
    for device in devices:
        for interface in device["interfaces"]:
            assert get_subnetmask(device["device_params"], interface["interface_name"], interface["vrf"]) == interface["subnet_mask"]
    print("test subnetmask complete")

def test_description():
    device = devices[0]
    # for device in devices:
    for interface in device["interfaces"]:
        assert get_description(device["device_params"], interface["interface_name"]) == interface["description"]
    # assert get_description(device_params, "G0/0") == "Connect to G0/2 of S0"
    # assert get_description(device_params, "G0/1") == "Connect to G0/2 of S1"
    # assert get_description(device_params, "G0/2") == "Connect to G0/1 of R2"
    # assert get_description(device_params, "G0/3") == "Not Use"
    print("test description complete")

def test_status():
    for device in devices:
        for interface in device["interfaces"]:
            assert get_description(device["device_params"], interface["interface_name"]) == interface["status"]
    # assert get_status(device_params, "G0/0") == "up/up"
    # assert get_status(device_params, "G0/1") == "up/up"
    # assert get_status(device_params, "G0/2") == "up/up"
    # assert get_status(device_params, "G0/3") == "admin down"
    print("test status complete")

