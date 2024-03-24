import dns.resolver
import time
import os
import sys
from tqdm import tqdm

class Cores:
    VERMELHO = '\033[91m'
    VERDE = '\033[92m'
    RESET = '\033[0m'

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def ler_dominios(arquivo_dominios):
    try:
        with open(arquivo_dominios, 'r') as arquivo:
            return [linha.strip() for linha in arquivo if linha.strip()]
    except Exception as e:
        print(f"{Cores.VERMELHO}Falha ao ler {arquivo_dominios}: {e}{Cores.RESET}")
        sys.exit(1)

def obter_ips_atuais(dominio):
    try:
        return sorted([ip.address for ip in dns.resolver.resolve(dominio, 'A')])
    except Exception as e:
        print(f"{Cores.VERMELHO}Falha ao resolver {dominio}: {e}{Cores.RESET}")
        return []

def ler_ips_antigos(arquivo_ip):
    try:
        with open(arquivo_ip, 'r') as arquivo:
            return arquivo.read().splitlines()
    except FileNotFoundError:
        return []

def salvar_ips_atuais(arquivo_ip, ips, dominio, ips_antigos):
    with open(arquivo_ip, 'w') as arquivo:
        arquivo.write('\n'.join(ips))
    ips_adicionados = set(ips) - set(ips_antigos)
    ips_removidos = set(ips_antigos) - set(ips)
    if ips_adicionados or ips_removidos:
        with open(f"{dominio.replace('.', '_')}_historico.txt", 'a') as arquivo_hist:
            arquivo_hist.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            if ips_adicionados:
                arquivo_hist.write(f"Adicionados: {', '.join(ips_adicionados)}\n")
            if ips_removidos:
                arquivo_hist.write(f"Removidos: {', '.join(ips_removidos)}\n")
            arquivo_hist.write("-" * 40 + "\n")

def monitorar_dominios(arquivo_dominios):
    dominios = ler_dominios(arquivo_dominios)
    for dominio in dominios:
        ips_atuais = obter_ips_atuais(dominio)
        arquivo_ip = f"{dominio.replace('.', '_')}_ips.txt"
        ips_antigos = ler_ips_antigos(arquivo_ip)

        if ips_atuais != ips_antigos:
            print("-" * 60)
            print(f"{Cores.VERMELHO}ALERTA: Mudança de IP detectada para {dominio}{Cores.RESET}")
            ips_adicionados = set(ips_atuais) - set(ips_antigos)
            ips_removidos = set(ips_antigos) - set(ips_atuais)
            if ips_adicionados:
                print(f"{Cores.VERMELHO}Adicionados: {', '.join(ips_adicionados)}{Cores.RESET}")
            if ips_removidos:
                print(f"{Cores.VERMELHO}Removidos: {', '.join(ips_removidos)}{Cores.RESET}")
            salvar_ips_atuais(arquivo_ip, ips_atuais, dominio, ips_antigos)
        else:
            print(f"{Cores.VERDE}Nenhuma mudança de IP para {dominio}{Cores.RESET}")
        print("-" * 60)

def iniciar_monitoramento():
    arquivo_dominios = 'dominios.txt'
    intervalo_entre_ciclos = 60
    try:
        while True:
            limpar_tela()
            print(f"{Cores.VERDE}Iniciando monitoramento dos domínios...{Cores.RESET}")
            monitorar_dominios(arquivo_dominios)
            print(f"{Cores.VERDE}Aguardando próximo ciclo...{Cores.RESET}")
            for _ in tqdm(range(intervalo_entre_ciclos), desc="Tempo até próximo ciclo", unit="s", leave=False):
                time.sleep(1)
    except KeyboardInterrupt:
        print(f"\n{Cores.VERDE}Monitoramento interrompido pelo usuário.{Cores.RESET}")

if __name__ == "__main__":
    iniciar_monitoramento()
