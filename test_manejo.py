import pytest
import socket
from unittest.mock import Mock, patch
from server import handle

# Fixture para configurar un cliente simulado 
@pytest.fixture
def setup_clients_and_nicknames():
    """
    Fixture para configurar un cliente simulado con un método 'recv' simulado para simular la recepción de datos.
    Este cliente simulado se utilizará en los casos de prueba para simular la comunicación entre el servidor y el cliente.
    """
    client = Mock()  # Crear un cliente simulado
    client.recv = Mock()  # Simular el método 'recv' para simular la recepción de datos del cliente
    return client  # Devolver el cliente simulado para usar en las pruebas

# Prueba 1: Caso óptimo - el cliente envía un mensaje válido
@patch('server.nicknames', new_callable=dict)
@patch('server.clients', new_callable=list)
@patch('server.broadcast')
def test_handle_optimal(mock_broadcast, mock_clients, mock_nicknames, setup_clients_and_nicknames):
    """
    Caso de prueba donde el cliente envía un mensaje válido. El mensaje debe ser difundido a todos los demás clientes.
    La función debe devolver True en este caso óptimo.
    """
    client = setup_clients_and_nicknames  # Configurar un cliente simulado usando la fixture
    mock_clients.append(client)  # Añadir el cliente simulado a la lista de clientes
    mock_nicknames[client] = "UsuarioPrueba"  # Añadir un nickname para el cliente simulado
    
    # Simular el cliente enviando un mensaje válido
    client.recv.return_value = b'Hola, mundo!'  # Simular la recepción de un mensaje del cliente en bytes
    
    # Llamar a la función handle con el cliente simulado
    result = handle(client)  # La función handle procesa el mensaje
    
    # Aserciones para verificar el comportamiento esperado
    mock_broadcast.assert_called_once_with(b'Hola, mundo!', client)  # Asegurar que la función broadcast es llamada con el mensaje correcto
    assert result is True  # Asegurar que la función handle devuelve True (indicando una operación exitosa)

# Prueba 2: Cliente sale limpiamente
@patch('server.nicknames', new_callable=dict)  # Simular el diccionario 'nicknames' en el módulo del servidor
@patch('server.clients', new_callable=list)  # Simular la lista 'clients' en el módulo del servidor
@patch('server.broadcast')  # Simular la función 'broadcast' en el módulo del servidor
def test_handle_client_exit(mock_broadcast, mock_clients, mock_nicknames, setup_clients_and_nicknames):
    """
    Caso de prueba donde el cliente se desconecta (envía un mensaje vacío). Esto simula una salida limpia.
    La función debe difundir un mensaje indicando que el cliente ha salido del chat.
    """
    client = setup_clients_and_nicknames  # Configurar un cliente simulado usando la fixture
    mock_clients.append(client)  # Añadir el cliente simulado a la lista de clientes
    mock_nicknames[client] = "UsuarioPrueba"  # Añadir un nickname para el cliente simulado
    
    # Simular que el cliente no envía ningún mensaje (desconexión)
    client.recv.return_value = b''  # Simular un mensaje vacío indicando la salida del cliente
    
    # Llamar a la función handle
    result = handle(client)  # La función handle debe manejar la desconexión
    
    # Aserciones para verificar el comportamiento esperado
    mock_broadcast.assert_called_once_with("UsuarioPrueba salió del chat.".encode('utf-8'))  # Asegurar que se difunde el mensaje de salida
    assert result is False  # La función debe devolver False cuando el cliente sale limpiamente

# Prueba 3: Cliente encuentra un error de socket
@patch('server.nicknames', new_callable=dict)  # Simular el diccionario 'nicknames' en el módulo del servidor
@patch('server.clients', new_callable=list)  # Simular la lista 'clients' en el módulo del servidor
@patch('server.broadcast')  # Simular la función 'broadcast' en el módulo del servidor
def test_handle_socket_error(mock_broadcast, mock_clients, mock_nicknames, setup_clients_and_nicknames):
    """
    Caso de prueba donde el cliente encuentra un error de socket al recibir datos.
    La función no debe difundir ningún mensaje y debe devolver False debido al error.
    """
    client = setup_clients_and_nicknames  # Configurar un cliente simulado usando la fixture
    mock_clients.append(client)  # Añadir el cliente simulado a la lista de clientes
    mock_nicknames[client] = "UsuarioPrueba"  # Añadir un nickname para el cliente simulado
    
    # Simular un error de socket durante la recepción de datos
    client.recv.side_effect = socket.error("Error de socket durante recv")  # Provocar un error de socket al intentar recv
    
    # Llamar a la función handle
    result = handle(client)  # La función handle debe manejar el error
    
    # Aserciones para verificar el comportamiento esperado
    mock_broadcast.assert_not_called()  # Asegurar que no se difunde nada cuando hay un error de socket
    assert result is False  # La función debe devolver False debido al error de socket

# Prueba 4: Cliente envía un mensaje demasiado largo
@patch('server.nicknames', new_callable=dict)  # Simular el diccionario 'nicknames' en el módulo del servidor
@patch('server.clients', new_callable=list)  # Simular la lista 'clients' en el módulo del servidor
@patch('server.broadcast')  # Simular la función 'broadcast' en el módulo del servidor
def test_handle_long_message(mock_broadcast, mock_clients, mock_nicknames, setup_clients_and_nicknames):
    """
    Caso de prueba donde el cliente envía un mensaje demasiado largo (p. ej., más largo que el tamaño permitido).
    La función no debe difundir el mensaje y debe devolver False.
    """
    client = setup_clients_and_nicknames  # Configurar un cliente simulado usando la fixture
    mock_clients.append(client)  # Añadir el cliente simulado a la lista de clientes
    mock_nicknames[client] = "UsuarioPrueba"  # Añadir un nickname para el cliente simulado
    
    # Simular el cliente enviando un mensaje que excede la longitud permitida (p. ej., más de 2048 bytes)
    long_message = b'LOL' * 2048  # Simular un mensaje más largo de 1024 bytes (límite)
    client.recv.return_value = long_message  # Simular la recepción de un mensaje largo
    
    # Llamar a la función handle
    result = handle(client)  # La función handle debe manejar el caso de mensaje largo
    
    # Aserciones para verificar el comportamiento esperado
    mock_broadcast.assert_not_called()  # Asegurar que no se difunde nada para un mensaje largo
    assert result is False  # La función debe devolver False para mensajes largos