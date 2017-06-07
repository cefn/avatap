from milecastles import Story, Box, ThroughPage

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
    
def run():
    from regimes.console import ConsoleSiteEmulator
    emulator = ConsoleSiteEmulator(story=story)
    emulator.run()

if __name__ == "__main__":
    run()