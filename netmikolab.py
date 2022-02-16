from netmiko import ConnectHandler
import re
import textfsm

NET_TEXTFSM = "/ntc_templates"

def get_data_from_device(device_params, command):
    with ConnectHandler(**device_params) as ssh:
        result = ssh.send_command(command)
        return result

def get_ip(device_params, intf):
    data = get_data_from_device(device_params, 'sh ip int br')
    with open("ntc_templates/cisco_ios_show_ip_interface_brief.textfsm") as template:
        fsm = textfsm.TextFSM(template)
        interfaces = fsm.ParseText(data)
        for interface in interfaces:
            if interface[0][0] == intf[0] and interface[0][-3:] == intf[1:]:
                if interface[1][:11] == "192.168.122":
                    return "DHCP"
                return interface[1]

def get_subnetmask(device_params, intf):
    data = get_data_from_device(device_params, "show interface " + intf)
    with open("ntc_templates/cisco_ios_show_interfaces.textfsm") as template:
        fsm = textfsm.TextFSM(template)
        interfaces = fsm.ParseText(data)
        for interface in interfaces:
            if interface[0][0] == intf[0] and interface[0][-3:] == intf[1:]:
                if interface[7][-3:] == '':
                    return 'unassigned'
                return interface[7][-3:]
                
def get_description(device_params, intf):
    data = get_data_from_device(device_params,'sh int description')
    with open("ntc_templates/cisco_ios_show_interfaces_description.textfsm") as template:
        fsm = textfsm.TextFSM(template)
        interfaces = fsm.ParseText(data)
        for interface in interfaces:
            if interface[0][0] == intf[0][0] and interface[0][2:] == intf[1:]:
                return interface[3]

def get_status(device_params, intf):
    data = get_data_from_device(device_params, 'sh int description')
    with open("ntc_templates/cisco_ios_show_interfaces_description.textfsm") as template:
        fsm = textfsm.TextFSM(template)
        interfaces = fsm.ParseText(data)
        for interface in interfaces:
            if interface[0][0] == intf[0][0] and interface[0][2:] == intf[1:]:
                if interface[1] == "admin down":
                    return interface[1]
                return interface[1] + '/' + interface[2]
            
def get_neighbor(device_params):
    neighbor_list = []
    data = get_data_from_device(device_params, 'sh cdp neighbor')
    with open("ntc_templates/cisco_ios_show_cdp_neighbors.textfsm") as template:
        fsm = textfsm.TextFSM(template)
        cdp_entries = fsm.ParseText(data)
        for entry in cdp_entries:
            connected_device = entry[0][:2]
            connected_interface = entry[3][0] + entry[4]
            local_interface = entry[1][0] + entry[1][-3:]
            neighbor_list.append([local_interface, connected_device, connected_interface])
        return neighbor_list

def configure_description(device_params, intf_list):
    commands = []
    neighbor_list = get_neighbor(device_params)
    for intf in intf_list:
        for neighbor in neighbor_list:
            local_interface = neighbor[0] 
            connected_device = neighbor[1]
            connected_interface = neighbor[2]
            if device_params["ip"] == "172.31.106.6" and intf == "G0/2":
                desc = "Connect to WAN"
                break
            elif local_interface == intf:    
                desc = "Connect to " + connected_interface + " of " + connected_device
                break
            else:
                desc = "Not Use"
        commands.append("int " + intf)
        commands.append("description " + desc)

    with ConnectHandler(**device_params) as ssh:
        ssh.send_config_set(commands)

#if run this file
if __name__ == '__main__':
    device_ip = '172.31.106.5'
    username = 'admin'
    password = 'cisco'

    device_params = {'device_type': 'cisco_ios',
                 'ip' : device_ip,
                 'username' : username,
                 'password' : password,
                 }
    # get_ip(device_params, 'G0/1')
    # print(get_data_from_device(device_params, "show ip int br"))
    # get_subnetmask(device_params, 'G0/3')
    # print(get_ip(device_params, 'G0/2'))
    configure_description(device_params, ["G0/0", "G0/1", "G0/2", "G0/3"])
    # print(get_description(device_params, "G0/0"))
    # get_status(device_params, "G0/3")
    # get_description(device_params, "G0/1")
    # get_neighbor(device_params)
    # print(get_subnetmask(device_params, 'G0/1', 'management'))




