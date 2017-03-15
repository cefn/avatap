from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange
from engines.console import ConsoleSiteEmulator
# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
    uid=storyName,
    # choose an alternative startNodeUid and startSack for debugging
    #startNodeUid = "stoneFork",
    startNodeUid = "landing",
    startSack={
            "money":  100,
            "points": 0,
            "hours":  0,
            "smithAnger": 0,
            "stone":  False,
            "sharp":  False,
    }
)

with story:
    
    # populate with boxes
    marketBox =         Box( uid="1",   label="Box I",      description="the Market")
    workshopBox =       Box( uid="2",   label="Box II",     description="the Workshop")
    tombBox =           Box( uid="3",   label="Box III",    description="the Tomb")
    quarryBox =         Box( uid="4",   label="Box IV",     description="the Quarry")
    
    entranceBox = marketBox

    # populate with passages
    ThroughSequence(
        uid =           "landing",
        change =        SackChange( 
                            reset=story.startSack 
                        ),
        goalBoxUid =    marketBox.uid,
        nextNodeUid =   "workshopArrive",
        sequence = [
            """ You are a stone mason working our of the military base at Corbridge.
                Flavinus, a respected young cavalryman has recently died and members
                of the Burial Club have approached you to create a tombstone in his honour""",
            """ Your quest is to gather the materials, tools and inspiration to complete
                the tombstone and honour the memory of Flavinus!
                You have {{sack.money}} for materials.""",
        ],
    )
    
    ConditionFork(
            uid=            "workshopArrive",
            change =        SackChange( 
                                plus={"hours":2} 
                            ),
            condition =     "sack.sharp or sack.smithAnger >= 3",
            falseNodeUid =  "workIntro",
            trueNodeUid =   "ending",
    )
            
    ThroughPage(
        uid=            "workIntro",
        missTemplate =  "To begin work go to {{node.goalBox.label}}",
        page =          "You are in your workshop. It's early in the morning but you don't have long to complete the tombstone.",
        goalBoxUid =    workshopBox.uid,
        nextNodeUid =   "work",
    )
            
    NodeFork(
        uid =   "work",
        choices = {
            "sharpening":   "Get your tools sharpened at the blacksmith",
            "stone":        "Go outside to order stone from the quarry",
            "inspiration":  "Look for inspiration"
        },
        hideChoices = {
            "sharpening":   "sack.sharp==True",
            "stone":        "sack.stone==True",
        },
    )
                   
    # ROUTE TO ANGRY OR COMPLIANT BLACKSMITH
    ConditionFork(
        uid=           "sharpening",
        condition =    "sack.hours > 6 and sack.smithAnger < 3",
        trueNodeUid=   "sharpeningSuccess",
        falseNodeUid=  "sharpeningFailure",
    )
    
    # compliant blacksmith
    ThroughPage(
        uid =           "sharpeningSuccess",
        goalBoxUid =    marketBox.uid,
        change = SackChange(
            trigger =   "sack.sharp == False",
            assign =    { "sharp":True},
            plus  =     { "points":1 },
            minus =     { "money":10 },
        ),
        page = """  
            {% if node.change.triggered %}
                {% if node.change.completed %}
                    It's now the afternoon and the blacksmith is ready for you.
                    Look at the tools in the box and pretend to sharpen a spearhead.
                    Sharpening costs {{node.change.minus['money']}} denarii. You have {{sack.money}} denarii left.
                {% else %}
                    You don't have enough money to sharpen your tools
                {% endif %}
            {% else %}
                You already sharpened your tools
            {% endif %}
        """,
        nextNodeUid = "workshopArrive"
    )
        
    #angry blacksmith
    ThroughPage(
        uid=            "sharpeningFailure",
        goalBoxUid=     marketBox.uid,
        change = SackChange( 
            plus = { "smithAnger":1 } 
        ),
        page=   """ 
            {% if sack.smithAnger == 1 %}You walk across the base to the blacksmith's workshop. The blacksmith says 'come back this afternoon, I'm too busy'{% endif %}
            {% if sack.smithAnger == 2 %}I said I'm busy!!! Come back later!!{% endif %}
            {% if sack.smithAnger == 3 %}That's it, Get out!! Don't come back ever again!{% endif %}
            {% if sack.smithAnger >= 4 %}The blacksmith shouts at you: 'I said that you're banned!!' You'll have to work with blunt tools now{% endif %}
        """, 
        nextNodeUid = "workshopArrive",
    )

    # ROUTE TO INSPIRATION AT TOMB (this has been switched from where it was originally at the workshop)
    ThroughSequence(
        uid="inspiration",
        goalBoxUid = tombBox.uid,
        sequence = [
            "You've seen cavalrymans' tombstones before but never actually carved one yourself. You'll need to get some ideas. INVESTIGATE the stone carvings in this part of the museum.",
            "Can you find the EAGLE MOUNT that is near this box? Make a sketch if you can. This is a good start but you will need to find more later. Look around until you have enough inspiration"            
        ],
        nextNodeUid = "workshopArrive",
    )
    
    # ROUTE TO GET STONE
    
    ThroughPage(
        uid="stone",
        page="You are on an East-West road used for supplying the fort. There are a number of shops here.",
        goalBoxUid = quarryBox.uid,
        nextNodeUid="stoneFork",
    )
    
    NodeFork(
        uid="stoneFork",
        choices = {
                "stoneAlone":    "Pretend to carry the stone yourself back to the workshop for a total of {{story.nodes.stoneAlone.change.minus['money']}} denarii",
                "stoneDonkey":   "Go to {{story.nodes.stoneDonkey.getGoalBox(story).description}}, pretend to hire and ride a donkey back to the workshop for a total of {{story.nodes.stoneDonkey.change.minus['money']}} denarii",
        }
    )
    
    ThroughPage(
        uid="stoneAlone", 
        goalBoxUid=workshopBox.uid,
        change=SackChange(
            assign={"stone":True},
            minus={"money":50}
        ),
        page="You carried the stone yourself", 
        nextNodeUid="workshopArrive"
    )

    ThroughPage(
        uid="stoneDonkey", 
        goalBoxUid=marketBox.uid,
        change=SackChange(
            assign={"stone":True},
            minus={"money":65}
        ),
        page="You hired a donkey to carry the stone, now ride the donkey back to the workshop", 
        nextNodeUid="workshopArrive"
    )
        
    ThroughPage(
        uid="ending",
        goalBoxUid=entranceBox.uid,
        page="Respawned. Tap to begin your adventure again",
        missTemplate="You completed your adventure with {{sack.points}} points. Return to {{node.goalBox.label}} to respawn.",
        nextNodeUid = "landing",
    )
        
if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()