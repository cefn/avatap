from milecastles import Uid, UidRegistry, Story, Box, LinearPassage

# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

storyUid = Uid(storyName)

nodeUids = UidRegistry([
        "landing",
        "workshopIntro",
        "sharpening",
        "sharpeningSuccess",
        "sharpeningFailure",
        "inspiration",
        "stone",
        "ending"
])

boxUids = UidRegistry([
        "entrance",
        "workshop",
        "tomb",
        "quarry"
])

# create story
story = Story(
    uid=storyUid,
    startPassageUid = nodeUids.landing,
    startSack=dict(
            money:  100,
            hour:   0,
            stone:  0,
            tool:   0,
            points: 0,
    )
)

with story:
    
    # populate with boxes
    Box( uid=boxUids.market,       label="Box I",      description="The Market")
    Box( uid=boxUids.workshop,     label="Box II",     description="The Workshop")
    Box( uid=boxUids.tomb,         label="Box III",    description="The Tomb")
    Box( uid=boxUids.quary,        label="Box IV",     description="The Quarry")

    # populate with passages
    LinearPageSequence(
        uid=nodeUids.landing,
        visitBoxUid = boxUids.entrance,
        nextNodeUid = nodeUids.workshopIntro
        pageSequence = [
            "You are a stone mason working our of the military base at Corbridge.\n" + 
            "Flavinus, a respected young cavalryman has recently died and members\n" + 
            "of the Burial Club have approached you to create a tombstone in his honour"
            ,
            "Your quest is to gather the materials, tools and inspiration to complete \n" + 
            "the tombstone and honour the memory of Flavinus!" + 
            "You have {{sack.money}} for materials."
        ],
    )
    
    ChoicePageFork(
        uid=nodeUids.workshopIntro,
        page="You are in your workshop. It's early in the morning but you don't have long to complete the tombstone.."
        otherBoxText="Find {{node.visitBoxLabel}} to go to your workshop",
        choices = {
                nodeUids.sharpening:    "Get your tools sharpened at the blacksmith",
                nodeUids.inspiration:   "Look for inspiration",
                nodeUids:stone:         "Go outside to order stone from the quarry",
        }
    )
   
    # ROUTE TO ANGRY OR COMPLIANT BLACKSMITH
    BoolExpressionFork(
        uid=            nodeUids.sharpening,
        condition=      "sack.time > 6 and sack.smithAnger < 2",
        trueNodeUid=    nodeUids.sharpeningSuccess,
        falseNodeUid=   nodeUids.sharpeningFailure,
    )
    # compliant blacksmith
    SackChangePage(
        uid=        nodeUids.sharpeningSuccess,
        condition = "sack.tool == 0",
        add =       { tool:1, points:1 },
        remove =    { money:10 }
        page =      "{% if sack.sharp == 0 %}" + 
                    "It's now the afternoon and the blacksmith is ready for you.\n" + 
                    "Look at the tools in the box and pretend to sharpen a spearhead.\n" + 
                    "Sharpening costs 10 denarii. You have {{sack.money}} denarii left." + 
                    "{% else %}" + 
                    "You already sharpened your tools" + 
                    "{% endif %}",
        nextNodeUid = nodeUids.workshopIntro
    )    
    #angry blacksmith
    SackChangePage(
        uid=nodeUids.sharpeningFailure,
        add={ smithAnger:1 }
        page=   "{% if sack.smithAnger == 0 %}You walk across the base to the blacksmith's workshop. The blacksmith says 'come back this afternoon, I'm too busy'{% endif %}" +
                "{% if sack.smithAnger == 1 %}I said I'm busy!!! Come back later!!{% endif %}" + 
                "{% if sack.smithAnger == 2 %}That's it, Get out!! Don't come back ever again!{% endif %}" + 
                "{% if sack.smithAnger == 3 %}The blacksmith shouts at you: 'I said that you're banned!!' You'll have to work with blunt tools now{% endif %}", 
        nextNodeUid = nodeUids.workshopIntro,
    )

    # ROUTE TO INSPIRATION AT TOMB (this has been switched from where it was originally at the workshop)
    LinearPageSequence(
        uid=nodeUids.inspiration,
        visitBoxUid = boxUids.tomb,
        pageSequence = [
            "You've seen cavalrymans' tombstones before but never actually carved one yourself. You'll need to get some ideas. INVESTIGATE the stone carvings in this part of the museum.",
            "Can you find the EAGLE MOUNT that is near this box? Make a sketch if you can. This is a good start but you will need to find more later. Look around until you have enough inspiration"            
        ]
        nextNodeUid = nodeUids.workshopIntro,
    )
    
    # ROUTE TO GET STONE
    ChoicePageFork(
        uid=nodeUids.stone,
        page="You are on an East-West road used for supplying the fort. There are a number of shops here.",
        choices = {
                nodeUids.stoneAlone:    "Carry the stone yourself for a total of 50 denarii",
                nodeUids.stoneDonkey:   "Hire a cart to carry it for a total of 65 denarii",
        }
    )
    
    SackChangePage(
        uid=nodeUids.stoneAlone,
        condition = "sack.stone == 0"
        add = {stone:1},
        remove = {money:50},
    )


        
    