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
            "points": 0,
            "hours":  0,
            "horseFat": 0,
            "sword":  False,
			"armour":  False,
            "helmet":  False,
            "recon":  False,
    }
)

with story:
    
    # populate with boxes
    
    barracksBox =         Box( uid="1",   label="Box I",      description="the Barracks")
    battleBox =           Box( uid="2",   label="Box II",    description="the Battle")
    westgateBox =         Box( uid="3",   label="Box III",     description="the West Gate")
    stablesBox =       	  Box( uid="4",   label="Box IV",     description="the Stables")
    
    entranceBox = barracksBox

# INTRO
	
    ThroughSequence(
        uid =           "landing",
        change =        SackChange( 
                            reset=story.startSack 
                        ),
        goalBoxUid =    barracksBox.uid,
        nextNodeUid =   "stables1",
        sequence = [
            """ Welcome to Milecastles! 
				Look for numbered boxes 
				and tap your card to  
				progress the story!""",
            """ You are a Cavalry member 
				stationed at Housesteads 
				Fort. News has reached you 
				of barbarians approaching
				from the West.""",	
            """ Your quest is to help the 
				fort repel the attack 
				using all of your 
				training...""",
            """ You wake up in your 
				barracks. MARCH up to 
				the fort and find 
				the stables at Box IV.""",
        ],
    )
    	       
    #1. MORNING / BATTLE PREP
    
    ThroughSequence(
		uid =           "stables1",
		goalBoxUid =    stablesBox.uid,
		nextNodeUid =   "stableFork",
		sequence = [
		""" You arrive at the stables.
			The latrine is nearby and
			It smells! HOLD YOUR NOSE
			for 60 seconds. Your 
			commander is here. He 
			orders you to prepare 
			for battle.""",
		""" You find your horse, 
			who seems a bit hungry.
			At the same time, you
			have a feeling that 
			you should do some
			scouting at the 
			West gate.""",
        ],
    )
      
    NodeFork(
        uid =   "stableFork",
        choices = {
            "food1":   """ Collect horse food from 
						   the South Gate""",
            "recon1":  """ Go to the West Gate to
						   survey the land""",
        },
    )
    
    ThroughPage(
		uid = 			"food1",
		page = 			""" You collect a bale of hay 
						    from the supply hut. 
						    CARRY it back to the 
						    stable to feed your horse.""",
		goalBoxUid = 	battleBox.uid,
		nextNodeUid =	"food2",
		)				
    
    ThroughPage(
		uid = 			"food2",
		change = 		SackChange(
								plus = {"horseFat":40},
								),
		page = 			""" Back at the stable,
							Your horse munches the 
							hay eagerly. Your horse's
							stomach is now {{node.change.plus['horseFat']}}% 
							full.""",
		goalBoxUid = 	stablesBox.uid,
		nextNodeUid =	"stables2",
		)				
    
    ThroughPage(
		uid =           "recon1",
		change = 		SackChange(
								assign = {"recon":True},
								),		
		missTemplate =  """ This isn't the West Gate! 
							Go to {{node.goalBox.label}}""",
		page =  		""" You find the WEST GATE 
							where you can see shapes 
							in the mist coming across 
							the hills. MAKE A NOTE of 
							their position on your 
							slate and return to the 
							stables.""",
		goalBoxUid =    westgateBox.uid,
		nextNodeUid =   "stables2",
    )
     
    ThroughPage(
		uid="stables2",
		missTemplate =  """ This isn't the stables! 
							Go to {{node.goalBox.label}}""",
		page=			""" You and your horse are 
							eager to enter the battle. 
							But are you ready?""",	
		goalBoxUid = stablesBox.uid,
		nextNodeUid="stablesCheck1",
    )
    
    ConditionFork(
        uid=           "stablesCheck1",
        condition =    "sack.sword==False and sack.helmet==False",
        trueNodeUid=   "stablesCheck2",
        falseNodeUid=  "battlePrep1",
    )
        
    ThroughPage(
		uid="stablesCheck2",
		missTemplate =  """ This isn't the stables! 
						    Go to {{node.goalBox.label}}""",
		page=			""" You don't quite feel
							ready yet... What did
							you forget to do?""",	
		goalBoxUid = stablesBox.uid,
		nextNodeUid="stableFork1",
    )
    
    NodeFork(
        uid =   "stableFork1",
        choices = {
			 "sword":  	""" Search for your sword
							back at the Barracks.""",
            "feed":   	""" Collect more horse feed 
							at the South Gate""",
            "groom":  	""" Collect your helmet
							from your groom
							at the West Gate""",
        },
    hideChoices = {
			"sword":	"sack.sword==True",
			"groom":	"sack.helmet==True",
		},
	)
              
    ThroughPage(
		uid="feed",
		change =        SackChange(
		plus={"horseFat":40}, 
                            ),
		goalBoxUid = battleBox.uid,
		page= 	""" You lead your horse to
					the supply hut. Pretend
					to FEED THE HORSE.
					The horse's stomach is now
					{{node.change.plus['horseFat']}}% more full.
					Let's get back to 
					the stables!""",
		nextNodeUid="stablesCheck1",
    )
 
    ThroughPage(
		uid="groom",
		change =   SackChange( 
                    assign={"helmet":True},
                            ),
		page= 	""" Your groom is lazy! 
					He wants to hang around
					with his mates at the 
					West Gate. You have to
					SHOUT AT HIM before he
					will fetch your helmet.
					Ouch. It's too small.""",
		goalBoxUid = westgateBox.uid,
		nextNodeUid="stablesCheck1",
			)

    ThroughPage(
		uid="sword",
		missTemplate =  "Head back to {{node.goalBox.label}}",
		change=SackChange(
            assign={"sword":True},
				),		
        page= 		""" Your sword is buried under 
						some old wolf skins and 
						barrels. You check the 
						blade. OW!! It's still 
						sharp. This will come in 
						handy later...
						Back to the stables (again)""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="stablesCheck1",
    )
	
	   
	#2. MORNING INSPECTION / BATTLE
 	
    ThroughSequence(
		uid="battlePrep1",
		goalBoxUid = stablesBox.uid,
		nextNodeUid="southGate1",
		missTemplate =  """ Quickly! Back to the 
							Stable{{node.goalBox.label}}""",
		sequence= [ 
		""" The commander is getting
			impatient. You need to get 
			into battle. 
			'HRMPH! Let's check your 
			things.'""",
		""" 'How full is your horse's
			stomach?' You answer:
			{{sack.horseFat}}%, sir!""",
		"""	'Do you have a nice sharp 
			sword?' 
			You answer:
			That's {{sack.sword}}, sir!""",
		""" 'And are you even wearing 
			a helmet?' 
			You answer: 
			That's {{sack.helmet}}, sir!""",
		""" 'Well, I've seen better, but 
			we've no more time, so...
			MARCH to the South Gate to 
			start the battle'. """,
			]
		 )

    ConditionFork(
        uid=           "southGate1",
        condition =    "sack.recon == True",
        trueNodeUid=   "reconYes",
        falseNodeUid=  "reconNo",
    )
   
    ThroughSequence(
		uid="reconYes",
		missTemplate =  """ Quick! Head back to the 
							BATTLE at {{node.goalBox.label}}""",
		goalBoxUid = battleBox.uid,
		nextNodeUid="battling1",
		sequence= [
		""" You meet with the cavalry
			to tell them about what
			you saw earlier and talk
			about the best way to 
			attack.""",
		""" You decide to flank the 
			enemy from either side 
			to surprise them and 
			catch them in a pincer.
			Pretend to RIDE out to 
			fight...""",
		]
    )

    ThroughSequence(
		uid="battling1",
		missTemplate =  """ Quick! Head back to the 
							BATTLE at {{node.goalBox.label}}""",
		goalBoxUid = battleBox.uid,
		nextNodeUid="stables3",
		sequence= [
		""" You BOP a barbarian.""",
		""" You PAF a barbarian.""",
		""" You WHACK a barbarian.""",
		""" You CLOMP a barbarian.""",
		""" You DISCOMBOBULATE 
			a barbarian.""",
		""" You BIFF a barbarian.""",
		""" You POP a barbarian.""",
		""" You PLOK a barbarian.""",
		""" You CRUNK a barbarian.""",
		""" This is getting rather 
			tiring! Better take a 
			rest and re-supply at 
			the stables.""",
				]
    )
 
    ThroughSequence(
		uid="reconNo",
		goalBoxUid = battleBox.uid,
		nextNodeUid="stables3",
		missTemplate =  "Quick! Head back to the BATTLE at {{node.goalBox.label}}",
		sequence= [
		""" Well... I'm afraid
			You didn't take the 
			chance to check out
			the area earlier and
			the cavalry take a
			beating from the enemy.""",
		""" You get BOPPED by a 
			barbarian.""",
		""" Your horse gets 
			PAFFED by a 
			barbarian.""",
		""" You get WHACKED by a 
			barbarian.""",
		""" Your horse gets 
			CLOMPED by a barbarian.""",
		""" You get DISCOMBOBULATED 
			by a barbarian.""",
		""" Your horse gets 
			PLOKKED by a 
			barbarian.""",
		""" You get CRUNKED by a 
			barbarian.""",
		""" Are you getting the
			idea? It's not going
			well is it? Better 
			take a rest, re-supply
			and chill with your
			horse at the stables.""",
		]
    )
    
