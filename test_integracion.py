import pytest
import socket
import threading
import time
import select

HOST = '127.0.0.1'  # Dirección del host del servidor
PORT = 55559  # Puerto para la comunicación del servidor

class ClientThread(threading.Thread):
    """
    Representa un cliente en el sistema de chat, que se ejecuta en un subproceso separado.
    Cada cliente se conecta al servidor, envía y recibe mensajes.
    """
    def __init__(self, nickname, event):
        super().__init__()
        self.nickname = nickname  # Apodo del cliente
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creación del socket para la comunicación
        self.received_messages = []  # Lista para almacenar los mensajes recibidos por el cliente
        self.running = True  # Bandera para controlar el estado de ejecución del cliente
        self.event = event  # Evento utilizado para sincronizar cuando el cliente está listo

    def run(self):
        """Bucle principal donde el cliente se conecta al servidor y escucha mensajes entrantes."""
        try:
            # Conectarse al servidor
            self.client.connect((HOST, PORT))
            # Esperar a que el servidor solicite un apodo
            self.client.recv(1024)  # Recibir el aviso 'NICK'
            # Enviar el apodo al servidor
            self.client.send(self.nickname.encode('utf-8'))
            # Señalar que el cliente está listo para recibir mensajes
            self.event.set()

            # Seguir ejecutándose y escuchando mensajes entrantes
            while self.running:
                # Usar select para verificar mensajes legibles (sin bloqueo)
                readable, writable, exceptional = select.select([self.client], [], [], 1)
                if readable:
                    # Recibir y decodificar el mensaje
                    message = self.client.recv(1024).decode('utf-8')
                    if message:
                        # Añadir el mensaje recibido a la lista
                        self.received_messages.append(message)

        except OSError:
            # Si ocurre un error (por ejemplo, la conexión está cerrada), detener el cliente
            pass

    def send_message(self, message):
        """Envía un mensaje al servidor."""
        try:
            # Enviar el mensaje al servidor
            self.client.send(message.encode('utf-8'))
        except socket.error:
            # Manejar errores de socket (por ejemplo, servidor no alcanzable)
            pass

    def stop(self):
        """Detiene el cliente y cierra la conexión."""
        self.running = False
        self.client.close()

@pytest.fixture
def multiple_clients():
    """
    Fixture para iniciar múltiples clientes para pruebas.
    Inicializa múltiples instancias de `ClientThread` y sincroniza su inicio.
    """
    event = threading.Event()  # Crear un evento de subproceso para sincronización
    clients = [ClientThread(f"Client{i}", event) for i in range(3)]  # Crear 3 clientes con diferentes apodos
    for client in clients:
        client.start()  # Iniciar cada cliente en un subproceso separado

    # Esperar hasta que todos los clientes estén conectados y listos
    event.wait()  # Asegurar que todos los clientes están conectados al servidor

    yield clients  # Proporcionar los clientes a la prueba
    for client in clients:
        # Detener cada cliente después de que la prueba haya terminado
        client.stop()
        client.join()  # Esperar a que finalice cada subproceso de cliente

# Prueba con sincronización usando Event
def test_message_distribution(multiple_clients):
    """
    Verifica que cuando un cliente envía un mensaje, los otros clientes lo reciban.
    Esto asegura la distribución correcta de mensajes en el sistema de chat.
    """
    clients = multiple_clients

    # Crear eventos para sincronización para que los clientes estén listos al mismo tiempo
    events = [client.event for client in clients]
    for event in events:
        event.wait()  # Esperar hasta que todos los clientes estén listos

    # Cliente 0 envía un mensaje
    test_message = "Hello from Client0"
    clients[0].send_message(test_message)
    time.sleep(1)  # Esperar un breve momento para que los clientes reciban el mensaje

    # Verificar si los otros clientes recibieron el mensaje
    for i, client in enumerate(clients[1:], start=1):
        assert any(test_message in msg for msg in client.received_messages), f"Client{i} did not receive the message."

def test_simultaneous_messaging(multiple_clients):
    """
    Prueba que múltiples clientes pueden enviar mensajes simultáneamente,
    y que reciben correctamente los mensajes de los demás (pero no los suyos).
    """
    clients = multiple_clients
    messages = [f"Message from {client.nickname}" for client in clients]  # Preparar mensajes para cada cliente

    # Crear eventos para sincronización para asegurar que todos los clientes estén listos para enviar mensajes
    events = [client.event for client in clients]

    # Esperar a que todos los clientes estén listos
    for event in events:
        event.wait()

    # Enviar mensajes desde todos los clientes simultáneamente
    for i, client in enumerate(clients):
        client.send_message(messages[i])

    # Dar tiempo a los clientes para recibir mensajes
    time.sleep(3)

    # Verificar que cada cliente reciba mensajes de otros, pero no el suyo
    for i, client in enumerate(clients):
        for j, message in enumerate(messages):
            if i != j:  # El cliente no debe recibir su propio mensaje
                assert any(message in msg for msg in client.received_messages), f"{client.nickname} did not receive {messages[j]}"

    # Asegurar que cada cliente no reciba su propio mensaje
    for i, client in enumerate(clients):
        own_message = messages[i]
        assert all(own_message not in msg for msg in client.received_messages), f"{client.nickname} received its own message."

def test_unexpected_disconnection(multiple_clients):
    """
    Simula la desconexión inesperada de un cliente y verifica que los otros clientes
    puedan seguir comunicándose sin errores.
    """
    clients = multiple_clients

    # Desconectar el cliente 0 para simular una desconexión inesperada
    clients[0].stop()
    time.sleep(5)  # Dar tiempo al servidor para procesar la desconexión

    # Verificar que los clientes restantes puedan seguir enviando y recibiendo mensajes
    test_message = "Message after Client0 disconnect"
    clients[1].send_message(test_message)

    time.sleep(1)  # Dar tiempo a los clientes para recibir el mensaje
    for i, client in enumerate(clients[2:], start=2):
        assert any(test_message in msg for msg in client.received_messages), f"Client{i} did not receive the message after the disconnection."