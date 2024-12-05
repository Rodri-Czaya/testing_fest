import pytest
from unittest.mock import Mock, patch
from server import remove 

# Datos simulados para pruebas
@pytest.fixture
def setup_clients_and_nicknames():
    """
    Fixture para crear un cliente simulado con un método 'close' simulado.
    Este mock simulará un objeto cliente que se puede utilizar en las pruebas.
    """
    client = Mock()  # Crear un cliente simulado
    client.close = Mock()  # Simular el método 'close' del cliente
    return client  # Devolver el cliente simulado para su uso en las pruebas

# Prueba 1: Caso óptimo - eliminación exitosa de un cliente
@patch('server.nicknames', new_callable=dict)  # Simular el diccionario 'nicknames' en el módulo del servidor
@patch('server.clients', new_callable=list)  # Simular la lista 'clients' en el módulo del servidor
def test_remove_optimal(mock_clients, mock_nicknames, setup_clients_and_nicknames):
    """
    Caso de prueba para el escenario óptimo donde se elimina correctamente un cliente válido
    tanto de la lista de clientes como del diccionario de nicknames.
    """
    client = setup_clients_and_nicknames  # Configurar un cliente simulado usando el fixture
    mock_clients.append(client)  # Añadir el cliente a la lista simulada de clientes
    mock_nicknames[client] = "TestUser"  # Añadir el apodo del cliente al diccionario simulado de nicknames
    
    # Simular 'clients' y 'nicknames' en el módulo del servidor, luego llamar a 'remove'
    with patch('server.clients', mock_clients), patch('server.nicknames', mock_nicknames):
        remove(client)
    
    # Aserciones para verificar el comportamiento correcto
    assert client not in mock_clients  # Asegurar que el cliente se elimina de la lista de clientes
    assert client not in mock_nicknames  # Asegurar que el apodo del cliente se elimina del diccionario de nicknames
    client.close.assert_called_once()

# Prueba 2: Caso de cliente inválido - el cliente es una cadena vacía
@patch('server.nicknames', new_callable=dict)  # Simular el diccionario 'nicknames' en el módulo del servidor
@patch('server.clients', new_callable=list)  # Simular la lista 'clients' en el módulo del servidor
def test_no_client(mock_clients, mock_nicknames):
    """
    Caso de prueba donde el cliente pasado a la función 'remove' es una cadena vacía, que es inválida.
    La función debe lanzar un ValueError.
    """
    with pytest.raises(ValueError):  # Esperando un ValueError al pasar un cliente inválido
        with patch('server.clients', mock_clients), patch('server.nicknames', mock_nicknames):
            remove("")  # Llamar a remove con una cadena vacía como cliente

# Prueba 3: Cliente no encontrado en clientes o nicknames
@patch('server.nicknames', new_callable=dict)  # Simular el diccionario 'nicknames' en el módulo del servidor
@patch('server.clients', new_callable=list)  # Simular la lista 'clients' en el módulo del servidor
def test_wrong_client(mock_clients, mock_nicknames, setup_clients_and_nicknames):
    """
    Caso de prueba donde el cliente pasado a 'remove' no existe en 'clients' o 'nicknames'.
    El cliente original no debe ser eliminado.
    """
    client = setup_clients_and_nicknames  # Configurar un cliente simulado usando el fixture
    fake_client = Mock()  # Crear otro cliente simulado (que no existe en la lista de clientes)

    # Añadir el cliente real a la lista simulada de clientes y al diccionario de nicknames
    mock_clients.append(client)
    mock_nicknames[client] = "TestUser"
    
    # Simular 'clients' y 'nicknames' en el módulo del servidor, luego llamar a 'remove' con un cliente falso
    with patch('server.clients', mock_clients), patch('server.nicknames', mock_nicknames):
        remove(fake_client)  # Intentar eliminar un cliente inexistente
    
    # Aserciones para verificar que el cliente original no se vio afectado
    assert client in mock_clients  # El cliente real aún debe estar en la lista de clientes
    assert mock_nicknames[client] == "TestUser"  # El apodo del cliente real aún debe ser "TestUser"