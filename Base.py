import string

class Proceso:

    def __init__(self, PID, CPUTime, tiempoLlegada, prioridad = 0):
        self.PID = PID # Se manejan de 0 a n-1
        self.tiempoRestante = CPUTime
        self.TIEMPO_LLEGADA = tiempoLlegada
        self.PRIORIDAD = prioridad
        self.CPU_TIME = CPUTime

        self.bloqueado = False
        self.terminado = -1 # Marca en cual timestamp termino
        self.ejecutandose = -1 # Marca en que cpu esta

class Command:

    def __init__(self, strCommand):
        self.error = False

        self.timestamp = -1
        self.command = ""
        self.params = [] # NOTA: Los parametros se guardaran como STRING!

        inicio = 0
        end = string.find(strCommand, " ")
        if end <= 0:
            self.error = True
            return
        
        self.timestamp = float(strCommand[inicio:end])
        print "TIMESTAMP=", self.timestamp

        strCommand = strCommand[end + 1:]

        inicio = 0
        end = string.find(strCommand, " ")
        if end == -1:
            end = len(strCommand)

        if end <= 0:
            self.error = True
            return

        self.command = string.upper(strCommand[inicio:end])
        print "COMMAND=", self.command

        strCommand = strCommand[end + 1:]

        if len(strCommand) > 0:
            self.params = [string.upper(a) for a in strCommand.split(" ")]
        print "PARAMS=", self.params




        
        