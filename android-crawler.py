# Goal: look in android.app at each interface, class, and exception
# for each, look for methods or fields with cautionary note
# for each, save in a file ./outFiles/<each-name>
#           with such an entity in format <api-name>:<note-text>
import urllib.request
from bs4 import BeautifulSoup
import re
import os

####################################################################################################
# https://developer.android.com/reference/android/app/Service
####################################################################################################

# get page and print contents
page = urllib.request.urlopen('https://developer.android.com/reference/android/app/package-summary')

# instantiate soup
soup = BeautifulSoup(page.read(), 'html.parser')
# find all td with the links we need
file_elems = soup.find_all('td', class_='jd-linkcol')
links_to_check = []
for file_elem in file_elems:
    #print(file_elem.text, end='\n'*2)
    thing = file_elem.text
    thing = re.sub(r'<.>', '', thing)
    links_to_check.append(thing)
#links_to_check.sort()
#print(links_to_check)

# Object to hold page data and page name
class Page:
    def __init__(self, name, data):
        self.name = name
        self.data = data
    def __repr__(self):
        return "Name: " + self.name + "   Data: " + str(self.data)[0:5] + "..."

# iterate through links and get page data
all_pages = []
# bigness of problem
for i in range(0,len(links_to_check)):
    url = 'https://developer.android.com/reference/android/app/{0}'
    url = url.format(links_to_check[i])
    print(str(i) + " " + url)
    page = urllib.request.urlopen(url)
    page = page.read()
    all_pages.append(Page(links_to_check[i], page))
#print(all_pages)
print()

# create ./outFiles if doesn't exist
if not os.path.exists('./outFiles'):
    os.makedirs('./outFiles')

# for each page, we need to create a file with the name page.name
# and then isolate the html elements with methods and fields, and
# check if there is a caution note, if there is, add a line to the file
for page in all_pages:
    filename = page.name
    print(filename)

    soup = BeautifulSoup(page.data, 'html.parser')
    deprecated_elems = soup.find_all("div", attrs={"data-version-added":True})
    print("Deprecated len " + str(len(deprecated_elems)))
    print()

    filetext = ""
    for i in range(len(deprecated_elems)):
        elem = str(deprecated_elems[i])
        #print(str(i+1) + " " + elem.strip(), end='\n'*2)
        # to get the name, we get text in between <h3>
        # to get the warning, we get text in between <p class="caution or note">
        soup = BeautifulSoup(elem, 'html.parser')

        entity_name = soup.find_all("h3")
        entity_note = soup.find_all('p', {'class':['caution', 'note']})

        if (len(entity_name) == 1 and len(entity_note) > 0):
            # if (len(entity_note) > 1):
            #     print("entity_name " + str(entity_name) + " entity_note " + str(entity_note))
            entity_name = str(entity_name[0].text)
            entity_name = re.sub(' +', ' ', entity_name)
            entity_name = re.sub('[\t\n\r]', '', entity_name)
            entity_name = entity_name.strip()
            #print(str(i+1) + " " + entity_name)
            filetext += entity_name + ":"
            for note in entity_note:
                entity_note = str(note.text)
                entity_note = re.sub(' +', ' ', entity_note)
                entity_note = re.sub('[\t\n\r]', '', entity_note)
                entity_note = entity_note.strip()
                #print(entity_note, end="\n"*2)

                filetext += entity_note + " "
                #print(filetext)
            filetext += "\n"

    if (filetext != ""):
        file = open("./outFiles/" + filename, "w")
        file.write(filetext)
        file.close()
        # file = open("./outFiles/" + filename, "r")
        # print(file.read())
        # file.close()
