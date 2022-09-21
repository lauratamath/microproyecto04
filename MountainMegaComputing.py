import numpy as np
from colorama import Fore, Style

class Server():
    def __init__(self, potencia, max_sol = 2400, serviSist = 1):
        self.potencia = potencia #  cantidad de solicitudes por segundo que puede tomar 
        self.lambda_max = max_sol  # cantidad máxima de solicitudes que se recibirán (lambda)/ minuto 
        self.serviSist = serviSist # cantidad de servidores que tiene el sistema 
    
    def next_ts(self, t): # No hace gran cosa, pero existe porque los eventos serán procesos de poisson homogeneos
        return t - (np.log(np.random.uniform())/self.lambda_max)

    def get_exponential(self, lamda):
        return -(1 / lamda)*np.log(np.random.uniform())

    def simulate(self):
        t = 0 
        n = 0 # estado del sistema, numero de solicitudes en t
        T = 60 # T = t0 + 60min 

        # contadores
        Na = 0 # llegadas 

        i_llegada = [] # tiempos de llegada de la i-esima solicitud, ids son indices
        i_salida = [] # tiempos de salida de la i-esima solicitud, ids son indices
        cliente_TE = [] # Tiempos de cada cliente en espera

        # eventos
        prox_llegada = self.next_ts(t) # tiempo de la proxima llegada
        setTiempo = np.zeros(self.serviSist) + np.infty # set de tiempos de salida de cada servidor, hay un setTiempo por cada server disponible
        tiempoOcupado = np.zeros(self.serviSist) # tiempo que cada server estuvo ocupado
        servidorNo = [] # se guardan cuales solicitudes fueron atendidas por cuales server
        servidores = np.zeros(self.serviSist) # para llevar registro de cual está ocupado

        while t < T: # Mientras no acceda el tiempo de cierre
            if prox_llegada <= min(setTiempo):
                # si el proximo tiempo de llegada es antes del proximo tiempo de salida, se encola
                t = prox_llegada 
                Na += 1 
                prox_llegada = self.next_ts(t) # siguiente tiempo de llegada
                i_llegada.append(t)
                if n < self.serviSist: # si hay menos clientes dentro que servidores, se le asigna uno que esté disponible
                    for i in range(self.serviSist):
                        if servidores[i] == 0: 
                            cliente_TE = np.append(cliente_TE,t - i_llegada[len(i_llegada)-1])
                            servidorNo.append(i)
                            setTiempo[i] = t + np.random.exponential(1/(self.potencia*60)) 
                            tiempoOcupado[i] += setTiempo[i]-t 
                            servidores[i] = 1 
                            break;
                n += 1 # Se agrefa al nuevo cliente en el sistema
            
            else:
                # si el proximo tiempo de llegada es después del próximo tiempo de salida, se atiende ya que
                servidorPED = np.argmin(setTiempo) 
                t = setTiempo[servidorPED] 
                i_salida.append(t)
                if n <= self.serviSist: # Si hay menos o igual cantidad de clientes que servidores
                    servidores[servidorPED] = 0
                    setTiempo[servidorPED] = np.infty
                else: # Hay mas clientes por atender
                    servidorNo.append(servidorPED) 
                    cliente_TE = np.append(cliente_TE,t - i_llegada[len(i_llegada)-1])
                    setTiempo[servidorPED] = t + np.random.exponential(1/(self.potencia*60)) 
                    tiempoOcupado[servidorPED] += setTiempo[servidorPED]-t
                    servidores[i] = 1 
                n -= 1 # Descontamos al cliente atendido del sistema
                
        # se calcula cuantas solicitudes atendio cada servidor 
        numSolicitudes = np.zeros(self.serviSist)
        for i in range(len(servidorNo)):
            numSolicitudes[servidorNo[i]] += 1

        return { 
            "en_cola": cliente_TE, "numSolicitudes": numSolicitudes, "setTiempo": setTiempo, "i_llegada": i_llegada, "i_salida": i_salida, "tiempoOcupado": tiempoOcupado
        }

## Mountain Mega Computing
mountain = Server(potencia = 100)
resultados = mountain.simulate()
print(Fore.GREEN + ">>>>>>>  2400 solicitudes máximas" + Style.RESET_ALL)
print("1. ¿Cuántas solicitudes atendió cada servidor?")
print(resultados["numSolicitudes"][0])
print("\n2. ¿Cuánto tiempo estuvo cada servidor ocupado?")
print(resultados["tiempoOcupado"][0])
print("\n3. ¿Cuánto tiempo estuvo cada servidor desocupado (idle)?")
print(np.maximum(np.ones(mountain.serviSist)*60 - resultados["tiempoOcupado"],0)[0])
print("\n4. Cuánto tiempo en total estuvieron las solicitudes en cola?")
print(np.round(sum(resultados["en_cola"]),5))
print("\n5. En promedio ¿cuánto tiempo estuvo cada solicitud en cola?")
print(np.round(np.mean(resultados["en_cola"]),5))
print("\n6. En promedio, ¿cuántas solicitudes estuvieron en cola cada segundo?")
sol_psec = [ 1/num if num != 0 else 0 for num in resultados["en_cola"] ]
print(np.round(np.mean(sol_psec),5))
print("\n7. ¿Cuál es el momento de la salida de la última solicitud?")
print(np.round(resultados["setTiempo"][-1],5), "min") 

print(Fore.GREEN + ">>>>>>>  6000 solicitudes máximas" + Style.RESET_ALL)
mountain = Server(potencia = 100, max_sol = 6000)
resultados_g2 = mountain.simulate()
print("1. ¿Cuántas solicitudes atendió cada servidor?")
print(resultados_g2["numSolicitudes"][0])
print("\n2. ¿Cuánto tiempo estuvo cada servidor ocupado?")
print(resultados_g2["tiempoOcupado"][0])
print("\n3. ¿Cuánto tiempo estuvo cada servidor desocupado (idle)?")
print(np.maximum(np.ones(mountain.serviSist)*60 - resultados_g2["tiempoOcupado"],0)[0])
print("\n4. Cuánto tiempo en total estuvieron las solicitudes en cola?")
print(np.round(sum(resultados_g2["en_cola"]),5))
print("\n5. En promedio ¿cuánto tiempo estuvo cada solicitud en cola?")
print(np.round(np.mean(resultados_g2["en_cola"]),5))
print("\n6. En promedio, ¿cuántas solicitudes estuvieron en cola cada segundo?")
sol_psec = [ 1/num if num != 0 else 0 for num in resultados_g2["en_cola"] ]
print(np.round(np.mean(sol_psec),5))
print("\n7. ¿Cuál es el momento de la salida de la última solicitud?")
print(np.round(resultados_g2["setTiempo"][-1],5), "min") 
