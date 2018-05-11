import string
from Base import Proceso, Command

def conditionToOrderProcess(proceso1, proceso2):
    if (proceso1.tiempoRestante < proceso2.tiempoRestante or 
        (proceso1.tiempoRestante == proceso2.tiempoRestante and
        proceso1.TIEMPO_LLEGADA < proceso2.TIEMPO_LLEGADA) or
        (proceso1.tiempoRestante == proceso2.tiempoRestante and
        proceso1.TIEMPO_LLEGADA == proceso2.TIEMPO_LLEGADA and
        proceso1.PID < proceso2.PID)):
        return -1
    elif (proceso1.tiempoRestante == proceso2.tiempoRestante and
        proceso1.TIEMPO_LLEGADA == proceso2.TIEMPO_LLEGADA and
        proceso1.PID == proceso2.PID):
        return 0 # Aunque este caso no puede pasar pues aqui esta
    else:
        return 1

def conditionToOrderCPUs(cpu1, cpu2):
    if (cpu1[1] < cpu2[1] or (cpu1[1] == cpu2[1] and cpu1[0] < cpu2[0])):
        return -1
    elif (cpu1[1] == cpu2[1] and cpu1[0] == cpu2[0]):
        return 0 # En teoria no deberia pasar
    else:
        return 1


