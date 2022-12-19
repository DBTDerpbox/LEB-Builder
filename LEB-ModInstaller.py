import json
import os
import shutil
from zipfile import ZipFile

##Set amount of maps from the base game
baseMapCount = 21 #I swear i will create a cleaner solution to this later

##Set datapack location
dpFolder = "world/datapacks/4jbattle/data/4jbattle/"

def extractmod():
    print("Extracting mod archive!")
    with ZipFile(mod_archive, 'r') as zip:
        #Extract files
        zip.extractall(path="4j.modtools-temp")

def loadmodconfig():
    ##Load mod config
    global modconfig
    with open('4j.modtools-temp/config.json', 'r') as modconfigfile:
        modconfig = json.load(modconfigfile)
    #Create spaceless mod name variable
    global modnameSpaceless
    modnameSpaceless = str(modconfig['name']).replace(' ', '-')
    #Create mod ID variable
    global modID
    modID = str(modconfig['id'])
    print("Loaded config for mod "+str(modconfig['name']))

def replaceInFile(filePath,stringToReplace,replaceWith):
    ##Open file and replace text
    #Open file for reading
    lbFile = open(filePath, "r")
    #Read data
    fileContents = lbFile.read()
    #Replace the text
    fileContents = fileContents.replace(stringToReplace, replaceWith)
    #Open file for writing
    lbFile = open(filePath, "w")
    #Write new file
    lbFile.write(fileContents)
    #Close file
    lbFile.close

def injectmotd():
    filePath = "server.properties"
    if os.path.exists(filePath):
        replaceInFile(filePath, "\\u00A7ogit-", "\\u00A7oM-git-")
        filePath = "config/MiniMOTD/main.conf"
        if os.path.exists(filePath):
            replaceInFile(filePath, "<italic>git-", "⚒<italic>-git-")
        else:
            print("WARNING: Unable to find MiniMOTD config! Is this not a LEB-ToolBox server?")
    else:
        print("WARNING: Unable to find server.properties! Is this server configured properly?")

def enablemenu():
    ##Enable the menu on host options to manage mods
    replaceInFile(dpFolder+"functions/menu/load/host/mods/run.mcfunction",
    "#tellraw",
    "tellraw"
    )

