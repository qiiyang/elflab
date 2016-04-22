from elflab import kernels
import elflab.projects.He3.janis_001 as janis001

plot_temperature = [
        [("T_sample", "R1"), ("T_sample", "R2")],
        [("t", "T_flow"), ("t", "T_sample")]
        ]

plot_field = [
        [("H", "R1"), ("H", "R2")],
        [("t", "T_flow"), ("t", "T_sample")]
        ]

plot_time = [
        [("t", "R1"), ("t", "R2")],
        [("t", "T_flow"), ("t", "T_sample")]
        ]

if __name__ == '__main__':
    #gui=janis001.Janis001GUI(kernels.Galileo, janis001.Janis001SR830SR830IPS120)
    gui=janis001.Janis001GUI(kernels.Galileo, janis001.Janis001Keithley617SR830, subplots=plot_time)
    gui.start()