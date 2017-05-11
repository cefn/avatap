import milecastles
from engines import Engine
from engines.console import ConsoleSiteEmulator

class AvatapSiteEmulator(ConsoleSiteEmulator):
    smallFont = milecastles.required
    bigFont = milecastles.required
    screen = milecastles.required
    blackPlotter = milecastles.required
    whitePlotter = milecastles.required

    def __init__(self, *a, **k):
        super().__init__(*a, **k)

    def createEngine(self, box):
        return AvatapEngine(
            box=box,
            smallFont=self.smallFont,
            bigFont=self.bigFont,
            screen=self.screen,
            blackPlotter=self.blackPlotter,
            whitePlotter=self.whitePlotter
        )

class AvatapEngine(Engine):
    screen = milecastles.required
    smallFont = milecastles.required
    bigFont = milecastles.required
    blackPlotter = milecastles.required
    whitePlotter = milecastles.required

    def displayGeneratedText(self, generator):
        self.screen.clear()
        self.smallFont.draw_generator(generator, self.blackPlotter)
        self.screen.redraw()

    """
    # TODO CH workaround for debugging
    def displayGeneratedText(self, generator):
        for chunk in generator:
            sys.stdout.write(chunk)
    """
