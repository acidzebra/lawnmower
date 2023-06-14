# The MassMower for Morrowind
version = "0.1"
#
# DANGER DANGER DANGER
# NOT READY FOR PRODUCTION AND NO DOCUMENTATION PROVIDED
# NO GUARDRAILS, NO SAFETIES, NO CRYING


# START OF USER-CONFIGURABLE STUFF

# moreinfo mode spits out more messages, defaults to True
moreinfo = True
deletemodjson = False
### END OF USER-CONFIGURABLE STUFF
# I mean you could change stuff below too if you wanted and you're welcome to do so

import json
import io
import sys
import os
import gc

grassmodlist = []
modlist = []
esplist = []
excludelist = ["TR_Data.esm","TR_Mainland.esm","TR_Mainland_21.esm","Tamriel_Data.esm","TR_merged_az.esm","Cyr_Main.esm","BCOM_mergedmaster.esm","Sky_Main.esm","TR_Preview_21.esp"]
reverse_exclude = False

def is_in_list(myrefid, reflist):
    if any(searchterm in myrefid for searchterm in reflist):
        return True
    else:
        return False

try:
    target_folder = sys.argv[1]
    target_folder = str(target_folder)
except:
    print("usage: python massmower.py \"target directory\"")
    sys.exit()
    

if not os.path.isdir(target_folder):
    print("FATAL: target directory \"",target_folder,"\"does not exist.")
    sys.exit()

if not os.path.isfile("tes3conv.exe"):
    print("FATAL: cannot find path to tes3conv.exe, is it in the same folder as this script?")
    sys.exit()

from os import listdir
from os.path import isfile, join

esplist += [each for each in os.listdir(target_folder) if each.endswith('.esm'.casefold())]
esplist += [each for each in os.listdir(target_folder) if each.endswith('.esp'.casefold())]


def hasgrass(myrefid, reflist):
    if any("GRS" in myrefid for searchterm in reflist):
        return True
    else:
        return False

#print(esplist)
#sys.exit()
filecounter = 1
grassmodcounter =0
normalmodcounter=0
checkedmod = 0
for files in esplist:
    #print(files)
    if files not in excludelist:
        jsonfilename = files[:-4]+".json"
        if deletemodjson and os.path.isfile(str(jsonfilename)):
            os.remove(jsonfilename)
        if not os.path.isfile(str(jsonfilename)):
            try:
                target = "tes3conv.exe \""+str(files)+"\" \""+str(jsonfilename)+"\""
                print(target)
                os.system(target)
            except Exception as e:
                print("FATAL: unable to convert mod to json: "+repr(e)) 
        if not os.path.isfile(str(jsonfilename)):
            sys.exit()
        f = io.open(jsonfilename, mode="r", encoding="utf-8")
        espfile_contents = f.read()
        modfile_parsed_json = json.loads(espfile_contents) 
        f.close()
        del espfile_contents
        if deletemodjson:
            os.remove(jsonfilename)
        print("examining file",filecounter,"of",len(esplist),":",files)
        grasscounter = 0
        for keys in modfile_parsed_json:
            #print(keys)
            # not a cell
            if keys["type"] != "Cell":
                pass
            # not an external cell
            elif (keys["data"]["grid"][0] > 512 or keys["data"]["grid"][1] > 512):
                pass
            # external cell and not a junk cell
            elif len(keys["references"])>0:
                # go through all keys
                for refs in keys["references"]:
                    #print(refs)
                    if "GRS" in refs["id"] and (files not in excludelist) and checkedmod == 0:
                        grasscounter+=1
                        checkedmod = 1
                    else:
                        if (files not in excludelist) and checkedmod == 0:
                            normalmodcounter+=1
                            modlist.append(files)
                            checkedmod = 1
        checkedmod = 0
        filecounter+=1
        if grasscounter > 0:
            grassmodlist.append(files)
            grassmodcounter+=1
            #print(files,"is a grassmod with",grasscounter,"GRS")

print("Total of",grassmodcounter,"grassmods found:",grassmodlist)
print("Total of",normalmodcounter,"other mods with exterior cell changes found:",modlist)
Prompt = None
# Loop until the user inputs a valid answer
state = 0
while True:
    Prompt = input("Do you wish to continue? answer y or n\n")
    if Prompt in ['y', 'yes']:
        state = 1 # switch state to processing state
        break
    elif Prompt in ['n', 'no']:
        break

if state == 0:
    print("breaking off at user request")
    sys.exit()

print("gogogo")

for mods in modlist:
    for grassmods in grassmodlist:
        target = "lawnmower.py \""+str(mods)+"\" \""+str(grassmods)+"\" \""+str(grassmods)+"\""
        print("executing",target)
        os.system(target)
    
