import threading, time
import RPi.GPIO as GPIO
import socket

from fysom import Fysom

fsm = Fysom({ 'initial': 'Idle',
              'events': [
                  {'name': 'Test', 'dst': 'testing'},
                  {'name': 'Breaktime', 'dst': 'Breaktiming'},
                  {'name': 'Evacuate', 'dst': 'Evacuating'},
                  {'name': 'Shelter', 'dst': 'Sheltering'},
                  {'name': 'Stop', 'dst': 'Idle'},
                  {'name': 'Rest', 'dst': 'Idle'}] })

UDP_IP = ""
UDP_PORT = 8888

# define 
ALLBuzzer = 0
Buzzer1st = 1
Buzzer2nd = 2
Buzzer3rd = 3
Buzzer4th = 4

# PIN Mapping defintion using BCM
SSR1Pin = 23 # Physical 16
SSR2Pin = 22 # Physical 15
SSR3Pin = 18 # Physical 12
SSR4Pin = 17 # Physical 11

Button1 = 26  # Physical 37
Button2 = 20  # Physical 38
Button3 = 19  # Physical 35
Button4 = 16  # Physical 36
Button5 = 6  # Physical 31
Button6 = 12  # Physical 32
Button7 = 5  # Physical 29
Button8 = 13  # Physical 33
Button9 = 4  # Physical 7

# 
nChoosenNum = 0
nPWMFreq = 500

