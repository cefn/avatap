from milecastles import Uid, Story, Box, PagePassage

# create a bunch of Uids which will be used later
storyUid = Uid("feature")
landingUid = Uid("hello")
endingUid = Uid("goodbye")

#create a story
story = Story(
	uid=storyUid,
	startPassageUid=landingUid
)

with story:

	# create a bunch of boxes
	startBox = Box(
		uid='1',
		label='Box I'
	)

	terminalBox = Box(
		uid='2',
		label='Box II'
	)

	# create some passages
	PagePassage(
		uid=landingUid,
		rightBoxUid=startBox.uid,
		rightBoxText="World",
		nextPassageUid=endingUid
	)

	PagePassage(
		uid=endingUid,
		rightBoxUid=terminalBox.uid,
		rightBoxText="End",
		nextPassageUid=landingUid
	)