def injectcode():
    print("Attempting to inject to datapack!")
    ##Get map ID
    #Open maprandom file
    filePath = dpFolder+"loot_tables/maprandom.json"
    with open(filePath, "r") as lbFile:
        loot_table = json.load(lbFile)
    #Get Map ID from file and add 1 to it
    maxMap = loot_table["pools"][0]["rolls"]["max"] + 1
    #Save to file
    loot_table["pools"][0]["rolls"]["max"] = maxMap
    with open(filePath, "w") as lbFile:
        json.dump(loot_table, lbFile)
    print("MapID: "+str(maxMap))
    #Set variable for the map id without the vanilla map count
    modCount = maxMap - baseMapCount
    #Close file
    lbFile.close
    ##Write to map load file
    # Open file
    filePath = dpFolder+"functions/game/setup/load.mcfunction"
    lbFile = open(filePath, "a")
    # Write header
    lbFile.write("\n##" + str(modconfig['name']))
    baseCmd = "execute if score #Store 4j.map matches " + str(
        maxMap) + " if score #Store 4j.maptype matches $MAPSIZE$ run dimensionloader prepareDimension 4jbattle:arena 4jbattle:$MAPNAME$ 4jbattle:game/loading/dimensionloaded"
    # Write teleport coordinates
    if modconfig['hassmall']:
        lbFile.write("\n#Small\n"+baseCmd.replace("$MAPSIZE$", "1").replace("$MAPNAME$", modID + "_small"))
    if modconfig['haslarge']:
        lbFile.write("\n#Large\n"+baseCmd.replace("$MAPSIZE$", "2").replace("$MAPNAME$", modID))
    if modconfig['haslargeplus']:
        lbFile.write("\n#Large+\n"+baseCmd.replace("$MAPSIZE$", "4").replace("$MAPNAME$", modID + "_largeplus"))
    if modconfig['hasremastered']:
        lbFile.write("\n#Remastered\n"+baseCmd.replace("$MAPSIZE$", "3").replace("$MAPNAME$", modID + "_remastered"))
    # Close file
    lbFile.close
    ##Write to map teleport file
    # Open file
    filePath = dpFolder+"functions/game/setup/teleport/load.mcfunction"
    lbFile = open(filePath, "a")
    # Write header
    lbFile.write("\n##" + str(modconfig['name']))
    baseCmd = "execute if score #Store 4j.map matches " + str(
        maxMap) + " if score #Store 4j.maptype matches $MAPSIZE$ in 4jbattle:arena run tp @s " + "$CENTERCOORDS$"
    # Write teleport coordinates
    if modconfig['hassmall']:
        lbFile.write("\n#Small\n"+baseCmd.replace("$MAPSIZE$", "1").replace("$CENTERCOORDS$", str(modconfig['centercoords_small'])))
    if modconfig['haslarge']:
        lbFile.write("\n#Large\n"+baseCmd.replace("$MAPSIZE$", "2").replace("$CENTERCOORDS$", str(modconfig['centercoords_large'])))
    if modconfig['haslargeplus']:
        lbFile.write("\n#Large+\n"+baseCmd.replace("$MAPSIZE$", "4").replace("$CENTERCOORDS$", str(modconfig['centercoords_largeplus'])))
    if modconfig['hasremastered']:
        lbFile.write("\n#Remastered\n"+baseCmd.replace("$MAPSIZE$", "3").replace("$CENTERCOORDS$", str(modconfig['centercoords_remastered'])))
    # Close file
    lbFile.close
    ##Have the map get loaded by mapdecider
    #Open file
    filePath = dpFolder+"functions/mapdecider/loadenabled.mcfunction"
    lbFile = open(filePath, "a")
    #Write header
    lbFile.write("\n#"+str(modconfig['name']))
    #Write code to enable the map if its enabled
    lbFile.write("\nexecute if score #Store 4j.enablemods matches 1 run scoreboard players operation #"+modID+" 4j.enablemap = #"+modID+" 4j.setenablemap\nexecute if score #Store 4j.enablemods matches 0 run scoreboard players set #"+modID+" 4j.enablemap 0")
    #Close file
    lbFile.close
    ##Allow map to be detected from voting
    #Open file
    filePath = dpFolder+"functions/mapdecider/findhighest.mcfunction"
    lbFile = open(filePath, "a")
    #Write header
    lbFile.write("\n#"+str(modconfig['name']))
    #Add code for finding the vote
    lbFile.write("\nexecute if score #"+modID+" 4j.enablemap matches 1 if score §a⚒:"+modnameSpaceless+" 4j.mapvote = #highestScore 4j.mapvote run scoreboard players set #Store 4j.map "+str(maxMap))
    #Close file
    lbFile.close
    ##Allow map to be detected from random chance
    #Open file
    filePath = dpFolder+"functions/mapdecider/randommod.mcfunction"
    lbFile = open(filePath, "a")
    #Write header
    lbFile.write("\n#"+str(modconfig['name']))
    #Add code for finding the vote
    lbFile.write("\nexecute if score #"+modID+" 4j.enablemap matches 1 if score #Store 4j.maprandom matches "+str(maxMap)+" run scoreboard players set #Store 4j.map "+str(maxMap))
    #Close file
    lbFile.close
    ##Set map types that arent available
    #Open file
    filePath = dpFolder+"functions/mapdecider/maptype/checkavailable.mcfunction"
    lbFile = open(filePath, "a")
    #Write header
    lbFile.write("\n##" + str(modconfig['name']))
    #Write disabled maps
    if modconfig['hassmall']:
        pass
    else:
        lbFile.write("\n#Small\nexecute if score #Store 4j.map matches "+str(maxMap)+" run scoreboard players set #Store 4j.maptypeavailable.small 0")
    if modconfig['haslarge']:
        pass
    else:
        lbFile.write("\n#Large\nexecute if score #Store 4j.map matches "+str(maxMap)+" run scoreboard players set #Store 4j.maptypeavailable.large 0")
    if modconfig['haslargeplus']:
        pass
    else:
        lbFile.write("\n#Large+\nexecute if score #Store 4j.map matches "+str(maxMap)+" run scoreboard players set #Store 4j.maptypeavailable.largeplus 0")
    if modconfig['hasremastered']:
        pass
    else:
        lbFile.write("\n#Remastered\nexecute if score #Store 4j.map matches "+str(maxMap)+" run scoreboard players set #Store 4j.maptypeavailable.remastered 0")
    #Close file
    lbFile.close
    ##Allow users to vote for the map
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/check/mods.mcfunction"
    lbFile = open(filePath, "a")
    #Write header
    lbFile.write("\n##add 1 to "+str(modconfig['name'])+"'s vote count if voted for")
    #If the user voted already
    lbFile.write("\n#If user has voted for this map\nexecute if score #"+modID+" 4j.enablemap matches 1 as @a[scores={4j.playermapvote="+str(maxMap)+"},tag=vote"+modID+"] run function 4jbattle:mapdecider/vote/error")
    #IF the user hasn't voted
    lbFile.write("\n#If the user hasnt voted for this map yet\nexecute if score #"+modID+" 4j.enablemap matches 1 as @a[scores={4j.playermapvote="+str(maxMap)+"}] run function 4jbattle:mapdecider/vote/add/"+modID)
    #Close file
    lbFile.close
    ##Load the map into the sidebar if enabeld
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/load.mcfunction"
    lbFile = open(filePath, "a")
    #Write header
    lbFile.write("\n#"+str(modconfig['name']))
    #Write code to load to sidebar
    lbFile.write("\n#"+str(modconfig['name'])+"\nexecute if score #"+modID+" 4j.enablemap matches 1 run scoreboard players set §a⚒:"+modnameSpaceless+" 4j.mapvote 0")
    #Close file
    lbFile.close
    ##Remove map from vote if another map is voted for
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/rmoldvote.mcfunction"
    lbFile = open(filePath, "a")
    #Write code to remove vote
    lbFile.write("\n##Remove "+str(modconfig['name'])+"map vote\nexecute if entity @s[tag=vote"+modID+"] run scoreboard players remove §a⚒:"+modnameSpaceless+" 4j.mapvote 1")
    #Close file
    lbFile.close
    ##Remove tag from user when switching votes
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/tagreset.mcfunction"
    lbFile = open(filePath, "a")
    #Write code to remove tag
    lbFile.write("\n##"+str(modconfig['name'])+"\ntag @s remove vote"+modID)
    #Close file
    lbFile.close
    ##Create file to execute when map is voted for
    #Create file
    filePath = dpFolder+"functions/mapdecider/vote/add/"+modID+".mcfunction"
    lbFile = open(filePath, "w")
    #Write code to add the vote
    lbFile.write("##Add vote\nscoreboard players add §a⚒:"+modnameSpaceless+" 4j.mapvote 1\n\n##Run global vote commands\nfunction 4jbattle:mapdecider/vote/add/global\n\n##Mark as voted\ntag @s add vote"+modID)
    #Close file
    lbFile.close
    ##Setup mod pages
    #Get current page count
    pageCount = int((modCount -1) / 5)
    pageOpenValue = pageCount + 2000
    #Create page folder if it doesnt exist already
    try:
        os.mkdir(dpFolder+"functions/mapdecider/vote/modmenu/page")
    except(FileExistsError):
        pass
    ##Take care of registering a page fully and adding adding the navigation buttons to it
    if os.path.exists(dpFolder+"functions/mapdecider/vote/modmenu/page/"+str(pageCount)+".mcfunction"):
        pass
    else:
        ##Add page to list of pages
        #Open file
        filePath = dpFolder+"functions/mapdecider/vote/modmenu/main.mcfunction"
        lbFile = open(filePath, "a")
        #Write code to display the button
        lbFile.write("\nexecute if score @s 4j.playermapvote matches -"+str(pageOpenValue)+" run function 4jbattle:mapdecider/vote/modmenu/page/"+str(pageCount))
        #Close file
        lbFile.close
        ##Add buttons to change page
        #Open file
        filePath = dpFolder+"functions/mapdecider/vote/modmenu/page/"+str(pageCount)+".mcfunction"
        lbFile = open(filePath, "a")
        #Add button to code
        lbFile.write("tellraw @s [\"\"")
        if pageCount > 0:
            lbFile.write(",{\"text\":\"<<\",\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(pageOpenValue-1)+"\"}}")
        else:
            lbFile.write(",{\"text\":\"<<\",\"color\":\"gray\"}")
        lbFile.write(",{\"text\":\" \",\"color\":\"blue\"},{\"translate\":\"4j.menu.mods.page\",\"color\":\"blue\"},{\"text\":\" "+str(pageCount+1)+" \",\"color\":\"blue\"}")
        lbFile.write(",{\"text\":\">>\",\"color\":\"gray\"},\"\\n\"]")
        #Close file
        lbFile.close
        ##Add forward button to previous page
        if pageCount > 0:
            replaceInFile(
                dpFolder+"functions/mapdecider/vote/modmenu/page/"+str(pageCount-1)+".mcfunction",
                "{\"text\":\">>\",\"color\":\"gray\"}",
                "{\"text\":\">>\",\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(pageOpenValue)+"\"}}"
                )
    ##Add map to map list
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/modmenu/page/"+str(pageCount)+".mcfunction"
    lbFile = open(filePath, "a")
    #Write code to display the button
    maxMapDisable = modCount + 3000
    lbFile.write("\nexecute if score #"+modID+" 4j.enablemap matches 1 run tellraw @s [\"\",{\"text\":\"["+str(modconfig['name'])+"] \",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(maxMapDisable)+"\"}},{\"text\":\"by "+str(modconfig['authors'])+"\",\"italic\":true,\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(maxMapDisable)+"\"}}]")
    lbFile.write("\nexecute if score #"+modID+" 4j.enablemap matches 0 run tellraw @s [\"\",{\"text\":\"["+str(modconfig['name'])+"] \",\"color\":\"gray\"},{\"text\":\"by "+str(modconfig['authors'])+"\",\"italic\":true,\"color\":\"dark_aqua\"}]")
    #Close file
    lbFile.close
    ##Add redirect to open GUI page for the mod
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/modmenu/map.mcfunction"
    lbFile = open(filePath, "a")
    #Write redirect code into the file
    lbFile.write("\n##"+str(modconfig['name'])+"\nexecute if score @s 4j.playermapvote matches -"+str(maxMapDisable)+" run function 4jbattle:mapdecider/vote/modmenu/map/"+modID)
    #Close file
    lbFile.close
    ##Add voting page for the map
    #Open file
    filePath = dpFolder+"functions/mapdecider/vote/modmenu/map/"+modID+".mcfunction"
    lbFile = open(filePath, "w")
    #Write header
    lbFile.write("##Display header\ntellraw @s {\"text\":\""+str(modconfig['name'])+" by "+str(modconfig['authors'])+"\\nVersion: "+str(modconfig['version'])+"\",\"color\":\"dark_aqua\"}")
    #Write description
    lbFile.write("\n\n##Display description\ntellraw @s {\"text\":\"\\n"+str(modconfig['description'])+"\\n\",\"color\":\"dark_aqua\"}")
    #Write vote button
    lbFile.write("\n\n##Display vote button\ntellraw @s [\"\",{\"text\":\"[\",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set "+str(maxMap)+"\"}},{\"translate\":\"4j.mapdecider.menu.vote\",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set "+str(maxMap)+"\"}},{\"text\":\"]\",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set "+str(maxMap)+"\"}}]")
    #Show go back button
    lbFile.write("\n\n##Display go back button\ntellraw @s [\"\",{\"text\":\"[\",\"color\":\"gray\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(pageOpenValue)+"\"},\"hoverEvent\":{\"action\":\"show_text\",\"contents\":[{\"translate\":\"4j.menu.mods.goback\",\"color\":\"dark_aqua\"}]}},{\"translate\":\"4j.generic.goback\",\"color\":\"gray\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(pageOpenValue)+"\"},\"hoverEvent\":{\"action\":\"show_text\",\"contents\":[{\"translate\":\"4j.menu.mods.goback\",\"color\":\"dark_aqua\"}]}},{\"text\":\"]\",\"color\":\"gray\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.playermapvote set -"+str(pageOpenValue)+"\"},\"hoverEvent\":{\"action\":\"show_text\",\"contents\":[{\"translate\":\"4j.menu.mods.goback\",\"color\":\"dark_aqua\"}]}}]")
    #Run the global functions
    lbFile.write("\n\n##Run global functions\nfunction 4jbattle:mapdecider/vote/modmenu/map/global")
    ##Create pages for maps management page
    #lbFile = open(filePath, "a")
    if os.path.exists(dpFolder+"functions/menu/load/host/mods/maps/list/"+str(pageCount)+".mcfunction"):
        pass
    else:
        ##Add page to list of pages
        #Open file
        filePath = dpFolder+"functions/menu/load/host/mods/maps/list/main.mcfunction"
        lbFile = open(filePath, "a")
        #Write code to display the button
        lbFile.write("\nexecute if score @s 4j.gamecfg matches "+str(pageOpenValue)+" run function 4jbattle:menu/load/host/mods/maps/list/"+str(pageCount))
        #Close file
        lbFile.close
        ##Add buttons to change page
        #Open file
        filePath = dpFolder+"functions/menu/load/host/mods/maps/list/"+str(pageCount)+".mcfunction"
        lbFile = open(filePath, "a")
        #Add button to code
        lbFile.write("tellraw @s [\"\"")
        if pageCount > 0:
            lbFile.write(",{\"text\":\"<<\",\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(pageOpenValue-1)+"\"}}")
        else:
            lbFile.write(",{\"text\":\"<<\",\"color\":\"gray\"}")
        lbFile.write(",{\"text\":\" \",\"color\":\"blue\"},{\"translate\":\"4j.menu.mods.page\",\"color\":\"blue\"},{\"text\":\" "+str(pageCount+1)+" \",\"color\":\"blue\"}")
        lbFile.write(",{\"text\":\">>\",\"color\":\"gray\"},\"\\n\"]")
        #Close file
        lbFile.close
        ##Add forward button to previous page
        if pageCount > 0:
            replaceInFile(
                dpFolder+"functions/menu/load/host/mods/maps/list/"+str(pageCount-1)+".mcfunction", 
                "{\"text\":\">>\",\"color\":\"gray\"}",
                "{\"text\":\">>\",\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(pageOpenValue)+"\"}}"
                )
    ##Add map to the GUI to enable/disable maps
    #Open file
    filePath = dpFolder+"functions/menu/load/host/mods/maps/list/"+str(pageCount)+".mcfunction"
    lbFile = open(filePath, "a")
    #Write code to display the button
    maxMapEnable = maxMap + 3000
    maxMapDisable = maxMap + 4000
    lbFile.write("\nexecute if score #"+modID+" 4j.setenablemap matches 1 run tellraw @s [\"\",{\"text\":\"[\",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapDisable)+"\"}},{\"text\":\"✔\",\"color\":\"green\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapDisable)+"\"}},{\"text\":\"] "+str(modconfig['name'])+" \",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapDisable)+"\"}},{\"text\":\"by "+str(modconfig['authors'])+"\",\"italic\":true,\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapDisable)+"\"}}]")
    lbFile.write("\nexecute if score #"+modID+" 4j.setenablemap matches 0 run tellraw @s [\"\",{\"text\":\"[\",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapEnable)+"\"}},{\"text\":\"❌\",\"color\":\"red\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapEnable)+"\"}},{\"text\":\"] "+str(modconfig['name'])+" \",\"color\":\"blue\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapEnable)+"\"}},{\"text\":\"by "+str(modconfig['authors'])+"\",\"italic\":true,\"color\":\"dark_aqua\",\"clickEvent\":{\"action\":\"run_command\",\"value\":\"/trigger 4j.gamecfg set "+str(maxMapEnable)+"\"}}]")
    ##Add the backend code to allow changing of the enabled/disabled state
    #Open file
    filePath = dpFolder+"functions/menu/configure/map.mcfunction"
    lbFile = open(filePath, "a")
    #Write code for allowing the changes
    lbFile.write("\n##Disable "+str(modconfig['name'])+" if set to "+str(maxMapDisable)+"\nexecute if score #Store 4j.mapcount matches 2.. if score #"+modID+" 4j.setenablemap matches 1 as @s[scores={4j.gamecfg="+str(maxMapDisable)+"}] run function 4jbattle:menu/load/host/map/"+modID+"/disable")
    lbFile.write("\n##Enable "+str(modconfig['name'])+" if set to "+str(maxMapEnable)+"\nexecute unless score #"+modID+" 4j.setenablemap matches 1 as @s[scores={4j.gamecfg="+str(maxMapEnable)+"}] run function 4jbattle:menu/load/host/map/"+modID+"/enable")
    #Close file
    lbFile.close
    ##Enable map by default
    #Open file
    filePath = dpFolder+"functions/menu/load/host/defaults/map.mcfunction"
    lbFile = open(filePath, "a")
    #Write code to enable the map
    lbFile.write("\nscoreboard players set #"+modID+" 4j.setenablemap 1")
    #Close file
    lbFile.close
    ##Set max map count for adding
    #Set text to replace
    stringToReplace = "#Store 4j.mapcount "+str(modCount -1)
    replaceWith = "#Store 4j.mapcount "+str(modCount)
    #Replace text for adding
    replaceInFile(dpFolder+"functions/menu/load/host/mods/enable.mcfunction", stringToReplace, replaceWith)
    replaceInFile(dpFolder+"functions/menu/load/host/mods/disable.mcfunction", stringToReplace, replaceWith)
    ##Create files for enabling the map
    #Create folder
    os.mkdir(dpFolder+"functions/menu/load/host/map/"+modID)
    #Create file
    filePath = dpFolder+"functions/menu/load/host/map/"+modID+"/enable.mcfunction"
    lbFile = open(filePath, "w")
    #Write code to enable the map
    lbFile.write("##Enable map\nscoreboard players set #"+modID+" 4j.setenablemap 1\n\n##Increase mapcount\nscoreboard players add #Store 4j.mapcount 1\n\n##Open menu\n#Set score\nscoreboard players set @s 4j.gamecfg "+str(pageOpenValue)+"\n#Run function\nfunction 4jbattle:menu/load/host/mods/open/maps")
    #Close file
    lbFile.close
    ##Create files for disabling the map
    #Create file
    filePath = dpFolder+"functions/menu/load/host/map/"+modID+"/disable.mcfunction"
    lbFile = open(filePath, "w")
    #Write code to disable the map
    lbFile.write("##Disable map\nscoreboard players set #"+modID+" 4j.setenablemap 0\n\n##Decrease mapcount\nscoreboard players remove #Store 4j.mapcount 1\n\n##Open menu\n#Set score\nscoreboard players set @s 4j.gamecfg "+str(pageOpenValue)+"\n#Run function\nfunction 4jbattle:menu/load/host/mods/open/maps")
    #Close file
    lbFile.close
    ##Add to preset save file
    #Add variable to count with
    presetCounter = 1
    while presetCounter <= 10:
        #Open file
        filePath = dpFolder+"functions/menu/load/host/preset/save/"+str(presetCounter)+".mcfunction"
        lbFile = open(filePath, "a")
        #Write save data
        lbFile.write("\nadvancement revoke @s only 4jbattle:menu/host/presets/"+str(presetCounter)+"/map/enabled/"+modID+"\nexecute if score #"+modID+" 4j.setenablemap matches 0 run advancement grant @s only 4jbattle:menu/host/presets/"+str(presetCounter)+"/map/enabled/"+modID)
        #Close file
        lbFile.close
        #Increment counter
        presetCounter = presetCounter + 1
    ##Add to preset load file
    #Set counter back to 1
    presetCounter = 1
    while presetCounter <= 10:
        #Open file
        filePath = dpFolder+"functions/menu/load/host/preset/load/"+str(presetCounter)+".mcfunction"
        lbFile = open(filePath, "a")
        #Write save data
        lbFile.write("\nexecute if entity @s[advancements={4jbattle:menu/host/presets/"+str(presetCounter)+"/map/enabled/"+modID+"=true}] run scoreboard players set #"+modID+" 4j.setenablemap 0\nexecute if entity @s[advancements={4jbattle:menu/host/presets/"+str(presetCounter)+"/map/enabled/"+modID+"=false}] run scoreboard players set #"+modID+" 4j.setenablemap 1\nexecute if entity @s[advancements={4jbattle:menu/host/presets/"+str(presetCounter)+"/mods/enabled=true,4jbattle:menu/host/presets/"+str(presetCounter)+"/map/enabled/"+modID+"=false}] run scoreboard players add #Store 4j.mapcount 1")
        #Close file
        lbFile.close
        #Increment counter
        presetCounter = presetCounter + 1
    ##Create preset savedata files
    #Set counter back to one
    presetCounter = 1
    while presetCounter <= 10:
        #Open file
        filePath = dpFolder+"advancements/menu/host/presets/"+str(presetCounter)+"/map/enabled/"+modID+".json"
        lbFile = open(filePath, "w")
        #Write data
        lbFile.write("{\n  \"criteria\": {\n    \"requirement\": {\n      \"trigger\": \"minecraft:impossible\"\n    }\n  }\n}\n")
        #Close file
        lbFile.close
        #Increment counter
        presetCounter = presetCounter + 1
    ##Set resource pack to load
    #Open file
    filePath = dpFolder+"functions/resource/load/id/game.mcfunction"
    lbFile = open(filePath, "a")
    #Get pack ID
    if str(modconfig['pack'])=="vanilla":
        packID = 0
    if str(modconfig['pack'])=="plastic":
        packID = 1
    if str(modconfig['pack'])=="fantasy":
        packID = 2
    if str(modconfig['pack'])=="city":
        packID = 3
    if str(modconfig['pack'])=="greek":
        packID = 4
    if str(modconfig['pack'])=="steampunk":
        packID = 5
    if str(modconfig['pack'])=="chinese":
        packID = 6
    if str(modconfig['pack'])=="halloween":
        packID = 7
    if str(modconfig['pack'])=="festive":
        packID = 8
    if str(modconfig['pack'])=="fallout":
        packID = 9
    #Write pack ID into file
    if packID > 0:
        lbFile.write("\n#"+str(modconfig['name'])+"\nexecute if score #Store 4j.map matches "+str(maxMap)+" run scoreboard players set #Store 4j.pack "+str(packID))
    #Close file
    lbFile.close
    ##Set music pack to load
    #Open file
    filePath = dpFolder+"functions/game/music/id.mcfunction"
    lbFile = open(filePath, "a")
    #Get pack ID
    packID = 0
    if str(modconfig['pack'])=="western":
        packID = 10
    #Write pack ID into file
    if packID > 0:
        lbFile.write("\n#"+str(modconfig['name'])+"\nexecute if score #Store 4j.map matches "+str(maxMap)+" run scoreboard players set #Store 4j.muspack "+str(packID))

