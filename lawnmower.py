# The LawnMower for Morrowind
version = "1.4"
#
# automatically clean all clipping grass from your Morrowind grass mods, no more grass sticking through floors and other places it doesn't belong.
# it is a little rough and there is very little handholding or much in the way of sanity checks. But it works.
#
# usage: python lawnmower.py INPUTMODFILE.ESP INPUTGRASSFILE.ESP OUTPUTGRASSFILE.ESP
#
# not tested on anything except Windows OS+openMW, both are English-language versions.

# 0.1-0.9 - various experiments to get this thing working
# 1.0 - IT WORKS
# 1.1 - code is faster, simpler, cleaner, with extra guard rails
# 1.2 - removed leftover debug stuff, fixed radius select loop
# 1.3 - further simplification, reduced amount of stuff to evaluate during loops
# 1.3.1 - minor radius list additions, minor reduced lookups, minor loop changes
# 1.3.2 - since I can't seem to fix the item matching stuff, added breaks to speed up exiting loops, so ugly ;_;
# 1.3.3 - reviewed the radius control lists and added debugradiuslist mode for same, added bunch of statics to lists
# 1.3.4 - added nograss_xxl for easier city cleaning, minor adjustments to radius control (reverted some rocks, added some more objects), added autoclean ESP for vanilla
# 1.4 - rollup of the above stuff for release

# START OF USER-CONFIGURABLE STUFF

# moreinfo mode spits out more messages, defaults to True
moreinfo = True
# delete the mod .json file after generation? Default True, set to False to speed up batch operations (will be reused). 
# DON'T FORGET TO TURN THIS OFF IF YOU'VE MADE CHANGES TO A MOD IN BETWEEN RUNNING LAWNMOWER.
deletemodjson = True
# radius to cut grass around mesh if no overrides on basis of refID, default 220.00
defaultradius = 220.00
# scale to use if no scale indicator present in the ref record, default 1
defaultscale = 1
# use the ingame scaling of the ref to help determine radius to cut grass in; default false, don't think it looks great. Maybe could work with scale = scale + (refscale/somenumber)?
userefscale = False

# radius control, the more things in these lists, the slower things go
skiplist = ["bridge","invis","collis","smoke","log","wreck","ship","boat","plank","light_de","sound","teleport","trigger","thiefdoor","_ward_","steam","beartrap","marker","fauna","fx","forcefield","scrib","_fau_","_cre_","cr_","lvl_","_lev+","_lev-","_cattle","_sleep","_und_","bm_ex_fel","bm_ex_hirf","bm_ex_moem","bm_ex_reav","wolf","bm_ex_isin","bm_ex_riek","kwama","crab","t_sky_stat_","t_sky_rstat","SP_stat_","berserk","terrain_rock_wg_06","terrain_rock_wg_04","terrain_rock_wg_11","terrain_rock_wg_13"]
smalllist = ["tree","parasol","railing","flora","dwrv_block","rubble","nograss_small","plant","pole","furn_de_","lamp","lantern","torch","hook","rings","scrapwood","barnac"]
smallradius = 120.00
largelist = ["strongh","pylon","portal","ex_velothi","entrance","_talker","entr_","terrwater","necrom","temple","fort","doomstone","lava","canton","altar","palace","tower","_keep","fire","tent","statue","nograss_large","striderport","bcom_gnisis_rock","terrain_rock_wg_09","terrain_rock_wg_10","terrain_rock_wg_12"]
largeradius = 600.00
mediumlist = ["ex_","house","building","shack","ruin","bw_hlaal","door","_d_","docks","gate","grate","waterfall","_x_","well","dae","stair","steps","bazaar","platf","tomb","exit","harbor","shrine","menhir","nograss_medium","pillar","terrain_rock_rm_12","terrain_rock_wg_05","terrain_rock_wg_07","terrain_rock_wg_08","terrain_rock_ac_10","terrain_rock_ac_11","terrain_rock_ac_12","_ranched"]
mediumradius = 400.00
xllist = ["nograss_xl"]
xlradius = 1000.00
xxllist = ["nograss_xxl"]
xxlradius = 2000.00

