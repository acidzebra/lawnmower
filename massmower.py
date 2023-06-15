# The MassMower for Morrowind
version = "0.3"
#
# DANGER DANGER DANGER
# NOT READY FOR PRODUCTION AND NO DOCUMENTATION PROVIDED
# NO GUARDRAILS, NO SAFETIES, NO CRYING

# TODO ADD INFO HERE

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
excludedmodlist = []
# TODO make a sane default list to speed stuff up
excludelist = ["TR_Mainland_21.esm","TR_Preview_21.esp","BCOM_mergedmaster.esm","Creatures.esp","bcsounds.esp","Cyr_Main.esm","Cyrodiil_Grass.ESP","Sky_Main_Grass.esp","Sky_Main.esm","Tamriel_Data.esm","TR_Data.esm"]

try:
    target_folder = sys.argv[1]
    target_folder = str(target_folder)
except:
# TODO explain this better
    print("usage: python massmower.py \"target directory\"")
    sys.exit()

if not os.path.isdir(target_folder):
    print("FATAL: target directory \"",target_folder,"\"does not exist.")
    sys.exit()

if not os.path.isfile("tes3conv.exe"):
    print("FATAL: cannot find path to tes3conv.exe, is it in the same folder as this script?")
    sys.exit()
    
if not os.path.isfile("lawnmower.py"):
    print("FATAL: cannot find path to lawnmower.py, is it in the same folder as this script?")
    sys.exit()
    
    
from os import listdir
from os.path import isfile, join

# TODO rewrite this to be case insensitive
esplist += [each for each in os.listdir(target_folder) if each.endswith('.esm')]
esplist += [each for each in os.listdir(target_folder) if each.endswith('.ESM')]
esplist += [each for each in os.listdir(target_folder) if each.endswith('.esp')]
esplist += [each for each in os.listdir(target_folder) if each.endswith('.ESP')]

filecounter = 1
grassmodcounter =0
normalmodcounter=0
checkedmod = False
fatalerror = False
for files in esplist:
    if files not in excludelist:
        jsonfilename = files[:-4]+".json"
        if deletemodjson and os.path.isfile(str(jsonfilename)):
            os.remove(jsonfilename)
        if not os.path.isfile(str(jsonfilename)):
            try:
                target = "tes3conv.exe \""+str(files)+"\" \""+str(jsonfilename)+"\""
                print("running",target)
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
            if keys["type"] != "Cell":
                pass
            elif (keys["data"]["grid"][0] > 512 or keys["data"]["grid"][1] > 512):
                pass
            elif len(keys["references"])>0:
                for refs in keys["references"]:
                    #print(refs)
                    if "GRS" in refs["id"] and (files not in excludelist) and not checkedmod:
                        grasscounter+=1
                        checkedmod = True
                    else:
                        if (files not in excludelist) and not checkedmod:
                            normalmodcounter+=1
                            modlist.append(files)
                            checkedmod = True
                    if checkedmod:
                        break
        checkedmod = 0
        filecounter+=1
        if grasscounter > 0:
            grassmodlist.append(files)
            grassmodcounter+=1
    else:
        print("skipping file",filecounter,"of",len(esplist),":",files,"(excludelist)")
        filecounter+=1
        excludedmodlist.append(files)
        
print("\nTotal of",str(grassmodcounter),"grassmods found:",str(grassmodlist))
print("\nTotal of",str(normalmodcounter),"other mods with exterior cell changes found:",str(modlist))
print("\nExcluded mods:",str(excludedmodlist),"due to being on the exclude list")
Prompt = None

gogogo = 0
while True:
    prompt = input("\nReview the above, does it look correct? (answer y or n):\n")
    if prompt in ['y', 'yes']:
        gogogo = 1
        break
    elif prompt in ['n', 'no']:
        break

if gogogo == 0:
    print("breaking off at user request")
    sys.exit()

for mods in modlist:
    for grassmods in grassmodlist:
        target = "lawnmower.py \""+str(mods)+"\" \""+str(grassmods)+"\" \""+str(grassmods)+"\""
        print("executing",target)
        os.system(target)
    
