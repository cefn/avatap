import cockle
from machine import Pin                                                                      
depowerPin = cockle.pins[6]
depowerPin.init(mode=Pin.OUT)                                                            
depowerPin.low()
