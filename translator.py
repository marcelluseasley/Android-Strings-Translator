#
# Filename: translator.py
# 6/19/2016 12:09 AM
#
#
from adm import AdmOAuthClient
from bs4 import BeautifulSoup
import requests

import os
import sys

from lxml import etree
from lxml.etree import Element, SubElement

apiCallUrl = "http://api.microsofttranslator.com/V2/Http.svc/TranslateArray"

admClient = AdmOAuthClient("","") #client_id and client_secret from MS Azure account

accessToken = admClient.get_access_token()

headers = {
    'authorization': "Bearer {}".format(accessToken),
    'content-type': "text/xml",
    'cache-control': "no-cache",
    'postman-token': "7d4a7f35-4efe-7c65-bb72-20c78added8a"
    }

# your raw strings.xml content...of course you can modify this app to accept it from the command line
xml = """<resources>
    <string name="network_dialog_title">Connected?</string>
    <string name="network_dialog_message">It appears there is no network connection.</string>
    <string name="network_dialog_button_text">OK</string>
    <!-- main menu options -->
    <string name="action_refresh">Refresh lists</string>
    <string name="action_playlist_add">Add playlist</string>
    <string name="action_settings">Settings</string>
    <string name="action_news">News</string>
    <string name="action_about">About</string>
    <string-array name="tabs">
        <item>Search</item>
        <item>Tracks</item>
        <item>Artists</item>
        <item>Albums</item>
        <!-- <item>Playlists</item> -->
    </string-array>
    <string name="hello_blank_fragment">Hello blank fragment</string>
</resources>
"""

def justResources(argXML):
    soup = BeautifulSoup(argXML)
    if soup.body:
        return soup.body.next
    elif soup.html:
        return soup.html.next
    else:
        return soup

soup = justResources(xml)

#handle strings

ss = soup.find_all("string")

nameAttributeL = list()
originalValueL = list()

for s in ss:
    nameAttributeL.append(s["name"])
    originalValueL.append(s.text)

nameAttributeT = tuple(nameAttributeL) # cast to tuple so order cannot accidentally change
originalValueT = tuple(originalValueL) # same for the values; they correspond to the values tuple

#construct XML for the TranslateArray call

tt = soup.find_all("string-array") # the string array section..this gets passed to translateStringArrays


