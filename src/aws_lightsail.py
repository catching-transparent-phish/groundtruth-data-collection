#!/usr/bin/python3

import boto3, csv, time, argparse, sys

class aws_lightsail:

    def __init__(self, configs_filename):
        self.configs_file = open(configs_filename, 'r')

    def create_instances(self):
        self.configs = csv.DictReader(self.configs_file)

        ips = []
        for config in self.configs:
            print('Creating instance %s' % config['instance_name'])

            self.lightsail = boto3.client('lightsail', region_name = config['region'])
            tags = config['tags'].split(',')
            tags = [{'key' : tag.split(':')[0], 'value' : tag.split(':')[1]} for tag in tags]

            response = self.lightsail.create_instances(
                    instanceNames = [config['instance_name']],
                    availabilityZone = config['region'] + 'a',
                    blueprintId = config['blueprint_id'],
                    bundleId = config['bundle_id'],
                    keyPairName = config['keypair_name'],
                    tags = tags
            )

            print('Instance created successfully!')
            print('Opening desired ports on instance %s' % config['instance_name'])

            tcpPorts = udpPorts = []
            if(len(config['tcp_ports']) > 0):
                tcpPorts = config['tcp_ports'].split(',')
                tcpPorts = [int(port) for port in tcpPorts]
                tcpPorts = [{'fromPort' : port, 'toPort' : port, 'protocol' : 'tcp'} for port in tcpPorts]
            if(len(config['udp_ports']) > 0):
                udpPorts = config['udp_ports'].split(',')
                udpPorts = [int(port) for port in udpPorts]
                udpPorts = [{'fromPort' : port, 'toPort' : port, 'protocol' : 'udp'} for port in udpPorts]
            ports = tcpPorts + udpPorts

            while(self.lightsail.get_instance(instanceName = config['instance_name'])['instance']['state']['name'] != 'running'):
                time.sleep(1)

            response = self.lightsail.put_instance_public_ports(
                    portInfos = ports,
                    instanceName = config['instance_name']
            )

            print('Ports opened successfully!')

            ips.append((self.lightsail.get_instance(instanceName = config['instance_name'])['instance']['publicIpAddress'], config['instance_name']))

        return ips

    def delete_instances(self):
        self.configs = csv.DictReader(self.configs_file)

        for config in self.configs:
            self.lightsail = boto3.client('lightsail', region_name = config['region'])
            self.lightsail.delete_instance(instanceName = config['instance_name'])


def process_args():
    programDescription = "Spinup or destroy a list of AWS Lightsail instances from config file"

    parser = argparse.ArgumentParser(description = programDescription)
    parser.add_argument("config_file",
                        nargs="?",
                        help="Location of config file to read instance configurations from")
    parser.add_argument("-c", "--create-instances", action="store_true",
                        help="Create instances from config file")
    parser.add_argument("-d", "--delete-instances", action="store_true",
                        help="Delete instances from config file")
    args = vars(parser.parse_args())

    if(args['config_file'] == None or (args['create_instances'] == True and args['delete_instances'] == True)
            or (args['create_instances'] == False and args['delete_instances'] == False)):
        parser.print_help(sys.stderr)
        sys.exit(1)

    lightsail = aws_lightsail(args['config_file'])
    if(args['create_instances'] == True):
        ips = lightsail.create_instances()
        with open('ips.csv', 'w') as f:
            for ip, region_name in ips:
                f.write('%s\n' % ip)
        with open('inventory', 'w') as f:
            f.write('[apache]\n')
            for ip, name in ips:
                f.write('%s ansible_python_interpreter=/usr/bin/python3 node_name=%s\n' % (ip, name))
    else:
        lightsail.delete_instances()

if __name__ == '__main__':
    process_args()
