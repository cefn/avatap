#include "LCD4Bit.h"
extern "C" {
  #include <stdio.h>  //not needed yet
  #include <string.h> //needed for strlen()
  #include <inttypes.h>
  #include "WConstants.h"  //all things wiring / arduino
}

//command bytes for LCD
#define CMD_CLR 0x01
#define CMD_RIGHT 0x1C
#define CMD_LEFT 0x18
#define CMD_HOME 0x02

// --------- PINS -------------------------------------
//is the RW pin of the LCD under our control?  If we're only ever going to write to the LCD, we can use one less microcontroller pin, and just tie the LCD pin to the necessary signal, high or low.
//this stops us sending signals to the RW pin if it isn't being used.
int USING_RW = false;

//RS, RW and Enable can be set to whatever you like
int RS = 6;
int RW = false;	//wird nicht verwendet, da direkt am LCD auf Masse
//legba7: two HD44780; per HD44780 one Enable Input
int Enable1 = 4;
int Enable2 = 5;
int Enable = Enable1;
//DB should be an unseparated group of pins  - because of lazy coding in pushNibble()
int DB[] = {0, 1, 2, 3};	//{7, 8, 9, 10};  //wire these to DB4~7 on LCD.

//--------------------------------------------------------

//how many lines has the LCD? (don't change here - specify on calling constructor)
int g_num_lines = 2;

void LCD4Bit::WriteCGRAM(int adress, char code[]) {
   commandWrite(0x40+(adress<<3));
   printIn(code);
   commandWrite(CMD_HOME); // How to return to previous position ?
}

//pulse the Enable pin high (for a microsecond).
//This clocks whatever command or data is in DB4~7 into the LCD controller.
void LCD4Bit::pulseEnablePin(){
  digitalWrite(Enable,LOW);
  delayMicroseconds(1);
  // send a pulse to enable
  digitalWrite(Enable,HIGH);
  delayMicroseconds(1);
  digitalWrite(Enable,LOW);
  delay(1);  // pause 1 ms.  TODO: what delay, if any, is necessary here? (it seems that 1ms is a good choice)
}

//push a nibble of data through the the LCD's DB4~7 pins, clocking with the Enable pin.
//We don't care what RS and RW are, here.
void LCD4Bit::pushNibble(int value){
  int val_nibble= value & 0x0F;  //clean the value.  (unnecessary)

  for (int i=DB[0]; i <= DB[3]; i++) {
    digitalWrite(i,val_nibble & 01);
    val_nibble >>= 1;
  }
  pulseEnablePin();
}

//push a byte of data through the LCD's DB4~7 pins, in two steps, clocking each with the enable pin.
void LCD4Bit::pushByte(int value){

  int val_lower = value & 0x0F;
  int val_upper = value >> 4;
  pushNibble(val_upper);
  pushNibble(val_lower);
}


//stuff the library user might call---------------------------------
//constructor.  num_lines must be 1 or 2 or 4, currently.
LCD4Bit::LCD4Bit (int num_lines) {
  g_num_lines = num_lines;
  if (g_num_lines != 1 && g_num_lines != 2 && g_num_lines != 4)
  {
    g_num_lines = 1;
  }
}

void LCD4Bit::commandWriteNibble(int nibble) {
  digitalWrite(RS, LOW);
  if (USING_RW) { digitalWrite(RW, LOW); }
  pushNibble(nibble);
}


void LCD4Bit::commandWrite(int value) {
  digitalWrite(RS, LOW);
  if (USING_RW) { digitalWrite(RW, LOW); }
  pushByte(value);
  //TODO: perhaps better to add a delay after EVERY command, here.  many need a delay, apparently.
}




//print the given character at the current cursor position. overwrites, doesn't insert.
void LCD4Bit::print(int value) {
  //set the RS and RW pins to show we're writing data
  digitalWrite(RS, HIGH);
  if (USING_RW) { digitalWrite(RW, LOW); }

  //let pushByte worry about the intricacies of Enable, nibble order.
  pushByte(value);
}


