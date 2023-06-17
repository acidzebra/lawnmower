# The LawnMower for Morrowind
version = "1.5.4"
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
# 1.4 - refinement of radius lists, code cleanup and optimization, added nograss_xxl for easier city cleaning using grassblocker, added autoclean_cities_vanilla.esp for cleaning stuff in vanilla that lawnmower can't reach by itself
# 1.5 - rewrote ref matching loops + bugfixes, futher refinement of radius lists, reduced memory use, minor changes to file loading, added autoclean_cities_TR.esp for cleaning cities and villages in TR
# 1.5.1 - removed "furn" from smalllists (now default radius), added step to delete json before start if deletemodjson = True
# 1.5.2 - updated grassblocker meshes to better match radii set here, added check to avoid writing file when no changes are made, added a little more detail to final report, made quieter when moreinfo=False, added overwrite switch, added Creatures mod stuff to skiplists
# 1.5.3 - forgot to add interior/exterior check to comparekeys, saves some time to skip. Time we need to extend the search grid for any cell to the eight cells around it to catch edge cases of grass+objects on bordering cells which do clip.
# 1.5.4 - made the "search eight cells around a cell" for extra accurate cleaning into a new switch: deepclean (default = False). Improved interior detection thanks to a discussion with abot on MMC discord

# START OF USER-CONFIGURABLE STUFF

# moreinfo mode spits out more messages, defaults to True
moreinfo = True
# delete the mod .json file after generation? Default True, set to False to speed up batch operations (json file will be reused). 
# DON'T FORGET TO TURN THIS OFF IF YOU'VE MADE CHANGES TO A MOD IN BETWEEN RUNNING LAWNMOWER.
deletemodjson = False
# radius to cut grass around mesh if no overrides on basis of refID, default 220.00
defaultradius = 220.00
# overwrite existing files? (normal behavior is to rename original grassfile to grassfile.00x.esp)
overwrite = False
# DeepClean will improve lawnmower's accuracy at the cost of speed by inspecting the eight cells surrounding each searched cell to catch edge cases, defaults to False. The difference in most cases is minimal.
deepclean = True

# radius control, the more things in these lists, the slower things go. This is a decent set and seems to catch vanilla/TR/OAAB/etc stuff pretty well.
skiplist = ["bridge","invis","collis","log","wreck","ship","boat","mist","sound","teleport","trigger","thiefdoor","steam","beartrap","marker","fauna","fx","forcefield","ranched","scrib","_ase_","rp_","plx_","_fau_","_cre_","cr_","lvl_","_lev+","_lev-","_cattle","_sleep","_und_","bm_ex_fel","bm_ex_hirf","bm_ex_moem","bm_ex_reav","wolf","bm_ex_isin","bm_ex_riek","kwama","crab","t_sky_stat_","t_sky_rstat","SP_stat_","berserk","terrain_rock_wg_06","terrain_rock_wg_04","terrain_rock_wg_11","terrain_rock_wg_13"]
smalllist = ["tree","parasol","railing","flora","dwrv_block","rubble","nograss_small","plant"]
largelist = ["strongh","pylon","portal","ex_velothi","entrance","foundation","entr_","terrwater","necrom","temple","fort","doomstone","lava","canton","altar","palace","tower","_keep","fire","tent","statue","nograss_large","striderport","bcom_gnisis_rock","terrain_rock_wg_09","terrain_rock_wg_10","terrain_rock_wg_12"]
mediumlist = ["ex_","house","building","shack","ruin","bw_hlaal","door","_d_","docks","gate","grate","waterfall","_x_","well","dae","stair","steps","bazaar","platf","tomb","exit","harbor","shrine","menhir","nograss_medium","pillar","terrain_rock_rm_12","terrain_rock_wg_05","terrain_rock_wg_07","terrain_rock_wg_08","terrain_rock_ac_10","terrain_rock_ac_11","terrain_rock_ac_12"]
xllist = ["nograss_xl"]
xxllist = ["nograss_xxl"]

