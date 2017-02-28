#TODO validation...
#test that {instruction} exists in all text

from milecastles import *

story = Story(
	uid="tullie"
)

story.registerPassage(PagePassage(
	uid="welcome",
	page="Welcome to Tullie House {instruction}",
	showBoxUid="0",
	nextPassageUid="intro"
))

'''
story.registerPassage(PagePassage(
	uid="intro",
	text="You are a roman! {instruction}",
	boxId="0",
	nextUid="buy"
))

story.registerPassage(ChoicePassage(
	uid="spend",
	text="You are in the market. Which kind of paint do you want to buy?",
	choices = {
		"The most expensive paint"	:	"highPaint",
		"A mid level paint"			:	"midPaint",
		"Cheap and nasty paint"		:	"lowPaint",
	}
))

story.registerPassage(ChoicePassage(
	uid="highPaint",
))
'''
