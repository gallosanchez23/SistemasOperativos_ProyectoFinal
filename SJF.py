import string
from Base import Proceso, Command, CPUScheduler, conditionToOrderProcess


class CPUSchedulerSJF(CPUScheduler):

    def __init__(self, cantCPU, quantum, CC):
        CPUScheduler.__init__(self, cantCPU, quantum, CC)


    def putNextProcessToRun(self, timestamp):
        # Checamos primero si hay procesos
        if len(self._filaTurnos) == 0:
            return

        # # Si son cosas que llegaron al mismo tiempo, pues vamos a intentar reacomodarlos mejor
        # if self._lastTime == timestamp:
        #     # Buscamos a cual es el mejor postor, si hay nos salimos. Si no hay nos quedamos a ver si
        #     # hay algun cpu vacio
        #     indexCPUMejorPostor = None
        #     for indexCPU in range(_CANT_CPU):
        #         if self._CPUs[indexCPU]["desde"] == timestamp and 
        #             self._listaProcesos[self._CPUs[indexCPU]["PID"]].tiempoRestante >
        #             self._listaProcesos[self._CPUs[indexCPUMejorPostor]["PID"]].tiempoRestante)
        #             (indexCPUMejorPostor == None or
        #             self._listaProcesos[self._CPUs[indexCPU]["PID"]].tiempoRestante >
        #             self._listaProcesos[self._CPUs[indexCPUMejorPostor]["PID"]].tiempoRestante):
        #             indexCPUMejorPostor = indexCPU

        #     if indexCPUMejorPostor != None:
        #         # Se re agrega el proceso a la fila de espera

        indexCPU = 0
        while (indexCPU < self._CANT_CPU and len(self._filaTurnos) > 0):
            if self._CPUs[indexCPU]["PID"] == -1:
                #Se obtiene el proceso con mayor prioridad y se borra de la fila 
                sigProceso = self._filaTurnos.pop(0)

                # Marcamos los datos debidos
                # NOTA: Al modificarlo aqui, en teoria se modifica tambien en _listaProcesos
                sigProceso.ejecutandose = indexCPU

                self._CPUs[indexCPU]["PID"] = sigProceso.PID
                self._CPUs[indexCPU]["desde"] = timestamp
            
            indexCPU += 1