### END OF USER-CONFIGURABLE STUFF
# I mean you could change stuff below too if you wanted and you're welcome to do so
debugradiuslist = False
import json
import io
import sys
import os

def is_clipping(circle_x, circle_y, rad, x, y):
    if ((x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad):
        return True;
    else:
        return False;

try:
    modinputfile,grassinputfile,lwnmwroutputfile = sys.argv[1:]
except:
    print("usage: python lawnmower.py \"INPUTMODFILE.ESP\" \"INPUTGRASSFILE.ESP\" \"OUTPUTGRASSFILE.ESP\"")
    print("example: python lawnmower.py \"morrowind.esm\" \"lush_synthesis_WG.esp\" \"clean_lush_synthesis_WG.esp\"")
    print("this will compare the grass objects in lush_synthesis_WG against all objects in morrowind.esm and remove any clipping grass, writing the output to clean_lush_synthesis_WG.esp")
    print("you can choose to overwrite the old file if you prefer: lawnmower.py morrowind.esm lush_synthesis_WG.esp lush_synthesis_WG.esp")
    sys.exit()
    

if not os.path.isfile(modinputfile) or not os.path.isfile(grassinputfile):
    print("FATAL: mod or grass input file does not exist, cannot continue")
    sys.exit()

if not os.path.isfile("tes3conv.exe"):
    print("FATAL: cannot find path to tes3conv.exe, is it in the same folder as this script?")
    sys.exit()

print("Lawnmower for Morrowind",str(version)," by acidzebra: grass go brrrr")

try:
    jsonmodname = modinputfile[:-4]+".json"
    if not os.path.isfile(str(jsonmodname)):
        if moreinfo:
            print("converting mod file to JSON...")
        target = "tes3conv.exe \""+str(modinputfile)+"\" \""+str(jsonmodname)+"\""
        os.system(target)
    if moreinfo:
        print("reading mod file JSON...")
    f = io.open(jsonmodname, mode="r", encoding="utf-8")
    modfile_contents = f.read()
    modfile_parsed_json = json.loads(modfile_contents) 
    f.close()
    modfile_contents = ""
    if deletemodjson:
        os.remove(jsonmodname)
except Exception as e:
    print("FATAL: unable to convert mod to json: "+repr(e))
    sys.exit()

try:
    if moreinfo:
        print("converting grass file to JSON...")
    target = "tes3conv.exe \""+str(grassinputfile)+"\" tempgrass.json"
    os.system(target)
    if moreinfo:
        print("reading grass file JSON...")
    f = io.open("tempgrass.json", mode="r", encoding="utf-8")
    grassfile_contents = f.read()
    grassfile_parsed_json = json.loads(grassfile_contents)
    f.close()
    grassfile_contents = ""
    os.remove("tempgrass.json")
except Exception as e:
    print("FATAL: unable to convert grassfile to json: "+repr(e))
    sys.exit()
    
exportfile = []
exported = False
skipitem = False
radius = defaultradius
scale = defaultscale
grasstotalcount = 0
grasskillcount = 0
grasskilltotalcount = 0
extcellcount = 0
matchcellcount = 0

if moreinfo:
    print("examining grass file...")
for keys in grassfile_parsed_json:
    if keys["type"] != "Cell":
        exportfile.append(keys)
        exported = True
    elif (keys["data"]["grid"][0] > 512 or keys["data"]["grid"][1] > 512):
        exportfile.append(keys)
        exported = True
    elif len(keys["references"])>0:
        extcellcount+=1
        for comparekeys in modfile_parsed_json:
            if comparekeys["type"] == "Cell":
                grasscell = keys["data"]["grid"]
                if len(comparekeys["references"])>0 and comparekeys["data"]["grid"] == grasscell:
                    if moreinfo:
                        print(grassinputfile,modinputfile,"matched cell",str(grasscell))
                    matchcellcount+=1
                    for refs in keys["references"]:
                        grasstotalcount+=1
                        alreadymoved = False
                        if refs["translation"][2] == -200000:
                            alreadymoved = True
                        if not alreadymoved:
                            for comparerefs in comparekeys["references"]:
                                checkthismesh = comparerefs["id"].casefold()
                                matchitem = False
                                for items in skiplist:
                                    if items in checkthismesh:
                                        skipitem = True
                                        radius = 1
                                        matchitem = True
                                        if debugradiuslist:
                                            print("skipitem",checkthismesh)
                                    if matchitem:
                                        break
                                if not matchitem:
                                    for items in smalllist:
                                        if items in checkthismesh:
                                            radius = smallradius
                                            matchitem = True
                                            if debugradiuslist:
                                                print("smalllist",checkthismesh)
                                        if matchitem:
                                            break
                                if not matchitem:            
                                    for items in largelist:
                                        if items in checkthismesh:
                                            radius = largeradius
                                            matchitem = True
                                            if debugradiuslist:
                                                print("largelist",checkthismesh)
                                        if matchitem:
                                            break
                                if not matchitem:  
                                    for items in mediumlist:
                                        if items in checkthismesh:
                                            radius = mediumradius
                                            matchitem = True
                                            if debugradiuslist:
                                                print("mediumlist",checkthismesh)
                                        if matchitem:
                                            break
                                if not matchitem:  
                                    for items in xllist:
                                        if items in checkthismesh:
                                            radius = xlradius
                                            matchitem = True
                                            if debugradiuslist:
                                                print("xllist",checkthismesh)
                                        if matchitem:
                                            break
                                if not matchitem:  
                                    for items in xxllist:
                                        if items in checkthismesh:
                                            radius = xxlradius
                                            matchitem = True
                                            if debugradiuslist:
                                                print("xxllist",checkthismesh)
                                        if matchitem:
                                            break
                                matchitem = False
                                if debugradiuslist:
                                    if radius == defaultradius:
                                        print("default",checkthismesh)
                                if not alreadymoved and not skipitem and is_clipping(comparerefs["translation"][0],comparerefs["translation"][1],radius,refs["translation"][0],refs["translation"][1]):
                                    refs["translation"][0] = 0
                                    refs["translation"][1] = 0
                                    refs["translation"][2] = -200000
                                    grasskillcount+=1
                                    grasskilltotalcount+=1
                                skipitem = False
                                scale = defaultscale
                                radius = defaultradius
        exportfile.append(keys)
        exported = True
    else:
        if not exported:
            exportfile.append(keys)
    if moreinfo:
        if grasskillcount > 0:
            print("removed "+str(grasskillcount)+" grass references")
    exported = False
    skipitem = False
    grasskillcount=0
    radius = defaultradius

try:
    if moreinfo:
        print("finished examination, writing json file")
    with open('export.json', 'w', encoding='utf-8') as f:
        json.dump(exportfile, f, ensure_ascii=False, indent=4)
    if moreinfo:
        print("converting final json file to "+str(lwnmwroutputfile))
    target = "tes3conv.exe export.json \""+str(lwnmwroutputfile)+"\""
    os.system(target)
    f.close()
    os.remove("export.json")
except Exception as e:
    print("FATAL: unable to convert finished grass to esp: "+repr(e))
    sys.exit()

print("lawnmower evaluated "+str(extcellcount)+" exterior cells in the grass file and found "+str(matchcellcount)+" matching cells in the mod file, inspecting "+str(grasstotalcount)+" grass references and removing "+str(grasskilltotalcount)+" clipping ones. Enjoy your clean countryside!")

# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.