from stories import corbridge
import st7920
screen = st7920.Screen()
def plot(x,y):
	screen.plot(x,y)
from agnostic import report_collect
from faces.font_5x7 import font
import read
#report_collect(); from faces.font_ArtosSerif_8 import font as bigFont
#screen.clear(); report_collect(); font.draw_line("Hello Moon", plot); report_collect();  screen.redraw();