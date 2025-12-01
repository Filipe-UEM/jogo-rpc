import xmlrpc.client
import sys
import time
import os

def limpar_tela():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_tabuleiro(tabuleiro):
    print("   A   B   C")
    for i in range(3):
        print(str(i+1) + "  " + tabuleiro[i][0] + " | " + tabuleiro[i][1] + " | " + tabuleiro[i][2])
        if i < 2:
            print("  -----------")

def animacao_cara_coroa():
    frames = [
        " ???  \n       \n    ",
        " OOO  \n CARA  \n    ",
        " XXX  \n COROA \n    ",
        " OOO  \n CARA  \n    ",
        " XXX  \n COROA \n    "
    ]
    
    print("\nSorteando quem começa...")
    time.sleep(1)
    
    for i in range(8):
        limpar_tela()
        frame_idx = i % len(frames)
        print(frames[frame_idx])
        time.sleep(0.3)
    
    time.sleep(1)
    limpar_tela()

if len(sys.argv) != 4:
    print("Uso: python cliente.py ip_servidor porta id_jogador")
    sys.exit()

ip_servidor = sys.argv[1]
porta = int(sys.argv[2])
id_jogador = sys.argv[3]

try:
    proxy = xmlrpc.client.ServerProxy("http://" + ip_servidor + ":" + str(porta))
    
    simbolo = proxy.registrar_jogador(id_jogador)
    
    if simbolo == "CHEIO":
        print("Servidor cheio. Não foi possível conectar.")
        sys.exit()
    elif simbolo == "ENCERRADO":
        print("Jogo já foi encerrado. Não é possível conectar.")
        sys.exit()
    
    print("Você está conectado como jogador", id_jogador)
    print("Aguardando outro jogador...")
    
    while True:
        jogadores = proxy.obter_jogadores()
        if len(jogadores) == 2:
            break
        
        # Verifica se o jogo foi encerrado
        if proxy.verificar_jogo_encerrado():
            print("Jogo foi encerrado:", proxy.obter_motivo_encerramento())
            sys.exit()
            
        # Verifica se o servidor ainda está ativo
        try:
            proxy.obter_tabuleiro()
        except:
            print("Conexão perdida com o servidor")
            sys.exit()
        
        time.sleep(1)
    
    simbolo = proxy.registrar_jogador(id_jogador)
    
    outro_jogador = None
    for jogador_id in jogadores:
        if jogador_id != id_jogador:
            outro_jogador = jogador_id
            break
    
    # Mostra animação do sorteio
    animacao_cara_coroa()
    
    print("Sorteio realizado! Você é:", simbolo)
    print("Você está jogando contra", outro_jogador)
    
    vez_de = proxy.obter_vez()
    if vez_de == id_jogador:
        print("Você começa jogando!")
    else:
        print("" + outro_jogador + " começa jogando.")
    
    time_ultima_verificacao = time.time()
    
    while True:
        # Verifica se o jogo foi encerrado a cada 5 segundos
        if time.time() - time_ultima_verificacao > 5:
            if proxy.verificar_jogo_encerrado():
                print("Jogo encerrado:", proxy.obter_motivo_encerramento())
                break
            time_ultima_verificacao = time.time()
        
        vez_de = proxy.obter_vez()
        tabuleiro = proxy.obter_tabuleiro()
        
        print()
        print("=" * 40)
        mostrar_tabuleiro(tabuleiro)
        
        if vez_de == id_jogador:
            print()
            print("Sua vez! (" + simbolo + ")")
            jogada_ok = False
            while not jogada_ok:
                jogada = input("Digite sua jogada (ex: A1) ou 'sair' para sair: ").strip().upper()
                
                if jogada == 'SAIR':
                    proxy.sair_jogo(id_jogador)
                    print("Você saiu do jogo. O jogo foi encerrado para ambos os jogadores.")
                    sys.exit()
                
                if len(jogada) == 2 and jogada[0] in ['A','B','C'] and jogada[1] in ['1','2','3']:
                    resultado = proxy.fazer_jogada(id_jogador, jogada)
                    if resultado["status"] == "ERRO":
                        print("Erro:", resultado["mensagem"])
                        # Se o erro for porque o jogo foi encerrado, sair
                        if "encerrado" in resultado["mensagem"].lower():
                            print("Jogo encerrado. Saindo...")
                            break
                    else:
                        jogada_ok = True
                        if resultado["status"] == "VITORIA":
                            print("Parabéns! Você venceu!")
                        elif resultado["status"] == "EMPATE":
                            print("Empate!")
                else:
                    print("Jogada inválida. Use formato A1, B2, C3, etc.")
        else:
            print()
            print("Vez de " + outro_jogador + "...")
            time.sleep(2)
        
        # Verifica se o jogo terminou normalmente
        tabuleiro = proxy.obter_tabuleiro()
        
        vencedor = None
        for i in range(3):
            if tabuleiro[i][0] == tabuleiro[i][1] == tabuleiro[i][2] != ' ':
                vencedor = tabuleiro[i][0]
        for j in range(3):
            if tabuleiro[0][j] == tabuleiro[1][j] == tabuleiro[2][j] != ' ':
                vencedor = tabuleiro[0][j]
        if tabuleiro[0][0] == tabuleiro[1][1] == tabuleiro[2][2] != ' ':
            vencedor = tabuleiro[0][0]
        if tabuleiro[0][2] == tabuleiro[1][1] == tabuleiro[2][0] != ' ':
            vencedor = tabuleiro[0][2]
        
        empate = True
        for i in range(3):
            for j in range(3):
                if tabuleiro[i][j] == ' ':
                    empate = False
        
        if vencedor or empate:
            print()
            print("=" * 40)
            mostrar_tabuleiro(tabuleiro)
            if vencedor:
                if jogadores[id_jogador] == vencedor:
                    print("Parabéns! Você venceu!")
                else:
                    print(outro_jogador + " venceu!")
            else:
                print("Empate!")
            
            stats = proxy.obter_estatisticas()
            print("Placar: X [" + str(stats[0]) + "] x O [" + str(stats[1]) + "]")
            
            resposta = input("\nDeseja jogar novamente? (S/N): ").strip().upper()
            if resposta == 'S':
                if proxy.reiniciar_jogo():
                    print("Novo jogo iniciado!")
                    jogadores = proxy.obter_jogadores()
                    simbolo = jogadores[id_jogador]
                    print("Você agora é:", simbolo)
                    time_ultima_verificacao = time.time()
                else:
                    print("Não foi possível reiniciar o jogo. Alguém saiu.")
                    break
            else:
                proxy.sair_jogo(id_jogador)
                print("Você saiu do jogo. Obrigado por jogar!")
                break

except Exception as e:
    print("Erro de conexão:", e)