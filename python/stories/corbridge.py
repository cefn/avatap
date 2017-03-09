from milecastles import Uid, UidRegistry, Story, Box, LinearPassage

# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

storyUid = Uid(storyName)

nodeUids = UidRegistry([
        "landing",
        "materialsIntro",
        "workshopIntro",
        "ending"
])

boxUids = UidRegistry([
        "market",
        "workshop",
        "tomb",
        "quarry"
])

# create story
story = Story(
	uid=storyUid,
	startPassageUid = nodeUids.landing
)

with story:
	
	# populate with boxes
	Box( uid=boxUids.entrance,     label="The Entrance, Box I")
	Box( uid=boxUids.workshop,     label="The Workshop, Box II")

	# populate with passages
	LinearPassage(
		uid=              nodeUids.landing,
		visitBoxUid =     boxUids.market,
		visitBoxText =	"You are a stone mason working our of the military base at Corbridge.\n" + 
    						"Flavinus, a respected young cavalryman has recently died and members\n" + 
						"of the Burial Club have approached you to create a tombstone in his honour"
		nextNodeUid=   nodeUids.materials,
	)

	LinearPassage(
		uid=              nodeUids.materialsIntro,
		visitBoxUid =     boxUids.market,
		visitBoxText = 	"Your quest is to gather the materials, tools and inspiration to complete \n" + 
						"the tombstone and honour the memory of Flavinus!" + 
						"You have {{sack.money}} for materials."
		nextNodeUid=   nodeUids.workshopIntro,
	)
    
    