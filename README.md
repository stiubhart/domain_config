# Domain Config
Quickly configure a domain name .vhost file with an SSL Certificate using Let's Encrypt

# Install
`git clone git@github.com:stiubhart/domain_config.git`  
`cd domain_config`  
`chmod +x domain_config`   
* Make sure to edit config.yaml to suit your needs

# Dependencies 
* Python3
* python3-yaml:  
`sudo apt install python3-yaml`
* Certbot By Let's Encrypt:  
`sudo apt-get install certbot`  
`yes N | certbot register --agree-tos -m your@email.com`

# Usage
`domain_config/domain_config --domain=example.com`<br>
or to delete a domain:<br>
`domain_config/domain_config --domain=example.com --delete`
