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
        "epona":False,
        "mars":False,
        "superhorse":False,
        "eponapoints":0,
        "marspoints":0,
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
            coastal fort at Senhouse.
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
            trueNodeUid =   "retirementsuccess",
    )

    ThroughPage(
        uid=            "yardIntro",
        time = incrementTime,
        page = """
        You are in the courtyard by
        the wall.
        {% if sack.hours <= 4 %}It's early in the morning
        and you can smell
        the sea air.
        {% endif %}
        {% if sack.hours > 4 and sack.hours < 12 %}It's lunchtime and people
        hurry by.{% endif %}
        {% if sack.hours == 12 %}It's raining {% endif %}
        {% if sack.hours > 12 %}The night is closing in{% endif %}
        """,
        goalBoxUid =    paddockBox.uid,
        nextNodeUid =   "work",
        missTemplate =  "To continue your adventure {{node.goalBox.label}}",
    )

    NodeFork(
        uid = "work",
        page = """
        What do you want to do?
        """,
        choices = {
            "altars":   "Make a spiritual visit to the altars",
            "seaview":  "Look out for attack from the Northern Sea!",
            },
        )

    ThroughSequence(
        uid =   "altars",
        time = incrementTime,
        #2345678901234567890123456
        sequence = [ """
        You are in the temple
        There are many altars
        Each belongs to a great
        warrior or nobleman
        """,
        """We must pay tribute to
        the gods!
        But who in your heart do
        you seek guidance from?""",
        ],
        goalBoxUid = altarBox.uid,
        nextNodeUid = "chooseGod",
        missTemplate =  "To continue your adventure {{node.goalBox.label}}",
        )

    NodeFork(
        uid = "chooseGod",
        choices  = {
            #2345678901234567890123456
            "epona" : """
            Epona, protector of horses
            """,
            "mars"  : """
            Mars, god of war & peace
            """,
            },
        )

    ThroughPage(
        uid = "epona",
        time = incrementTime,
        #2345678901234567890123456
        change = SackChange(
            trigger = "sack.epona == False",
            assign = { "epona":True },
            plus = { "eponapoints":1 },
            ),
        page = """
        {% if node.change.triggered %}
            {% if node.change.completed %}
                Epona protector of horses!
                May our mounts stay strong
                steady and fertile!
                we must make an offering!
            {% else %}
                Epona is displeased
            {% endif %}
        {% else %}
            Epona is with us already!
        {% endif %}
        """,
        goalBoxUid = paddockBox.uid,
        nextNodeUid = "eponaoffers",
        missTemplate =  "To continue goto {{node.goalBox.label}}"
        ,)

    ThroughPage(
        uid = "mars",
        goalBoxUid = seaBox.uid,
        time = incrementTime,
        #2345678901234567890123456
        change = SackChange(
            trigger = "sack.mars == False",
            assign = { "mars":True },
        ),
        page = """
        {% if node.change.triggered %}
            {% if node.change.completed %}
                Mars!
                We need great warriors!
                And we need to enforce
                peace and prosperity!
            {% else %}
                Mars is displeased
            {% endif %}
        {% else %}
            You feel strong!
            Mars is with us already!
            He also helps with the
            harvest you know...
        {% endif %}
        """,
        nextNodeUid = "marsoffers",
        missTemplate =  "To continue goto {{node.goalBox.label}}"
        )



    NodeFork(
            uid =   "eponaoffers",
            choices = {
                "eponawine": "Offer some wine",
                "eponagrain": "Seek some ears of grain"
                },
            )

    ThroughPage(
        uid =   "eponawine",
        goalBoxUid = seaBox.uid,
        change = SackChange(
            trigger = "sack.epona == True",
            assign = {"epona":False},
        ),
        page = """
        {% if node.change.triggered %}
            {% if node.change.completed %}
                You leave a cup of wine
                for her. Should she really
                drink and ride?
            {% else %}
            Epona can be seen with
            ears of grain
            {% endif %}
        {% else %}
        Epona is satisfied
        {% endif %}
        """,
        nextNodeUid = "yardArrive",
        missTemplate =  "To continue your adventure {{node.goalBox.label}}",
        )

    ThroughPage(
        uid =   "eponagrain",
        goalBoxUid = altarBox.uid,
        change = SackChange(
            assign = { "epona":True },
            plus = { "eponapoints":10 },
        ),
        page = """
        You offer grain
        from the local
        harvest
        """,
        nextNodeUid = "yardArrive",
        missTemplate =  "To continue your adventure {{node.goalBox.label}}",
        )

    NodeFork(
        #2345678901234567890123456
        uid =   "marsoffers",
        choices = {
            "marswine": "Offer some wine",
            "marsgrain": "Seek some ears of grain",
        },
        )

    ThroughSequence(
        uid =   "marswine",
        goalBoxUid = altarBox.uid,
        time = incrementTime,
        change = SackChange(
            plus = { "marspoints":2 }
        ),
        sequence = [
        """
        You leave a cup of wine
        for him. He also helps with
        the harvest which help us
        """,
        """
        Make more wine!
        """
        ],
        nextNodeUid = "yardArrive",
        missTemplate =  "To continue your adventure {{node.goalBox.label}}",
        )

    ThroughPage(
        uid =   "marsgrain",
        goalBoxUid = paddockBox.uid,
        change = SackChange(
            trigger = "sack.mars == True",
            assign = {"mars":False},
        ),
        page = """
        {% if node.change.triggered %}
            {% if node.change.completed %}
            You offer grain from the
            local harvest. What is he
            supposed to do with this?
            He's not Bruno Mars!
            {% else %}
            Mars is bored of grain
            He encourages harvests
            but its no fun!
            {% endif %}
        {% else %}
        Mars is satisfied
        {% endif %}
        """,
        nextNodeUid = "yardArrive",
        missTemplate =  "To continue your adventure {{node.goalBox.label}}",
        )


# ROUTE TO SPOTTING invaders
    ConditionFork(
        uid =       "seaview",
        condition = "sack.hours >= 10",
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
        condition =    "sack.mars == True",
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
            plus  =     { "marspoints":4 },
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
        Mars help us!
        """,
        goalBoxUid =    paddockBox.uid,
        nextNodeUid =   "retirement",
    )

    ThroughPage(
        uid = "retirement",
        goalBoxUid = entranceBox.uid,
        page = "Bad luck. Respawned. Tap to begin your adventure again",
        missTemplate = "You completed your adventure with {{sack.points}} points. Return to {{node.goalBox.label}} to respawn.",
        nextNodeUid = "landing",
    )

    ThroughSequence(
        uid = "retirementsuccess",
        goalBoxUid = paddockBox.uid,
        #2345678901234567890123456
        sequence = [
        """
        WELL DONE! VICTORY!
        The gods must be with you!
        """,
        """{% if sack.eponapoints < 10 %}
        You've driven back
        the hordes but will
        you manage next time?
        Will we have the
        right horses?
        {% endif %}
        {% if sack.eponapoints >= 10 %}
        With this horse
        we can breed horses
        for the next generation
        of Hadrian's cavalry
        {% endif %}
        """,
        """You completed your adventure with {{sack.eponapoints}} points. Return to {{node.goalBox.label}} to respawn.""",
        ],
        missTemplate = "You completed your adventure with {{sack.eponapoints}} points. Return to {{node.goalBox.label}} to respawn.",
        nextNodeUid = "landing",
    )

if __name__ == "__main__":
    print("Loading emulator")
    emulator = ConsoleSiteEmulator(story=story)
    print("Running Emulator")
    emulator.run()
