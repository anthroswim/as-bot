import json

ASDEBUG = True
GUILD = 834100481839726693
DEV = 954419840251199579
FORCESYNC = False

# load jsons
def loadjson(jsonname: str) -> dict:
    with open(f"{jsonname}.json", "r") as inpoot:
        return json.load(inpoot)
    
# save jsons
def savejson(jsonname: str, jdata):
    with open(f"{jsonname}.json", "w+") as outpoot:
        json.dump(jdata, outpoot, sort_keys=True, indent=4)


# TODO: make it a property instead
redditfollows = loadjson("conf/redditfollows")
