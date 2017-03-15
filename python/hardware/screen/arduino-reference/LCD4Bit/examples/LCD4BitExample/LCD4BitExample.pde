//example use of LCD4Bit library

#include <LCD4Bit.h> 
//create object to control an LCD.  
//number of lines in display=1
LCD4Bit lcd = LCD4Bit(1); 

//some messages to display on the LCD
char msgs[6][15] = {"apple", "banana", "pineapple", "mango", "watermelon", "pear"};
int NUM_MSGS = 6;

void setup() { 
  pinMode(13, OUTPUT);  //we'll use the debug LED to output a heartbeat

  lcd.init();
  //optionally, now set up our application-specific display settings, overriding whatever the lcd did in lcd.init()
  //lcd.commandWrite(0x0F);//cursor on, display on, blink on.  (nasty!)
}

void loop() {  
  digitalWrite(13, HIGH);  //light the debug LED

  //pick a random message from the array
  int pick = random(NUM_MSGS);
  char* msg = msgs[pick];
  
  lcd.clear();
  lcd.printIn(msg);
  delay(1000);
  digitalWrite(13, LOW);
  
  //print some dots individually
  for (int i=0; i<3; i++){
    lcd.print('.');
    delay(100);
  }
  //print something on the display's second line. 
  //uncomment this if your display HAS two lines!
  /*
  lcd.cursorTo(2, 0);  //line=2, x=0.
  lcd.printIn("Score: 6/7");
  delay(1000);
  */
  
  //scroll entire display 20 chars to left, delaying 50ms each inc
  lcd.leftScroll(20, 50);
}
