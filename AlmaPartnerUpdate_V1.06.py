import requests
from urllib.parse import urlencode, quote_plus
from urllib.request import Request
from urllib.request import urlopen as uReq
from bs4 import BeautifulSoup as bs
from datetime import datetime
import time
from http import HTTPStatus
import os
import yaml
import sys
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

ts = datetime.now()  # time start
## ######################################################################
## Written by Murray Deerbon - La Trobe University - January 2019
## m.deerbon@latrobe.edu.au 
##
## Program to screen scrape 'LADD members & suspensions' website.
## Results are stored in a CSV file
## CSV file results are then used to update the Alma Partner records
## marking partners as Active or Inactive, as appropriate.

## Version 1.06 April 2019
## Updated to change to a PUT rather than a Delete & Post
## Included the SSL import 
## #######################################################################

def check_for_code(a_key, cde, url):  # checks for a partner, and if it exists, returns the XML
    url =  url +'/{partner_code}'.replace('{partner_code}',quote_plus(cde))
    queryParams = '?' + urlencode({ quote_plus('APIKey') : a_key  })
    r = requests.get(url + queryParams)
    return r.status_code, r.text

def put_code(a_key, cde, values, url):  # PUTS the revised record
    url =  url +'/{partner_code}'.replace('{partner_code}',quote_plus(cde))
    queryParams = '?' + urlencode({ quote_plus('APIKey') : a_key  })
    values = values.encode()
    headers = {  'Content-Type':'application/xml'  }
    request = Request(url + queryParams
                      , data=values
                      , headers=headers)
    # PUT the data
    request.get_method = lambda: 'PUT'
    # read the data that has just been PUT
    response_body = uReq(request).read()  ## changed urlopen to uReq
    return

def now():
    dt = datetime.now().strftime(' %Y%m%d_%H%M%S ')
    return dt

# create folders for data and log files
dirLog='./logs'
dirData='./data'
yaml_folder = '../yaml/'
config = yaml_folder + 'config.yaml'

for d in [ dirLog, dirData ]:
    if not os.path.exists(d):
        os.makedirs(d)  #  create folders if they don't exist
        
# load config data  
try:       
    with open(config, 'r') as f:
        conf = yaml.load(f, Loader=yaml.FullLoader)
except FileNotFoundError:
    print(f'{config} file not found')
    print('This file is critical and the program will not run without it.')
    print('Press cancel at the window pop-up')
    quit()   # program terminates here if config file not found
except:
    print('Unexpected error: ', sys.exec_info()[0])
    quit() 
    
print('Program starts\n')
print('Starting screen scape from:')

## define counters and other variables  
log_string = ""
del_flag = False
newline = ' \n'
changed = 0
unchanged = 0
errors = 0
logtime = now().strip()
start_time = now().strip()
logfileName = dirLog + '//' + 'logfile' + logtime + '.log'  # log file for Alma Partner update

#####Screen Scrape variables #######
log_file_ss = dirLog + '//' + 'rotaScreenScrape.log'    # log file for screen scrape
ladd_url = conf['ladd_url']
print(ladd_url,'\n')

csv_in = dirData + '/' + 'LibAusSuspendlst' + now().strip() + '.csv'  ## CSV  file that holds the LADD data

### get web site page ###
data = uReq(ladd_url)
page_html = data.read()
data.close()

#####################################################################################

## get config.yaml data  
url = conf['alma_url']
s_url = conf['sand_alma_url']
APIKey = conf['APIKey']
s_APIKey = conf['sand_APIKey']
sandbox = conf['sandbox']
#####################################################################################

if sandbox == True:
    url = s_url
    APIKey =s_APIKey
    print(url)
    print(APIKey)
    print('Updating ALMA Sandbox')
    logfileName = logfileName + '_sand' + '.log'
    csv_in = dirData + '/' + 'LibAusSuspendlst' + now().strip() + '_sand' + '.csv'  ## CSV  file that holds the LADD data
    in_key = input('Press the any key to continue: ')
