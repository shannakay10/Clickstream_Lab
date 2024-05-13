#!/usr/bin/python
import time
import datetime
import random
import gzip
import zipfile
import sys
sys.path.insert(0, '/home/ec2-user/.local/lib/python3.7/site-packages')
import pytz
import numpy
import argparse
import socket
from faker import Faker
from random import randrange
from tzlocal import get_localzone
local = get_localzone()
from ip2geotools.databases.noncommercial import DbIpCity
local = get_localzone()

class switch(object):
    def __init__(self, value):
        self.value = value
        self.fall = False

    def __iter__(self):
        """Return the match method once, then stop"""
        yield self.match
        raise StopIteration

    def match(self, *args):
        """Indicate whether or not to enter a case suite"""
        if self.fall or not args:
            return True
        elif self.value in args: # changed for v1.5, see below
            self.fall = True
            return True
        else:
            return False

parser = argparse.ArgumentParser(__file__, description="Fake Apache Log Generator")
parser.add_argument("--output", "-o", dest='output_type', help="Write to a Log file, a gzip file or to STDOUT", choices=['LOG','GZ','CONSOLE'] )
parser.add_argument("--log-format", "-l", dest='log_format', help="Log format, Common or Extended Log Format ", choices=['CLF','ELF'], default="ELF" )
parser.add_argument("--num", "-n", dest='num_lines', help="Number of lines to generate (0 for infinite)", type=int, default=1)
parser.add_argument("--prefix", "-p", dest='file_prefix', help="Prefix the output file name", type=str)
parser.add_argument("--sleep", "-s", help="Sleep this long between lines (in seconds)", default=0.0, type=float)

args = parser.parse_args()

log_lines = args.num_lines
file_prefix = args.file_prefix
output_type = args.output_type
log_format = args.log_format

faker = Faker()

timestr = time.strftime("%Y%m%d-%H%M%S")
otime = datetime.datetime.now()
def get_rtime():
    rtime = faker.date_time_between(start_date="-1w", end_date="now")
    return rtime

outFileName = 'access_log_geo_'+timestr+'.log' if not file_prefix else file_prefix+'_access_log_geo_'+timestr+'.log'

for case in switch(output_type):
    if case('LOG'):
        f = open(outFileName,'w')
        break
    if case('GZ'):
        f = gzip.open(outFileName+'.gz','w')
        break
    if case('CONSOLE'): pass
    if case():
        f = sys.stdout

# modern iPhone with Safari
iPhone = 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X) AppleWebKit/536.1 (KHTML, like Gecko) CriOS/13.0.848.0 Mobile/65R242 Safari/16.2'
# modern Android device with Firefox 
Android = 'Mozilla/5.0 (Android 12.0.0; Mobile; rv:53.0) Gecko/53.0 Firefox/53.0'
# modern windows PC with Chrome
Windows = 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/531.2 (KHTML, like Gecko) Chrome/111.0.553.2.0.854.0'
# modern Macintosh with Firefox
mac = 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 12.6.1; rv:1.9.3.20) Gecko/6156-07-12 15:15:32 Firefox/102.6.0)'

ualist_new = [
    iPhone,
    Android,
    Windows, 
    mac
]

hostname = socket.gethostname()
ipAddress = socket.gethostbyname(hostname)

