#!/bin/bash

#Script to download information for a compound in an IDDQD library.
#Usage:
#   ./getmolinfo.sh ABC001
#       (to download info in JSON format for the compound named ABC001)
#
#   or
#
#   ./getmolfile 591
#       (to download info in JSON format for compound associated with molid 591)
#
#User will be prompted for username/password/compound if not supplied.
#

server_url="https://domain:port"
ssl_cert="/location/of/cert/iddqd.crt"
username=""
password=""
molarg=$1
##########
if [ ! $username ];then
    read -p "Username:" -t 10 username
fi

if [ ! $password ];then
    read -s -p "Password:" -t 10 password
    echo
fi

if [ ! $molarg ];then
    read -p "Enter molid or molname:" -t 10 molarg
fi
##########
#Send request.
#Assume molarg is a molid if it contains only digits
#Assume molarg is a molname if it contains characters or digits

if [[ $molarg =~ ^[0-9]*$ ]];then
    response=$(curl --cacert $ssl_cert -s $server_url/molinfo -d username=${username} -d password=${password} -d molid=$molarg)
elif [[ $molarg =~ ^[_a-zA-Z0-9-]*$ ]];then
    response=$(curl --cacert $ssl_cert -s $server_url/molinfo -d username=${username} -d password=${password} -d molname=$molarg)
fi    

if [[ $response == Error:* ]];then
    echo $response
    exit
else
    echo "$response" 
fi


