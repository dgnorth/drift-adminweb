"""
Utility methods for determining country and region information for ip address
"""
from flask import g
import requests
import logging

log = logging.getLogger(__name__)

URL_IPINFO = 'https://ipinfo.io/%s?token=4bd0bd84ebc7b6'
URL_RESTCOUNTRIES = 'https://restcountries.eu/rest/v2/alpha/%s?fields=name;region;flag'

cached_ip_addresses = {}


def get_cached_country(ip_address):
    cache_key = 'ip_address_to_country1'
    global cached_ip_addresses
    if not cached_ip_addresses:
        cached_ip_addresses = g.redis.get(cache_key) or {}
    try:
        return cached_ip_addresses[ip_address]
    except KeyError:
        try:
            resp = requests.get(URL_IPINFO % ip_address)
            country = resp.json()['country']
            resp = requests.get(URL_RESTCOUNTRIES % country)
            js = resp.json()

            data = {'country_code': country, 'country_name': js['name'], 'flag': js['flag']}
            cached_ip_addresses[ip_address] = data
            g.redis.set(cache_key, cached_ip_addresses, expire=86400)
            return data
        except Exception as e:
            log.error("Error fetching country for %s: %s" % (ip_address, e))
            return {}
