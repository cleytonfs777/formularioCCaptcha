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

def converter_texto_captcha(texto):
    # Dicionário de mapeamento de palavras para números
    numero_map = {
        'zero': '0', 'um': '1', 'dois': '2', 'três': '3', 'tres': '3',
        'quatro': '4', 'cinco': '5', 'seis': '6', 'sete': '7',
        'oito': '8', 'nove': '9', 'dez': '10',
        # Variações comuns
        'ver': 'V', 'v': 'V', 've': 'V',
        'x': 'X', 'y': 'Y', 'z': 'Z',
        'i': 'I', 'w': 'W', 'k': 'K'
    }
    
    # Converte o texto para minúsculo para facilitar o processamento
    palavras = texto.lower().split()
    resultado = []
    
    for palavra in palavras:
        # Se a palavra está no mapeamento, usa o valor mapeado
        if palavra in numero_map:
            resultado.append(numero_map[palavra])
        # Se é um número por extenso não mapeado, tenta converter
        elif palavra.isdigit():
            resultado.append(palavra)
        # Se é uma letra única, converte para maiúscula
        elif len(palavra) == 1 and palavra.isalpha():
            resultado.append(palavra.upper())
        # Se não é número nem letra única, verifica cada caractere
        else:
            for char in palavra:
                if char.isdigit():
                    resultado.append(char)
                elif char.isalpha():
                    resultado.append(char.upper())
    
    return ''.join(resultado)

def reconhecer_captcha_audio(driver, audio_button_xpath=None, audio_tag="audio", captcha_input_id="txtInfraCaptcha", submit_id=None):
    # Clique na imagem para gerar o áudio do captcha
    audio_img = driver.find_element(By.ID, "infraImgAudioCaptcha")
    audio_img.click()
    
    # Aguarde até que o elemento de áudio esteja presente
    WebDriverWait(driver, 10).until(
        lambda d: d.find_element(By.TAG_NAME, "audio") and d.find_element(By.TAG_NAME, "audio").find_element(By.TAG_NAME, "source")
    )
    sleep(1)  # Pequeno delay extra para garantir que o áudio foi carregado

    # Script JavaScript para baixar o áudio
    download_script = """
    const audioSrc = new URL(document.querySelector('audio source').src, window.location.origin).href;
    return audioSrc;
    """
    audio_url = driver.execute_script(download_script)
    print(f"URL do áudio capturada: {audio_url}")

    if not audio_url or not audio_url.strip():
        raise Exception("O URL do áudio está vazio. O áudio ainda não foi gerado ou houve erro no carregamento.")

    # Baixe o áudio usando os cookies do Selenium
    session = requests.Session()
    for cookie in driver.get_cookies():
        session.cookies.set(cookie['name'], cookie['value'])
    
    response = session.get(audio_url)
    print("Content-Type:", response.headers.get("Content-Type"))
    audio_content = response.content

    # Salve como WAV
    wav_path = "captcha.wav"
    with open(wav_path, "wb") as audio_file:
        audio_file.write(audio_content)

    # Verifique se o arquivo foi salvo corretamente e tem tamanho > 0
    if not os.path.exists(wav_path) or os.path.getsize(wav_path) == 0:
        print("Arquivo de áudio não foi salvo corretamente ou está vazio.")
        with open("captcha_download_error.html", "wb") as f:
            f.write(audio_content)
        return

    # Tente abrir o arquivo com pydub para garantir que é um WAV válido
    try:
        # Carrega e normaliza o áudio
        audio_segment = AudioSegment.from_wav(wav_path)
        print(f"Duração do áudio original: {audio_segment.duration_seconds:.2f} segundos")
        
        # Normaliza o volume do áudio
        normalized_audio = audio_segment.normalize(headroom=0.1)
        
        # Remove ruído de fundo (aumenta um pouco o volume)
        normalized_audio = normalized_audio + 10
        
        # Salva o áudio processado
        normalized_audio.export("captcha_processed.wav", format="wav")
        print("Áudio normalizado e processado salvo.")
        
    except Exception as e:
        print(f"Erro ao processar áudio com pydub: {e}")
        with open("captcha_download_error.html", "wb") as f:
            f.write(audio_content)
        if os.path.exists(wav_path):
            os.remove(wav_path)
        return

    # Realizar o reconhecimento de fala
    recognizer = sr.Recognizer()
    
    # Configurações do reconhecedor
    recognizer.energy_threshold = 300  # Aumenta sensibilidade
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 0.8  # Reduz pausa entre palavras
    recognizer.operation_timeout = 30  # Aumenta timeout

    text = ""
    try:
        # Primeira tentativa com áudio original
        with sr.AudioFile(wav_path) as source:
            print("Tentando reconhecimento com áudio original...")
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language="pt-BR")
            print("Texto reconhecido (áudio original):", text)
    except Exception as e:
        print(f"Erro no primeiro reconhecimento: {e}")
        try:
            # Segunda tentativa com áudio processado
            with sr.AudioFile("captcha_processed.wav") as source:
                print("Tentando reconhecimento com áudio processado...")
                audio = recognizer.record(source)
                text = recognizer.recognize_google(audio, language="pt-BR")
                print("Texto reconhecido (áudio processado):", text)
        except Exception as e:
            print(f"Erro no segundo reconhecimento: {e}")
            if not isinstance(e, sr.UnknownValueError):
                with open("captcha_download_error.html", "wb") as f:
                    f.write(audio_content)

    # Processa o texto reconhecido
    if text:
        text = converter_texto_captcha(text)
        print(f"Texto convertido para formato do captcha: {text}")
        captcha_field = driver.find_element(By.ID, captcha_input_id)
        captcha_field.clear()  # Limpa o campo antes de inserir
        captcha_field.send_keys(text)

        # (Opcional) Enviar o formulário ou continuar o fluxo
        if submit_id:
            submit_button = driver.find_element(By.ID, submit_id)
            submit_button.click()

    # Limpeza dos arquivos
    if os.path.exists(wav_path):
        os.remove(wav_path)
    if os.path.exists("captcha_processed.wav"):
        os.remove("captcha_processed.wav")
    
    return text
