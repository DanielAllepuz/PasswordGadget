import serial

GREET = bytes([0x42])
GREET_RESPONSE = "hi"

class Arduino(object):
    """
    Arduino is a class that represents the Arduino
    that controls the gadget
    """

    def __init__(self, port = '/dev/tty.usbmodemHIDPC1', baud = 9600):
        super(Arduino, self).__init__()
        self.port = port
        self.serial = serial
        self.ser = serial.Serial(port, baud, dsrdtr = True)

        #We check if the arduino is listening
        for i in range(10):
            print(">Greeting  arduino... Attempt {}".format(i+1))
            start_up_message = self.send_message(GREET).decode().strip()
            if start_up_message == GREET_RESPONSE:
                print(">[SUCCESS] Found the Arduino!")
                break
            else: #bad start_up_message
                print(">[ERROR] The Arduino says: {}".format(start_up_message))

    def send_message(self, message):
        """
        Sends a message via serial and returns the response not decoded
        input:
            - message, bytearray
        returns:
            - response, bytearray
        """
        self.ser.write(message)
        return self.ser.readline()

    def recv_message(self):
        """
        Waits for a new message and returns it not decoded
        """
        return self.ser.readline()

    def close(self):
        self.ser.close()

SAVE_PASSWORD = bytes([1])

PSWRD_NAME_SIZE = 8
PSWRD_CONTENT_SIZE = 12

def send_password(ardu, slot, name, content):
    #Starts save password protocol
    print(">Sending SAVE_PASSWORD command")
    resp = ardu.send_message(SAVE_PASSWORD)
    print(">EEPROM size is {} bytes".format(resp.decode().strip()))
    #Sends desired slot
    resp = ardu.send_message(str(slot).encode()).decode().strip()

    #Checks that the Arduino has understood the slot
    try:
        resp = int(resp)
        if int(resp) == slot*(PSWRD_NAME_SIZE + PSWRD_CONTENT_SIZE):
            print(">Slot OK (address: {})".format(resp))
        else:
            print(">[ERROR] Arduino returns wrong address, make sure size constants are common.")
            return False
    except ValueError as e:
        print(">[ERROR] Couldn't select slot {}, Arduino says: {}".format(slot, resp))
        return False

    #Sends password name
    resp = ardu.send_message(name[:PSWRD_NAME_SIZE].encode()).decode().strip()
    if resp == name:
        print(">Password name transferred correctly")
    else:
        print(">[ERROR] Arduino understood {} as the name")
        return False

    #Sends password content
    resp = ardu.send_message(content[:PSWRD_CONTENT_SIZE].encode()).decode().strip()
    if resp == content:
        print(">Password content transferred correctly")
    else:
        print(">[ERROR] The password echoed back was different {}".format(resp))
        return False

    #Waits for Arduino to confirm EEPROM write
    resp = ardu.recv_message().decode().strip()

    if resp == "done":
        print(">[SUCCESS] Password saved correctly!")
        return True
    else:
        print(">[ERROR] Something went wrong saving the password")
        return False

DUMP_EEPROM = bytes([2])
def dump_EEPROM(ardu):
    """
    Makes the Arduino dump EEPROM content
    """
    resp = ardu.send_message(DUMP_EEPROM).decode()
    print(resp)

GET_NAME = bytes([3])
def get_name(ardu, slot):
    """
    Gets password name at given slot
    """
    resp = ardu.send_message(GET_NAME).decode().strip()
    if resp == "ready":
        resp = ardu.send_message(str(slot).encode()).decode().strip()
        print(">[SUCCESS] Name is: {}".format(resp))
    else:
        print(">[ERROR] Something went wrong in the Arduino: {}".format(resp))

GET_CONTENT = bytes([4])
def get_content(ardu, slot):
    """
    Gets password content at given slot
    """
    resp = ardu.send_message(GET_CONTENT).decode().strip()
    if resp == "ready":
        resp = ardu.send_message(str(slot).encode()).decode().strip()
        print(">[SUCCESS] Content is: {}".format(resp))
    else:
        print(">[ERROR] Something went wrong in the Arduino: {}".format(resp))

FILL_WITH_EMPTY = bytes([0])
def fill_with_empty(ardu):
    resp = ardu.send_message(FILL_WITH_EMPTY)

EXIT_SERIAL_MODE = bytes([0xFF])
def exit_serial_mode(ardu):
    resp = ardu.send_message(EXIT_SERIAL_MODE)
