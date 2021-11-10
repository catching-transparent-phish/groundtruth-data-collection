# MITM Phishing Toolkit Groundtruth Data Collection 
This repository contains Python and Ansible scripts used to setup a cloud environment to collect ground truth data on MITM phishing toolkits. It works by creating cloud VMs on Amazon AWS Lightsail; each with an Apache web server,  a MITM phishing toolkit , and our MITM phishing toolkit detection tool, PHOCA. Then, network-level data is collected on each permutation of PHOCA -> MITM phishing toolkit -> Apache web server. 

## Prerequisites
* A domain
* An SSL certificate (more information below), also:
	* Certificate private key
	* Root CA certificate
* Source code for the MITM phishing toolkit you would like to record data on

### SSL Certificate
Each node used in this experiment is assigned an ID, which is simply an integer ranging from 1 to n, where n is the total number of nodes. PHOCA makes requests by visiting URLs in the form of i.j.example.com, where i and j are arbitrary IDs from the range of 1 to n; in this case i would be the node hosting the MITM phishing toolkit and j would be the node hosting the Apache web server. 

Therefore, you will need to create an SSL certificate containing the following domains:
* 1.example.com
* *.1.example.com
…
* n.example.com
* *.n.example.com

Once created, save the certificate file, private key file, and the certificate file for the root CA you used.

### Preparing Your Chosen MITM Phishing Toolkit
Each node used in this experiment hosts not only a MITM phishing toolkit, but also an Apache web server. This leads to a port conflict as both want to listen on ports 80 and 443 by default. To prevent this conflict, modify the source code of the MITM phishing toolkit you choose to listen on ports 8080 and 8443 instead.

Additionally, each MITM requires configuration files to be created for your particular domain. Follow the guides on each Github repo on how to do this. If you are using Evilginx, you must also “create” a site for each node. To do this, modify the `.evilginx` home directory folder to match the `config.yaml` and `crt` example provided in `inputFiles/evilginxHomeDirectoryExample/`, replacing example.com with your domain, and adding more or less nodes depending on your needs.

### AWS CLI Setup
If you would like to use the supplied Python scripts to create VMs on Amazon AWS Lightsail, you must setup the AWS CLI on your local machine by following these instructions: [Configuring the AWS CLI - AWS Command Line Interface](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)

## Getting Started
This infrastructure is broken into two sections, a Python script `create_nodes.py` which is used to spin up AWS nodes, as well as create the required configuration files to be used in the second section. 

To run this script, first fill out the required information in the `aws_config.csv` file.  This file contains information about the nodes you would like to create on AWS. Each row in this file corresponds to a different node with the following information for each:
* instance_name: the label to identify a particular node on AWS
* region: AWS datacenter region to house node
* blueprint_id: pre-configured OS to use (e.g. ubuntu_18_04)
* bundle_id: machine size tier to use
* keypair_name: name of SSH public key pair to use to login to node (set this up on AWS Lightsail)
* tags: additional labels to apply to node in AWS
* tcp_ports: comma-separated list of TCP ports to open on node
* udp_ports: comma-separated list of UDP ports to open on node

Once you have filled out the relevant information, run the script with the following command:
`python3 create_nodes.py -d example.com`

This will produce the  `inventory` file which will be used with the Ansible scripts described in the next section. Additionally, it will add in your domain to the Apache config files.

### Ansible Scripts
Once you have run the `create_nodes.py` script, you can use the Ansible playbooks located in the `playbooks/` directory to install the required software on each node, as well as start and manage the experiment.

First, to install everything you need on each node other than the MITM phishing toolkit, use the script located in `playbooks/install/install_all.yml`. To do this, enter your domain and the paths to your certificate files in `playbooks/install/install_apache.yml`. Then, run the script using:
`ansible-playbook -i inventory playbooks/install/install_all.yml`.

Similarly, to install your chosen MITM phishing toolkit on each node, you will need to complete the script located in `playbooks/install/install_phishing_tools/` by entering the information requested under the `vars` directive. Then, run the chosen script as follows:
`ansible-playbook -i inventory playbooks/install/install_phishing_tools/evilginx.yml`

Once everything is installed, you can use the scripts located `playbooks/manage/` to start the experiment, and gather output files at the end of the experiment.