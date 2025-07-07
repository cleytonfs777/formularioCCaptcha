import pandas as pd

def normalize_name(nome_in):
    partes = nome_in.strip().split()
    preposicoes = {"do", "de", "da", "das", "dos"}
    partes_norm = [
        p.lower() if p.lower() in preposicoes else p.capitalize()
        for p in partes
    ]
    return " ".join(partes_norm)

def ler_planilha_para_dict(caminho_arquivo):
    df = pd.read_excel(caminho_arquivo)
    dados_dict = df.to_dict(orient='records')
    return dados_dict

def interagir_com_dados(dados):
    for i, registro in enumerate(dados, 1):
        print(f"Registro {i}:")
        for chave, valor in registro.items():
            print(f"  {chave}: {valor}")
        print("-" * 30)

if __name__ == "__main__":
    # caminho = "dados.xlsx"
    # dados = ler_planilha_para_dict(caminho)
    # interagir_com_dados(dados)
    print(normalize_name("MARIA APARECIDA DOS ANJOS DE ALMEIDA"))