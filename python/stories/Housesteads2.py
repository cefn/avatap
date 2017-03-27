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
            "horseXP": 0,
            "sword":  False,
            "spear":  False,
    }
)

with story:
    
    # populate with boxes
    barracksBox =         Box( uid="1",   label="Box I",      description="the Barracks")
    stablesBox =       Box( uid="2",   label="Box II",     description="the Stables")
    battleBox =           Box( uid="3",   label="Box III",    description="the Battle")
    westgateBox =         Box( uid="4",   label="Box IV",     description="the West Gate")
    
    entranceBox = barracksBox



    # populate with passages


	#INTRO AT BARRACKS
	
    ThroughSequence(
        uid =           "landing",
        change =        SackChange( 
                            reset=story.startSack 
                        ),
        goalBoxUid =    barracksBox.uid,
        nextNodeUid =   "stables",
        sequence = [
            """ Welcome to Milecastles at Housesteads. Look out
				for the numbered boxes and tap your card to 
				progress the story!"""
            """ You are a Cavalryman stationed at Housesteads Fort. 
				News has reached you of barbarians arriving 
				by ship from the West.""",	
            """ Your quest is to help the fort repel the barbarian
				attack using all of your training.
				(and crazy horse skills)""",
            """ You wake up in your barracks.
				You need to march up to the fort
				and find the stables.""",
        ],
    )
    
    #1. FIRST STABLES VISIT
    
    ThroughSequence(
		uid =           "stables",
		goalBoxUid =    stablesBox.uid,
		nextNodeUid =   "recon",
		sequence = [
		""" You arrive at the stables. Your commander is here.
			He tells you to start preparing your horse.""",
		""" Your horse seems hungry. Maybe you should go to 
			the supply store at the WEST GATE to find some food.""",
        ],
    )
    
    
    #2. WEST GATE VISIT
    
    ThroughSequence(
		uid =           "recon",
		goalBoxUid =    westgateBox.uid,
		nextNodeUid =   "stableFork",
		sequence = [
		""" You arrive at the WEST GATE and survey the landscape.""",
		""" Ominous shapes and sounds come from across the hills.
			You gather some hay for your horse and return to the STABLES.""",
        ],
    )
    
    #3. STABLE CHOICES    
    NodeFork(
        uid =   "stableFork",
        choices = {
            "feed":   "Collect more food for your horse",
            "groom":  "Order your groom to dress your horse",
            "sword":  "Search for your weapon"
        },
    )
    
       
    ThroughPage(
		uid="feed",
		change =        SackChange( 
                                plus={"horseXP":20} 
                            ),
		page="Your horse is so happy. You are a good Cavalryman. Your horse just hit {{sack.horseXP}} XP. Oh yeah!",
		goalBoxUid = battleBox.uid,
		nextNodeUid="battling",
    )

    ThroughPage(
		uid="groom",
		missTemplate =  "Head back to the {{node.goalBox.label}}",
		change =        SackChange( 
                                plus={"horseXP":50} 
                            ),
		page="Your horse is so blingin'. Your horse just hit {{sack.horseXP}} XP. You are a stylin' Cavalryman.",
		goalBoxUid = westgateBox.uid,
		nextNodeUid="battling",
	)

    ThroughPage(
		uid="sword",
		missTemplate =  "Head back to the {{node.goalBox.label}}",
		change=SackChange(
            assign={"sack.sword":True}
				),		
        page="Your sword is so sharp. You are a badass Cavalryman. THE END.",
		goalBoxUid = barracksBox.uid,
		nextNodeUid="battling",
    )

	
	#4. BATTLE A
	
    ConditionFork(
        uid=           "battling",
        condition =    "sack.horseXP > 25",
        trueNodeUid=   "battlingSuccess",
        falseNodeUid=  "battlingFailure",
    )
   

    ConditionFork(
        uid=           "battlingSuccess",
        condition =    "sack.sword==True",
        trueNodeUid=   "endingBad",
        falseNodeUid=  "endingGood",
    )
   
    ThroughPage(
		uid="endingGood",
		page="Your horse is amazing and so is your sword. You won big style!! END",
		goalBoxUid = battleBox.uid,
		nextNodeUid="ending",
    )

    ThroughPage(
		uid="endingBad",
		page="Your horse is sluggish and you are WEAK! You got pwnd. END",
		goalBoxUid = battleBox.uid,
		nextNodeUid="ending",
    )

    ThroughPage(
		uid="battlingFailure",
		page="You're not cut out for this, give up. END",
		goalBoxUid = battleBox.uid,
		nextNodeUid="ending",
    )
          
     
    ThroughPage(
		uid="ending",
		page="Go back to the BARRACKS to start again." 
			 "Try to prepare for battle better next time!",
		goalBoxUid = battleBox.uid,
		nextNodeUid="landing",
    )
          
     



	    
if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()
    
