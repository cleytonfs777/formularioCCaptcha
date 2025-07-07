from datetime import datetime
from selenium.common.exceptions import TimeoutException  # Importar TimeoutException
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

from selenium.webdriver.common.action_chains import ActionChains

from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from time import sleep
import os

# Bibliotecas Externas
from captcha_view import reconhecer_captcha
from utils import ler_planilha_para_dict, normalize_name



def query(nome_n, cpf_n, tel_n, email_n,rg_n="50.070.805-8", org_exp="SSPMG", end_n="Rod. Papa João Paulo II, 4001", bairro_n="Serra Verde", est_n="MG", cep_n="31630-901", cidade_n="Belo Horizonte", senha_n="12345678"):


    NOME = nome_n
    CPF = cpf_n
    RG=rg_n
    EXPED=org_exp
    END=end_n
    BAIRRO=bairro_n
    ESTADO=est_n
    CEP=cep_n
    CIDADE=cidade_n
    TEL = tel_n
    EMAIL=email_n
    SENHA_PADRAO=senha_n

    try:
        semaforo = "green"
        
        options = webdriver.ChromeOptions()
        options.add_argument("--window-size=1920,1080")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
        # options.add_argument("--headless")
        # Desativa completamente o gerenciador de senhas e seus prompts
        options.add_experimental_option("prefs", {
            "credentials_enable_service": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.default_content_setting_values.automatic_downloads": 1,
            "autofill.profile_enabled": False,
            "profile.password_manager_enabled": False,
            "profile.default_content_settings.popups": 0,
            "credentials_enable_autosignin": False,
            "credentials_enable_service": False
        })
        # Desativa outros prompts de automação
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--disable-save-password-bubble")
        options.add_experimental_option("useAutomationExtension", False)

        servico = Service(ChromeDriverManager().install())
        navegador = webdriver.Chrome(service=servico, options=options)
        navegador.implicitly_wait(10)

        url = "https://www.sei.mg.gov.br/sei/controlador_externo.php?acao=usuario_externo_enviar_cadastro&acao_origem=usuario_externo_avisar_cadastro&id_orgao_acesso_externo=0"
        navegador.get(url)

        while semaforo == "green":

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
            
            # # Reconhecimento de Captcha por áudio
            # from captcha_view import reconhecer_captcha_audio
            # from selenium.webdriver.support.ui import WebDriverWait
            # from selenium.webdriver.support import expected_conditions as EC
            # # Clica no botão de áudio
            # reconhecer_captcha_audio(
            #     navegador,
            #     audio_button_xpath='//img[@id="infraImgAudioCaptcha"]',
            #     audio_tag="audio",
            #     captcha_input_id="txtInfraCaptcha",
            #     submit_id=None
            # )
            # # Aguarda o elemento <audio> aparecer e captura a URL do áudio
            # WebDriverWait(navegador, 10).until(EC.presence_of_element_located((By.TAG_NAME, "audio")))
            # audio_source = navegador.find_element(By.TAG_NAME, "audio").get_attribute("src")
            # import requests
            # audio_content = requests.get(audio_source).content
            # with open("captcha.mp3", "wb") as audio_file:
            #     audio_file.write(audio_content)
                
                
            navegador.find_element(By.ID, "txtInfraCaptcha").send_keys("123456")
            
            navegador.find_element(By.ID, "sbmEnviar").click()
            
            sleep(1)
            
            try:
                msg_element = navegador.find_element(By.ID, "divInfraMsg0")
                if "Código de confirmação inválido" in msg_element.text:
                    print("Código de confirmação inválido....recarregando a página!!")
                    navegador.get(url)
                    continue
                else:
                    print("Cadastro realizado com sucesso !!")
                    semaforo = "red"  # Corrigido '==' para '='
                    navegador.quit()  # Fecha o navegador após sucesso
                    return {"sucesso": True, "erro": None}
            except:
                navegador.get(url)
        
        # Se saiu do loop sem sucesso
        navegador.quit()
        return {"sucesso": False, "erro": "Máximo de tentativas excedido"}

    except Exception as e:
        if navegador:
            navegador.quit()
        return {"sucesso": False, "erro": str(e)}


if __name__ == "__main__":
    # Teste único
    resultado = query("Nome Teste", "123.456.789-00", "(31) 99999-9999", "teste@teste.com")
    print(resultado)
