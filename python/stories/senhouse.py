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
        "epona":0,
        "mars":0,
        "superhorse":False,
        "dead":False,
        "points":0,
        "hours":0,
        }
)

with story:

    paddockBox =    Box( uid="1",   label="Box I",      description="Looking out to sea")
    altarBox =   Box( uid="2",   label="Box II",     description="Before the altars of the gods")
    seaBox = Box( uid="3",   label="Box III",     description="in the paddock breeding horses")

    entranceBox = paddockBox
# An additional var if you're doing hella SackChanges
    incrementTime = SackChange(
        plus={ "hours":1 }
    )

    # populate with passages
    ThroughSequence(
            uid =           "landing",
            change =        SackChange(
                reset=story.startSack
                ),
            goalBoxUid =    paddockBox.uid,
            nextNodeUid =   "yardArrive",
            sequence = [
            """Welcome to Milecastles
            at Senhouse! Look out for
            the numbered boxes and use
            your card on them to play!""",
            """You are an officer at the
            coastal fort at Senhosue.
            You must watch the coast
            for attack from the sea!""",
            """You must also care for
            and breed horses for the
            cavalry and pay tribute to
            the gods with libations.
            """,
            ],
            )

    ConditionFork(
            uid=            "yardArrive",
            condition =     "sack.superhorse == True",
            falseNodeUid =  "yardIntro",
            trueNodeUid =   "retirement",
    )

    ThroughPage(
        uid=            "yardIntro",
        time = incrementTime,
        page = """
        You are in the courtyard by
        the wall.
        {% if sack.hours <= 4 %}It's early in the morning
        and you can smell
        the sea air{% endif %}
        {% if sack.hours > 4 and sack.hours < 12 %}It's lunchtime and people
        hurry by{% endif %}
        {% if sack.hours == 12 %}It's raining {% endif %}
        {% if sack.hours > 12 %}The night is closing in{% endif %}
        """,
        goalBoxUid =    paddockBox.uid,
        nextNodeUid =   "work",
        #missTemplate =  "To continue your adventure {{node.goalBox.label}}",
    )

    NodeFork(
        uid = "work",
        page = """
        What do you want to do?
        """,
        choices = {
            "altars":   "Make a spiritual visit to the altars",
            "seaview":  "Look our for attack from the Northern Sea!",
            },
        )

    ThroughSequence(
        uid =   "altars",
        time = incrementTime,
        sequence = [ """
        You are in the temple
        There are many altars
        Each attributed to a
        great warrior or cavalry
        commander
        """,
        """We must pay tribute
        to make sure they favour
        our work here
        But who in your heart do
        you seek guidance from?""",
        ],
        goalBoxUid = altarBox.uid,
        nextNodeUid = "chooseGod",
        )

    NodeFork(
        uid = "chooseGod",
        choices  = {
            "epona" : """
            Epona a northerners goddess
            """,
            "mars"  : """
            Mars the great god of war
            """,
            },
        hideChoices = {
            "epona" : "sack.epona == 2",
            "mars": "sack.mars == 2",
            },
        )

    ThroughPage(
        uid = "epona",
        time = incrementTime,
        page = """
        We need favoured horses
        and she surely would
        foster in our beasts
        stregnth and loyalty
        """,
        goalBoxUid = paddockBox.uid,
        nextNodeUid = "libation",
        )

    ThroughPage(
        uid = "mars",
        time = incrementTime,
        page = """
        We need great warriors!
        He would
        foster in our beasts
        stregnth and skill in
        the art of death!
        """,
        goalBoxUid = seaBox.uid,
        nextNodeUid = "libation",
        )

# GOD AND LIBATION FORK
    NodeFork(
        uid =   "libation",
        choices = {
            "wine": "Look for some wine",
            "food": "Look for some food to offer",
        },
    )

    ThroughPage(
        uid =   "wine",
        time = incrementTime,
        change = SackChange(
            plus = { "mars":2 },
            ),
        page = """
        You offer wine
        """,
        goalBoxUid = paddockBox.uid,
        nextNodeUid = "yardArrive",
        )

    ThroughPage(
        uid =   "food",
        change = SackChange(
            plus = { "epona":2 },
            ),
        time = incrementTime,
        page = """
        You offer food
        from the local
        harvest
        """,
        goalBoxUid = altarBox.uid,
        nextNodeUid = "yardArrive",
        )

# ROUTE TO SPOTTING invaders
    ConditionFork(
        uid =       "seaview",
        condition = "sack.hours >= 1",
        falseNodeUid =  "seaviewclear",
        trueNodeUid =   "seaviewinvaders",
        )

    ThroughPage(
        uid =   "seaviewclear",
        time = incrementTime,
        page = """
        You can see the sea
        """,
        goalBoxUid = seaBox.uid,
        nextNodeUid = "yardArrive",
        )

    # ROUTE TO COASTAL BATTLE
    ThroughSequence(
        uid =   "seaviewinvaders",
        time = incrementTime,
        sequence = [ """
        You can see the sea
        On the horizon
        you can see a sail!
        """,
        """
        We must fight off the
        invaders and prepare
        to defend the coastal
        outpost!
        """,
        ],
        goalBoxUid = seaBox.uid,
        nextNodeUid = "bravery",
        #missTemplate =  "To continue goto {{node.goalBox.label}}",
        )

    NodeFork(
        uid =   "bravery",
        choices = {
            "altars": "Make another visit to the altars",
            "battle": "Defend the outpost! Get a sword!",
            },
        )


    # ROUTE TO SUCCESSFUL BATTLE
    ConditionFork(
        uid=           "battle",
        condition =    "sack.mars > 1",
        trueNodeUid=   "battleSuccess",
        falseNodeUid=  "battleFailure",
    )

    # battle win
    ThroughPage(
        uid =           "battleSuccess",
        time = incrementTime,
        goalBoxUid =    paddockBox.uid,
        change = SackChange(
            trigger =   "sack.superhorse == False",
            assign =    { "superhorse":True},
            plus  =     { "mars":4 },
        ),
        page = """
            {% if node.change.triggered %}
                {% if node.change.completed %}
                    You bravely hold back the
                    wall so the cavalry can
                    charge down the coastal
                    path to victory.
                    You kill the fleeing barbarian
                    and take his horse
                {% else %}
                    You hold back the wall as
                    best you can but are driven
                    back! the coastal path may be
                    over run!
                {% endif %}
            {% else %}
                A desperate battle took place here
            {% endif %}
        """,
        nextNodeUid = "yardArrive"
    )

    ThroughPage(
        uid =           "battleFailure",
        time = incrementTime,
        page = """
        You bravely hold back
        the invaders charging
        up the coastalpath
        but are forced back
        to the wall and die!
        """,
        goalBoxUid =    paddockBox.uid,
        nextNodeUid =   "retirement",
    )

    ThroughPage(
        uid="retirement",
        goalBoxUid=entranceBox.uid,
        page="Bad luck. Respawned. Tap to begin your adventure again",
        missTemplate="You completed your adventure with {{sack.points}} points. Return to {{node.goalBox.label}} to respawn.",
        nextNodeUid = "landing",
    )

if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()
