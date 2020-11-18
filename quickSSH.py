#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os, sys, yaml
from cryptography.fernet import Fernet
#import variable set in the config file qsh_config.py
from qsh_config import *


def print_help():
    print('Usage : qsh hostname or ip')
    print("By default qsh will search (with a regex) for a hostname or an ip defined in the hosts.yml file.")
    print("Exemple: qsh myhost")
    print("qsh commands :")
    print(" - decrypt_file; decrypt the host.yml file with the encrypt_key.")
    print(" - encrypt_file; encrypt the host.yml file with the encrypt_key.")
    print(" - generate_key; generate a key to use for encrypting the host.yml file. You need to set the key in the qsh_config.py file.")
    print(" - list; list all the hosts defined in the file hosts.yml.")
    print(" - help; print this help.")

def connect():
    # Connect to the host
    cmd ="ssh "+user+"@"+ip+" -p "+port
    print(cmd)
    os.system(cmd)

def generate_key():
    """
    Generates a key and print it to the user
    """
    key = Fernet.generate_key()
    print(key)

def encrypt_file():
    """
    Encrypts the file and write it
    """
    f = Fernet(encrypt_key)

    with open(host_file, "rb") as file:
        # read all file data
        file_data = file.read()

    # encrypt data
    encrypted_data = f.encrypt(file_data)

    # write the encrypted file
    with open(host_file, "wb") as file:
        file.write(encrypted_data)
    
    print("the file "+ host_file +" has been encrypted")

def decrypt_file():
    """
    Decrypt the file and write it
    """
    f = Fernet(encrypt_key)

    with open(host_file, "rb") as file:
        # read all file data
        file_data = file.read()

    # decrypt data
    decrypted_data = f.decrypt(file_data)

    # write the encrypted file
    with open(host_file, "wb") as file:
        file.write(decrypted_data)

    print("the file "+ host_file +" has been decrypted")

def read_yaml_file():
    #test if the variable encrypt_key is set
    try:
        encrypt_key
    except:
        #not set, open the plain yaml hosts file
        with open(host_file) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
    else:
        #set, open the encrypted yaml hosts file
        f = Fernet(encrypt_key)
        with open(host_file, "rb") as file:
           # read all file data
           file_data = file.read()
        # decrypt data
        decrypted_data = f.decrypt(file_data)
        data = yaml.load(decrypted_data, Loader=yaml.FullLoader)
    return data;

def search_host():
    global ip, user, port

    search=sys.argv[1]

    # we get the optionnal port number
    if len (sys.argv) == 3 :
        port=sys.argv[2]

    data = read_yaml_file()
    ip_find = []
    hostname_find = []

    # search for the hostname and for the ip
    for ip, hostname in data.items() :
        if "," in hostname :
            hostname_clean, users_id = hostname.split(",",1)
        else :
            hostname_clean = hostname
        if search in hostname_clean :
            hostname_find.append(hostname)
            ip_find.append(ip)

        if "," in ip :
            ip_clean, port = ip.split(",",1)
        else :
            ip_clean = ip
        if search in ip_clean :
            ip_find.append(ip)
            hostname_find.append(hostname)

    # if one hostname or ip matched the search
    if len(hostname_find) == 1 :
        choice=0

    # if multiple hostname or ip matched the search
    elif len (hostname_find) > 1 :
        print ("Multiple hosts find :")
        search_nb=0
        for host in hostname_find :
            print (" [ "+str(search_nb)+" ] : "+host)
            search_nb += 1
        choice = int(input("On wich server do you wish to connect ? :"))

    else :
       print ("No host matching your search")
       sys.exit()

    # get the user, ip and port of the host matched
    if "," in hostname_find[choice] :
        # get the list of users_id
        hostname, users_id = hostname_find[choice].split(",",1)
        users_id = users_id.split()
        # search if an users_id match one from our dict other_user to replace the user
        for f in users_id :
           if f in other_user :
               user = other_user.get(f)
    if ":" in ip_find[choice] :
        ip, port = ip_find[choice].split(":",1)
    else :
        ip = ip_find[choice]


try:
    sys.argv[1]
except:
    print("ERROR : qsh need at least one argument")
    print_help()
    sys.exit()

# generate a key
if sys.argv[1] == "generate_key":
    generate_key()
    sys.exit()

# encrypt the host file with the encrypt_key
if sys.argv[1] == "encrypt_file":
    encrypt_file()
    sys.exit()

# decrypt the host file with the decrypt_key
if sys.argv[1] == "decrypt_file":
    decrypt_file()
    sys.exit()

# list all the hosts defined
if sys.argv[1] == "list" :
    data = read_yaml_file()
    for ip, hostname in data.items() :
        print (ip + " : " + hostname)
    sys.exit()

# print the help
if sys.argv[1] == "help" :
    print_help()
    sys.exit()

# we get the search term the user as passed
if len (sys.argv) >= 2 :
    # search the host matching
    search_host()
    # connect to the host
    connect()

