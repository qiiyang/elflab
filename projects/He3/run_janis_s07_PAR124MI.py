from elflab import kernels
import elflab.projects.He3.janis_s07 as s07

if __name__ == '__main__':
    gui=s07.JanisS07GUI(kernels.Galileo, s07.JanisS07PAR124MI, s07.JanisS07Controller)
    gui.start()