from elflab import abstracts

        
class Logger(abstracts.LoggerBase):
    """Not Logging at All"""
    def __init__(self, filename=None):
        pass
        
    def start(self):
        pass
    
    def log(self, dataToLog):  # To write down a data point
        pass
        
    def finish(self):
        pass