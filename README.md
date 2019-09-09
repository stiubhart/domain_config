# Domain Config
Quickly configure a domain name .vhost file with an SSL Certificate using Let's Encrypt

# Dependencies 
* Python3
* python3-yamal: `sudo apt install python3-yaml`
* Certbot By Let's Encrypt

# Usage
`domain_config/main.py --domain=example.com`<br>
or to delete a domain:<br>
`domain_config/main.py --domain=example.com --delete`