//print the given string to the LCD at the current cursor position.  overwrites, doesn't insert.
//While I don't understand why this was named printIn (PRINT IN?) in the original LiquidCrystal library, I've preserved it here to maintain the interchangeability of the two libraries.
void LCD4Bit::printIn(char msg[]) {
  uint8_t i;  //fancy int.  avoids compiler warning when comparing i with strlen()'s uint8_t
  for (i=0;i < strlen(msg);i++){
    print(msg[i]);
  }
}


//send the clear screen command to the LCD
void LCD4Bit::clear(){
  commandWrite(CMD_CLR);
  delay(1);
}


// initiatize lcd after a short pause
//while there are hard-coded details here of lines, cursor and blink settings, you can override these original settings after calling .init()
void LCD4Bit::init () {
  pinMode(Enable,OUTPUT);
  pinMode(RS,OUTPUT);
  if (USING_RW) { pinMode(RW,OUTPUT); }
  pinMode(DB[0],OUTPUT);
  pinMode(DB[1],OUTPUT);
  pinMode(DB[2],OUTPUT);
  pinMode(DB[3],OUTPUT);

  delay(50);

  //The first 4 nibbles and timings are not in my DEM16217 SYH datasheet, but apparently are HD44780 standard...
  commandWriteNibble(0x03);
  delay(5);
  commandWriteNibble(0x03);
  delayMicroseconds(100);
  commandWriteNibble(0x03);
  delay(5);

  // needed by the LCDs controller
  //this being 2 sets up 4-bit mode.
  commandWriteNibble(0x02);
  commandWriteNibble(0x02);
  //todo: make configurable by the user of this library.
  //NFXX where
  //N = num lines (0=1 line or 1=2 lines).
  //F= format (number of dots (0=5x7 or 1=5x10)).
  //X=don't care
  int num_lines_ptn ;
  if (g_num_lines != 4) {
  	num_lines_ptn = g_num_lines - 1 << 3;
  } else {
	num_lines_ptn = 2 - 1 << 3; // we are controlling the 4 lines display as an 2 lines.
  }
  int dot_format_ptn = 0x00;      //5x7 dots.  0x04 is 5x10

  commandWriteNibble(num_lines_ptn | dot_format_ptn);
  delayMicroseconds(60);

  //The rest of the init is not specific to 4-bit mode.
  //NOTE: we're writing full bytes now, not nibbles.

  // display control:
  // turn display on, cursor off, no blinking
  commandWrite(0x0C);
  delayMicroseconds(60);

  //clear display
  commandWrite(0x01);
  delay(3);

  // entry mode set: 06
  // increment automatically, display shift, entire shift off
  commandWrite(0x06);

  delay(1);//TODO: remove unnecessary delays
}


//non-core stuff --------------------------------------
//move the cursor to the given absolute position.  line numbers start at 1.
//if this is not a 2-line LCD4Bit instance, will always position on first line.
//
//legba7: second controller, with its own Enable input, for line 3 and 4
void LCD4Bit::cursorTo(int line_num, int x){

  //if we are on a 1-line display, set line_num to 1st line, regardless of given
  if (g_num_lines==1){
    line_num = 1;
    Enable = Enable1;
  }
  //offset 40 chars in if second line requested
  //
  switch (line_num){
  case 1:
    Enable = Enable1;
    x=0x00 ; break;;
  case 2: 
    Enable = Enable1;
    x= 0x40 ; break;;
  case 3: 
    //line_num = 1;
    Enable = Enable2;
    x=0x00; break;;
    //x+= 0x14 ; break;; // In fact, line 3 is an extension of the line 1 (beyond the 20 first characters)
  case 4: 
    Enable = Enable2;
    //x+= 0x54 ; break;; // Line 4 is an extension of line 2
    x= 0x40 ; break;; // Line 4 is an extension of line 3
  }

  commandWrite(0x80+x);
}

//scroll whole display to left
//Doesn't seems to be usefull with 4 lines displays!
//
void LCD4Bit::leftScroll(int num_chars, int delay_time){
  for (int i=0; i<num_chars; i++) {
    commandWrite(CMD_LEFT);
    delay(delay_time);
  }
}

//Improvements ------------------------------------------------
//Remove the unnecessary delays (e.g. from the end of pulseEnablePin()).
//Allow the user to pass the pins to be used by the LCD in the constructor, and store them as member variables of the class instance.
//-------------------------------------------------------------