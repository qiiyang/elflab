from elflab import kernels
import elflab.projects.He3.janis_001 as janis001

if __name__ == '__main__':
    gui=janis001.Janis001GUI(kernels.Galileo, janis001.Janis001SR830PAR124)
    gui.start()