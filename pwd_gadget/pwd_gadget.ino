
#include <LiquidCrystal.h>
#include <Keyboard.h>
#include <EEPROM.h>

//Constants:
//LCD PINs:
const unsigned int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
//Button PINs:
const int leftB = 6; //Pin left button
const int rightB = 7; //Pin right button
const int select = 10; //Pin right button
//Command codes:
const byte FILL_WITH_EMPTY = 0x0;
const byte SAVE_PASSWORD = 0x1;
const byte DUMP_EEPROM = 0x2;
const byte GET_NAME = 0x3;
const byte GET_CONTENT = 0x4;
const byte GREET = 0x42;
const byte EXIT_SERIAL_MODE = 0xFF;

//EPPROM constants
#define PSWRD_NAME_SIZE 8
#define PSWRD_CONTENT_SIZE 12

//Global variables
//LCD controller
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
//Buttons
int bStateR = 0;         //State right button
int bStateL = 0;         //State left button
int sState = 0;         //State select button

int oldR = 0;         //Old state right button
int oldL = 0;         //Old state left button
int oldsel = 0;         //Old state select button

//Menu
int iter = 0;

//Password data
unsigned int num = 0;

void setup() {
  // Pin setup:
  pinMode(rightB, INPUT);
  pinMode(leftB, INPUT);
  pinMode(select, INPUT);

  // LCD setup
  lcd.begin(16, 2);
  lcd.setCursor(0, 0);
  lcd.print("pwd gadget");
  lcd.setCursor(0, 1);
  lcd.print("HackUPC - 2018");

  //Keyboard emulation setup
  Keyboard.begin();

  num = slotsAvailable();
  updatePasswordName();

//  Serial.begin(9600);
//  while(!Serial){;}
}

void loop() {

  bStateR = digitalRead(rightB);
  bStateL = digitalRead(leftB);
  sState = digitalRead(select);

  if (bStateR == HIGH && oldR == LOW) { //when right button is pressed
    //Serial.println("R");
    do {
      iter = (iter + 1) % num;
    } while (get_password_name(iter) == "[empty]");

    updatePasswordName();
  }

  else if (bStateL == HIGH && oldL == LOW) { //when left button is pressed
    //Serial.println("L");
    do {
      iter = (iter - 1) % num;
      if (iter < 0) {
        iter = num - 1;
      }
    } while (get_password_name(iter) == "[empty]");

    updatePasswordName();
  }

  else if (sState == HIGH && oldsel == LOW) { //when select button is pressed
    //Serial.println("S");
    Keyboard.print(get_password_content(iter));
    lcd.setCursor(0, 1);
    lcd.print("Password sent!");
  } else if (bStateL == HIGH && bStateR == HIGH) {
    startSerialMode();
  }

  oldR = bStateR;
  oldL = bStateL;
  oldsel = sState;

}

/*
   Serial mode, to program the gadget from the computer
*/
void startSerialMode() {
  lcd.clear();
  lcd.print("Serial mode, connect to PC");
  
  
  Serial.begin(9600);
  while (!Serial) {
    ; //waiting for serial to be available
  }
  bool serial = true;
  while (serial) {
    if (Serial.available()) {
      byte rcvd = Serial.read(); //reads byte

      switch (rcvd) {
        case FILL_WITH_EMPTY:
          fill_with_empty();
          Serial.println("done");
          break;
        case SAVE_PASSWORD:
          start_save_protocol();
          break;
        case GET_NAME:
          start_get_name_protocol();
          break;
        case GET_CONTENT:
          start_get_content_protocol();
          break;
        case GREET:
          Serial.println("hi");
          break;
        case EXIT_SERIAL_MODE:
          serial = false;
          Serial.println("bye");
          updatePasswordName();
          break;
      }
    }
  }
}


/*
   What to show when listing passwords
*/
void updatePasswordName() {
  lcd.clear();
  lcd.print("Name: " + get_password_name(iter));
}

/*
   Converts slot index to EEPROM address
*/
unsigned int slotToAddress(unsigned int slot) {
  return slot * (PSWRD_NAME_SIZE + PSWRD_CONTENT_SIZE);
}

/*
   Slots available
*/
unsigned int slotsAvailable() {
  return EEPROM.length() / (PSWRD_NAME_SIZE + PSWRD_CONTENT_SIZE);
}
/*
   Get password name in given slot
*/
String get_password_name(unsigned int slot) {
  //computes address from slot number
  unsigned int addrs = slot * (PSWRD_NAME_SIZE + PSWRD_CONTENT_SIZE);
  //memory will be dumped here
  char pswrd_name[PSWRD_NAME_SIZE];
  for (unsigned int i = 0; i < PSWRD_NAME_SIZE; i++) {
    pswrd_name[i] = EEPROM[addrs + i];
  }
  return String(pswrd_name);
}

/*
   Get password content in given slot
*/
String get_password_content(unsigned int slot) {
  //computes address from slot number
  unsigned int addrs = slot * (PSWRD_NAME_SIZE + PSWRD_CONTENT_SIZE);
  //memory will be dumped here
  char pswrd_content[PSWRD_CONTENT_SIZE];
  for (unsigned int i = 0; i < PSWRD_CONTENT_SIZE; i++) {
    pswrd_content[i] = EEPROM[addrs + PSWRD_NAME_SIZE + i];
  }
  return String(pswrd_content);
}

void start_save_protocol() {
  unsigned int EEPROM_length = EEPROM.length();
  //Sends size of the EEPROM
  Serial.println(EEPROM_length);

  //Computer now sends the desired slot
  unsigned int slot = Serial.parseInt();
  unsigned int addrs = slotToAddress(slot);
  //Checks if addrs is a valid addrs
  if (addrs < EEPROM_length) {
    Serial.println(addrs);
  } else {
    Serial.println("too big");
  }

  //PC sends the password name
  String pswrd_name = Serial.readString();
  Serial.println(pswrd_name); //echoes name

  //PC sends the password content
  String pswrd_content = Serial.readString();
  Serial.println(pswrd_content); //echoes content

  //Writes to EEPROM
  save_password(slot, pswrd_name, pswrd_content);

  //Success!
  Serial.println("done");
}

void start_get_name_protocol() {
  Serial.println("ready");
  unsigned int slot = Serial.parseInt();
  Serial.println(get_password_name(slot));
}

void start_get_content_protocol() {
  Serial.println("ready");
  unsigned int slot = Serial.parseInt();
  Serial.println(get_password_content(slot));
}

void fill_with_empty()
{
  const unsigned int n_slots = EEPROM.length() / (PSWRD_NAME_SIZE + PSWRD_CONTENT_SIZE);
  for (unsigned int slot = 0; slot < n_slots; slot++) {
    save_password(slot, "[empty]", "");
  }
}

void save_password(unsigned int slot, String pswrd_name, String pswrd_content) {
  //Writes to EEPROM
  unsigned int addrs = slotToAddress(slot);
  for (unsigned int i = 0; i < PSWRD_NAME_SIZE; i++)
    EEPROM.write(addrs + i, pswrd_name.c_str()[i]);
  for (unsigned int i = 0; i < PSWRD_CONTENT_SIZE; i++)
    EEPROM.write(addrs + PSWRD_NAME_SIZE + i, pswrd_content.c_str()[i]);
}