# lists are extensible, you could create a new one with your custom stuff and then add the relevant data to the lists below (name of list, radius setting, whether to skip for cutting grass)
reftable = [skiplist,smalllist,largelist,mediumlist,xllist,xxllist]
radiustable = [1,120,600,400,1000,2000]
skiptable = [True,False,False,False,False,False]

# if you want to see what decisions are made about refs set one or both of these to True, would recommend to pipe output to a text file (it's a LOT of text)
debugradiuslist = False
debugmove = False 
### END OF USER-CONFIGURABLE STUFF
# I mean you could change stuff below too if you wanted and you're welcome to do so

import json
import io
import sys
import os
import gc

def is_clipping(circle_x, circle_y, rad, x, y):
    if ((x - circle_x) * (x - circle_x) + (y - circle_y) * (y - circle_y) <= rad * rad):
        return True
    else:
        return False

def is_in_list(myrefid, reflist):
    if any(searchterm in myrefid for searchterm in reflist):
        return True
    else:
        return False

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

if moreinfo:
    print("Lawnmower for Morrowind",str(version),"by acidzebra: grass go brrrr")

jsonmodname = modinputfile[:-4]+".json"
if deletemodjson and os.path.isfile(str(jsonmodname)):
    os.remove(jsonmodname)
if not os.path.isfile(str(jsonmodname)):
    if moreinfo:
        print("converting mod file to JSON...")
    try:
        target = "tes3conv.exe \""+str(modinputfile)+"\" \""+str(jsonmodname)+"\""
        os.system(target)
    except Exception as e:
        print("FATAL: unable to convert mod to json: "+repr(e)) 
if not os.path.isfile(str(jsonmodname)):
    sys.exit()
if moreinfo:
    print("reading mod file JSON...")
f = io.open(jsonmodname, mode="r", encoding="utf-8")
modfile_contents = f.read()
modfile_parsed_json = json.loads(modfile_contents) 
f.close()
del modfile_contents
if deletemodjson:
    os.remove(jsonmodname)

if moreinfo:
    print("converting grass file to JSON...")
try:
    target = "tes3conv.exe \""+str(grassinputfile)+"\" tempgrass.json"
    os.system(target)
except Exception as e:
    print("FATAL: unable to convert grassfile to json: "+repr(e))
if not os.path.isfile("tempgrass.json"):
    sys.exit()
if moreinfo:
    print("reading grass file JSON...")
f = io.open("tempgrass.json", mode="r", encoding="utf-8")
grassfile_contents = f.read()
grassfile_parsed_json = json.loads(grassfile_contents)
f.close()
del grassfile_contents
os.remove("tempgrass.json")

gc.collect()
    
exportfile = []
exported = False
skipitem = False
radius = defaultradius
grasstotalcount = 0
grasskillcount = 0
grasskilltotalcount = 0
extcellcount = 0
matchcellcount = 0
tempx = 0
tempy = 0
changesmade = False
if moreinfo:
    print("examining grass file...")