flag = True
while (flag):
    if args.sleep:
        increment = datetime.timedelta(seconds=args.sleep)
    else:
        increment = datetime.timedelta(seconds=random.randint(0, 1))
    otime += increment

    ip = faker.ipv4()
    geo = DbIpCity.get(ip, api_key='free')
    geo_country = geo.country
    geo_region = geo.region
    geo_city = geo.city
    geo_lat = geo.latitude
    geo_long = geo.longitude
    
    # accessing cafe landing page on the webserver.
    uri = "/cafe"
    fn = "/var/www/html/cafe"
    dt = get_rtime()
    vrb ="GET"
    if uri.find("apps")>0:
        uri += str(random.randint(1000,10000))
    resp = "200"
    byt = int(random.gauss(5000,50))
    referer = "-"
    # 40 percent probablity for iPhone, 30 percent for Android (biasing mobile for people on the go). 20 percent Windows PC and 10 percent Mac. This is loosely based upon research at https://gs.statcounter.com/platform-market-share/desktop-mobile-tablet and https://www.statista.com/statistics/1228163/global-device-installed-base-by-type-worldwide/.
    useragent = numpy.random.choice(ualist_new,p=[0.4,0.3,0.2,0.1])
    if log_format == "CLF":
        f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s\n' % (ip,dt,tz,vrb,uri,resp,byt))
    elif log_format == "ELF":
        f.write('{ "time":"%s", "process":"%s", "filename":"%s", "remoteIP":"%s", "host":"%s", "request":"%s", "query":"", "method":"%s", "status":"%s", "useragent":"%s", "referer":"%s", "country":"%s", "region":"%s", "city":"%s", "lat": "%s", "lon":"%s"}\n' % (dt,byt,fn,ip,ipAddress,uri,vrb,resp,useragent,referer,geo_country,geo_region,geo_city,geo_lat,geo_long))        
    f.flush()
    
    # Accessing the menu. Note: not all users will access the menu, so using random function, if 1 access menu.  If 0, user leaves the website.
    Step2 = bool(random.getrandbits(1))
    if Step2 == 1:
        uri = "/cafe/menu.php"
        fn = "proxy:fcgi://localhost/var/www/html/cafe/menu.php"
        dt = get_rtime()
        vrb ="GET"
        if uri.find("apps")>0:
            uri += str(random.randint(1000,10000))
        resp = "200"
        byt = int(random.gauss(5000,50))
        referer = "http://" + ipAddress + "/cafe/index.php"
        if log_format == "CLF":
            f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s\n' % (ip,dt,tz,vrb,uri,resp,byt))
        elif log_format == "ELF": 
            f.write('{ "time":"%s", "process":"%s", "filename":"%s", "remoteIP":"%s", "host":"%s", "request":"%s", "query":"", "method":"%s", "status":"%s", "useragent":"%s", "referer":"%s", "country":"%s", "region":"%s", "city":"%s", "lat": "%s", "lon":"%s"}\n' % (dt,byt,fn,ip,ipAddress,uri,vrb,resp,useragent,referer,geo_country,geo_region,geo_city,geo_lat,geo_long)) 
        f.flush()
        
        # Making a purchase from the menu.  processOrder.php through method POST only occurs when a purchase is made.  Again using random function to simulate real world usage.
        Step3 = bool(random.getrandbits(1))
        if Step3 == 1:
            uri = "/cafe/processOrder.php"
            fn = "proxy:fcgi://localhost/var/www/html/cafe/processOrder.php"
            dt = get_rtime()
            vrb ="POST"
            if uri.find("apps")>0:
                uri += str(random.randint(1000,10000))
            resp = "200"
            byt = int(random.gauss(5000,50))
            referer = "http://" + ipAddress + "/cafe/menu.php"
            if log_format == "CLF":
                f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s\n' % (ip,dt,tz,vrb,uri,resp,byt))
            elif log_format == "ELF": 
                f.write('{ "time":"%s", "process":"%s", "filename":"%s", "remoteIP":"%s", "host":"%s", "request":"%s", "query":"", "method":"%s", "status":"%s", "useragent":"%s", "referer":"%s", "country":"%s", "region":"%s", "city":"%s", "lat": "%s", "lon":"%s"}\n' % (dt,byt,fn,ip,ipAddress,uri,vrb,resp,useragent,referer,geo_country,geo_region,geo_city,geo_lat,geo_long))      
            f.flush()        
            
            # Making a second purchase from the menu.  This is a repeat customer. Again using random function to simulate real world usage.
            Step4 = bool(random.getrandbits(1))
            if Step4 == 1:
                uri = "/cafe/processOrder.php"
                fn = "proxy:fcgi://localhost/var/www/html/cafe/processOrder.php"
                dt = get_rtime()
                vrb ="POST"
                if uri.find("apps")>0:
                    uri += str(random.randint(1000,10000))
                resp = "200"
                byt = int(random.gauss(5000,50))
                referer = "http://" + ipAddress + "/cafe/menu.php"
                if log_format == "CLF":
                    f.write('%s - - [%s %s] "%s %s HTTP/1.0" %s %s\n' % (ip,dt,tz,vrb,uri,resp,byt))
                elif log_format == "ELF": 
                    f.write('{ "time":"%s", "process":"%s", "filename":"%s", "remoteIP":"%s", "host":"%s", "request":"%s", "query":"", "method":"%s", "status":"%s", "useragent":"%s", "referer":"%s", "country":"%s", "region":"%s", "city":"%s", "lat": "%s", "lon":"%s"}\n' % (dt,byt,fn,ip,ipAddress,uri,vrb,resp,useragent,referer,geo_country,geo_region,geo_city,geo_lat,geo_long))      
                f.flush()
            else:
                Step4 == 0
        else:
            Step3 == 0
    else:
        Step2 == 0

    # log_lines reduced by 1, as the loop finishes.
    log_lines = log_lines - 1
    # When log_lines reaches 0 end loop.
    flag = False if log_lines == 0 else True
    if args.sleep:
        time.sleep(args.sleep)
