import sys
import milecastles
from engines import Engine

# Ensure minimal 'binding' closure

def blackPlotterFactory(screen):
    def blackPlotter(x,y):
        screen.plot(x,y,True)
    return blackPlotter

def whitePlotterFactory(screen):
    def whitePlotter(x,y):
        screen.plot(x,y,False)
    return whitePlotter

# Could be parameterised by reader, writer, plotter, font?
class AvatapEngine(Engine):
    screen = milecastles.required
    font = milecastles.required
    reader = milecastles.required

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.blackPlotter = blackPlotterFactory(self.screen)
        self.whitePlotter = whitePlotterFactory(self.screen)

    def displayGeneratedText(self, generator):
        self.screen.clear()
        self.font.draw_generator(generator, self.blackPlotter)
        self.screen.redraw()

    """
    # TODO CH workaround for debugging
    def displayGeneratedText(self, generator):
        for chunk in generator:
            sys.stdout.write(chunk)
    """
