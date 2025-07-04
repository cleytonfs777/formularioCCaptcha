from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageFilter
import pytesseract
from time import sleep
import requests
import io
import base64
import openai
import base64
from dotenv import load_dotenv
import os
from pydub import AudioSegment
import speech_recognition as sr
from selenium.webdriver.support.ui import WebDriverWait

load_dotenv()  # take environment variable
# Define explicitamente o caminho do executável do Tesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def reconhecer_captcha_openai():
    image_path='captcha_processed.png'
    api_key=os.getenv("API_KEY_OPENAI")
    
    openai.api_key = api_key
    with open(image_path, "rb") as img_file:
        img_base64 = base64.b64encode(img_file.read()).decode("utf-8")
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Leia o texto do captcha da imagem.traga apenas o conteudo do captcha"},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_base64}"}}
                ]
            }
        ],
        max_tokens=10
    )
    texto = response.choices[0].message.content.strip()
    
    return texto

def reconhecer_captcha(driver):
    # Espera carregar a página completamente
    sleep(1)

    # Localize a imagem captcha
    captcha_element = driver.find_element(By.ID, "imgCaptcha")

    # Tenta obter a imagem em alta resolução, se disponível
    # Procura por atributos de srcset ou data-srcset
    captcha_url = None
    if captcha_element.get_attribute('srcset'):
        # Se houver srcset, pega a maior resolução
        srcset = captcha_element.get_attribute('srcset')
        # srcset pode ser algo como: 'url1 1x, url2 2x'
        urls = [u.strip().split(' ') for u in srcset.split(',')]
        # Pega a última (maior resolução)
        captcha_url = urls[-1][0]
    elif captcha_element.get_attribute('data-srcset'):
        srcset = captcha_element.get_attribute('data-srcset')
        urls = [u.strip().split(' ') for u in srcset.split(',')]
        captcha_url = urls[-1][0]
    else:
        captcha_url = captcha_element.get_attribute('src')

    if captcha_url.startswith('data:image'):
        # Caso a imagem venha em base64 embutida no src
        header, encoded = captcha_url.split(',', 1)
        captcha_image = base64.b64decode(encoded)
    else:
        # Caso seja uma URL normal
        captcha_image = requests.get(captcha_url).content

    # Abra a imagem para processamento
    image = Image.open(io.BytesIO(captcha_image))

    # Processamento básico da imagem para melhorar o OCR
    image = image.convert('L')  # Converte para tons de cinza
    image = image.filter(ImageFilter.MedianFilter())  # Filtro para reduzir ruído
    image = image.point(lambda x: 0 if x < 140 else 255)  # Binarização simples

    # Salvar imagem processada (para debug)
    image.save('captcha_processed.png')

    print("Iniciando a conversão do captcha...")
    resultado = reconhecer_captcha_openai()

    print("Captcha detectado:", resultado)

    return resultado

    # Continuar preenchendo o formulário...
    # driver.find_element(By.ID, "submit").click()

    # Fechar navegador (quando finalizar tudo)
    # driver.quit()

def reconhecer_captcha_audio(driver, audio_button_xpath=None, audio_tag="audio", captcha_input_id="txtInfraCaptcha", submit_id=None):
    # Clique na imagem para gerar o áudio do captcha
    audio_img = driver.find_element(By.ID, "infraImgAudioCaptcha")
    audio_img.click()
    # Aguarde até que o src do <source> seja preenchido
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.ID, "infraSrcAudioCaptcha").get_attribute("src")
    )
    sleep(1)  # Pequeno delay extra para garantir
    audio_source_elem = driver.find_element(By.ID, "infraSrcAudioCaptcha")
    audio_src = audio_source_elem.get_attribute("src")
    print(f"URL do áudio capturada: {audio_src}")
    if not audio_src or not audio_src.strip():
        raise Exception("O atributo src do áudio está vazio. O áudio ainda não foi gerado ou houve erro no carregamento.")

    # Se a URL for relativa, torne-a absoluta
    if audio_src.startswith("/"):
        from urllib.parse import urljoin
        audio_src = urljoin(driver.current_url, audio_src)

    # Baixe o áudio usando os cookies do Selenium
    import requests
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])
    response = session.get(audio_src)
    print("Content-Type:", response.headers.get("Content-Type"))
    audio_content = response.content

    # Salve como WAV diretamente
    with open("captcha.wav", "wb") as audio_file:
        audio_file.write(audio_content)

    # Verifique se o arquivo foi salvo corretamente e tem tamanho > 0
    if not os.path.exists("captcha.wav") or os.path.getsize("captcha.wav") == 0:
        print("Arquivo captcha.wav não foi salvo corretamente ou está vazio.")
        with open("captcha_download_error.html", "wb") as f:
            f.write(audio_content)
        return

    # Tente abrir o arquivo com pydub para garantir que é um WAV válido
    try:
        audio_segment = AudioSegment.from_wav("captcha.wav")
        print(f"Duração do áudio: {audio_segment.duration_seconds:.2f} segundos")
    except Exception as e:
        print(f"Erro ao abrir captcha.wav com pydub: {e}")
        with open("captcha_download_error.html", "wb") as f:
            f.write(audio_content)
        return

    # Realizar o reconhecimento de fala
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile("captcha.wav") as source:
            audio = recognizer.record(source)
        # Tenta transcrever usando o reconhecimento do Google
        text = recognizer.recognize_google(audio, language="pt-BR")
        print("Texto reconhecido:", text)
    except Exception as e:
        print("Erro ao reconhecer o áudio:", e)
        with open("captcha_download_error.html", "wb") as f:
            f.write(audio_content)
        text = ""

    # Insere o texto reconhecido no campo do captcha
    captcha_field = driver.find_element(By.ID, captcha_input_id)
    captcha_field.send_keys(text)

    # (Opcional) Enviar o formulário ou continuar o fluxo
    if submit_id:
        submit_button = driver.find_element(By.ID, submit_id)
        submit_button.click()

    # Limpeza dos arquivos
    if os.path.exists("captcha.wav"):
        os.remove("captcha.wav")
