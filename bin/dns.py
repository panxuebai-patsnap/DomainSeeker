# -*- coding:utf-8 -*-
import dnslib.dnsfucation as dns
import socket
import threading
import json
import logging

logging.basicConfig(level=logging.INFO)
hosts = {}
config = {}
remote_dns_server = '114.114.114.114'
remote_dns_port = 53
local_dns_server = '127.0.0.1'
local_dns_port = 53


def init():
    global hosts
    global config
    global remote_dns_server
    global remote_dns_port
    global local_dns_server
    global local_dns_port
    with open("./conf/config.json", 'r') as d:
        config = json.load(d)

    with open(config['rpz_json_path'], 'r') as c:
        hosts = json.load(c)

    with open("./data/wildcards.json", 'r') as f:
        wildcards = json.load(f)

    if config['sni_proxy_on']:
        for key in wildcards:
            wildcards[key] = config['sni_proxy_ip']
    hosts.update(wildcards)

    remote_dns_server = config['remote_dns_server']
    remote_dns_port = config['remote_dns_port']
    local_dns_server = config['local_dns_server']
    local_dns_port = config['local_dns_port']

    logging.info("==========Config===========")
    logging.info("local_dns_server:%s", local_dns_server)
    logging.info("local_dns_port:%s", local_dns_port)
    logging.info("remote_dns_server:%s", remote_dns_server)
    logging.info("remote_dns_port:%s", remote_dns_port)
    logging.info("===========Config==========")


def sendDnsData(data, s, addr):
    global remote_dns_server
    global remote_dns_port
    global hosts
    local, data = dns.analysis(data, hosts)
    if local == 1:
        s.sendto(data, addr)
    else:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(data, (remote_dns_server, remote_dns_port))
        sock.settimeout(15)
        while True:
            try:
                rspdata = sock.recv(4096)
            except Exception as e:
                logging.warning("Recv:\t%s" % e)
                break
            s.sendto(rspdata, addr)
            break


def main():
    init()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        logging.info("Trying start bind local IP：%s and port:%s",
                     str(local_dns_server),
                     str(local_dns_port))
        s.bind((local_dns_server, local_dns_port))
    except Exception as e:
        logging.info("\nBinding failed! Please run as administrator，\n"
                     "\nAnd check the local IP address and port is correct?\n\n")
        logging.info("==========Error message==========")
        logging.critical(e)
        return
    logging.info("Bind successfully! Running ...")
    while True:
        try:
            data, addr = s.recvfrom(2048)
            worker = threading.Thread(target=sendDnsData, args=(data, s, addr,))
            worker.setDaemon(True)
            worker.start()
        except Exception as e:
            logging.warning("Unknow error:\t%s" % e)


if __name__ == '__main__':
    main()
