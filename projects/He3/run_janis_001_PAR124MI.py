from elflab import kernels
import elflab.projects.He3.janis_001_v2 as janis001

if __name__ == '__main__':
    gui=janis001.JanisS07GUI(kernels.Galileo, janis001.Janis001PAR124MI)
    gui.start()