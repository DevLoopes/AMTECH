import pyautogui as pyg
import time

pyg.PAUSE = 0.3

pyg.press("win") # Abre o windowa
pyg.write("edge") # Escreve edge
pyg.press("enter") # da enter
time.sleep(2) # Espera 2 segundos

pyg.write("https://mail.google.com") # digita o email no google
pyg.press("enter") # da enter

time.sleep(2) # espera 2 segundos
pyg.click(x=111, y=214, duration=1) # move o mouse e clica em escrever e-mail


time.sleep(1) # espera 3 segundos
pyg.click(x=1171, y=433, duration=1) # Clica em To: 

pyg.write("alexsimaslopes@gmail.com") # escreve para onde enviar
pyg.press("enter") # seleciona

pyg.click(x=1176, y=506, duration=1) # arrasta o mouse e clica no Subject

pyg.write("Teste em Python com autogui") # Escreve Título do texto

pyg.click(x=1166, y=543, duration=1) # arrasta o mouse e clica no assunto

pyg.write("Teste em Python com autogui\nAGORA VAAAI\nAtenciosamente,\nAlexsandro Simas Lopes =)") # Escreve texto

time.sleep(1) # espera 1 segundos

pyg.hotkey("ctrl" , "enter")


