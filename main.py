import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, TaskID
from rich.table import Table
from rich import print as rprint
from rich.live import Live
import time
from search import query
from utils import ler_planilha_para_dict

console = Console()
app = typer.Typer()

def mostrar_menu_principal():
    console.clear()
    console.print(Panel.fit(
        "[bold yellow]SEI EXTERNO AUTOMATIZADO[/bold yellow]",
        border_style="yellow",
        padding=(1, 2)
    ))
    
    table = Table(show_header=False, box=None)
    table.add_row("[1]", "[green]Iniciar BOT[/green]")
    table.add_row("[2]", "[blue]Configurar Sistema[/blue]")
    table.add_row("[3]", "[cyan]Informações[/cyan]")
    table.add_row("[4]", "[red]Sair[/red]")
    
    console.print(table)
    return console.input("\n[yellow]Escolha uma opção:[/yellow] ")

def mostrar_informacoes():
    console.clear()
    console.print(Panel(
        "[bold yellow]Informações do Sistema[/bold yellow]\n\n"
        "Este BOT foi desenvolvido para automatizar o cadastro de usuários externos no SEI/MG.\n"
        "Funcionalidades:\n"
        "- Leitura automática de planilha Excel\n"
        "- Preenchimento automático do formulário\n"
        "- Reconhecimento de captcha por áudio\n"
        "- Tratamento de erros e retry automático\n\n"
        "[bold cyan]Pressione ENTER para voltar ao menu principal[/bold cyan]",
        border_style="yellow",
        padding=(1, 2)
    ))
    console.input()

def iniciar_bot():
    console.clear()
    caminho = "dados.xlsx"
    dados = ler_planilha_para_dict(caminho)
    total = len(dados)
    
    # Cria tabelas para sucessos e falhas
    sucessos = Table(title="[green]Cadastros Realizados com Sucesso[/green]")
    sucessos.add_column("Nome", style="green")
    sucessos.add_column("CPF", style="green")
    sucessos.add_column("Email", style="green")
    
    falhas = Table(title="[red]Cadastros com Falha[/red]")
    falhas.add_column("Nome", style="red")
    falhas.add_column("CPF", style="red")
    falhas.add_column("Email", style="red")
    falhas.add_column("Erro", style="red")
    
    with Progress() as progress:
        # Adiciona a tarefa principal
        task1 = progress.add_task("[cyan]Processando cadastros...", total=total)
        
        for idx, i in enumerate(dados, 1):
            console.print(f"\n[yellow]Processando {idx}/{total}:[/yellow] {i['CANDIDATO']}")
            
            try:
                status = query(i['CANDIDATO'], i['CPF'], i['CELULAR'], i['EMAIL'])
                if status['sucesso']:
                    sucessos.add_row(i['CANDIDATO'], i['CPF'], i['EMAIL'])
                else:
                    falhas.add_row(i['CANDIDATO'], i['CPF'], i['EMAIL'], status['erro'])
            except Exception as e:
                falhas.add_row(i['CANDIDATO'], i['CPF'], i['EMAIL'], str(e))
            
            progress.update(task1, advance=1)
    
    # Mostra resultados finais
    console.print("\n[bold yellow]Resultados Finais:[/bold yellow]")
    console.print(sucessos)
    console.print(falhas)
    
    console.print("\n[bold cyan]Pressione ENTER para voltar ao menu principal[/bold cyan]")
    console.input()

def main():
    while True:
        opcao = mostrar_menu_principal()
        
        if opcao == "1":
            iniciar_bot()
        elif opcao == "2":
            console.print("[yellow]Função em desenvolvimento[/yellow]")
            time.sleep(2)
        elif opcao == "3":
            mostrar_informacoes()
        elif opcao == "4":
            console.print("[yellow]Encerrando o programa...[/yellow]")
            break
        else:
            console.print("[red]Opção inválida![/red]")
            time.sleep(2)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Programa encerrado pelo usuário.[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Erro não tratado: {str(e)}[/red]")
