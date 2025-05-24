import csv
from pynput import mouse

# Arquivo para salvar os cliques
csv_file = "mouse_clicks.csv"

# Criar ou abrir o arquivo e escrever o cabeçalho se necessário
with open(csv_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(["x", "y", "button", "pressed"])  # Cabeçalho

# Função para registrar os cliques
def on_click(x, y, button, pressed):
    with open(csv_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([x, y, button, pressed])
    print(f"Posição: ({x}, {y}), Botão: {button}, Pressionado: {pressed}")

# Configurar o listener do mouse
with mouse.Listener(on_click=on_click) as listener:
    listener.join()