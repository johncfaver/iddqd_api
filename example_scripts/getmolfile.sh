#!/bin/bash

#Script to download MOL file for a compound in an IDDQD library.
#Usage:
#   ./getmolfile.sh ABC001
#       (to download 3D MOL file for the compound named ABC001)
#
#   or
#
#   ./getmolfile.sh 591
#       (to download 3D MOL file for compound associated with molid 591)
#
#User will be prompted for username/password/compound if not supplied.
#

server_url="https://host:port"
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
fi

if [ ! $molarg ];then
    echo
    read -p "Enter molid or molname:" -t 10 molarg
fi
##########
#Send request.
#Assume molarg is a molid if it contains only digits
#Assume molarg is a molname if it contains characters or digits

if [[ $molarg =~ ^[0-9]*$ ]];then
    response=$(curl --cacert $ssl_cert -s $server_url/molfile -d username=${username} -d password=${password} -d molid=$molarg)
elif [[ $molarg =~ ^[_a-zA-Z0-9-]*$ ]];then
    response=$(curl --cacert $ssl_cert -s $server_url/molfile -d username=${username} -d password=${password} -d molname=$molarg)
fi    

if [[ $response == Error:* ]];then
    echo $response
    exit
else
    echo "$response" 
fi

echo
