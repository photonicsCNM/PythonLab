class Switch():
    
    def __init__(self, BCM_number):
        self.BCM_number = BCM_number
        from subprocess import call
        self.call = call
        
    def high(self):
        cmds = 'import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(%i, GPIO.OUT); GPIO.output(%i, 1)' %(self.BCM_number,self.BCM_number)
        self.call(["/usr/bin/python3", "-c", cmds] )

    def low(self):
        cmds = 'import RPi.GPIO as GPIO; GPIO.setmode(GPIO.BCM); GPIO.setup(%i, GPIO.OUT); GPIO.output(%i, 0)' %(self.BCM_number,self.BCM_number)
        self.call(["/usr/bin/python3", "-c", cmds] )