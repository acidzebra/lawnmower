# weedwhacker for morrowind 1.0
# 
# usage: python weedwhacker.py grassmod.esp grassmodoutput.esp [percentage of grass to remove, number between 1-99]
# example: python weedwhacker lush_synthesis_wg lush_50_reduced.esp 50 - half the grass will be removed
#
# code is repurposed from lawnmower so might contain references and nuts.

import json
import io
import sys
import os
import os.path
import random

# okay let's go, grab the commandline arguments and stuff them in variables
try:
    grassinputfile1,lwnmwroutputfile,percentage = sys.argv[1:]
except:
    print("usage: python weedwhacker.py \"grassmod.esp\" \"grassmodoutput.esp\" [percentage of grass to remove, number between 1-99]")
    print("example: python weedwhacker \"lush_synthesis_wg\" \"lush_50_reduced.esp\" 50")
    print("50% of the grass will be removed from the lush_synthesis_wg.esp plugin and saved as lush_50_reduced.esp")
    sys.exit()
# sanity check, did you actually type the right names or are you an idiot like me
if not os.path.isfile(grassinputfile1):
    print("FATAL: grass input file does not exist, cannot continue")
    sys.exit()

print("Weedwhacker by acidzebra")

# take input grass file, convert to json, and clean up
try:
    print("converting grass file to JSON...")
    target = "tes3conv.exe \""+str(grassinputfile1)+"\" tempgrass1.json"
    os.system(target)
    print("reading grass file JSON...")
    f = io.open("tempgrass1.json", mode="r", encoding="utf-8")
    grassfile1_contents = f.read()
    grassfile1_parsed_json = json.loads(grassfile1_contents)
    f.close()
    os.remove("tempgrass1.json")
except Exception as e:
    print("FATAL: unable to convert grassfile to json: "+repr(e))
    sys.exit()
    

# some variables we will need
exportfile = []
currentcell = ""
exteriorcell = 0
matchingcell = 0
exported = 0
extcellcount = 0
matchcellcount = 0
grasstotalcount = 0
grasskillcount = 0
percentage = int(percentage)
if percentage > 99:
    percentage = 99
if percentage < 1:
    percentage = 1
# loop through all keys in the grass file
print("examining grass file...")
for keys in grassfile1_parsed_json:
# copy as-is anything which isn't a cell
    if keys["type"] != "Cell":
        exportfile.append(keys)
        exported = 1
# copy as-is anything which looks like an interior cell
    if keys["type"] == "Cell" and (keys["data"]["grid"][0] > 512 or keys["data"]["grid"][1] > 512) and exported == 0:
        exportfile.append(keys)
        exported = 1
# if it's a cell and not an interior cell it must be exterior but let's check anyway, the esp format is full of surprises
    if keys["type"] == "Cell" and (keys["data"]["grid"][0] < 512 and keys["data"]["grid"][1] < 512):
        currentcell = keys["data"]["grid"]
        exteriorcell = 1
        extcellcount+=1
    if exteriorcell == 1:
        print("examining exterior cell:",currentcell)
        matchcellcount+=1
        for refs in keys["references"]:
            grasstotalcount+=1
            if random.randrange(1,100) >= (100-percentage):
                grasskillcount+=1
                refs["translation"][0] = 0
                refs["translation"][1] = 0
                refs["translation"][2] = -200000
        exportfile.append(keys)
    else:
        if exported == 0:
            exportfile.append(keys)
# reset everything for the next cell
    exteriorcell = 0
    exported = 0
    skipitem = 0
    matchingcell = 0
# we have exited the loop so assume we're done, write everything out to json and convert back to esp
try:
    print("finished examination, writing json file")
    with open('export.json', 'w', encoding='utf-8') as f:
        json.dump(exportfile, f, ensure_ascii=False, indent=4)
    print("converting final json file to "+str(lwnmwroutputfile))
    target = "tes3conv.exe export.json \""+str(lwnmwroutputfile)+"\""
    os.system(target)
    f.close()
    os.remove("export.json")
except Exception as e:
    print("FATAL: unable to convert finished grass to esp: "+repr(e))
    sys.exit()
# we are done, let everyone know how unefficient we were
print("grassclipper has finished after evaluating "+str(extcellcount)+" exterior cells and evaluating "+str(grasstotalcount)+" grass objects, removing "+str(grasskillcount)+" grass objects")

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.