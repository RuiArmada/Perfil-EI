#!/usr/bin/python3

import requests

def public_ip():
    return requests.get('https://api.ipify.org').text