def copyworld():
    print("Copying world files!")
    ##Copy files to world folder
    #data, entities, poi, region
    if modconfig['hassmall']:
        try:
            shutil.copytree("4j.modtools-temp/world/small","world/dimensions/4jbattle/"+modID+"_small")
        except(FileNotFoundError):
            print("Small map type not found!")
    if modconfig['haslarge']:
        try:
            shutil.copytree("4j.modtools-temp/world/large","world/dimensions/4jbattle/"+modID)
        except(FileNotFoundError):
            print("Large map type not found!")
    if modconfig['haslargeplus']:
        try:
            shutil.copytree("4j.modtools-temp/world/largeplus","world/dimensions/4jbattle/"+modID+"_largeplus")
        except(FileNotFoundError):
            print("Large+ map type not found!")
    if modconfig['hasremastered']:
        try:
            shutil.copytree("4j.modtools-temp/world/remastered","world/dimensions/4jbattle/"+modID+"_remastered")
        except(FileNotFoundError):
            print("Remastered map type not found!")
    #Dimension data
    if modconfig['hassmall']:
        shutil.copyfile("4j.modtools-temp/world/dimension_type.json",dpFolder+"dimension_type/"+modID+"_small.json")
    if modconfig['haslarge']:
        shutil.copyfile("4j.modtools-temp/world/dimension_type.json",dpFolder+"dimension_type/"+modID+".json")
    if modconfig['haslargeplus']:
        shutil.copyfile("4j.modtools-temp/world/dimension_type.json",dpFolder+"dimension_type/"+modID+"_largeplus.json")
    if modconfig['hasremastered']:
        shutil.copyfile("4j.modtools-temp/world/dimension_type.json",dpFolder+"dimension_type/"+modID+"_remastered.json")

for fileList in os.listdir("lebmods/"):
    if fileList.endswith(".lebmod"):
        mod_archive = "lebmods/"+str(fileList)
        print("Installing mod: "+mod_archive)
        ##Extract the mod
        extractmod()
        ##Load the config of the mod
        loadmodconfig()
        if os.path.exists(dpFolder+"dimension_type/"+modID+".json"):
            print("This mod is already installed! Skipping...")
        else:
            ##Inject code into the datapack
            injectcode()
            ##Copy world data
            copyworld()
            print("Installed mod "+str(modconfig['name']))
        ##Remove temp directory
        shutil.rmtree("4j.modtools-temp")

##Inject to MOTD upon installation being finished
injectmotd()

##Enable the mods menu upon installation being finished
enablemenu()

##Display finish message
print("\033[32mFinished installing mods!")
