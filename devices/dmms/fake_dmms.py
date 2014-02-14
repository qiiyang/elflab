""" Simulated DMMs """

class ConstDMM:
    """ A fake DMM only reads constant value """
    def __init___(self, reading=0.):
        self.reading = reading
    
    def read(self):
        return self.reading

        