#3. PM BATTLE PREP

    ThroughSequence(
		uid="stables3",
		change = SackChange(
					minus={"sack.horseXP":20},
					),
		goalBoxUid = stablesBox.uid,
		nextNodeUid="stablesFork3",
		sequence = [
        """ Tired from the battle,
			you head back to the
			stables to rest.""",
		""" You fall asleep in
			the hay for an hour.
			When you wake up,
			your horse is making
			snorting noises.""",
		""" The commander is
			imapatient, but 
			there's still a bit 
			of time to prepare 
			before going back 
			to the battle.""",
			]
    )
    
    NodeFork(
        uid =   "stablesFork3",
        choices = {
			"hide1":    """ This might be a good time 
							to chicken out and HIDE 
							under your bed in the 
							BARRACKS.""",
			"groom2": 	""" Get your armour from 
							the SOUTH GATE.""",				
            "feed3":   	""" Get more horse feed 
							at the WEST Gate""",
    	},
	)

    ThroughPage(
		uid="groom2",
		change=SackChange(
            assign={"armour":True},
				),		
        page=	""" Your groom is asleep.
					You wake him up with
					a KICK. He digs
					around in a large sack 
					and finds your armour.
					Except... it's too big.
					Oh well, go back to the 
					stable for inspection.""",
		goalBoxUid = battleBox.uid,
		nextNodeUid="stablesCheck3",
    )

    ThroughPage(
		uid="feed3",
		missTemplate =  "MARCH over to {{node.goalBox.label}}",
		change=SackChange(
            plus={"horseFat":40},
				),		
        page=
        """ You lead your horse
			to the hay bale and 
			he eats half,
			meaning that he's 
			roughly {{node.change.plus['horseFat']}}%
			more full. Now go back 
			to the stables.""",
		goalBoxUid = westgateBox.uid,
		nextNodeUid="stablesCheck3",
    )

    ThroughSequence(
		uid="hide1",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="landing",
		missTemplate =  "Head over to {{node.goalBox.label}}",
		sequence= [
        """ You played it safe 
			and decided to hide
			out for the rest of
			the battle.""",
		""" Curled up in a wolf
			skin, you dream of
			being the hero/heroine
			of the wall...""",
		"""	you THWACK a barbarian.""",
		""" You THWAP a barbarian.""",
		""" You WALLOP a barbarian.""",
		""" You KERPOW a barbarian.""",
		""" You DISMANTLE a barbarian.""",
		""" You PUNCTURE a barbarian.""",
		""" You CRUSH a barbarian.""",
		""" Wow, this is a repetitive 
			dream!""",
		"""	The cavalry won the
			battle but you were
			lazy and your commander
			will be FURIOUS!! 
			TAP to try again or
			visit another museum
			to play as another
			character. """,
		]
	)

