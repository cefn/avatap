from milecastles import Uid, UidRegistry, Story, Box, LinearPage
# create uids to wire up/trigger story+passages

storyUid = Uid("teststory")

nodeUids = UidRegistry(
    "landing",
    "ending",
)

boxUids = UidRegistry(
    "north",
    "east",
    "south",
    "west"
)


# create story
story = Story(
        uid=storyUid,
        startNodeUid=nodeUids.landing
        
)
        
# populate passages and boxes
with story:

    # configure boxes            
    for boxUid in boxUids.getUids():
        Box(uid=boxUid, label="The box called " + boxUid.idString) 
    
    # create a beginning passage which points to the end passage
    LinearPage(
        uid=nodeUids.landing,
        visitBoxUid=boxUids.north,
        visitBoxText="Welcome to Milecastles.",
        nextNodeUid=nodeUids.ending
    )

    # create an ending passage for the story
    LinearPage(
        uid=nodeUids.ending,
        visitBoxUid=boxUids.south,
        visitBoxText="You have finished your adventure",
        nextNodeUid=nodeUids.landing
 )
