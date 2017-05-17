from engines.console import ConsoleSiteEmulator
from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange

storyName = "corbridge"

# create story
story = Story(
    uid=storyName,
    # choose an alternative startNodeUid and startSack for debugging
    # startNodeUid = "stoneFork",
    startNodeUid="landing",
    startSack={
        "money": 100,
        "points": 0,
        "smithAnger": False,
        "stone": False,
        "sharp": False,
        "inspire": False,
        "afternoon": False,
    }
)

with story:
    # populate with boxes

    smithBox = Box(uid="1", label="Box I", description="the Blacksmith")
    workshopBox = Box(uid="2", label="Box II", description="the Workshop")
    tombBox = Box(uid="3", label="Box III", description="the Tomb")
    quarryBox = Box(uid="4", label="Box IV", description="the Quarry")

    entranceBox = smithBox

    # BOX I

    # 1a - intro / landing

    ThroughSequence(
        uid="landing",
        change=SackChange(
            reset=story.startSack
        ),
        goalBoxUid=smithBox.uid,
        nextNodeUid="workshop1",
        sequence=[
				#23456789012345678901234
            """ Welcome to Milecastles!
                Look for numbered boxes
                and hold your tag to
                progress the story...""",
            """ You are a stonemason
                working at the military
                base at Corbridge...""",
            """ Your quest is to get
                materials, tools and
                inspiration to complete
                the tombstone....""",
            """ You have an advance of
                {{sack.money}} Denarii
                for materials.
                Spend it wisely...""",
        ],
    )
   
    # 1b Blacksmith am/pm
				#23456789012345678901234
    ThroughPage(
        uid="smith1",
        missTemplate="This isn't the blacksmith! {{node.goalBox.label}}",
        page="""You walk across the fort 
				to the blacksmith's 
				workshop. A sign says 
				'Half-day closing today'""",
        goalBoxUid=smithBox.uid,
        nextNodeUid="sharpening",
    )
   
    ConditionFork(
        uid="sharpening",
        condition="sack.afternoon == True",
        trueNodeUid="sharpeningSuccess",
        falseNodeUid="sharpeningFailure",
    )
    
    # changed this to ThroughPage as logic wont work so well in a ThroughSequence
    ThroughPage(
        uid="sharpeningSuccess",
        change=SackChange(
            # may need to include trigger condition in case you get here again with sharp tools
            trigger="sack.sharp == False",
            # it's false so lets make it True because blacksmith is not grumpy
            assign={"sharp": True},
            plus={"points": 1},
            minus={"money": 15},
        ),
        goalBoxUid=smithBox.uid,
        page="""
        {% if node.change.triggered %}
            {% if node.change.completed %}
                It's now the afternoon
                and the blacksmith is
                ready for you. 
                Sharpening costs 
                {{node.change.minus['money']}} Denarii.
                You now have 
                {{sack.money}} Denarii.
            {% else %}
                You don't have enough 
                money to sharpen your 
                tools.
            {% endif %}
        {% else %}
				You already sharpened 
				your tools.
        {% endif %}
        """,
        nextNodeUid="sharpened",
    )
				#23456789012345678901234

    ThroughPage(
        uid="sharpened",
        missTemplate="This isn't the blacksmith! {{node.goalBox.label}}",
        # 23456789012345678901234| 24 char limit
        page="""
        Look at the tools in 
        the display and PRETEND 
        to sharpen a spearhead.
        Now your tools are 
        sharp, you can add lots 
        of detail to the 
        carving!
        """,
        # superfluous {{story.nodes.fromSmith.getGoalBox(story).description}} to the workshop.",
        goalBoxUid=smithBox.uid,
        nextNodeUid="fromSmith",
    )
    
						#23456789012345678901234
		
    # Now our sharpening fail
    ThroughPage(
        uid="sharpeningFailure",
        missTemplate="""This isn't the 
						blacksmith! 
						Go to {{node.goalBox.label}}""",
        change=SackChange(
            assign={"smithAnger": True},
        ),
        # 23456789012345678901234| 26 char limit
        page="""
        The Blacksmith is 
        furious!
        'You're banned...!' 
        No sharp tools 
        for you...
        """,
        goalBoxUid=smithBox.uid,
        nextNodeUid="workshop1",
    )
    
    # BOX II

    # 2a Morning / First Workshop Fork

    ThroughPage(
        uid="workshop1",
        missTemplate="""To begin work, 
						go to {{node.goalBox.label}}""",
        page="""		You are in your 
						workshop.
						It's early, but you will
						have to work quickly to 
						complete the carving.""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop2",
    )
							#23456789012345678901234
    NodeFork(
        uid="workshop2",
        choices={
            "smith1": """	Go to the
							blacksmith""",
            "stone1": """	Go outside to the 
							quarry""",
            "inspire1": """	Look for 
							inspiration""",
        },
        hideChoices={
            "smith1": "sack.sharp==True",
            "stone1": "sack.stone==True",
            "smith1": "sack.smithAnger==True",
        },
    )
    
    # 2b Afternoon / Second Workshop Fork

    ThroughSequence(
        uid="workshop3",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="firstSnack",
        sequence=[
            """ You've done a good 
				morning's work...""",
            """	You think about 
				your home and how 
				you first traveled 
				here to service 
				the camp...""",
        ],
    )
   			#23456789012345678901234
			
    ThroughPage(
        uid="firstSnack",
        change=SackChange(
            minus={"money": 5},
            plus={"points": 1},
            assign={"afternoon": True}
        ),
        nextNodeUid="workshop4",
        # use {{node.change.minus['money']}} to pull in the actual money you will spend
        # helps test against the logic
        page=""" 	You stop for some food
					at a local inn. 
					It costs
					{{node.change.minus['money']}} Denarii.
					You now have 
					{{sack.money}} Denarii...""",
        goalBoxUid=workshopBox.uid,
    )
   
							#23456789012345678901234

    ThroughPage(
        uid="fromSmith",
        missTemplate="""To carry on working, 
						go to {{node.goalBox.label}}""",
        page=		""" You're feeling more 
						equipped!""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop4",
    )
    
    NodeFork(
        uid="workshop4",
        choices={
            "smith1": """	Get your tools 
							sharpened""",
            "stone1": """	I need to order the 
							stone""",
            "burial1": """	Talk to the Burial 
							Club"""
        },
        hideChoices={
            "smith1": "sack.sharp==True",
            "stone1": "sack.stone==True",
            "smith1": "sack.smithAnger==True",
        },
    )
							#23456789012345678901234

    # 2c - Carving Fork

    ThroughPage(
        uid="workshop5",
        missTemplate=	""" Time to get back to the 
							workshop at {{node.goalBox.label}}""",
        page=			""" Next morning, the stone
							arrives...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="carve",
    )

    ConditionFork(
        uid="carve",
        condition="sack.sharp == True",
        trueNodeUid="goodCarve",
        falseNodeUid="badCarve",
    )
							#23456789012345678901234
    ThroughPage(	
        uid="goodCarve",
        missTemplate=	""" Stop slacking! 
							Go back to {{node.goalBox.label}}!""",
        page=			""" You start carving the
							tombstone. Your tools 
							are nice and sharp± 
							You make a detailed 
							carving. Npw it's time 
							to get it painted...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )

    ThroughPage(
        uid="badCarve",
        missTemplate="""Stop slacking! 
						Back to {{node.goalBox.label}}!""",
				# 23456789012345678901234| 26 char limit
        page="""You start carving the
				tombstone. Your tools 
				are blunt and it looks
				a bit wrong...
				Still, you'd better get 
				it painted...""",
        goalBoxUid=workshopBox.uid,
        nextNodeUid="painter1",
    )

    # BOX III

    # 3a - Inspiration
						#23456789012345678901234
    ThroughPage(
        uid="inspire1",
        change=SackChange(
            assign={"inspire": True}
        ),
        missTemplate="""This isn't the tomb! 
						Go to {{node.goalBox.label}}!""",
        page="""		This is where the 
						finished tombstone 
						will be displayed.""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="inspire2",
    )

				#23456789012345678901234

    ThroughSequence(
        uid="inspire2",
        goalBoxUid=tombBox.uid,
        nextNodeUid="workshop3",
        sequence=[
            """ You've seen a Cavalry-
                man's tombstone before
                but never carved one.
                You'll need to get some
                ideas before starting...""",
            """ INVESTIGATE the stone
                carvings in the museum. 
                Make a SKETCH, at the 
                drawing area and then 
                come back...
                """,
        ],
    )

    # 3b - Burial Club

    ThroughPage(
        uid="burial1",
        missTemplate="This isn't the tomb site! {{node.goalBox.label}}",
        #23456789012345678901234| 24 char limit
        page="""
        The Burial Club are 
        making preparations for 
        the tombstone to be 
        displayed. You ask them 
        for some help with 
        research.
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="burial2",
    )
							#23456789012345678901234
    NodeFork(
        uid="burial2",
        choices={
            "drink": """	Come with us for a 
							drink and we can tell 
							you about Flavinus!!""",
            "inspire3": """ You should look for 
							Flavinus' helmet 
							plate...""",
        },
    )			#23456789012345678901234

    ThroughSequence(
        uid="inspire3",
        # QUESTION
        # Wondered if this should still be at box II? Seem to be there all the time...
        # And seems weird to say go back to the workshop which is where we are already
        # Maybe this should be Box 3? 
        #(feels a bit wrong, but are limited by number of boxes available without sending players back outside...)
        goalBoxUid=workshopBox.uid,
        nextNodeUid="workshop5",
        sequence=[
            """ You go to the armoury
                to look for Flavinus'
                helmet plate. Find the
                HELMET near box II, 
                make a sketch then 
                come back...""",
            """ INVESTIGATE the spear-
				heads and weapons in 
				the cabinet near Box I 
				then come back...""",
            """ That's plenty of 
				research for now! 
				Go back to
                your workshop to 
                rest up!
                """,
        ],
    )
				#23456789012345678901234
    ThroughSequence(
        uid="drink",
        goalBoxUid=smithBox.uid,
        nextNodeUid="buydrinks",
        sequence=[
            """ They tell you that 
				Flavinus was 25 years 
				old and that he died 
				after 7 years of service 
				with the Ala Petriana 
				as a standard bearer...""",
            """ They tell you lots more 
				about Flavinus but you 
				are starting to feel a 
				bit drunk and tired...""",
            # seperated this from logic with a thru page
        ],
    )

    # Seperated this from story.node.drink sequence so logic works
    ThroughPage(
        uid="buydrinks",
        change=SackChange(
            minus={"money": 10},
        ),
			#23456789012345678901234
        # Maybe have something that refers to beign in the pub?
        # missTemplate =  "Get back to the pub! goto {{node.goalBox.label}}",
        missTemplate="""Go back to the pub 
						at {{node.goalBox.label}}""",
        page="""
            You buy drinks for 
            {{node.change.minus['money']}} Denarii.
            You have {{sack.money}} Denarii.
			That's plenty of 
			research for now! 
			Go back to your 
			workshop to rest.""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="workshop5",
    )

    # 3c - Painter fork

						#23456789012345678901234
    ThroughPage(
        uid="painter1",
        missTemplate="""Stop slacking! 
						Get back to {{node.goalBox.label}}""",
        page=	""" 	You meet the painter at 
						the tomb site to put the 
						finishing touches to the 
						tombstone...""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="painter2",
    )

    ConditionFork(
        uid="painter2",
        # added inspire logic so looking for inspiration makes a difference?
        condition="sack.sharp == True and sack.inspire == True",
        trueNodeUid="goodPaint",
        falseNodeUid="badPaint",
    )

    ThroughPage(
        uid="goodPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""Stop slacking! 
						Get back to {{node.goalBox.label}}""",
        page="""
        The finished stone 
        looks stunning! 
        The painter charges 
        {{node.change.minus['money']}} Denarii,
        leaving you with 
        {{sack.money}} Denarii.
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingGood",
    )
		#23456789012345678901234
		
    ThroughPage(
        uid="badPaint",
        change=SackChange(
            minus={"money": 15},
        ),
        missTemplate="""
        Stop slacking! 
        Go back to {{node.goalBox.label}}
        to find the painter""",
        page="""
        The painter does their 
        best, but it doesn't 
        look good...
        The painter charges 
        {{node.change.minus['money']}} Denarii, 
        leaving you with 
        {{sack.money}} Denarii.""",
        goalBoxUid=tombBox.uid,
        nextNodeUid="endingBad",
    )

    # 3d - Endings
				#23456789012345678901234
    ThroughSequence(
        uid="endingGood",
        goalBoxUid=tombBox.uid,
        nextNodeUid="reward",
        sequence=[
			"""	You're now ready for 
				the unveiling...""",
            """	That evening, the 
				Cavalrymen and members 
				of the Burial Club arrive 
				to unveil the 
				tombstone...""",
            """'Flavinus is well-
				represented - the Gods 
				and all that pass by 
				his tomb will see what 
				a great soldier he was.' 
				they say...""",
        ]
    )
    # Added the node.change.plus code so checks against logic

    ThroughPage(
        uid="reward",
        change=SackChange(
            plus={"money": 100},
        ),
        page="""
        The soldiers pay you a
        bonus of {{node.change.plus['money']}} Denarii 
        and give you a 
        LAUREL WREATH!
        """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )
		#23456789012345678901234
				#23456789012345678901234
    ThroughSequence(
        uid="endingBad",
        goalBoxUid=tombBox.uid,
        nextNodeUid="refund",
        sequence=[
            """ You're now ready for 
				the unveiling...""",
            """ That evening, the 
				Cavalrymen and members 
				of the Burial Club 
				arrive to unveil the
                tombstone...""",
            """ The soldiers tell you 
				that Flavinus is wearing 
				the wrong helmet and 
				that his horse is 
				wonky-looking. 
				They refuse to pay...""",
        ],
    )

    ThroughPage(
        uid="refund",
        change=SackChange(
            minus={"money": 50},
        ),
        page="""
            The soldiers demand a 
            refund of 
            {{node.change.minus['money']}} Denarii. 
            You now have 
            {{sack.money}} Denarii.
            """,
        goalBoxUid=tombBox.uid,
        nextNodeUid="ending",
    )
				#23456789012345678901234

    # BOX IV

    # 4a Quarry

    ThroughPage(
        uid="stone1",
        missTemplate="""This isn't the quarry! 
						Go to {{node.goalBox.label}}.""",
        page="""You are on an East-West 
				road used for supplying 
				the fort. There are a 
				number of shops here...""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stone2",
    )
				#23456789012345678901234

    ThroughPage(
        uid="stone2",
        change=SackChange(
            assign={"stone": True},
            minus={"money": 50}
        ),
        page="""You meet the quarry 
				manager and place an 
				order for stone to 
				arrive tomorrow. 
				It costs 
				{{node.change.minus['money']}} Denarii, 
				leaving you with 
				{{sack.money}} Denarii.""",
        goalBoxUid=quarryBox.uid,
        nextNodeUid="stoneFork",
    )

    NodeFork(
        uid="stoneFork",
        # Note the difference between getGoalBox(story).description and
        # getGoalBox(story).label, it means you can tell people to go to a box
        # to do something without it being associated with the description
        # so you dont think youre hiring a donkey from the grumpy blacksmith
        choices={
            "stoneAlone": """	PRETEND to CARRY the 
								stone yourself""", 
            "stoneDonkey": """	Hire a donkey and 
								PRETEND to RIDE it 
								back to the workshop""",
        }
    )
								#23456789012345678901234
    ThroughPage(
        uid="stoneAlone",
        goalBoxUid=workshopBox.uid,
        page="""What strength!
				You carried the 
				stone yourself!""",
        nextNodeUid="workshop1"
    )
  				#23456789012345678901234

    ThroughPage(
        uid="stoneDonkey",
        goalBoxUid=smithBox.uid,
        change=SackChange(
            minus={"money": 5}
        ),
        page="""You hired a donkey to 
				carry the stone, now 
				RIDE the donkey back to 
				the workshop. It cost 
				{{node.change.minus['money']}} Denarii, 
				leaving you with 
				{{sack.money}} Denarii.""",
        nextNodeUid="stoneTime"
    )
  
    ConditionFork(
        uid="stoneTime",
        condition="sack.afternoon == False",
        trueNodeUid="workshop1",
        falseNodeUid="fromSmith",
    )
		#23456789012345678901234
    ThroughPage(
        uid="ending",
        page="""
        You completed your game
        with a total of 
        {{sack.money}} Denarii
        Can you do better?
        Return to {{node.goalBox.label}} 
        to try again or visit 
        another museum to play 
        more MileCastles!
        """,
        nextNodeUid="landing",
        goalBoxUid=entranceBox.uid,
        # goalBoxUid = tombBox.uid,
    )

def run():
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()


if __name__ == "__main__":
    run()

  

    
