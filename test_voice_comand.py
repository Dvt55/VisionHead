import speech_recognition as sr
import pyautogui
import time

def ouvir_comando():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Diga o comando...")
        audio = r.listen(source)

    try:
        comando = r.recognize_google(audio, language='pt-BR')

        print(f"Você disse: {comando}")
        return comando.lower()
    except sr.UnknownValueError:
        print("Não entendi o que voce quis dizer.")
        return ""
    except sr.RequestError as e:
        print(f"Erro ao acessar o serviço de reconhecimento de voz: {e}")
        return ""
    

def aplicar_zoom():
    pyautogui.keyDown('ctrl')
    pyautogui.press('+')
    pyautogui.keyUp('ctrl')
    print("zoom aplicado")


def main():
    while True:
        comando = ouvir_comando()
        if "zoom" in comando:
            aplicar_zoom()
        elif "sair" in comando:
            print("Encerrando...")
            break 


if __name__ == "__main__":
    main()