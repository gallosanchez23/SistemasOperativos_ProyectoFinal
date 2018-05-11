import string

class Process:

	def __init__(self, process_id, cpu_time, arrival_time, priority = 0):
		self.id = process_id		# rango de 0 a n-1
		self.priority = priority		# prioridad del proceso
		self.cpu_time = cpu_time		# tiempo que tarda el proceso en terminar
		self.remaining_time = cpu_time		# tiempo que falta para terminar
		self.arrival_time = arrival_time		# tiempo en el que llega el proceso

		self.locked = False
		self.end_time = -1
		self.current_cpu = -1



class Command:

	def __init__(self, str_command):
		self.error = False

		self.params = []
		self.command = ''
		self.current_timestamp = -1

		# extrae timestamp del str_command
		i = 0
		j = string.find(str_command, ' ')
		if j <= 0:
			self.error = True
			return

		self.current_timestamp = float(str_command[i : j])
		print "Current Timestamp: ", self.current_timestamp

		str_command = str_command[j + 1 :]

		# extrae el comando del str_command
		i = 0
		j = string.find(str_command, ' ')
		if j == -1:
			j = len(str_command)

		if j <= 0:
			self.error = True
			return

		self.command = string.upper(str_command[i : j])
		print "Command: ", self.command

		str_command = str_command[j + 1 :]

		# extrae el resto de los parametros
		if len(str_command) > 0:
			self.params = [string.upper(a) for a in str_command.split(' ')]
		print "Params: ", self.params



def sort_process_queue_condition(process_1, process_2):
	process_id_1 = process_1.id
	process_id_2 = process_2.id
	arrival_time_1 = process_1.arrival_time
	arrival_time_2 = process_2.arrival_time
	remaining_time_1 = process_1.remaining_time
	remaining_time_2 = process_2.remaining_time
	if remaining_time_1 < remaining_time_2 or (remaining_time_1 == remaining_time_2 and arrival_time_1 < arrival_time_2) or (remaining_time_1 == remaining_time_2 and arrival_time_1 == arrival_time_2 and process_id_1 < process_id_2):
		return -1

	elif remaining_time_1 == remaining_time_2 and arrival_time_1 == arrival_time_2 and process_id_1 == process_id_2:
		return 0

	else:
		return 1



def sort_cpus_list_condition(cpu_1, cpu_2):
  if (cpu_1[1] < cpu_2[1] or (cpu_1[1] == cpu_2[1] and cpu_1[0] < cpu_2[0])):
    return -1

  elif (cpu_1[1] == cpu_2[1] and cpu_1[0] == cpu_2[0]):
    return 0

  else:
    return 1



