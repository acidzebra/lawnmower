# Lawnmower
Lawnmower for Morrowind will clean grassmods faster, better, and more consistently than you can. Removes 99% of unwanted&amp;clipping grass.

# Prerequisites

- the source mods, scripts, and tes3conv all need to be in the same folder to run. If you use MO2 or some other VFS shenanigans, it's on you to figure out how to make that happen. Afterwards you can move the standalone output file wherever you want and do whatever with it.
- Python >= 3.5: https://www.python.org/downloads/windows/
- tes3conv - https://github.com/Greatness7/tes3conv/releases
- I only tested this on English-language Morrowind and OS, I think it will work on any other, but I can't test.
- Windows OS - python can run on other OSes but I've used some os and sys calls, I've no idea if they work as-is. You might have to change some code. The bulk of the code will run, you will need a working version of tes3conv for your OS.


# Using Lawnmower

Lawnmower will take an input esp/esm file, a grass mod, and an output file as commandline arguments. It will compare them and if there is any clipping detected, it will move the grass out of sight. The new grass file will have almost no clipping, guaranteed (or your money back). You can chain commands in a batch file to process multiple masters and mods:

`python lawnmower.py "Morrowind.esm" "mygrassmod.esp" "grassout1.esp"`

`python lawnmower.py "Vivec_Lighthouse.ESP" "grassout1.esp" "grassout2.esp"`

`python lawnmower.py "autoclean_cities_vanilla.esp" "grassout2.esp" "grassout3.esp"`  <---- NEW IN V1.4: CLEAN OUT ALL VANILLA CITIES AND OTHER DIFFICULT SPOTS AUTOMATICALLY WITH INCLUDED PATCH

`python lawnmower.py "Beautiful cities of morrowind.esp" "grassout3.esp" "shinynewnoclipgrassplugin.esp"`

The above would take your grassmod, compare it against morrowind.esm, vivec lighthouse, and bcom, remove any grass that clips with any object in those three mods, and saves the output to shinynewnoclipgrassplugin.esp
If you want, you can set the grassmod and output file to the same filename, e.g. "Morrowind.esm" "mygrassmod.esp" "mygrassmod.esp" will update your grassmod with the latest cuts.

Program speed depends on grass mod size and amount of objects in target mod file and your processor, vanilla morrowind regions take about two minutes per region for me. TR regions take noticeably longer because of the many, many objects placed and the large surface area.

# using Weedwhacker

Weedwhacker code was based on lawnmower. It will take a grass mod and a number between 1-99 as input, and will move a corresponding percentage of grass objects out of sight, effectively thinning it out by 1-99%. If you like a grass mod but think there's too much grass and don't want to regenerate the whole thing, this will quickly thin out the grass for you.

`python weedwhacker.py "mygrassmod.esp" "myfiftypercentreducedgrassmod" 50`

This command will go through every cell of mygrassmod.esp, remove 50% of grass randomly (dice roll for each grass object found), and save the output to myfiftypercentreducedgrassmod.esp

Program speed: very fast

# using Grassclipper

(probably more for mod authors, patch maintainers, and advanced users) Grassclipper code was based on lawnmower. It takes two grass mods as input. It will compare mod A with mod B and for any cell they have in common, will overwrite the cells of mod A with the cells of mod B, then saving the combined output to a single output file. BOTH GRASSMODS MUST BE GENERATED WITH THE SAME INI FILE.

This can fix floating grass and speed up creating patches - example: you have your favorite grassmod but use BCOM and have some floating grass. You then run https://www.nexusmods.com/morrowind/mods/23065mesh generator to generate a new grass file with only the BCOM esp as input. Grassclipper can now combine the grassmods for you:

`python grassclipper.py "myfavoritegrassmod.esp" "mynewlygeneratedtinygrasspatch.esp" "combinedgrassmod.esp"`


Result: no more floating grass in BCOM areas with your favorite grass mod (I do recommend manual inspection and clean afterwards, but it will be much less painful). 

Program speed: very fast
