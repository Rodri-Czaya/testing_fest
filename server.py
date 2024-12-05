import socket
import select
import time

# Configurar las direcciones
HOST = '127.0.0.1'  # localhost
PORT = 55559 

# Definir el tipo de conexión y protocolo
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# Configurar el host y puerto para ser reutilizables
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Aplicar configuraciones al servidor e iniciarlo
server.bind((HOST, PORT))
server.listen(100)

# Crear listas para clientes/nicknames
clients = [server]
nicknames = {}

# Función para eliminar y desconectar clientes
def remove(client):
    if client in clients:
        clients.remove(client)
    if client in nicknames:
        print(f"Cliente {nicknames[client]} ha desconectado")
        del nicknames[client]
    client.close()

# Difundir mensajes a todos los clientes (anuncio)
def broadcast(message, sender=None):
    # Lista de clientes problemáticos
    clients_to_remove = []
    
    for client in clients:
        if client != sender and client != server:
            
            # Intentar enviar un mensaje
            for attempt in range(3):
                try:
                    print(f"Intentando enviar mensaje: {message}")
                    client.send(message)
                    break
                
                except socket.error as error:
                    print(f"Error enviando mensaje a un cliente: {error}\n        Reintentando: {attempt+1}...")
                    time.sleep(1)  # Esperar antes de reintentar
            
            # Si después de 3 intentos aún no funciona
            else:
                clients_to_remove.append(client)
    
    # Eliminar clientes problemáticos
    for client in clients_to_remove:
        remove(client)
        broadcast(f"{nicknames.get(client, 'Desconocido')} salió del chat.".encode('utf-8'))

# Manejar recepción y transmisión de mensajes de un cliente
def handle(client):
    for attempt in range(3):
        
        # Intentar recibir un mensaje
        try:
            message = client.recv(1024)
            if message:
                print(f"mensaje recibido intentando difundir: {message}")
                broadcast(message, client)
                return True
            
            else:
                # Cliente salió limpiamente
                broadcast(f"{nicknames.get(client, 'Desconocido')} salió del chat.".encode('utf-8'))
                return False
            
        except socket.error as error:
            print(f"Error recibiendo datos de un cliente: {error}\n        Reintentando: {attempt+1}...")
            time.sleep(1)
            
    return False

# Aceptar nuevas conexiones
def accept(server):
    client, address = server.accept()
    print(f"Dirección {str(address)} conectada")

    # Solicitar el nickname del cliente
    client.send('NICK'.encode('utf-8'))
    nickname = client.recv(1024).decode('utf-8')
    nicknames[client] = nickname
    clients.append(client)

    # Anunciar la nueva conexión
    print(f"El nickname del cliente es '{nickname}'.")
    broadcast(f"{nickname} se unió al chat".encode('utf-8'), client)

if __name__ == "__main__":

    print(f"-> Servidor escuchando en {HOST}:{PORT}")


    while True:
        
        # Usar select para monitorear sockets
        read_sockets, write_sockets, exception_sockets = select.select(clients, [], clients)  # lectura, escritura, excepciones (error)

        # Para cada socket listo para leer
        for sock in read_sockets:

            if sock == server:
                accept(server)
            
            else:
                # Intentar recibir/transmitir
                if not handle(sock):
                    remove(sock)
        
        # Para cada socket con errores
        for sock in exception_sockets:
            remove(sock)