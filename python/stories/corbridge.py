from milecastles import Uid, UidRegistry, Story, Box, LinearPassage

# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
    uid=storyName,
    startNodeUid = "landing",
    startSack={
            money:  100,
            points: 0,
            hours:  0,
            stone:  False,
            sharp:  False,
    }
)

with story:
    
    # populate with boxes
    entranceBox =   Box( uid="entrance",    label="Box I",      description="the Market")
    workshopBox =   Box( uid="workshop",    label="Box II",     description="the Workshop")
    tombBox =       Box( uid="tomb",        label="Box III",    description="the Tomb")
    quarryBox =     Box( uid="quarry",      label="Box IV",     description="the Quarry")

    # populate with passages
    LinearSequence(
        uid=            "landing",
        visitBoxUid =   "entrance",
        nextNodeUid =   "workshopIntro"
        sequence = [
            "You are a stone mason working our of the military base at Corbridge.\n" + 
            "Flavinus, a respected young cavalryman has recently died and members\n" + 
            "of the Burial Club have approached you to create a tombstone in his honour"
            ,
            "Your quest is to gather the materials, tools and inspiration to complete \n" + 
            "the tombstone and honour the memory of Flavinus!" + 
            "You have {{sack.money}} for materials."
        ],
    )
    
    ChoicePage(
        uid=            "workshopIntro",
        page=           "You are in your workshop. It's early in the morning but you don't have long to complete the tombstone.."
        choices = {
                        "sharpening":    "Get your tools sharpened at the blacksmith",
                        "inspiration":   "Look for inspiration",
                        "stone":         "Go outside to order stone from the quarry",
        }
        otherBoxText=   "Find {{node.visitBox.label}} to go to your workshop",
    )
   
    # ROUTE TO ANGRY OR COMPLIANT BLACKSMITH
    ConditionFork(
        uid=           "sharpening",
        condition=     "sack.hours > 6 and sack.smithAnger < 2",
        trueNodeUid=   "sharpeningSuccess",
        falseNodeUid=  "sharpeningFailure",
    )
    # compliant blacksmith
    LinearPage(
        uid=         "sharpeningSuccess",
        change = SackChange(
            trigger =   "sack.tool == False",
            assign =    { tool:True},
            add  =      { points:1 },
            remove =    { money:10 },
        ),
        page = """  
            {% if node.change.triggered %}
                {% if node.change.completed %}
                    It's now the afternoon and the blacksmith is ready for you.
                    Look at the tools in the box and pretend to sharpen a spearhead.
                    Sharpening costs {{node.change.remove['money']}} denarii. You have {{sack.money}} denarii left.
                {% else %}
                    You don't have enough money to sharpen your tools
                {% endif %}
            {% else %}
                You already sharpened your tools
            {% endif %}
        """,
        nextNodeUid = "workshopIntro"
    )    
    #angry blacksmith
    LinearPage(
        uid="sharpeningFailure",
        change =SackChange( 
                add = { smithAnger:1 } 
        ),
        page=   """ {% if sack.smithAnger == 0 %}You walk across the base to the blacksmith's workshop. The blacksmith says 'come back this afternoon, I'm too busy'{% endif %}
                    {% if sack.smithAnger == 1 %}I said I'm busy!!! Come back later!!{% endif %}
                    {% if sack.smithAnger == 2 %}That's it, Get out!! Don't come back ever again!{% endif %}
                    {% if sack.smithAnger >= 3 %}The blacksmith shouts at you: 'I said that you're banned!!' You'll have to work with blunt tools now{% endif %}""", 
        nextNodeUid = "workshopIntro",
    )

    # ROUTE TO INSPIRATION AT TOMB (this has been switched from where it was originally at the workshop)
    LinearSequence(
        uid="inspiration",
        visitBoxUid = tombBox.uid,
        sequence = [
            "You've seen cavalrymans' tombstones before but never actually carved one yourself. You'll need to get some ideas. INVESTIGATE the stone carvings in this part of the museum.",
            "Can you find the EAGLE MOUNT that is near this box? Make a sketch if you can. This is a good start but you will need to find more later. Look around until you have enough inspiration"            
        ]
        nextNodeUid = "workshopIntro",
    )
    
    # ROUTE TO GET STONE
    ChoicePageFork(
        uid="stone",
        page="You are on an East-West road used for supplying the fort. There are a number of shops here.",
        choices = {
                "stoneAlone":    "Carry the stone yourself for a total of {{story.boxes.stoneAlone.change.remove['money']}} denarii",
                "stoneDonkey":   "Hire a cart to carry it for a total of {{story.boxes.stoneDonkey.change.remove['money']}} denarii",
        }
    )
    