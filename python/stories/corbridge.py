from milecastles import *

# inspects the module to figure out the story name (e.g. corbridge)
story = Story(__name__.split(".")[-1])

landingUid = Uid("landing")
PagePassage(story=story,
	uid=landingUid, 
	page="Welcome to Milecastles at Corbridge!\nGet your registration card from the till and tap the symbol below to begin!"),
)

endingUid = Uid("ending")
PagePassage(story=story,
	uid=endingUid,
	page="You have reached the end of your journey"
)
