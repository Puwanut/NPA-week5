from netmiko import ConnectHandler

def get_data_from_device(device_params, command):
    with ConnectHandler(**device_params) as ssh:
        result = ssh.send_command(command)
        return result

def get_ip(device_params, intf):
    data = get_data_from_device(device_params, 'sh ip int br')
    result = data.strip().split('\n')
    for line in result[1:]:
        words = line.split()
        if words[3] == "DHCP" and words[0][-3:] == intf[1:]:
            return "DHCP"
        if words[0][0] == intf[0] and words[0][-3:] == intf[1:]:
            return words[1]
        

def get_subnetmask(device_params, intf, vrf):
    if vrf == "management":
        data = get_data_from_device(device_params, 'sh ip route vrf management | include ^C')
    elif vrf == "control-Data":
        data = get_data_from_device(device_params, 'sh ip route vrf control-Data | include ^C')
    else:
        return "unassigned"
    result = data.strip().split('\n')
    for line in result[1:]:
        words = line.split()
        if words[-1][0] == intf[0] and words[-1][-3:] == intf[1:]:
            return (words[1][-3:]) # /xx

def get_description(device_params, intf):
    data = get_data_from_device(device_params,'sh int description')
    result = data.strip().split("\n")
    for line in result[1:]:
        interface_name = line[0] + line[2:5] # G0/0 G0/1 G0/2
        if interface_name == intf:
            description = line[55:] #don't have any idea
            return description

def get_status(device_params, intf):
    data = get_data_from_device(device_params, 'sh ip int br')
    result = data.strip().split("\n")
    for line in result[1:]:
        words = line.split()
        interface_name = words[0][0] + words[0][-3:]
        if interface_name == intf:
            status = words[4]
            if status == "administratively":
                return "admin down"
            else:
                return status + "/" + words[5]
            
def get_neighbor(device_params):
    neighbor_list = []
    data = get_data_from_device(device_params, 'sh cdp neighbor')
    result = data.strip().split("\n")
    for line in result[5:8]:
        words = line.split()
        connected_device = words[0][:2]
        connected_interface = words[-2][0] + words[-1]
        local_interface = words[1][0] + words[2]
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
    device_ip = '172.31.106.6'
    username = 'admin'
    password = 'cisco'

    device_params = {'device_type': 'cisco_ios',
                 'ip' : device_ip,
                 'username' : username,
                 'password' : password,
                 }
    configure_description(device_params, ["G0/0", "G0/1", "G0/2", "G0/3"])
    # print(get_description(device_params, "G0/0"))
    # get_status(device_params, "G0/0")
    # get_description(device_params, "G0/0")
    # get_neighbor(device_params)
    # configure_description(device_params, "G0/2")
    # print(get_subnetmask(device_params, 'G0/1', 'management'))




