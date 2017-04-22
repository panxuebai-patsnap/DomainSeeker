# -*- coding:utf-8 -*-
import urllib2
import json


# get hosts from remote url and wrap the data into dict
def fetchHosts(url):
    print("fetching hosts from:" + url)
    ips = []
    domains = []
    data = urllib2.urlopen(url).read()
    with open("./data/tmp", 'w') as f:
        f.write(data)
    with open("./data/tmp", 'r') as f:
        for line in f:
            if len(line) > 4 and line[0:1] != '#' and '\n' and '\r' and '\r\n':
                record = (' '.join(line.split())).split(' ')
                ips.append(record[1])
                domains.append(record[0])
    hosts = dict(zip(ips, domains))
    return hosts


# save dict into local file
def saveHosts(hosts):
    print("starting [save hosts]...")

    with open("./data/rpz.json", 'w') as f:
        json.dump(hosts, f)
    print("success! [save hosts] have done ! ")


# update wildcards from remote url
def fetchAndSaveWildcards(url):
    print("fetch wildcards from:" + url)
    data = urllib2.urlopen(url).read()
    with open("./data/wildcards.json", 'w') as f:
        f.write(data)
    print("success! [fetch wildcards] have done ! ")


def main():
    with open("./conf/hosts_repository_config.json", 'r') as d:
        repo = json.load(d)
    allHosts = {}

    for type in repo:
        if type == "hosts":
            for url in repo[type].values():
                hosts = fetchHosts(url)
                allHosts.update(hosts)
        elif type == "wildcards":
            fetchAndSaveWildcards(repo[type])
    saveHosts(allHosts)
    print("Congratulations! All updates completed.")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        raise e
