#!/usr/bin/env python

# Prints a formatted table of information for a given
# compound in an IDDQD database.

##################################################
server_url  = 'https://domain:port'
username    = None
password    = None
molarg      = None
##################################################

import urllib, urllib2
from getpass import getpass
import sys, json
    
def request(route,data):
    """"Make POST request to server
        data are arguments in a dict
        return response as dict
    """
    data = urllib.urlencode(data)
    response = urllib2.urlopen(server_url+route,data).read()
    if response[:6] == 'Error:':
        print response
        sys.exit()
    else:
        return json.loads(response)

if username is None:
    username = raw_input("Username:")
if password is None:
    password = getpass("Password:")
if len(sys.argv) == 2:
    molarg = sys.argv[1]
else:
    molarg = raw_input("Enter molname or molid:")

data = { 'username' : username,
         'password' : password }

if molarg.isdigit():
    data['molid'] = molarg
else:
    data['molname'] = molarg

#request info for molarg
response = request('/molinfo',data)

#Print data in response as table
print '\n'+''.join(['=' for i in xrange(40)])
print '\tINFO FOR {0} (molid {1}):'.format(response['molname'],response['molid'])
print '{0:2}Uploaded by {1} on {2}'.format('',response['author'],response['dateadded'].split()[0])
print '{0:2}MW: {1} Formula: {2}'.format('',response['molweight'],response['molformula'])
print ''.join(['=' for i in xrange(40)])

for row in response['data']:
    print '{0:>15}'.format(row['type']),
    if row['target']:
        print '      {0:<20}'.format(row['target']),
    print 
    for value in row['values']:
        print u'     {0:>10} {1:>10}'.format(value,row['units'])
    if len(row['values']) > 1:
        print '{0:<5}{1}'.format('',''.join(['-' for i in xrange(30)]))
        print u'     {0:>10} {1:>10} avg'.format(sum(row['values'])/len(row['values']),row['units'])
    print 

