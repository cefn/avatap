# Originally from http://www.multiwingspan.co.uk/micro.php?page=lcd

from cockle import pins, sleep
from machine import Pin

# pin connections
rs = pins[2]
enable = pins[3]
datapins = [pins[num] for num in  range(4,8)]

# set all the pins to out mode
[pin.init(mode=Pin.OUT) for pin in ([rs, enable] + datapins)]

# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00


def InitDisplay():
    # at least 50ms after power on
    sleep(50)
    # send rs, enable low - rw is tied to GND
    rs.value(0)
    enable.value(0)
    write4bits(0x03)
    sleep(5)
    write4bits(0x03)
    sleep(5)
    write4bits(0x03)
    sleep(2)
    write4bits(0x02)
    send(LCD_FUNCTIONSET | 0x08, 0)
    sleep(5)
    send(LCD_FUNCTIONSET | 0x08, 0)
    sleep(2)
    send(LCD_FUNCTIONSET | 0x08, 0)
    sleep(2)
    send(LCD_FUNCTIONSET | 0x08, 0)
    sleep(2)
    send(LCD_DISPLAYCONTROL | LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF,0)
    clear()
    send(LCD_ENTRYMODESET | LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT,0)
     
# high level commands    
def clear():
    send(LCD_CLEARDISPLAY,0)
    sleep(2)

def home():
    send(LCD_RETURNHOME,0)
    sleep(2)

def setCursor(col, row):
    orpart = col
    if row>0:
        orpart = orpart + 0x40
    send(LCD_SETDDRAMADDR | orpart, 0)

def showText(t):
    for c in t:
        send(ord(c), 1)

# mid and low level commands        
def send(value, mode):
    rs.value(mode)
    write4bits(value>>4)
    write4bits(value)
    
def pulseEnable():
    enable.value(0)
    sleep(1)
    enable.value(1)
    sleep(1)
    enable.value(0)
    sleep(1)

def write4bits(value):
    for i in range(0,4):
        datapins[i].value((value>>i) & 0x01)
    pulseEnable()

# Test
def run():
    InitDisplay()
    showText("Hello")
    setCursor(0,1)
    showText("World")
    sleep(5000)
    clear()
    showText("How are you?")