def InitPorts():
    global Currthread
    global myevent

    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setwarnings(False)
    # PWM Output Pin Config
    GPIO.setup(SSR1Pin, GPIO.OUT)     
    GPIO.setup(SSR2Pin, GPIO.OUT) 
    GPIO.setup(SSR3Pin, GPIO.OUT)    
    GPIO.setup(SSR4Pin, GPIO.OUT)   
    
    GPIO.output(SSR1Pin, GPIO.LOW)
    GPIO.output(SSR2Pin, GPIO.LOW)
    GPIO.output(SSR3Pin, GPIO.LOW)
    GPIO.output(SSR4Pin, GPIO.LOW)

    # PWM Input Pin Config
    GPIO.setup(Button1, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.setup(Button2, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.setup(Button3, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.setup(Button4, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.setup(Button5, GPIO.IN, pull_up_down=GPIO.PUD_UP)     
    GPIO.setup(Button6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Button7, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Button8, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(Button9, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    Currthread = None
    myevent = None

# 
def BuzzerOn(nNum):
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(SSR1Pin, GPIO.OUT)     
    GPIO.setup(SSR2Pin, GPIO.OUT) 
    GPIO.setup(SSR3Pin, GPIO.OUT)    
    GPIO.setup(SSR4Pin, GPIO.OUT)   

    if nNum == 0:
        GPIO.output(SSR1Pin, GPIO.HIGH)
        GPIO.output(SSR2Pin, GPIO.HIGH)
        GPIO.output(SSR3Pin, GPIO.HIGH)
        GPIO.output(SSR4Pin, GPIO.HIGH)
    elif nNum == 1:
        GPIO.output(SSR1Pin, GPIO.HIGH)
        GPIO.output(SSR2Pin, GPIO.LOW)
        GPIO.output(SSR3Pin, GPIO.LOW)
        GPIO.output(SSR4Pin, GPIO.LOW)
    elif nNum == 2:
        GPIO.output(SSR1Pin, GPIO.LOW)
        GPIO.output(SSR2Pin, GPIO.HIGH)
        GPIO.output(SSR3Pin, GPIO.LOW)
        GPIO.output(SSR4Pin, GPIO.LOW)
    elif nNum == 3:
        GPIO.output(SSR1Pin, GPIO.LOW)
        GPIO.output(SSR2Pin, GPIO.LOW)
        GPIO.output(SSR3Pin, GPIO.HIGH)
        GPIO.output(SSR4Pin, GPIO.LOW)
    elif nNum == 4:
        GPIO.output(SSR1Pin, GPIO.LOW)
        GPIO.output(SSR2Pin, GPIO.LOW)
        GPIO.output(SSR3Pin, GPIO.LOW)
        GPIO.output(SSR4Pin, GPIO.HIGH)

def BuzzerOff():
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(SSR1Pin, GPIO.OUT)     
    GPIO.setup(SSR2Pin, GPIO.OUT) 
    GPIO.setup(SSR3Pin, GPIO.OUT)    
    GPIO.setup(SSR4Pin, GPIO.OUT)   

    GPIO.output(SSR1Pin, GPIO.LOW)
    GPIO.output(SSR2Pin, GPIO.LOW)
    GPIO.output(SSR3Pin, GPIO.LOW)
    GPIO.output(SSR4Pin, GPIO.LOW)

cycle = 0.0
Interval = 0.1

def TestProfile(e, nNum):
    cycle = 0
    BuzzerOn(nNum)
    while not e.isSet():
        event_is_set = e.wait(Interval)
        print('Test!')

        if event_is_set:
            fsm.Rest()
            print('Test Sopped!')
        else:
            cycle = cycle + 1

        if cycle == 5:
            BuzzerOff()
            print('Test 1st Step End!')
        if cycle == 10:
            BuzzerOn(nNum)
            print('Test 2nd Step End!')
        if cycle == 15:
            BuzzerOff()
            print('Test End!')
            fsm.Rest()
            e.set()
    BuzzerOff()
    Currthread = None

def BreaktimeProfile(e, nNum):
    cycle = 0
    BuzzerOn(nNum)
    print('Breaktime Started!')
    while not e.isSet():
        event_is_set = e.wait(Interval)
        if event_is_set:
            print('Breaktime Stopped!')
            fsm.Rest()
        cycle = cycle + 1
        if cycle == 50:
            BuzzerOff()
            print('Breaktime End!')
            fsm.Rest()
            e.set()
    BuzzerOff()
    Currthread = None

def ShelterProfile(e, nNum):
    cycle = 0
    BuzzerOn(nNum)
    print('Shelter Started!')
    while not e.isSet():
        event_is_set = e.wait(Interval)
        if event_is_set:
            fsm.Rest()
        cycle = cycle + 1
        if cycle == 5:
            BuzzerOff()
        elif cycle == 10:
            BuzzerOn(nNum)
        elif cycle == 15:
            BuzzerOff()
        elif cycle == 25:
            BuzzerOn(nNum)
            cycle = 0
            print('Shelter one step is ended!')
    print('Shelter Stopped!')
    BuzzerOff()
    Currthread = None

def EvacuateProfile(e, nNum):
    cycle = 0.0
    BuzzerOn(nNum)
    print('Evacuate Started!')
    while not e.isSet():
        event_is_set = e.wait(Interval)
        BuzzerOn(nNum)
    print('Evacuate End!')
    BuzzerOff()
    BuzzerOff()
    Currthread = None

def UDPServerthreadProc(e):
    global Currthread
    global myevent
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Make Socket Reusable
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1) # Allow incoming broadcasts
    sock.setblocking(False) # Set socket to non-blocking mode
    sock.bind((UDP_IP, UDP_PORT))
    FormatErrMsg = "Command Format Error: Valid Command Format is M(0~3),N(0~4)!" 
    while not e.isSet():
        try:
            message, address = sock.recvfrom(8192) # Buffer size is 8192. Change as needed.
            if message:
                print address, "> ", message
                if len(message) < 3:
                    print FormatErrMsg
                    #sock.send("Command Format Error: Valid Command Format is M(0~3),N(0~4)!")
                else:
                    CmdType = message[0]
                    nNum = int(message[2])
                    print CmdType, ">", nNum
                    if CmdType == '0': # test command
                        if nNum > 4:
                            print FormatErrMsg
                        else:
                            print "test Command issued!"
                            if fsm.current != "Idle":
                                print "Now No idle status, I will stop current actino and start!"
                                myevent.set()
                                time.sleep(Interval)
                            fsm.Test()
                            myevent = threading.Event()
                            CurrentThread = threading.Thread(target=TestProfile, args=(myevent,nNum))
                            CurrentThread.start()
                            Currthread = CurrentThread

                    elif CmdType == '1': # Breaktime command
                        if nNum > 4:
                            print FormatErrMsg
                        else:
                            print "Breaktime Command issued!"
                            if fsm.current != "Idle":
                                print "Now No idle status, I will stop current actino and start!"
                                myevent.set()
                                time.sleep(Interval)
                            fsm.Breaktime()
                            myevent = threading.Event()
                            CurrentThread = threading.Thread(target=BreaktimeProfile, args=(myevent,nNum))
                            CurrentThread.start()
                            Currthread = CurrentThread

                    elif CmdType == '2': # Evacuate command
                        if nNum > 4:
                            print FormatErrMsg
                        else:
                            print "Evacuate Command issued!"
                            if fsm.current != "Idle":
                                print "Now No idle status, I will stop current actino and start!"
                                myevent.set()
                                time.sleep(Interval)
                            fsm.Evacuate()
                            myevent = threading.Event()
                            CurrentThread = threading.Thread(target=EvacuateProfile, args=(myevent,nNum))
                            CurrentThread.start()
                            Currthread = CurrentThread

                    elif CmdType == '3': # Shelter command
                        if nNum > 4:
                            print FormatErrMsg
                        else:
                            print "Shelter Command issued!"
                            if fsm.current != "Idle":
                                print "Now No idle status, I will stop current actino and start!"
                                myevent.set()
                                time.sleep(Interval)
                            fsm.Shelter()
                            myevent = threading.Event()
                            CurrentThread = threading.Thread(target=ShelterProfile, args=(myevent,nNum))
                            CurrentThread.start()
                            Currthread = CurrentThread

                    elif CmdType == 'S': # Stop command
                        print "Buzzer Stop Command issued!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Stop()
        except:
            pass

InitPorts()

Udpevent = threading.Event()
UdpThread = threading.Thread(target=UDPServerthreadProc, args=(Udpevent,))
UdpThread.start()

print("Here we go! Press CTRL+C to exit")
RELEASED = 1
PUSHED = 0
try:
    prev_inputs = [RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED]
    inputs = [RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED, RELEASED]
    while 1:
        inputs[0] = GPIO.input(Button1)
        inputs[1] = GPIO.input(Button2)
        inputs[2] = GPIO.input(Button3)
        inputs[3] = GPIO.input(Button4)
        inputs[4] = GPIO.input(Button5)
        inputs[5] = GPIO.input(Button6)
        inputs[6] = GPIO.input(Button7)
        inputs[7] = GPIO.input(Button8)
        inputs[8] = GPIO.input(Button9)
        for idx in range(0, 9):
            if prev_inputs[idx] != inputs[idx]:
                prev_inputs[idx] = inputs[idx]
                if prev_inputs[idx] == PUSHED: # Any button Pushed 
                    if idx == 0: # Button1 Pushed
                        print "Button1 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Evacuate()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=EvacuateProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 1: # Button2 Pushed
                        print "Button2 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Shelter()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=ShelterProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 2: # Button3 Pushed
                        print "Button3 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Evacuate()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=EvacuateProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 3: # Button4 Pushed
                        print "Button4 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Shelter()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=ShelterProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 4: # Button5 Pushed
                        print "Button5 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Evacuate()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=EvacuateProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 5: # Button6 Pushed
                        print "Button6 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Shelter()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=ShelterProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 6: # Button7 Pushed
                        print "Button7 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Evacuate()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=EvacuateProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 7: # Button8 Pushed
                        print "Button8 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Shelter()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=ShelterProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                    elif idx == 8: # Button9 Pushed
                        print "Button9 pushed!"
                        if fsm.current != "Idle":
                            myevent.set()
                            time.sleep(Interval)
                        fsm.Shelter()
                        myevent = threading.Event()
                        CurrentThread = threading.Thread(target=ShelterProfile, args=(myevent,0))
                        CurrentThread.start()
                        Currthread = CurrentThread

                elif prev_inputs[idx] == RELEASED: # Any button RELEASED
                    print "Button%d Released!" % idx # Button Released
                    if fsm.current != "Idle":
                        myevent.set()
                        time.sleep(Interval)
                    fsm.Stop()
                    
        time.sleep(0.5)        
except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
    Udpevent.set()

    if Currthread != None:
        myevent.set()
    BuzzerOff()
    GPIO.cleanup() # cleanup all GPIO