else:
    print(url)
    print(APIKey)
    print('Updating ALMA Production')
    csv_in = dirData + '/' + 'LibAusSuspendlst' + now().strip() + '.csv'  ## CSV  file that holds the LADD data
    #in_key = input('Press the any key to continue: ')
    
#######################################################################################
    
# html parsing
page_soup = bs(page_html, 'html.parser')
# grabs all the suspension directory table
table_content = page_soup.find("table", {"class":"views-table cols-6"})
tbody = table_content.find('tbody')
count_rec = 0
with open(csv_in,'w') as f:
    headers = 'nuc,lib_name,iso_ill,suspended,date_from,date_to \n'
    f.write(headers)
    for tr in tbody.findAll('tr'):
        nuc = tr.findAll('td')[0].text.strip()
        lib_name = tr.findAll('td')[1].text.strip()
        iso_ill = tr.findAll('td')[2].text.strip()
        suspended = tr.findAll('td')[3].text.strip()
        date_from = tr.findAll('td')[4].text.strip()
        date_to = tr.findAll('td')[5].text.strip()
        string = (nuc +','+ lib_name.replace(',',' ') +','+ iso_ill +','+ suspended +','+ date_from.replace(',',' ')  + ','+ date_to.replace(',',' ') +"\n").strip()
        f.write(string + '\n')
        count_rec += 1
        
with open(log_file_ss,'a') as lg:
    lg.write(f'Date time: {now()} filename: {csv_in}, records {count_rec} \n')

### - the CSV file of the rota changes has been created and the log file updated  
print('Screen scrape completed\n')
print('Updating Alma.  Working ... ')

with open(logfileName, 'w') as lg:
    lg.write(f'Source file for changes: {csv_in}\n')   
    with open(csv_in,'r') as fin:   # opens the file with all the partner codes 
        next(fin)                   # skips the first line to ignore the headers
        for lines in fin:
            line = lines.split(',')
            nuc = line[0].upper()       
            suspend = line[3]
            #print(nuc)     
            if suspend == 'Suspended':
                suspend = 'INACTIVE'
            else:
                suspend = 'ACTIVE'              
            new_values = 'New value for: ' + nuc + ' ' + suspend  # comment for log file
            valid_code = check_for_code(APIKey, nuc, url)  # uses internal get function
            if valid_code[0] == HTTPStatus.OK:            
                soup = bs(valid_code[1], 'xml') # covert to a 'soup' object
                active_stat = soup.find('status')
                a_s = active_stat.string    # the string component of the (active status) 
                if a_s == suspend:          # there is no need to delete and re-post
                    log_string = now() + nuc + ' before ' + suspend + ' after ' + a_s + ' no change ' + newline  #####
                    lg.write(log_string)                
                    unchanged += 1               
                else:               
                    active_stat.string = suspend  # the new value is assigned here
                    log_string = now() + nuc + ' Original values: ' + a_s + ' ' + new_values + newline
                    lg.write(log_string)
                    print(log_string.strip())               
                    put_partner = put_code(APIKey, nuc, soup, url)
                    changed += 1
            else:
                valid_code[0] != HTTPStatus.OK   # 200
                log_string = now() + nuc + " generated an error. Error code is " + str(valid_code[0]) + newline
                lg.write(log_string)        # log file update
                
                errors += 1
    lg.write(f'Errors: {errors}; NUCs changed: {changed}; NUCs unchanged: {unchanged} \n')
    lg.write(f'Time start: {start_time}, Time finished: '+ now())
### duration calcuations ########  
    tstop = datetime.now() # time stop
    diff = tstop - ts
    mins = int((diff.total_seconds()) / 60 )
    secs = int(diff.total_seconds() - (mins * 60))
    lg.write(f'Duration: {mins} minutes {secs} seconds')
    
print(f'Duration: {mins} minutes {secs} seconds')
print(f'Errors: {errors}; NUCs changed: {changed}; NUCs unchanged: {unchanged}')
print('Program finished')

