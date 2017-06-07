from milecastles import Story, Box, ThroughPage

# inspects the module to figure out the story name (e.g. corbridge)
storyName = __name__.split(".")[-1]

# create story
story = Story(
    uid=storyName,
    startNodeUid="landing",
    startSack = {
        "money": 100,
    }
)
        
# populate passages and boxes
with story:

    northBox =  Box( uid="north",   label="Box I",      description="the Northern Quarter")
    eastBox =   Box( uid="east",    label="Box II",     description="the Eastern Promise")
    southBox =  Box( uid="south",   label="Box III",    description="the Southern White House")
    westBox =   Box( uid="west",    label="Box IV",     description="the Wild West")

    # create a beginning passage which points to the end passage
    ThroughPage(
        uid="landing",
        goalBoxUid=northBox.uid,
        page="Welcome to Milecastles.",
        nextNodeUid="ending"
    )

    # create an ending passage for the story
    ThroughPage(
        uid="ending",
        goalBoxUid=southBox.uid,
        page="You have finished your adventure",
        nextNodeUid="landing"
    )

def run():
    from regimes.console import ConsoleSiteEmulator
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()

if __name__ == "__main__":
    run()