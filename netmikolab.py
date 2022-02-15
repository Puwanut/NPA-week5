from netmiko import ConnectHandler
import re

def get_data_from_device(device_params, command):
    with ConnectHandler(**device_params) as ssh:
        result = ssh.send_command(command)
        return result

def get_ip(device_params, intf):
    data = get_data_from_device(device_params, 'sh ip int br')
    result = data.strip().split('\n')
    for line in result[1:]:
        #example text --> "GigabitEthernet0/0  172.31.106.6  YES NVRAM  up  up"
        intf_type, intf_num, intf_ip, ip_type = re.search(r'(\w)\w+(\d+/\d)\s+(\d+\.\d+\.\d+.\d+|unassigned)\s+\w+\s(\w+).*', line).groups()
        if intf_type == intf[0] and intf_num == intf[1:]:
            if ip_type == "DHCP":
                return "DHCP" 
            return intf_ip
        

def get_subnetmask(device_params, intf, vrf):
    if vrf == "management":
        data = get_data_from_device(device_params, 'sh ip route vrf management | include ^C')
    elif vrf == "control-Data":
        data = get_data_from_device(device_params, 'sh ip route vrf control-Data | include ^C')
    else:
        return "unassigned"
    result = data.strip().split('\n')
    for line in result[1:]:
        # example text --> "C        172.31.106.0/28 is directly connected, GigabitEthernet0/0"
        subnet_mask, intf_type, intf_num = re.search(r'\w\s+\d+\.\d+\.\d+.\d+(/\d+)\s\w+\s\w+\s\w+\,\s(\w)\w+(\d+/\d).*', line).groups()
        if intf_type == intf[0] and intf_num == intf[1:]:
            return subnet_mask # /xx

def get_description(device_params, intf):
    data = get_data_from_device(device_params,'sh int description')
    result = data.strip().split("\n")
    for line in result[1:]:
        intf_type, intf_num, intf_status = re.search(r'(\w)\w(\d+/\d+|.)\s+(\w+).*', line).groups()
        if (intf_type == intf[0] and intf_num == intf[1:]):
            if intf_status == "admin": #admin down
                description = re.search(r'\w+\d+/\d\s+\w+\s\w+\s+\w+\s+(.*)', line).groups()
            else: #down or up
                description = re.search(r'\w+\d+/\d\s+\w+\s+\w+\s+(.*)', line).groups()
            #description = ('Connect to Gx/x of xx',) 
            #description[0] = 'Connect to Gx/x of xx'
            return description[0]

def get_status(device_params, intf):
    data = get_data_from_device(device_params, 'sh int description')
    result = data.strip().split("\n")
    for line in result[1:]:
        #example text 1 --> "Gi0/3  admin down  down  Not Use"
        #example text 2 --> "Gi0/0  up          up    Connect to G1/0 of S0"
        intf_type, intf_num, intf_status = re.search(r'(\w)\w(\d+/\d|.)\s+(\w+)\s', line).groups()
        if intf_type == intf[0] and intf_num == intf[1:]:
            if intf_status == "admin":
                return "admin down"
            else:
                intf_protocol = re.search(r'\w+\d+/\d\s+\w+\s+(\w+)\s', line).groups()
                return intf_status + "/" + intf_protocol[0]
            
def get_neighbor(device_params):
    neighbor_list = []
    data = get_data_from_device(device_params, 'sh cdp neighbor')
    result = data.strip().split("\n")
    for line in result[5:8]:
        connected_device, local_intf_type, local_intf_num, connected_intf_type, connected_intf_num = \
        re.search(r'(\w\d)\.\w+\.\w+\s+(\w)\w+\s(\d+/\d)\s+\d+\s+\w\s\w\s+(\w)\w+\s(\d+/\d)', line).groups()
        local_interface = local_intf_type + local_intf_num
        connected_interface = connected_intf_type + connected_intf_num
        neighbor_list.append([local_interface, connected_device, connected_interface])
    return neighbor_list
    
    #     words = line.split()
    #     connected_device = words[0][:2]
    #     connected_interface = words[-2][0] + words[-1]
    #     local_interface = words[1][0] + words[2]
    #     neighbor_list.append([local_interface, connected_device, connected_interface])
    # return neighbor_list

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
    device_ip = '172.31.106.4'
    username = 'admin'
    password = 'cisco'

    device_params = {'device_type': 'cisco_ios',
                 'ip' : device_ip,
                 'username' : username,
                 'password' : password,
                 }

    # get_subnetmask(device_params, 'G0/1', "control-Data")
    # print(get_ip(device_params, 'G0/2'))
    configure_description(device_params, ["G0/0", "G0/1", "G0/2", "G0/3"])
    # print(get_description(device_params, "G0/0"))
    # get_status(device_params, "G0/3")
    # get_description(device_params, "G0/3")
    # get_neighbor(device_params)
    # configure_description(device_params, "G0/2")
    # print(get_subnetmask(device_params, 'G0/1', 'management'))




