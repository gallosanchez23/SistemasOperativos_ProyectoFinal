import string
from Base import Proceso, Command, CPUScheduler, conditionToOrderProcess


def conditionToOrderCPUsOnSlowest(cpu1, cpu2):
    if (cpu1[1] > cpu2[1] or (cpu1[1] == cpu2[1] and cpu1[0] < cpu2[0])):
        return -1
    elif (cpu1[1] == cpu2[1] and cpu1[0] == cpu2[0]):
        return 0 # En teoria no deberia pasar
    else:
        return 1


class CPUSchedulerSRT(CPUScheduler):

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

        # Primero asignamos a los CPU vacios
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


        # Vamos a ver si alguno de los CPU ocupados por procesos es peor que los que
        # tenemos en la fila
        # Ordenamos los CPU con proceso poniendo los tiemposRestantes mayores primero
        cpusOrdenadas = []
        for i in range(len(self._CPUs)):
            if self._CPUs[i] != -1:
                cpusOrdenadas.append([i,
                    self._listaProcesos[self._CPUs[i]["PID"]].tiempoRestante])

        cpusOrdenadas = sorted(cpusOrdenadas, cmp=conditionToOrderCPUsOnSlowest)


        # Vamos agregando los procesos con mayor prioridad hasta que estos
        # ya sean peor que los peores CPU
        while (len(cpusOrdenadas) > 0 and len(self._filaTurnos) > 0):
            # Vemos si el proceso en la fila con mayor prioridad no tiene un tiempo
            # menor restante que el mas viable mejor de los CPU, nos salimos
            for proc in self._listaProcesos:
                if proc.PID == self._CPUs[cpusOrdenadas[0][0]]["PID"]:
                    break

            if self._filaTurnos[0].tiempoRestante >= proc.tiempoRestante:
                break

            # Se quita al proceso anterior y se vuelve a agregar a la fila
            self._filaTurnos.append(proc)

            proc.ejecutandose = -1

            #Se obtiene el proceso con mayor prioridad y se borra de la fila 
            sigProceso = self._filaTurnos.pop(0)

            # Marcamos los datos debidos
            # NOTA: Al modificarlo aqui, en teoria se modifica tambien en _listaProcesos
            sigProceso.ejecutandose = cpusOrdenadas[0][0]

            self._CPUs[cpusOrdenadas[0][0]]["PID"] = sigProceso.PID
            self._CPUs[cpusOrdenadas[0][0]]["desde"] = timestamp


            # Se ordena de nuevo la fila de procesos
            self._filaTurnos = sorted(self._filaTurnos, 
                cmp=conditionToOrderProcess)

            # Se quita este CPU de la lista ordenados
            cpusOrdenadas.pop(0)

