# v1.2.0-server.py
# Filipe Amadeu Santana RA: 123515
# Rafael Nascimento de Angelis RA: 124164

import xmlrpc.server
import random
import threading
import time
import uuid

class JogoDaVelha:
    def __init__(self):
        self.tabuleiro = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
        self.jogadores = {}  # {id_jogador: simbolo}
        self.tokens_jogadores = {}  # {id_jogador: token}
        self.jogadores_conectados = 0
        self.vez_de = None
        self.jogo_iniciado = False
        self.lock = threading.Lock()
        self.vitorias = [0, 0]
        self.vencedor = None
        self.ultima_jogada_time = time.time()
        self.jogo_ativo = True
        self.jogo_encerrado = False
        self.motivo_encerramento = ""

    def verificar_inatividade(self):
        while self.jogo_ativo and not self.jogo_encerrado:
            time.sleep(10)
            with self.lock:
                if self.jogo_iniciado and (time.time() - self.ultima_jogada_time) > 45:
                    print("Jogo encerrado por inatividade")
                    self.jogo_iniciado = False
                    self.jogo_encerrado = True
                    self.motivo_encerramento = "Jogo encerrado por inatividade de um dos jogadores"
                    return "INATIVIDADE"

    def registrar_jogador_com_token(self, id_jogador, token):
        with self.lock:
            if self.jogo_encerrado:
                return "ENCERRADO"

            if id_jogador in self.tokens_jogadores:

                if self.tokens_jogadores[id_jogador] != token:
                    return "NICK_EM_USO"
                else:
                    return self.jogadores.get(id_jogador, "RECONECTADO")
            

            if self.jogadores_conectados >= 2:
                return "CHEIO"
            
            self.tokens_jogadores[id_jogador] = token
            self.jogadores[id_jogador] = "AGUARDANDO"
            self.jogadores_conectados += 1
            
            if self.jogadores_conectados == 2:
                ids_jogadores = list(self.jogadores.keys())
                random.shuffle(ids_jogadores)
                
                self.jogadores[ids_jogadores[0]] = 'X'
                self.jogadores[ids_jogadores[1]] = 'O'
                
                self.vez_de = ids_jogadores[0]
                self.jogo_iniciado = True
                self.ultima_jogada_time = time.time()
                
                threading.Thread(target=self.verificar_inatividade, daemon=True).start()
            
            return "AGUARDANDO"

    def obter_simbolo_jogador(self, id_jogador, token):
        with self.lock:
            if id_jogador not in self.tokens_jogadores:
                return "NAO_REGISTRADO"
            
            if self.tokens_jogadores[id_jogador] != token:
                return "TOKEN_INVALIDO"
            
            return self.jogadores.get(id_jogador, "AGUARDANDO")

    def verificar_jogo_ativo(self):
        return self.jogo_iniciado and not self.jogo_encerrado
    
    def verificar_jogo_encerrado(self):
        return self.jogo_encerrado
    
    def obter_motivo_encerramento(self):
        return self.motivo_encerramento

    def converter_coordenadas(self, jogada):
        if len(jogada) != 2:
            return None
        
        coluna = jogada[0].upper()
        linha = jogada[1]
        
        if coluna not in ['A', 'B', 'C']:
            return None
        if linha not in ['1', '2', '3']:
            return None
        
        col_idx = ord(coluna) - ord('A')
        lin_idx = int(linha) - 1
        
        return (lin_idx, col_idx)

    def fazer_jogada_com_token(self, id_jogador, token, jogada):
        with self.lock:
            if id_jogador not in self.tokens_jogadores:
                return {"status": "ERRO", "mensagem": "Jogador não autenticado"}
            
            if self.tokens_jogadores[id_jogador] != token:
                return {"status": "ERRO", "mensagem": "Token inválido"}
            
            if self.jogo_encerrado:
                return {"status": "ERRO", "mensagem": self.motivo_encerramento}
                
            if not self.jogo_iniciado:
                return {"status": "ERRO", "mensagem": "Jogo não iniciado"}
            
            if id_jogador != self.vez_de:
                return {"status": "ERRO", "mensagem": "Não é sua vez"}
            
            coordenadas = self.converter_coordenadas(jogada)
            if coordenadas is None:
                return {"status": "ERRO", "mensagem": "Jogada inválida"}
            
            lin, col = coordenadas
            
            if self.tabuleiro[lin][col] != ' ':
                return {"status": "ERRO", "mensagem": "Posição já ocupada"}
            
            simbolo = self.jogadores[id_jogador]
            self.tabuleiro[lin][col] = simbolo
            self.ultima_jogada_time = time.time()
            
            vencedor = self.verificar_vencedor()
            if vencedor:
                self.vencedor = vencedor
                if vencedor == 'X':
                    self.vitorias[0] += 1
                else:
                    self.vitorias[1] += 1
                return {"status": "VITORIA", "vencedor": vencedor, "tabuleiro": self.tabuleiro}
            
            if self.verificar_empate():
                return {"status": "EMPATE", "tabuleiro": self.tabuleiro}
            
            for jogador_id in self.jogadores:
                if jogador_id != id_jogador:
                    self.vez_de = jogador_id
                    break
            
            return {"status": "OK", "tabuleiro": self.tabuleiro}

    def verificar_vencedor(self):
        for i in range(3):
            if self.tabuleiro[i][0] == self.tabuleiro[i][1] == self.tabuleiro[i][2] != ' ':
                return self.tabuleiro[i][0]
        
        for j in range(3):
            if self.tabuleiro[0][j] == self.tabuleiro[1][j] == self.tabuleiro[2][j] != ' ':
                return self.tabuleiro[0][j]
        
        if self.tabuleiro[0][0] == self.tabuleiro[1][1] == self.tabuleiro[2][2] != ' ':
            return self.tabuleiro[0][0]
        if self.tabuleiro[0][2] == self.tabuleiro[1][1] == self.tabuleiro[2][0] != ' ':
            return self.tabuleiro[0][2]
        
        return None

    def verificar_empate(self):
        for i in range(3):
            for j in range(3):
                if self.tabuleiro[i][j] == ' ':
                    return False
        return True

    def obter_tabuleiro(self):
        return self.tabuleiro

    def obter_vez(self):
        return self.vez_de

    def obter_jogadores(self):
        return self.jogadores

    def reiniciar_jogo(self):
        with self.lock:
            if self.jogo_encerrado:
                return False
                
            self.tabuleiro = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
            self.vencedor = None
            self.ultima_jogada_time = time.time()
            
            jogadores_list = list(self.jogadores.keys())
            if self.vencedor:
                vencedor_id = None
                for jogador_id, simbolo in self.jogadores.items():
                    if simbolo == self.vencedor:
                        vencedor_id = jogador_id
                        break
                if vencedor_id:
                    outro_id = jogadores_list[0] if jogadores_list[1] == vencedor_id else jogadores_list[1]
                    self.jogadores[vencedor_id] = 'O'
                    self.jogadores[outro_id] = 'X'
                    self.vez_de = outro_id
            else:
                simbolo_antigo = self.jogadores[jogadores_list[0]]
                self.jogadores[jogadores_list[0]] = 'O' if simbolo_antigo == 'X' else 'X'
                self.jogadores[jogadores_list[1]] = 'X' if simbolo_antigo == 'X' else 'O'
                self.vez_de = jogadores_list[0] if self.jogadores[jogadores_list[0]] == 'X' else jogadores_list[1]
            
            return True

    def obter_estatisticas(self):
        return self.vitorias

    def sair_jogo_com_token(self, id_jogador, token):
        with self.lock:
            if id_jogador not in self.tokens_jogadores:
                return False
            
            if self.tokens_jogadores[id_jogador] != token:
                return False
            
            self.jogo_encerrado = True
            self.motivo_encerramento = f"Jogo encerrado porque {id_jogador} saiu do jogo"
            self.jogadores.clear()
            self.tokens_jogadores.clear()
            self.jogadores_conectados = 0
            
            return True

    def registrar_jogador(self, id_jogador):
        with self.lock:
            if self.jogo_encerrado:
                return "ENCERRADO"
                
            if id_jogador in self.jogadores:
                return self.jogadores[id_jogador]
            
            if self.jogadores_conectados >= 2:
                return "CHEIO"
            
            token = str(uuid.uuid4())
            self.tokens_jogadores[id_jogador] = token
            self.jogadores[id_jogador] = "AGUARDANDO"
            self.jogadores_conectados += 1
            
            if self.jogadores_conectados == 2:
                ids_jogadores = list(self.jogadores.keys())
                random.shuffle(ids_jogadores)
                
                self.jogadores[ids_jogadores[0]] = 'X'
                self.jogadores[ids_jogadores[1]] = 'O'
                
                self.vez_de = ids_jogadores[0]
                self.jogo_iniciado = True
                self.ultima_jogada_time = time.time()
                
                threading.Thread(target=self.verificar_inatividade, daemon=True).start()
                
            return self.jogadores[id_jogador]

    def fazer_jogada(self, id_jogador, jogada):
        return self.fazer_jogada_com_token(id_jogador, self.tokens_jogadores.get(id_jogador, ""), jogada)

    def sair_jogo(self, id_jogador):
        return self.sair_jogo_com_token(id_jogador, self.tokens_jogadores.get(id_jogador, ""))

porta = 8000
server = xmlrpc.server.SimpleXMLRPCServer(("0.0.0.0", porta))
server.register_instance(JogoDaVelha())
print("Servidor do jogo iniciado na porta", porta)
print("Para conectar de outra rede, use seu IP público e porta", porta)
server.serve_forever()