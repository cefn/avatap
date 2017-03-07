from milecastles import Uid, Story, Box, PagePassage

storyUid = Uid("feature")
landingUid = Uid("hello")
endingUid = Uid("goodbye")

story = Story(
	uid=storyUid
	startPassageUid=landingUid
)

# create a bunch of boxes
for boxIdString in [str(boxPos) for boxPos in range()]
	box = Box(
		uid=boxIdString
	)
	story.registerBox(box)

# create some passages
landingPassage = PagePassage(
	uid=landingUid,
	rightBox
)