class CPUScheduler:

	def __init__(self, quantity_cpus, quantum, cc):
		self.cc = cc
		self.quantum = quantum
		self.quantity_cpus = quantity_cpus

		self.cpu_list = [{'current_process_id': -1, 'start_timestamp': 0} for _ in range(self.quantity_cpus)]
		self.last_timestamp = 0
		self.process_queue = []
		self.process_list = []

		self.next_process_id = 0
		self.arriving_processes = []
		self.finished_and_killed_processes = set()


	def execute_command(self, command):
		if not command.error:

			if self.last_timestamp != command.current_timestamp:
				self.arriving_processes = []
				self.imprimir_resumen()

			self.updates_remaining_times(command.current_timestamp)

			
			self.last_timestamp = command.current_timestamp

			# Posibles mensajes:

			# <timestamp> CREATE CPUTIME n
			# <timestamp> QUANTUM
			# <timestamp> INICIA I/O <PID>
			# <timestamp> TERMINA I/O <PID>
			# <timestamp> KILL <PID>
			# <timestamp> END

			if command.command == 'CREATE':
				self.execute_create_command(command.current_timestamp, command.params[1])

			elif command.command == 'QUANTUM':
				pass

			elif command.command == 'INICIA':
				self.execute_begin_io_command(command.params[1])

			elif command.command == 'TERMINA':
				self.execute_finish_io_command(command.params[1])

			elif command.command == 'KILL':
				self.execute_kill_process_command(command.params[0])

			elif command.command == 'END':
				self.execute_end_server_command()
			else:
				print 'Accion no permitida'

			self.locate_pending_processes_using_SJF()


	def execute_create_command(self, current_timestamp, cpu_time):
		new_process = Process(self.next_process_id,
													float(cpu_time),
													current_timestamp)

		self.next_process_id += 1
		self.process_list.append(new_process)
		self.process_queue.append(new_process)
		self.arriving_processes.append(new_process)

		self.process_queue = sorted(self.process_queue, cmp = sort_process_queue_condition)


	def execute_begin_io_command(self, process_id):
		# buscar si el proceso existe
		existing_process = False
		for index in range(len(self.process_list)):
			if self.process_list[index].id == int(process_id) - 1:
				existing_process = True
				break

		# si no existe
		if not existing_process:
			print 'El proceso', process_id, 'no existe'

		# si ya esta bloqueado
		elif self.process_list[index].locked:
			print 'El proceso', process_id, 'ya esta bloqueado'

		# si existe y no esta bloqueado
		else:
			# si el proceso esta en cpu, lo quita
			if self.process_list[index].current_cpu != -1:
				self.cpu_list[self.process_list[index].current_cpu]['current_process_id'] = -1
				self.process_list[index].current_cpu = -1

			# si el proceso esta en lista de espera, lo quita
			else:
				for x in range(len(self.process_queue)):
					if self.process_queue[x].id == int(process_id) - 1:
						self.process_queue.pop(x)
						break

			# bloquea el proceso
			self.process_list[index].locked = True


	def execute_finish_io_command(self, process_id):
		# busca si el proceso existe
		existing_process = False
		for index in range(len(self.process_list)):
			if self.process_list[index].id == int(process_id) - 1:
				existing_process = True
				break

		# si no existe
		if not existing_process:
			print 'El proceso', process_id, 'no existe'

		# si no esta bloqueado
		elif not self.process_list[index].locked:
			print 'El proceso', process_id, 'no esta bloqueado'

		# si existe y esta bloqueado
		else:
			self.process_list[index].locked = False
			self.process_queue.append(self.process_list[index])
			self.process_queue = sorted(self.process_queue, cmp = sort_process_queue_condition)


	def execute_kill_process_command(self, process_id):
		# busca si el proceso existe
		existing_process = False
		for index in range(len(self.process_list)):
			if self.process_list[index].id == int(process_id) - 1:
				existing_process = True
				break

		# si no existe
		if not existing_process:
			print 'El proceso', process_id, 'no existe'

		# si existe pero esta completo
		elif self.process_list[index].end_time != -1:
			print 'El proceso', process_id, 'ya ha sido completado'

		# si existe y no esta completo
		else:
			# si el proceso esta en cpu, lo quita
			if self.process_list[index].current_cpu != -1:
				self.cpu_list[self.process_list[index].current_cpu]['current_process_id'] = -1

			# si el proceso esta en lista de espera, lo quita
			else:
				for x in range(len(self.process_queue)):
					if self.process_queue[x].id == int(process_id) - 1:
						self.process_queue.pop(x)
						break

			for x in range(len(self.arriving_processes)):
				if self.arriving_processes[x].id == int(process_id) - 1:
					self.arriving_processes.pop(x)
					break

			# marca el proceso como terminado
			self.process_list[index].end_time = self.last_timestamp
			self.process_list[index].current_cpu = -1


	def execute_end_server_command(self):
		for index in range(len(self.process_list)):
			self.execute_kill_process_command(self.process_list[index].id)

		print 'Termina servidor'


	def updates_remaining_times(self, current_timestamp):
		current_cpus = []
		# para cada cpu
		for i in range(self.quantity_cpus):
			# si se esta corriendo un proceso
			if self.cpu_list[i]['current_process_id'] != -1:
				# guardar en el arreglo
				current_cpus.append([i, self.last_timestamp + float(self.process_list[self.cpu_list[i]['current_process_id']].remaining_time)])

		current_cpus = sorted(current_cpus, cmp = sort_cpus_list_condition)
		sort_cpus_list = True

		while len(current_cpus) > 0:
			cpu_index = current_cpus[0][0]
			expected_ending_timestamp = current_cpus[0][1]
			process_index = int(self.process_list[self.cpu_list[cpu_index]['current_process_id']].id)

			# si no se ha terminado el proceso
			if expected_ending_timestamp > current_timestamp:
				# se ajusta el tiempo restante del proceso
				self.process_list[process_index].remaining_time = expected_ending_timestamp - current_timestamp
				sort_cpus_list = False

			# si ya se termino el proceso
			elif expected_ending_timestamp < current_timestamp:
				# se establece el tiempo restante como 0 y el tiempo de termino
				self.process_list[process_index].end_time = expected_ending_timestamp
				self.process_list[process_index].current_cpu = -1
				self.process_list[process_index].remaining_time = 0

				self.finished_and_killed_processes.add(self.process_list[process_index].id)

				# se elimina el proceso del cpu
				self.cpu_list[cpu_index]['current_process_id'] = -1

				# si no hay mas procesos en la lista de espera
				if len(self.process_queue) == 0:
					sort_cpus_list = False

				# si si hay mas procesos en la lista de espera
				else:
					# obtiene el siguiente proceso por ejecutar
					next_process = self.process_queue.pop(0)

					# modificar referencia al cpu en el que se ejecuta
					self.process_list[next_process.id].current_cpu = cpu_index
					self.cpu_list[cpu_index]['current_process_id'] = next_process.id

					current_cpus.append([cpu_index, expected_ending_timestamp + float(self.process_list[next_process.id].remaining_time)])

			# si se termina el proceso en el timestamp actual
			elif expected_ending_timestamp == current_timestamp:
				# se establece el tiempo restante como 0 y el tiempo de termino
				self.process_list[process_index].end_time = expected_ending_timestamp
				self.process_list[process_index].current_cpu = -1
				self.process_list[process_index].remaining_time = 0

				self.finished_and_killed_processes.add(self.process_list[process_index].id)

				# se elimina el proceso del cpu
				self.cpu_list[cpu_index]['current_process_id'] = -1

			current_cpus.pop(0)
			if sort_cpus_list:
				current_cpus = sorted(current_cpus, cmp = sort_cpus_list_condition)



	def locate_pending_processes_using_SJF(self):
		if len(self.process_queue) == 0:
			return

		cpu_index = 0
		while cpu_index < self.quantity_cpus and len(self.process_queue) > 0:
			if self.cpu_list[cpu_index]['current_process_id'] == -1:
				next_process = self.process_queue.pop(0)

				self.process_list[next_process.id].current_cpu = cpu_index

				self.cpu_list[cpu_index]['current_process_id'] = next_process.id

			cpu_index += 1


	def imprimir_resumen(self):
		print '-----------------------------------------------------------------'
		print 'Timestamp:', self.last_timestamp
		print ' '
		print 'Todos los procesos creados:'
		for proceso in self.process_list:
			print 'Proceso:', int(proceso.id) + 1
			print 'Cpu time:', proceso.cpu_time
			print 'Remaining time:', proceso.remaining_time
			print 'Arrival time:', proceso.arrival_time
			print 'locked:', proceso.locked
			print 'End time:', proceso.end_time
			print 'Current CPU:', proceso.current_cpu
			print ' '

		print ' '
		print 'Fila de espera priorizada (cola de listos):'
		for proceso in self.process_queue:
			print 'Proceso:', int(proceso.id) + 1

		print ' '
		print 'Procesos bloqueados:'
		for proceso in self.process_list:
			if proceso.locked:
				print 'Proceso:', int(proceso.id) + 1

		print ' '
		print 'Procesos terminados:'
		for id_proceso in self.finished_and_killed_processes:
			print 'Proceso:', int(id_proceso) + 1

		print ' '
		print 'Proceso en CPU 1:'
		print 'Proceso:', int(self.cpu_list[0]['current_process_id']) + 1