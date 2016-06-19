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


def translateStrings(originalValueT, sourceLanguage, destinationLanguage):
    payloadBegin = """<TranslateArrayRequest>
    <AppId />
    <From>{}</From>
    <Options>
    <Category xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\" />
    <ContentType xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\" />
    <ReservedFlags xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\" />
    <State xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\" />
    <Uri xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\" />
    <User xmlns=\"http://schemas.datacontract.org/2004/07/Microsoft.MT.Web.Service.V2\" />
    </Options>
    <Texts>
    """.format(sourceLanguage)

    payloadEnd = """</Texts>
    <To>{}</To>
    </TranslateArrayRequest>
    """.format(destinationLanguage)

    payloadString =""

    for originalValue in originalValueT:
        payloadString += """<string xmlns=\"http://schemas.microsoft.com/2003/10/Serialization/Arrays\">{}</string>""".format(originalValue)

    finalPayload = payloadBegin + payloadString + payloadEnd

    response = requests.request("POST", apiCallUrl, data=finalPayload, headers=headers)
    #response.encoding="utf-8"

    response.raise_for_status()

    stringSoup = BeautifulSoup(response.text)

    translatedStringsL=list()
    for translatedString in stringSoup.find_all("translatearrayresponse"):
        translatedStringsL.append(translatedString.translatedtext.text)

    translatedStringsT = tuple(translatedStringsL)

    return translatedStringsT


def translateStringArrays(stringArrayChunk, sourceLanguage, destinationLanguage):
    stringArrayChunkD = dict()
    stringArrayChunkL = list()
    for t in stringArrayChunk:
        stringArrayChunkD[t["name"]] = translateStrings(tuple(t.text.strip().split("\n")), sourceLanguage,
                                                        destinationLanguage)

    return stringArrayChunkD


def constructStringXML(nameAttributes, translatedStrings,stringArraysDictionary):

    root = Element("resources")
    for i in range(len(nameAttributes)):
        child = SubElement(root, "string", name=nameAttributes[i])
        child.text = translatedStrings[i]

    for key in stringArraysDictionary:
        child = SubElement(root, "string-array", name=key)
        for item in stringArraysDictionary[key]:
            child2 = SubElement(child, "item")
            child2.text = item

    return etree.tostring(root,encoding="UTF-8")


language_codes = ['ar', 'zh', 'hi', 'es', 'pt',
                  'ru', 'ja', 'fr', 'de', 'ko',
                  'bg', 'ca', 'hr', 'cs', 'da',
                  'nl', 'et', 'fi', 'he', 'id',
                  'ms', 'ro', 'th', 'ur', 'vi',
                  'sv', 'cy']


if __name__ == "__main__":

    #this is the folder of your default values folder...where the values-{language code} folders will be created
    destinationFolder = r".......AndroidStudioProjects\MusiQuik\app\src\main\res"

    for language in language_codes:

        val = translateStrings(originalValueT, "en", language)
        val2 = translateStringArrays(tt, "en", language)
        output = constructStringXML(nameAttributeT, val, val2)

        completeFolderPath = destinationFolder + r"\values-" + language
        os.makedirs(completeFolderPath)
        with open(completeFolderPath + r"\strings.xml", "w") as fd:
            fd.write(output)