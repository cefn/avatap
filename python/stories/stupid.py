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
        "beans":False
    }
)

with story:

    homeBox =       Box( uid="1",   label="Box I",      description="at Jack's Mother's house")
    roadBox =       Box( uid="2",   label="Box II",     description="on The Road To Market")
    
    incrementTime = SackChange(
        plus={"hours":1}
    )

    ThroughPage(
        uid="landing",
        change=SackChange(
            reset=story.startSack
        ),
        time = incrementTime,
        page="Jack, you need to sell the cow",
        goalBoxUid = homeBox.uid,
        nextNodeUid = "sellcow"
    )

    ThroughPage(
        uid="sellcow",
        time=incrementTime,
        change = SackChange(
            assign={"beans":True}
        ),
        missTemplate="Go to {{node.getGoalBox(story).label}} to sell the cow",
        page="You sold the cow for a handful of beans",
        goalBoxUid = roadBox.uid,
        nextNodeUid = "ending"
    )

    ThroughPage(
        uid="ending",
        page="You have finished your adventure. {% if sack.beans %}You have the beans{% else %}You don't have the beans{% endif %}",
        goalBoxUid = homeBox.uid,
        nextNodeUid = "landing"
    )
    
if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()