class CPUSchedulerSJF:

    def __init__(self, cantCPU, quantum, CC):
        self._CANT_CPU = cantCPU
        self._QUANTUM = quantum
        self._CC = CC

        self._CPUs = [{"PID":-1, "desde":0} for _ in range(self._CANT_CPU)]

        self._lastTime = 0

        self._listaProcesos = []
        self._filaTurnos = []

        self._nextPID = 0

        self._procesosYaMuertosEImpresos = set()
        self._recienLlegados = []

    def parseNewCommand(self, command):
        print "VEAMOS=", command.command
        muere = False

        self.attendChanges(command.timestamp)
        self.limpiarMuertosYLlegadosPasados(command.timestamp) # El metodo utiliza el self._lastTime

        self._lastTime = command.timestamp

        if command.command == "QUANTUM":
            pass # Nothing
        elif command.command == "KILL":
            index = 0
            while (index < len(self._listaProcesos) and 
                self._listaProcesos[index].PID != int(command.params[0])) - 1: # - 1 porque los indices se guardan de 0 a n-1
                    index += 1

            if index == len(self._listaProcesos): #UPS no existe
                print "ERROR: PID NO ENCONTRADO"

            elif self._listaProcesos[index].terminado == -1: # Comprobamos que no estaba ya muerto
                # Marcamos en el proceso que ya termino con su tiempo de muerte
                self._listaProcesos[index].terminado = command.timestamp # Marcamos que ya acabo

                if self._listaProcesos[index].ejecutandose != -1:
                    # Marcamos al CPU si esque estaba siendo ejecutado, como libre
                    self._CPUs[self._listaProcesos[index].ejecutandose]["PID"] = -1 # En el CPU
                    self._listaProcesos[index].ejecutandose = -1 # En el proceso
                else:
                    #Eliminamos al proceso de la fila de prioridad
                    for i in range(len(self._filaTurnos)):
                        if self._filaTurnos[i].PID == int(command.params[0]) - 1:
                            self._filaTurnos.pop(i)
                            break

                # Lo borramos tambien si fue recien llegado
                if self._recienLlegados.count(self._listaProcesos[index]) > 0:
                    self._recienLlegados.remove(self._listaProcesos[index])

            else:
                print "Error: Este proceso ya estaba muerto"

        elif command.command == "CREATE":
            print "OLAAA"
            nuevoProceso = Proceso(self._nextPID, float(command.params[1]),
                command.timestamp)
            self._nextPID += 1

            self._listaProcesos.append(nuevoProceso)
            self._filaTurnos.append(nuevoProceso)

            self._filaTurnos = sorted(self._filaTurnos, 
                cmp=conditionToOrderProcess)

            self._recienLlegados.append(nuevoProceso)

        elif command.command == "TERMINA":
            # Se busca el proceso que termina i/o
            for proc in self._listaProcesos:
                if proc.PID == int(command.params[1]) - 1: # - 1 porque los indices se guardan de 0 a n-1
                    break

            if proc.PID != int(command.params[1]) - 1: # Ver si se encontro el proceso
                print "ERROR: NO EXISTE ESE PROCESO"

            elif proc.bloqueado == False:
                print "Error: Este proceso ya era libre"

            else:

                proc.bloqueado = False

                # Se agrega a la fila de turnos ordenadamente
                self._filaTurnos.append(proc)
                self._filaTurnos = sorted(self._filaTurnos, 
                    cmp=conditionToOrderProcess)

        elif command.command == "INICIA":
            # Se busca el proceso que lo inicia
            for proc in self._listaProcesos:
                if proc.PID == int(command.params[1]) - 1: # - 1 porque los indices se guardan de 0 a n-1
                    break

            if proc.PID != int(command.params[1]) - 1: # No existe el proceso indicado
                print "ERROR: NO EXISTE EL PROCESO"

            elif proc.bloqueado: 
                print "Error: Ya esta Bloqueado"

            else:

                # Se quita de los CPUs
                if proc.ejecutandose != -1:
                    self._CPUs[proc.ejecutandose]["PID"] = -1

                    proc.ejecutandose = -1
                    proc.bloqueado = True
                else:
                    ## Borrarlo tambien de la lista de prioridad, si es que puede no estar en el CPU
                    proc.bloqueado = True

                    # Se elimina de la fila de bloqueados... pues nose que otra cosa entonces
                    for i in range(len(self._filaTurnos)):
                        if self._filaTurnos[i].PID == proc.PID:
                            self._filaTurnos.pop(i)
                            break

        elif command.command == "END":
            muere = True
        else:
            print "ACHISACHIS"
            
        self.putNextProcessToRun(command.timestamp)

        self.imprimirIteracion()

        return muere


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


    ## Aqui NO se agrega ningun proceso que correra apenas en este tiempo
    def attendChanges(self, timestamp):

        cpusOrdenadas = []
        for indexCPU in range(self._CANT_CPU):
            if self._CPUs[indexCPU]["PID"] != -1: 
                print "ES STR:", type(self._listaProcesos[self._CPUs[indexCPU]["PID"]].tiempoRestante) ###############################
                cpusOrdenadas.append([indexCPU, 
                    self._lastTime + float(self._listaProcesos[self._CPUs[indexCPU]["PID"]].tiempoRestante)])
        cpusOrdenadas = sorted(cpusOrdenadas, cmp=conditionToOrderCPUs) # key=lambda tupla: tupla[1]

        seguimosSorteando = True
        while len(cpusOrdenadas) > 0:
            indexCPU = cpusOrdenadas[0][0]
            print "Y AHORA:",self._CPUs[indexCPU]["PID"]
            proceso = self._listaProcesos[self._CPUs[indexCPU]["PID"]]

            if cpusOrdenadas[0][1] > timestamp:
                proceso.tiempoRestante = cpusOrdenadas[0][1] - timestamp

                seguimosSorteando = False
            elif cpusOrdenadas[0][1] <= timestamp:
                # Dejamos en 0 el tiempoRestante
                proceso.tiempoRestante = 0

                # Marcamos al CPU como libre
                self._CPUs[indexCPU]["PID"] = -1 # En el CPU
                proceso.ejecutandose = -1 # En el proceso

                # Marcamos en el proceso que ya termino con su tiempo de muerte
                proceso.terminado = timestamp

                if cpusOrdenadas[0][1] == timestamp:
                    # No se agrega otro y por esto no se siguen ordenando porque se asume
                    # que no enviaran procesos de cputime=0 y se pondran sus procesos
                    # en putNextProcessToRun()
                    seguimosSorteando = False
                    
                else:
                    if len(self._filaTurnos) == 0:
                        seguimosSorteando = False
                    else:
                        # Agregamos el de mayor prioridad que siga
                        sigProceso = self._filaTurnos.pop(0)

                        # Marcamos los datos debidos
                        # NOTA: Al modificarlo aqui, en teoria se modifica tambien en _listaProcesos
                        sigProceso.ejecutandose = indexCPU

                        self._CPUs[indexCPU]["PID"] = sigProceso.PID
                        self._CPUs[indexCPU]["desde"] = cpusOrdenadas[0][1]

                        cpusOrdenadas.append([indexCPU, cpusOrdenadas[0][1] + sigProceso.tiempoRestante])

            cpusOrdenadas.pop(0)

            if seguimosSorteando:
                cpusOrdenadas = sorted(cpusOrdenadas, cmp=conditionToOrderCPUs)


    def limpiarMuertosYLlegadosPasados(self, timestamp):
        # Vemos si a estos no los hemos ya agregado a la lista negra
        if self._lastTime != timestamp:

            for proc in self._listaProcesos:
                if proc.terminado == self._lastTime:
                    self._procesosYaMuertosEImpresos.add(proc.PID)

            self._recienLlegados = []

    def imprimirIteracion(self):
        print "Timestamp: ", self._lastTime
        print "Llegadas: ", [int(proc.PID)+1 for proc in self._recienLlegados]
        print "Cola Listos: ", [int(proc.PID)+1 for proc in self._filaTurnos]
        for cpu in self._CPUs:
            if cpu["PID"] != -1:
                print "CPU: ", int(cpu["PID"])+1, self._listaProcesos[cpu["PID"]].tiempoRestante
            else:
                print "CPU: ", cpu["PID"]
        print "Bloqueados:"
        for proc in self._listaProcesos:
            if proc.bloqueado:
                print int(proc.PID)+1
        print "Terminado:"
        for proc in self._listaProcesos:
            if (proc.terminado != -1 and 
                proc.PID not in 
                self._procesosYaMuertosEImpresos):
                print int(proc.PID)+1
        print "Todos:"
        for proc in self._listaProcesos:
            print int(proc.PID)+1, proc.tiempoRestante

        print ""
        print ""