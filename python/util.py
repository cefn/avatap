import sys

if sys.implementation.name == "micropython":
	from utime import time
	from utime import ticks_ms
else:
	from time import time
	def ticks_ms():
		return int(time()*1000)
