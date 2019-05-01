#####################################################################
## Writen by Murray Deerbon - La Trobe University Library Ver 0.3
## April 2019  m.deerbon@latrobe.edu.au  
## Program to read Partner data from Alma to an XML file
## and clean it up suitable for reload and save it to data sub-directory
##
## Stores the file as 'resource_partnersYYYYMMDD_HHMMSS.xml' 
##
#################################################################
## Note:  To get a fully clean record, variable 'remove2' must match
## the number of records in Alma
## If is doesn't change it in this code, and re-run it
print('Program starts - extracting all partner records from Alma')

from urllib.request import Request, urlopen
from urllib.parse import urlencode, quote_plus
from datetime import datetime
import yaml
import math
import os
import sys 

# create folders for data and log files
dirData='./data'
yaml_folder = '../yaml/'
config = yaml_folder + 'config.yaml'

for d in [ dirData ]:
    if not os.path.exists(d):
        os.makedirs(d)  #  create folders if they don't exist

def replace_stuff(f, r, in_string):
    in_string = in_string.replace(f,r)
    return in_string

def roundup(x):  # rounds up the records to extract to the next 100 
    return int(math.ceil(x/100))*100

def now():
    dt = datetime.now().strftime('%Y%m%d_%H%M%S')
    return dt
def pause():
    nxt = input('press the any key to continue ' )
    return nxt

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

def get_records(APIKey, off_set, url):
    queryParams = '?' + urlencode({ quote_plus('limit') : 100 ,quote_plus('offset') : x-100 ,quote_plus('APIKey') : APIKey  })
    request = Request(url + queryParams)
    request.get_method = lambda: 'GET'
    response_body = urlopen(request).read()
    line_in = response_body.decode('utf-8')
    return line_in

ladd_url = conf['ladd_url']
url = conf['alma_url']   
APIKey = conf['APIKey']
sand_alma_url = conf['sand_alma_url']
sand_APIKey = conf['sand_APIKey']
numrecs = conf['numrecs']   #: 1199

numRecs = conf['numrecs']
remove1 = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
remove2 = '<partners total_record_count="' + str(numRecs) + '">' #  the number of records as reported by Alma 
remove3 = '</partners>'
newline = "</partner>\n<partner "
oldline = "</partner><partner "
empty_str = ''
url = conf['alma_url']   
APIKey = conf['APIKey']
recds = roundup(numRecs)+1

# sort out the output file name
fout = dirData + '//' + 'resource_partners' + now() + '.xml'
print(f'Output filename is: {fout}')
 
with open(fout,'w') as fo:
    fo.write(remove1 + '\n' + remove2 + '\n')
    for x in range(100,recds,100):  
        
        # this bit hits the API to 'get' the next 'x' records
        line_in = get_records(APIKey, x, url)
        while oldline in line_in:
            # remove strings from the data until oldline is done
            line_in = replace_stuff(remove1, empty_str, line_in) # remove strings from 
            line_in = replace_stuff(remove2, empty_str, line_in)
            line_in = replace_stuff(remove3, empty_str ,line_in)
            line_in = replace_stuff(oldline, newline, line_in)
        fo.write(line_in + '\n')
        print(f'{x} records processed ')
    fo.write('\n' + remove3)
print('Program finished')








            
