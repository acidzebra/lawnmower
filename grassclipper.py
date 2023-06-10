# grassclipper for morrowind 1.0
# 
# usage: python grassclipper.py grassmod1.esp grassmod2.esp grassmodoutput.esp
# cells between grassmod1 and grassmod2 will be compared, if a cell exists in both files, the cell from grassmod2 will be copied and replace the corresponding cell from grassmod1 in its entirety.
# the resulting file (mostly cells from grassmod1 with all matching cells replaced by grassmod2 will be written to grassmodoutput.esp
# 
# code is repurposed from lawnmower so might contain references and nuts.

import json
import io
import sys
import os
import os.path

# okay let's go, grab the commandline arguments and stuff them in variables
try:
    grassinputfile1,grassinputfile2,lwnmwroutputfile = sys.argv[1:]
except:
    print("usage: python grassclipper.py \"INPUTGRASSFILE1.ESP\" \"INPUTGRASSFILE2.ESP\" \"OUTPUTGRASSFILE.ESP\"")
    print("example: python lawnmower.py \"mod_A.esp\" \"mod_B.esp\" \"modABmerged.esp\"")
    print("this will compare the exterior cells in mod_A with cells in mod_B.esp, and overwrite any cells which exist in both with cells from mod_B, saving the result as modABmerged.esp")
    sys.exit()
# sanity check, did you actually type the right names or are you an idiot like me
if not os.path.isfile(grassinputfile1) or not os.path.isfile(grassinputfile2):
    print("FATAL: mod or grass input file does not exist, cannot continue")
    sys.exit()

print("Grassclipper by acidzebra")

# take input grass file 1, convert to json, and clean up
try:
    print("converting grass file 1 to JSON...")
    target = "tes3conv.exe \""+str(grassinputfile1)+"\" tempgrass1.json"
    os.system(target)
    print("reading grass file 1 JSON...")
    f = io.open("tempgrass1.json", mode="r", encoding="utf-8")
    grassfile1_contents = f.read()
    grassfile1_parsed_json = json.loads(grassfile1_contents)
    f.close()
    os.remove("tempgrass1.json")
except Exception as e:
    print("FATAL: unable to convert grassfile 1 to json: "+repr(e))
    sys.exit()
    

# take input grass file 2, convert to json, and clean up
try:
    print("converting grass file 2 to JSON...")
    target = "tes3conv.exe \""+str(grassinputfile2)+"\" tempgrass2.json"
    os.system(target)
    print("reading grass file 2 JSON...")
    f = io.open("tempgrass2.json", mode="r", encoding="utf-8")
    grassfile_contents2 = f.read()
    grassfile2_parsed_json = json.loads(grassfile_contents2)
    f.close()
    os.remove("tempgrass2.json")
except Exception as e:
    print("FATAL: unable to convert grassfile 2 to json: "+repr(e))
    sys.exit()

# some variables we will need
exportfile = []
currentcell = ""
exteriorcell = 0
matchingcell = 0
exported = 0
extcellcount = 0
matchcellcount = 0

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
# we have an exterior cell, now find a matching cell in the second file. I should rewrite this.
        for comparekeys in grassfile2_parsed_json:
            if comparekeys["type"] == "Cell" and comparekeys["data"]["grid"][0] < 512 and comparekeys["data"]["grid"][1] < 512:
                if comparekeys["data"]["grid"] == currentcell:
                    matchingcell = 1
            if matchingcell == 1:
                break
# if we found a corresponding cell in the second file
    if exteriorcell == 1 and matchingcell == 1:
        print("found overlapping exterior cell:",currentcell)
        matchcellcount+=1
        keys = comparekeys
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
print("grassclipper has finished after evaluating "+str(extcellcount)+" exterior cells and replacing "+str(matchcellcount)+" matching cells in "+str(grassinputfile1)+" with cells copied from "+str(grassinputfile2))

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.