from datetime import datetime
from selenium.common.exceptions import TimeoutException  # Importar TimeoutException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import os

# Bibliotecas Externas
from captcha_view import reconhecer_captcha



def query():


    NOME = "TESTE NOME"
    CPF = "38719801610"
    RG="50.070.805-8"
    EXPED="SSPMG"
    END="Rod. Papa João Paulo II, 4001"
    BAIRRO="Serra Verde"
    ESTADO="MG"
    CEP="31630-901"
    CIDADE="Belo Horizonte"
    TEL = "37999445587"
    EMAIL="exemplo@gmail.com"
    SENHA_PADRAO="12345678"

    try:

        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])  # Suprime logs do ChromeDriver
        # options.add_argument("--headless")
        # Defina o tamanho da janela
        options.add_argument("--window-size=1920,1080")

        servico = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servico, options=options)
        navegador.implicitly_wait(10)

        url = "https://www.sei.mg.gov.br/sei/controlador_externo.php?acao=usuario_externo_enviar_cadastro&acao_origem=usuario_externo_avisar_cadastro&id_orgao_acesso_externo=0"
        navegador.get(url)


        # Insere a credencial de Nome
        navegador.find_element(By.ID, "txtNome").send_keys(NOME)
    
        # Insere a credencial de CPF
        navegador.find_element(By.ID, "txtCpf").send_keys(CPF)
        ###
        # Insere a credencial de RG
        navegador.find_element(By.ID, "txtRg").send_keys(RG)
        
        # Insere a credencial de EXPED
        navegador.find_element(By.ID, "txtExpedidor").send_keys(EXPED)
       
        # Insere a credencial de END
        navegador.find_element(By.ID, "txtEndereco").send_keys(END)
       
        # Insere a credencial de BAIRRO
        navegador.find_element(By.ID, "txtBairro").send_keys(BAIRRO)
        
        # Insere a credencial de ESTADO
        select_element = navegador.find_element(By.ID, "selUf")
        select = Select(select_element)
        select.select_by_visible_text(ESTADO)

        # Insere a credencial de CIDADE
        select_element = navegador.find_element(By.ID, "selCidade")
        select = Select(select_element)
        select.select_by_visible_text(CIDADE)

        # Insere a credencial de CEP
        navegador.find_element(By.ID, "txtCep").send_keys(CEP)

        # Insere a credencial de Telefone
        navegador.find_element(By.ID, "txtTelefoneComercial").send_keys(TEL)

        # Insere a credencial de Email
        navegador.find_element(By.ID, "txtEmail").send_keys(EMAIL)

        # Insere a credencial de senha
        navegador.find_element(By.ID, "pwdSenha").send_keys(SENHA_PADRAO)

        # Insere a credencial de confirmação de senha
        navegador.find_element(By.ID, "pwdSenhaConfirma").send_keys(SENHA_PADRAO)
        
        # Reconhecimento de Captcha por áudio
        from captcha_view import reconhecer_captcha_audio
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        # Clica no botão de áudio
        reconhecer_captcha_audio(
            navegador,
            audio_button_xpath='//img[@id="infraImgAudioCaptcha"]',
            audio_tag="audio",
            captcha_input_id="txtInfraCaptcha",
            submit_id=None
        )
        # Aguarda o elemento <audio> aparecer e captura a URL do áudio
        WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.TAG_NAME, "audio")))
        audio_source = navegador.find_element(By.TAG_NAME, "audio").get_attribute("src")
        import requests
        audio_content = requests.get(audio_source).content
        with open("captcha.mp3", "wb") as audio_file:
            audio_file.write(audio_content)
        

    except Exception as e:

        print(f"Erro: {e}")


if __name__ == "__main__":
    query()
