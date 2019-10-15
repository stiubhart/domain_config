#!/usr/bin/env python3

import yaml, sys, getopt, re, os, subprocess, time, shutil
from subprocess import Popen, PIPE


class colours:
    # Display differentt colours and fonts
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    CYAN = '\033[96m'
    UNDERLINE = '\033[4m'


def config():
    dirname = os.path.dirname(__file__)
    filename = os.path.join(dirname, 'config.yaml')

    with open(filename, 'r') as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            sys.exit()


def main(argv):
    print()

    domain = config()['root']
    host_type = 'general'
    domain_present = False
    action = 'create'
    dirname = os.path.dirname(__file__)
    file_prefix = config()['file_prefix']
    if file_prefix is None:
        file_prefix = ''

    try:
        opts, args = getopt.getopt(argv, "ht:d:", ["help", "domain=", "type=", "delete"])
    except getopt.GetoptError:
        print ('1: you must choose a domain [-d | --domain]')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print ('2: you must choose a domain [-d | --domain]')
            sys.exit()
        elif opt in ("-d", "--domain"):
            domain = arg
            domain_present = True
        elif opt in ("-t", "--type"):
            host_type = arg
        elif opt in ("--delete"):
            action = 'delete'

    if domain_present == False:
        print (colours.RED, 'you must choose a domain [-d | --domain]', colours.END)
        sys.exit()

    domain = re.sub(r'[^0-9a-zA-Z\.\-]', '', domain).lower()

    if len(domain) <= 5:
        print (colours.RED, "Domian name is too short, must be greater than 5 characters.", colours.END)
        sys.exit()

    print ('Your domain is: ' + colours.BLUE + domain + colours.END)

    if action == 'create':
        print ('Create domain')
        # print ('Host Type: ', host_type)
        print()

        withSSL = buildDomainVhost(domain, file_prefix, host_type)
        if withSSL == True:
            print(colours.YELLOW + 'Your web root is: ' + colours.END + config()['root']['web'] + file_prefix + domain + "/web/")
            print(colours.GREEN, "SSL Certificate already exists for ", colours.BLUE,  colours.UNDERLINE, "https://", domain, colours.END, sep='')
            print()
            sys.exit()
        else:
            removeSSLCerttificate(domain)
            generateSSLCertificatte(domain, file_prefix)
            withSSL = buildDomainVhost(domain, file_prefix, host_type)

        if withSSL == True:
            print(colours.GREEN + "Success!" + colours.END)
            print(colours.YELLOW + 'Your web root is: ' + colours.END + config()['root']['web'] + file_prefix + domain + "/web/")
            print(colours.BLUE + colours.UNDERLINE + 'https://' + domain + colours.END)
        else:
            print(colours.RED +'There may be an error configuring your SSL certificate for ' + colours.BLUE + 'http://' + domain + colours.END)

    elif action == 'delete':
        print ('Delete domain')
        print()
        deleteDomainVhost(domain, file_prefix)

    print()



def buildDomainVhost(domain, file_prefix, host_type):
    print (colours.YELLOW, "About to write VHost file for " + colours.BLUE + domain + colours.END, sep='')

    ssl = checkSSLValidation(domain)
    letsencrypt_dir = getLetsEncryptDir(domain)

    comment = '' if ssl else '# ';
    letsencrypt_dir = letsencrypt_dir if len(letsencrypt_dir) > 1 else domain;

    dirname = os.path.dirname(__file__)
    if host_type == 'general':
        vhost_file = open(os.path.join(dirname, "vhost_files/generic.vhost"), "r")
    else:
        print(colours.RED + 'host_type: ' + host_type + ' not recognised' + colours.END)
        print()
        sys.exit()

    vhost = vhost_file.read()

    vhost = vhost.replace('#COMMENT#', comment)
    vhost = vhost.replace('#DOMAIN#', domain)
    vhost = vhost.replace('#FILE_PREFIX#', file_prefix)
    vhost = vhost.replace('#PHP_SOCK#', config()['php_sock'])
    vhost = vhost.replace('#LETSENCRYPT_DIR#', letsencrypt_dir)

    my_file = config()['root']['sites-available'] + file_prefix + domain + ".vhost";
    symlink_file = config()['root']['sites-enabled'] + file_prefix + domain + ".vhost";

    if os.path.exists(my_file):
            os.unlink(my_file)

    if os.path.exists(symlink_file):
            os.unlink(symlink_file)

    output = os.popen("sudo grep -ni ' " + domain + "' " + config()['root']['sites-available'] + "* 2>&1").read()
    if len(output) > 1:
            print ("\n" + colours.RED, "The Domain " + colours.BLUE + domain + colours.RED + " is already taken" + colours.END + "\n\n", sep='')
            if not ssl:
                print (colours.YELLOW + "No valid SSL Certificate, let's get it")
                generateSSLCertificatte(domain, file_prefix)
                letsencrypt_dir = getLetsEncryptDir(domain)
            print ("ssl_certificate /etc/letsencrypt/live/" + letsencrypt_dir + "/fullchain.pem;")
            print ("ssl_certificate_key /etc/letsencrypt/live/" + letsencrypt_dir + "/privkey.pem;")
            print ()
            sys.exit()

    f = open(my_file, 'w')
    f.write(vhost)
    f.close()

    if not os.path.islink(symlink_file):
        os.symlink(my_file, symlink_file);

    print (colours.GREEN + "Vhost file created" + colours.END)

    buildWebFiles(domain, file_prefix)

    status = restartNginx(domain, file_prefix)
    if status is False:
        deleteDomainVhost(domain, file_prefix)
        sys.exit()

    return checkSSLValidation(domain)

