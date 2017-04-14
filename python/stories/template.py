from milecastles import Story, Box, ThroughPage, ThroughSequence, ConditionFork, NodeFork, SackChange
from engines.console import ConsoleSiteEmulator
# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
    uid=storyName,
    startNodeUid = "landing",
    startSack={
    }
)

with story:

    marketBox =         Box( uid="1",   label="Box I",      description="the Market")
    workshopBox =       Box( uid="2",   label="Box II",     description="the Workshop")
    tombBox =           Box( uid="3",   label="Box III",    description="the Tomb")
    quarryBox =         Box( uid="4",   label="Box IV",     description="the Quarry")

    ThroughPage(
        uid="landing",
    )

    ThroughPage(
        uid="ending",
    )
    
if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()
