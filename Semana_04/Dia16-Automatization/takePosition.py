import pyautogui as pyg
import time

# Espera 3s e pega a ultima localização do mouse na tela
time.sleep(3)
print(pyg.position())

# Possíveis teclas
# print(pyg.KEYBOARD_KEYS)

# Faz um scroll da teta para baixo ou para cima
# pyg.scroll(-300)
