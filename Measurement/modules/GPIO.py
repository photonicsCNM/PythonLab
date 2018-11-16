class Switch():
    RPi = __import__('RPi.GPIO')
    GPIO = RPi.GPIO
    
    def __init__(self, BCM_number, mode = 'bcm'):
        self.BCM_number = BCM_number
        self.GPIO.setwarnings(False)
        if mode == 'bcm':
            self.GPIO.setmode(self.GPIO.BCM)
        elif mode == 'board':
            self.GPIO.setmode(self.GPIO.BOARD)
        self.GPIO.setup(self.BCM_number, self.GPIO.OUT) 
        
    def high(self):
        self.GPIO.output(self.BCM_number,1)
        
    def low(self):
        self.GPIO.output(self.BCM_number,0)

        

