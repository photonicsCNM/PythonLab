class LoopControlButtons():
    def __init__(self):
        import numpy as np
        import ipywidgets as widgets
        from ipywidgets import interact
        from IPython.display import display
        
        self.stop = False
        np.save('stop', self.stop)
        self.button1 = widgets.Button(description='Stop/Resume')
        self.button1.on_click(self.stop_clicked)
        self.button2 = widgets.Button(description='Abort')
        self.button2.on_click(self.abort_clicked)
        
    def stop_clicked(self, b):
        import numpy as np
        self.stop = not self.stop
        np.save('stop', self.stop)
        
    def abort_clicked(self, b):
        import numpy as np
        np.save('stop', 'abort')
        
    def show(self):
        display(self.button1)
        display(self.button2)
