import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import time
import json

from src.ctr_sh import crtshAPI
import src.sys as siis

DOMAIN = ""
NAME = ""
FOLDER = "files/"
URLS = []
TAB = "   "
SLEEP = 6

def bruteCracking(uri, urls, vulnerabilities, log):
    siis.writeHeader(log, TAB, uri)
    siis.writeHeader(vulnerabilities, TAB, uri)

    count = 1
    count_vulnerabilities = 0
    for url in urls:
        try:
            print("{}{}/{}".format(TAB*2, count, len(urls)), end="\r")
            count += 1

            url = 'http://' + url

            session = requests.Session()
            retry = Retry(connect=3, backoff_factor=0.5)
            adapter = HTTPAdapter(max_retries=retry)
            session.mount('http://', adapter)
            session.mount('https://', adapter)

            response = requests.get(url)
            table = "{}\t=>\t{}\n".format(response.status_code, url)

            log.write(table)

            if(response.status_code != 404):
                count_vulnerabilities += 1
                vulnerabilities.write(table)

        except Exception as e:
            table = "{}\t=>\t{}\t{}\n".format("000", url, e)
            log.write(table)
            time.sleep(SLEEP)

    print("{}{} vulnerabilities\n".format(TAB*2, count_vulnerabilities))


def getSubdomains():
    path = FOLDER + NAME + ".json"

    f = open(path, "w")
    subdomains = json.dumps(crtshAPI().search(DOMAIN))
    f.write(subdomains)
    f.close()

    subdomains_obj = json.loads(subdomains)

    for sub in subdomains_obj:
        if sub['common_name'] not in URLS:
            URLS.append(sub['common_name'])

    URLS.sort()

    print("{}{} urls found \n".format(TAB, len(URLS)))


if __name__ == "__main__":
    siis.start()

    if(siis.checkArgs() == False):
        siis.end("The domain is not correct")
        
    DOMAIN = siis.getDomain()
    NAME = DOMAIN.split('.', 1)[0]

    print("- Get all subdomains of {} \n".format(DOMAIN))
    getSubdomains()

    print("- Generating Log and Vulnerabilities files \n")

    log = open(FOLDER + NAME + ".txt", "w")
    vulnerabilities = open(FOLDER + NAME + "_vulnerabilities.txt", "w")

    for uri in URLS:
        print("{}-- Start of {} check\n".format(TAB, uri))

        with open("src/force.txt", "r") as f:
            contents = f.read()
            urls = contents.replace("{{BaseURL}}", uri)
            urls = urls.split(",")
            bruteCracking(uri, urls, vulnerabilities, log)

    vulnerabilities.close()
    log.close()

    siis.end()
