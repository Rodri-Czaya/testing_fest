from client import nickname_checker
import pytest
from unittest.mock import patch # Para simular funciones integradas como `input`

# Prueba 1: El usuario elige un nickname válido
def test_valid_nickname(): # HAPPY PATH
    """
    Simula un escenario donde el usuario proporciona un nickname válido ('TestUser')
    a través de input, y la función nickname_checker debe devolverlo.
    """
    with patch('builtins.input', return_value='TestUser'): # Simulando entrada de usuario
        result = nickname_checker() 
        assert result == "TestUser"

# Prueba 2: El usuario ingresa una cadena vacía (debe reintentar)
def test_empty_nickname(): # EDGE CASE
    """
    Simula un escenario donde el usuario ingresa una cadena vacía y reintenta
    con un nickname válido ('ValidNick').
    """
    with patch('builtins.input', side_effect=['', 'ValidNick']): # Primero vacío, luego válido
        result = nickname_checker() # Llamar a la función
        assert result == "ValidNick"

# Prueba 3: El usuario proporciona nicknames prohibidos tres veces
def test_banned_nicknames(): # ERROR CASE
    """
    Simula un escenario donde el usuario ingresa repetidamente nicknames prohibidos
    ('admin', 'system', 'moderator'). La función debe provocar una Salida del Sistema
    después de tres intentos inválidos.
    """
    with patch('builtins.input', side_effect=['admin', 'system', 'moderator']): # Simular entradas inválidas
        with pytest.raises(SystemExit): # Esperando una salida del sistema después de 3 intentos inválidos
            nickname_checker()

# Prueba 4: El usuario proporciona un nickname prohibido y luego uno válido
def test_invalid_then_valid_nickname(): # RECOVERY CASE
    """
    Simula un escenario donde el usuario proporciona inicialmente un nickname prohibido ('admin'),
    seguido de un nickname válido ('ValidNick'). La función debe aceptar el nickname válido.
    """
    with patch('builtins.input', side_effect=['admin', 'ValidNick']): # Primero prohibido, luego válido
        result = nickname_checker() # Llamar a la función
        assert result == "ValidNick"