#4. PM INSPECTION / BATTLE

    ThroughPage(
		uid="stablesCheck3",
		missTemplate =  "Head over to {{node.goalBox.label}}",
		page=
        """ Your (forgetful)
			commander is here.
			He wants to make an
			inspection.	
			'First, let's look at
			what you're wearing...'""",
		goalBoxUid = stablesBox.uid,
		nextNodeUid="gearCheck1",
    )
  
    ThroughPage(
		uid="gearCheck1",
		missTemplate =  "Head over to {{node.goalBox.label}}",
		page=
        """ 'Are you wearing a proper 
			HELMET?'
			Answer: That's {{sack.helmet}} 
			sir!
			'Are you wearing decent 
			ARMOUR?'
			Answer: That's {{sack.armour}} 
			sir!""",
		goalBoxUid = stablesBox.uid,
		nextNodeUid="gearCheck2",
    )
    
    ConditionFork(
        uid=           "gearCheck2",
        condition =    "sack.armour and sack.helmet == True",
        trueNodeUid=   "goodGear",
        falseNodeUid=  "badGear",
    )
    
    ThroughPage(
		uid="goodGear",
		page=
        """ 'YOU WILL MAKE THE 
			CAVALRY PROUD!
            (Even if your helmet is
            a bit small and your
            armour is baggy) 
            GOOD WORK! NOW, 
            ONWARDS TO BATTLE!
            HRMMMRRPPH""",
		goalBoxUid = stablesBox.uid,
		nextNodeUid="horseCheck",
    )

    ThroughPage(
		uid="badGear",
		page=
        """ 'YOU'RE A DISGRACE! 
			I'VE SEEN BETTER 
			DRESSED PONIES THAN
			YOU!!
			Oh well, we're short
			of soldiers so I'll
			have to pass you if
			I must...'""",
		goalBoxUid = stablesBox.uid,
		nextNodeUid="horseCheck",
    )

    ThroughPage(
        uid =           "horseCheck",
        goalBoxUid =    stablesBox.uid,
        change = SackChange(
            trigger = "sack.horseFat >= 80",
            plus  =     {"horseFat":10},
        ),
        page = """  
            {% if node.change.triggered %}
                {% if node.change.completed %}
                    'LET ME LOOK AT YOUR
                    HORSE NOW!! OH DEAR 
                    HE'S EATEN TOO MUCH!!' 
                    How embarrassing...
                    Your horse's stomach is 
                    {{sack.horseFat}}% full.
                    He's too fat to ride!
           {% else %}
				'LET'S LOOK AT YOUR
				HORSE NOW! HMM, HE'S
				IN GOOD SHAPE!
				Your horse's stomach 
				is a perfect {{node.change.plus['horseFat']}}% full.
				He's Healthy and ready to 
				go to battle!                
			{% endif %}
            {% else %}
				'LET'S LOOK AT YOUR
				HORSE NOW! HMM, HE'S
				IN GOOD SHAPE!
				Your horse's stomach 
				is a perfect {{node.change.plus['horseFat']}}% full.
				He's Healthy and ready to 
				go to battle!                      
			{% endif %}
        """,
        nextNodeUid = "endingCheck",
    )
        
     # CHECK THIS FORK!
     
    ConditionFork(
        uid=           "endingCheck",
        condition =    "sack.horseFat>=90",
        trueNodeUid=   "badEnding",
        falseNodeUid=  "battling2",
    )
          
    ThroughSequence(
		uid="battling2",
		missTemplate =  """ Quick! Head back to 
							the BATTLE at {{node.goalBox.label}}""",
		goalBoxUid = battleBox.uid,
		nextNodeUid="goodEnding",
		sequence= [
		""" You passed the inspection!
			RIDE out with your
			fellow cavalry to save 
			the day!""",
		"""	you THWACK a barbarian.""",
		""" You POKE a barbarian.""",
		""" You WALLOP a barbarian.""",
		""" You KERPOW a barbarian.""",
		""" You DISCOMBOBULATE 
			a barbarian.""",
		""" You PUNCTURE a barbarian.""",
		""" You CRUSH a barbarian.""",
		""" Are you getting the idea yet?""",
		""" The cavalry won!!
			Your tired now, but you
			still manage to go 
			and celebrate at the
			barracks.""",
				]
    )
  
#5. ENDINGS  
     
    ThroughPage(
		uid="goodEnding",
		page="""You are a legend! You
				helped defend the fort, 
				kept your horse from 
				eating too much!
				TAP to play again or 
				visit another museum 
				to play as another
				character!""",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="landing",
    )
           
    ThroughPage(
		uid="badEnding",
		page="""That was a poor show...
				You surived the battle
				but your horse is fat
				and you will be demoted.
				TAP at the BARRACKS to 
				try again!""",
		goalBoxUid = stablesBox.uid,
		nextNodeUid="landing",
    )
   
   
if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()
    

