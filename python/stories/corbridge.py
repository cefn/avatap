from milecastles import *

# inspects the module to figure out the story name (e.g. corbridge)
storyUid = Uid(__name__.split(".")[-1])

landingPassageUid = Uid("landingIntro")

# create story
story = Story(
	uid=storyUid,
	startPassageUid = landingPassageUid
)

with story:
	
	# uids which need to be referenced
	materialsPassageUid = Uid("materialIntro")
	endingPassageUid = Uid("ending")

	registrationBoxUid = Uid("registration")
	workshopBoxUid = Uid("workshop")

	# populate with boxes
	Box( uid=registrationBoxUid, 	label="The Entrance, Box I")
	Box( uid=workshopBoxUid, 		label="The Workshop, Box II")

	# populate with passages
	PagePassage(
		uid=landingPassageUid,
		nextPassageUid=materialsPassageUid,
		rightBoxUid = registrationBoxUid,
		rightBoxText =	"You are a stone mason working our of the military base at Corbridge." + 
						"Flavinus, a respected young cavalryman has recently died and members\n" + 
						"of the Burial Club have approached you to create a tombstone in his honour"
	)

	PagePassage(story=story,
		uid=endingUid,
		rightBoxUid=workshopBoxUid,
		rightBoxText = 	"Your quest is to gather the materials, tools and inspiration to complete \n" + 
						"the tombstone and honour the memory of Flavinus!" + 
						"You have {money} for materials."
	)