for keys in grassfile_parsed_json:
    if keys["type"] != "Cell":
        exportfile.append(keys)
        exported = True
    elif "INTERIOR" in keys["data"]["flags"]:
        exportfile.append(keys)
        exported = True
    elif len(keys["references"])>0:
        extcellcount+=1
        for comparekeys in modfile_parsed_json:
            if comparekeys["type"] == "Cell" and "INTERIOR" not in comparekeys["data"]["flags"]:
                x = -1
                y = -1
                while x < 2:
                    y=-1
                    while y < 2:
                        if not deepclean:
                            x=0
                            y=0
                        searchgrid = []
                        searchgrid = [int((comparekeys["data"]["grid"][0])+x),(int(comparekeys["data"]["grid"][1])+y)]
                        if not deepclean:
                            x = 3
                            y = 3
                        #print(searchgrid)
                        if len(comparekeys["references"])>0 and (searchgrid == keys["data"]["grid"]):
                            if moreinfo:
                                if deepclean:
                                    print(grassinputfile+" and "+modinputfile+" matched cell "+str(searchgrid)+" searching nearby cell "+str(comparekeys["data"]["grid"]))
                                else:
                                    print(grassinputfile+" and "+modinputfile+" matched cell "+str(searchgrid))
                            matchcellcount+=1
                            for refs in keys["references"]:
                                if refs["translation"][2] != -200000:
                                    grasstotalcount+=1
                                    for comparerefs in comparekeys["references"]:
                                        checkthismesh = comparerefs["id"].casefold()
                                        matchitem = False
                                        tablecount = 0
                                        for letsref in reftable:
                                            if not matchitem and is_in_list(checkthismesh,reftable[tablecount]):
                                                skipitem = skiptable[tablecount]
                                                radius = radiustable[tablecount]
                                                matchitem = True
                                                if debugradiuslist and comparekeys["data"]["grid"][0] == 23 and comparekeys["data"]["grid"][1] == 10:
                                                    print("checking",refs["id"],"against",checkthismesh,",skip:",skipitem,",radius:",radius)
                                            tablecount+=1
                                            if matchitem:
                                                break
                                        matchitem = False 
                                        if not skipitem and refs["translation"][2] != -200000 and is_clipping(comparerefs["translation"][0],comparerefs["translation"][1],radius,refs["translation"][0],refs["translation"][1]):
                                            changesmade = True
                                            if debugmove:
                                                print("CLIPPING",refs["id"],refs["translation"][0],refs["translation"][1],"with",checkthismesh,",skip:",skipitem,",radius:",radius,comparerefs["translation"][0],comparerefs["translation"][1])
                                            refs["translation"][0] = 0
                                            refs["translation"][1] = 0
                                            refs["translation"][2] = -200000
                                            grasskillcount+=1
                                            grasskilltotalcount+=1
                                        skipitem = False
                                        radius = defaultradius
                        y+=1
                    x+=1
        exportfile.append(keys)
        exported = True
    else:
        if not exported:
            exportfile.append(keys)
    if moreinfo:
        if grasskillcount > 0:
            print("removed "+str(grasskillcount)+" grass references in",str(searchgrid)," for a total of",grasskilltotalcount)
    exported = False
    skipitem = False
    grasskillcount=0
    radius = defaultradius

if changesmade:
    try:
        if moreinfo:
            print("finished examination, writing json file")
        with open('export.json', 'w', encoding='utf-8') as f:
            json.dump(exportfile, f, ensure_ascii=False, indent=4)
        if moreinfo:
            print("converting final json file to "+str(lwnmwroutputfile))
        if overwrite:
            target = "tes3conv.exe -o export.json \""+str(lwnmwroutputfile)+"\""
        else:
            target = "tes3conv.exe export.json \""+str(lwnmwroutputfile)+"\""
        os.system(target)
        f.close()
        os.remove("export.json")
    except Exception as e:
        print("FATAL: unable to convert finished grass to esp: "+repr(e))
        sys.exit()
    if deletemodjson and os.path.isfile(str(jsonmodname)):
        os.remove(jsonmodname)
    print("lawnmower evaluated "+str(extcellcount)+" exterior cells in "+str(grassinputfile)+" and found "+str(matchcellcount)+" matching cells in "+str(modinputfile)+", inspecting "+str(grasstotalcount)+" grass references and removing "+str(grasskilltotalcount)+" clipping ones. Enjoy your clean countryside!")
else:
    print("lawnmower made no modifications after examining "+str(extcellcount)+" exterior cells in "+str(grassinputfile)+" and "+str(matchcellcount)+" matching cells in "+str(modinputfile))
# Copyright © 2023 acidzebra

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.