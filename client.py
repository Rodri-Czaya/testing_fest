import socket
import threading
import sys


# Lista de nicknames prohibidos
BANNED_NICKS = ["admin", "moderator", "system", "root"]

def nickname_checker():
    """
    Solicita al usuario que elija un nickname válido.
    Asegura que el nickname no esté en la lista prohibida.
    """
    print(f"Nicknames prohibidos: {', '.join(BANNED_NICKS)}")

    for i in range(3):
        nick = input("Escoge tu nickname: ").strip()
        
        # Comprueba si el nickname está vacío o está prohibido
        if nick == "":
            print("El nickname no puede estar vacío.")
        elif nick.lower() in BANNED_NICKS:
            print(f"El nickname '{nick}' no está permitido. Por favor, elige un nickname diferente.")
        else:
            return nick  # Devuelve nickname válido
    
    # Si el usuario no logra elegir un nickname válido, sale del programa
    print("No se pudo elegir un nickname válido. Cerrando el programa...")
    sys.exit(0)


# Función para recibir mensajes
def receive():
    while True:
        # Intenta recibir mensajes del servidor
        try:
            message = client.recv(1024).decode('utf-8')
            if message == 'NICK':  # Si el servidor solicita nuestro nickname
                client.send(nickname.encode('utf-8'))
            else:
                print(message)
        # Si hubo un error al recibir mensajes, cierra la conexión
        except:
            print("¡Ocurrió un error!")
            client.close()
            break

# Función para enviar mensajes
def write():
    while True:
        message = f'{nickname}: {input("")}'
        client.send(message.encode('utf-8'))
        
if __name__ == "__main__":

    nick = input("Introduce tu nickname: ")

    nickname = nickname_checker(nick)

    # Conectar al servidor
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(('127.0.0.1', 55555))
        print("Conectado al servidor")
        
    # Si hubo un error de conexión
    except ConnectionRefusedError:
        print("No se pudo conectar al servidor. Asegúrate de que el servidor esté en línea")
        exit()

    # Crear hilos para las funciones de recibir y escribir
    receive_thread = threading.Thread(target=receive)
    receive_thread.start()

    write_thread = threading.Thread(target=write)
    write_thread.start()