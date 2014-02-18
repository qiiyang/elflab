from elflab import abstracts

        
class Logger(abstracts.Logger):
    """Not Logging at All"""
    def __init__(self):
        pass
        
    def start(self):
        pass
    
    def log(self, dataToLog):  # To write down a data point
        pass
        
    def finish(self):
        pass