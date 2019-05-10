```

usage: default_sg_rules.py [-h] [-v] (-S | -D | -A) [-rg RG_ID] [-sg SG_ID]
                           [-in INBOUND] [-out OUTBOUND]

Program to display all the default security groups along with their rules. And
Deletes them if requested to.

optional arguments:
  -h, --help            show this help message and exit
  -v, --verbose         Display verbose output; can be used more than once for
                        greater verbosity.
  -S, --describe        Describes Default SG Details
  -D, --delete          Deletes Default SG Rules
  -A, --add             Adds Rule to SGs
  -rg RG_ID, --region RG_ID
                        Region Name
  -sg SG_ID, --security-group SG_ID
                        SG Id
  -in INBOUND, --ingress-rule INBOUND
                        Ingress Rule
  -out OUTBOUND, --egress-rule OUTBOUND
                        Egress Rule

```

```

usage: vpc_cleanup.py [-h] [-vpc VPC] [-rg REGION]

Program to Delete All the Dependencies of the VPC followed by VPC too.
 Order of operations
 1.) Terminates the Instances
 2.) Deletes subnets
 3.) Detach and Delete the internet gateway
 4.) Deletes VPC Peering Connections
 5.) Deletes Non-Default Security Groups
 6.) Detach and Deletes Non-Main Route Tables
 7.) Deletes VPC EndPoints
 8.) Deletes the VPC

optional arguments:
  -h, --help            show this help message and exit
  -vpc VPC, --vpc-id VPC
                        VPC Id
  -rg REGION, --region REGION
                        Region

```
