# Jogo da Velha (RPC / Sistema Distribuído)

## Visão geral

Este projeto implementa um Jogo da Velha multiplayer simples usando **XML-RPC** para comunicação entre cliente e servidor.
O servidor mantém todo o estado do jogo (tabuleiro, jogadores, vez e estatísticas), enquanto o cliente se conecta remotamente e realiza jogadas através de chamadas RPC.

---

## Arquivos principais

- **server.py** — Implementação do servidor XML-RPC responsável pela lógica do jogo, validação, sincronização e controle do estado.
- **cliente.py** — Cliente que se conecta ao servidor, registra o jogador, exibe o tabuleiro e controla a interação.

---

## Modelo de Comunicação

### 1. Protocolo

A comunicação utiliza **XML-RPC sobre HTTP**, empregando:

- `xmlrpc.server.SimpleXMLRPCServer` no servidor
- `xmlrpc.client.ServerProxy` no cliente

### 2. RPCs expostas pelo servidor

O servidor disponibiliza métodos que podem ser chamados remotamente:

- `registrar_jogador(id_jogador)`
- `obter_jogadores()`
- `obter_tabuleiro()`
- `obter_vez()`
- `fazer_jogada(id_jogador, jogada)`
- `reiniciar_jogo()`
- `sair_jogo(id_jogador)`
- `verificar_jogo_encerrado()`
- `obter_motivo_encerramento()`
- `obter_estatisticas()`

### 3. Comunicação pelo cliente

O cliente cria um `ServerProxy("http://<IP>:<PORTA>")` e então:

- Registra o jogador
- Realiza _polling_ com `time.sleep` para verificar:

  - vez atual
  - alterações no tabuleiro
  - estado de encerramento

- Envia jogadas usando `fazer_jogada()`

---

## Trechos responsáveis (Mapa rápido)

### **Servidor**

- Inicialização RPC:
  `SimpleXMLRPCServer(("0.0.0.0", porta))`
- Registro da instância:
  `server.register_instance(JogoDaVelha())`
- Controle de concorrência:
  `threading.Lock()` com `with self.lock:`
- Controle de inatividade (thread daemon):
  Encerramento automático após 45s sem jogadas.

### **Cliente**

- Conexão RPC:
  `ServerProxy(f"http://{ip}:{porta}")`
- Polling:
  Loops utilizando `obter_jogadores()`, `obter_tabuleiro()`, `obter_vez()` e `verificar_jogo_encerrado()`.

---

## Comportamento de espera e sincronização

### **Cliente — Polling**

- Atualiza estado do jogo com intervalos entre 1–5s.
- Simples de implementar, porém gera tráfego contínuo.

### **Servidor — Sincronização**

- O uso de `Lock` garante que apenas uma thread modifica o tabuleiro por vez, evitando condições de corrida.

---

## Pontos importantes (Considerações para Sistema Distribuído)

1. **Single Point of Failure**
   Se o servidor cair, todo o jogo é perdido.
2. **Escalabilidade**
   XML-RPC + polling não escalam para grande quantidade de jogos simultâneos.
3. **Segurança**
   Não há autenticação e o tráfego é HTTP simples.
4. **Timeouts / falhas de cliente**
   Servidor verifica inatividade e encerra automaticamente.
5. **Idempotência**
   Chamadas duplicadas de registro são tratadas corretamente.

---

## Como executar

### 1. Iniciar o servidor

```bash
python server.py
```

### 2. Iniciar o cliente em outra máquina ou terminal

```bash
python cliente.py <IP_DO_SERVIDOR> 8000 <ID_DO_JOGADOR>
```

Exemplo:

```bash
python cliente.py 192.168.0.10 8000 jogadorA
```

### 3. Iniciar um segundo cliente

```bash
python cliente.py 192.168.0.10 8000 jogadorB
```

---

## Como permitir que OUTRAS máquinas acessem o servidor (Configurar Firewall do Windows)

Para que o servidor seja acessível na rede local (LAN), você precisa liberar a porta do servidor (por padrão, **8000**).

### **Passo a passo (Firewall do Windows)**

### 🔹 1. Abrir o Firewall do Windows

- Pressione **Windows + R**
- Digite: `wf.msc`
- Pressione **Enter**

### 🔹 2. Criar uma regra de entrada

1. No menu à esquerda, clique em **Regras de Entrada**
2. No menu à direita, clique em **Nova Regra**
3. Escolha **Porta** → Avançar
4. Selecione **TCP**
5. Em **Portas locais específicas**, coloque:

   ```
   8000
   ```

6. Avançar
7. Selecione **Permitir a conexão**
8. Avançar
9. Marque as três opções:
   ✔ Domínio
   ✔ Privado
   ✔ Público
10. Avançar
11. Nome da regra:

    ```
    jogo-da-velha-rpc
    ```

12. Concluir

### 🔹 3. Confirmar que a porta abriu

Execute no terminal:

```bash
netstat -an | find "8000"
```

Você deve ver algo como:

```
TCP    0.0.0.0:8000    LISTENING
```

### 🔹 4. Descobrir seu IP para enviar aos jogadores

```bash
ipconfig
```

Anotar o IPv4, por exemplo:

```
IPv4: 192.168.0.10
```

Esse é o IP usado pelos clientes:

```bash
python cliente.py 192.168.0.10 8000 jogador1
```

---