def restartNginx(domain, file_prefix):
    output = ''.join(os.popen('sudo nginx -t 2>&1').read().split())
    success = output[-10:len(output)]

    if (success != "successful"):
        print(output)
        print (colours.RED + "Nginx config syntax error" + colours.END + "\n\n")
        return False
    else:
        print (colours.YELLOW + "Restarting Nginx..." + colours.END)
        cmd = ['service', 'nginx', 'restart']
        p = subprocess.call(cmd)
        return True

def buildWebFiles(domain, file_prefix):
    dirname = os.path.dirname(__file__)

    webroot = config()['root']['web'] + file_prefix + domain
    if not os.path.exists(webroot):
        subprocess.call(['sudo', 'mkdir', webroot])

    webroot = config()['root']['web'] + file_prefix + domain + "/web"
    if not os.path.exists(webroot):
        subprocess.call(['sudo', 'mkdir', webroot])
    
    logroot = config()['root']['web'] + file_prefix + domain + "/log"
    if not os.path.exists(logroot):
        os.popen('sudo mkdir -p ' + logroot)
    
    errorroot = config()['root']['web'] + file_prefix + domain + "/web/error"
    if not os.path.exists(errorroot):
        os.popen('sudo cp -r ' + dirname + '/error_pages ' + errorroot)
    
    indexHtml = config()['root']['web'] + file_prefix + domain + "/web/index.html"
    indexPhp = config()['root']['web'] + file_prefix + domain + "/web/index.php"
    if not os.path.exists(indexHtml) and not os.path.exists(indexPhp):
        os.popen('sudo cp  ' + dirname + '/template.php ' + indexPhp)


def generateSSLCertificatte(domain, file_prefix):
    print(colours.YELLOW + "Generating SSL Certificate " + colours.END)
    cmd = ['sudo', 'certbot', 'certonly', '--webroot', '-w', config()['root']['web'] + file_prefix + domain + '/web/', '-d', domain]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    output = p.communicate()[0]
    output = format(output)

    if "The following errors were reported by the server" in output:
        print(output)
        print()
        print(colours.RED + "Error generating certificatei. Try running the command above in your terminal" + colours.END)
        print()
        sys.exit()

    if "Congratulations!" in output:
        print(colours.GREEN + 'SSL Certificate generated' + colours.END)
        return

    print(output)
    print()
    print(colours.RED +'OOPS! There may be an error configuring your SSL certificate for ' + colours.BLUE + 'http://' + domain + colours.END)
    print()
    sys.exit()


def deleteDomainVhost(domain, file_prefix):
    my_file = config()['root']['sites-available'] + file_prefix + domain + ".vhost";
    symlink_file = config()['root']['sites-enabled'] + file_prefix + domain + ".vhost";

    if (os.path.exists(my_file)):
        os.unlink(my_file)

    if (os.path.islink(symlink_file)):
        os.unlink(symlink_file)

    if not os.path.exists(config()['root']['web'] + file_prefix + 'remove.at.your.peril/'):
        os.makedirs(config()['root']['web'] + file_prefix + 'remove.at.your.peril/')

    if os.path.exists(config()['root']['web'] + file_prefix + domain):
        os.popen('rsync -av ' + config()['root']['web'] + file_prefix + domain + ' ' + config()['root']['web'] + file_prefix+ 'remove.at.your.peril/ --remove-source-files && rm -r ' + config()['root']['web'] + file_prefix + domain).read()

    removeSSLCerttificate(domain)

    restartNginx(domain, file_prefix)

    print (colours.RED + "Removed generated files" + colours.END )


def removeSSLCerttificate(domain):
    letsencrypt_dir = getLetsEncryptDir(domain)
    letsencrypt_dir = letsencrypt_dir if len(letsencrypt_dir) > 1 else domain;

    if len(letsencrypt_dir) > 5:
        certs = '/etc/letsencrypt/live/' + letsencrypt_dir
        if (os.path.exists(certs)):
            shutil.rmtree(certs)

        certs = '/etc/letsencrypt/archive/' + letsencrypt_dir
        if (os.path.exists(certs)):
            shutil.rmtree(certs)

        certs = '/etc/letsencrypt/renewal/' + letsencrypt_dir + '.conf'
        if (os.path.exists(certs)):
            os.remove(certs)


def checkSSLValidation(domain):
    output = os.popen("certbot certificates -d " + domain + " 2>&1").read()
    return "(VALID:" in output


def getLetsEncryptDir(domain):
    cmd = 'sudo certbot certificates | grep \'/' + domain + '\''
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, shell=True)
    output = p.communicate()[0]
    output = format(output)

    directory = ''
    if "Certificate Path: " in output:
        result = re.search('letsencrypt\/live\/(.*)\/fullchain', output)
        directory = result.group(1)

    return directory


if __name__ == "__main__":
    main(sys.argv[1:])



