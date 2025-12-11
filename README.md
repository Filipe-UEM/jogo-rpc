# Jogo da Velha Distribuído com RPC em Python

Um jogo da velha multiplayer implementado com arquitetura cliente-servidor usando RPC (Remote Procedure Call) em Python. O servidor central gerencia o estado do jogo, enquanto os clientes se conectam remotamente para jogar.

## Visão Geral

Este projeto implementa um jogo da velha distribuído onde:

- O servidor atua como autoridade central.
- Os clientes não compartilham estado diretamente.
- Toda comunicação é feita via chamadas RPC.

## Arquitetura

- **Cliente-Servidor**: Arquitetura centralizada com servidor como ponto único de verdade.
- **Comunicação**: RPC via XML sobre HTTP.
- **Bibliotecas**: `xmlrpc.server.SimpleXMLRPCServer` (servidor) e `xmlrpc.client.ServerProxy` (cliente).

## Funcionamento do RPC

### No Cliente:

```python
proxy = xmlrpc.client.ServerProxy("http://" + ip_servidor + ":" + str(porta))
resultado = proxy.registrar_jogador(id_jogador)
```

### No Servidor:

```python
server = xmlrpc.server.SimpleXMLRPCServer(("0.0.0.0", porta))
server.register_instance(JogoDaVelha())
server.serve_forever()
```

## Comunicação

Cada interação do jogador é uma requisição RPC ao servidor. Exemplos de métodos disponíveis:

- `registrar_jogador()`
- `fazer_jogada()`
- `obter_tabuleiro()`
- `obter_vez()`

Padrão **request-response**: cada chamada bloqueia até receber resposta.

## Controle de Concorrência

O servidor utiliza **exclusão mútua** (`threading.Lock`) para proteger o estado compartilhado:

```python
self.lock = threading.Lock()

with self.lock:
    # operações críticas
```

Isso previne condições de corrida e garante:

- Jogadas não simultâneas.
- Controle preciso de turnos.
- Consistência do tabuleiro.

## Monitoramento de Inatividade

Uma thread _daemon_ monitora o tempo desde a última jogada:

```python
threading.Thread(target=self.verificar_inatividade, daemon=True).start()
```

Se um jogador ficar inativo por **45 segundos**, o jogo é encerrado automaticamente.

## Tolerância a Falhas

O sistema lida com:

- **Inatividade do jogador**: timeout automático.
- **Desconexão do cliente**: tratamento de exceções no cliente.
- **Saída explícita**: comando `sair` para encerramento limpo.

Exemplo no cliente:

```python
except Exception as e:
    print("Erro de conexão:", e)
```

## Consistência do Estado

O servidor mantém um estado centralizado e consistente, incluindo:

- Tabuleiro atual.
- Símbolos (X/O).
- Controle de turno.
- Status de vitória/empate.

O cliente nunca modifica o estado diretamente, apenas solicita atualizações via `proxy.obter_tabuleiro()`.

## Autenticação e Controle de Acesso

- Tokens únicos são gerados com `uuid` para cada jogador.
- Cada token é vinculado a um jogador.
- Operações sensíveis exigem validação do token.

Isso garante que:

- Um jogador não possa impersonar outro.
- Conexões repetidas sejam bloqueadas.
- Nicks duplicados não interfiram no jogo.

## Como Executar

1. Inicie o servidor em uma máquina acessível:

   ```bash
   python servidor.py
   ```

2. Os clientes conectam-se via:

   ```bash
   python cliente.py <ip_servidor> <porta>
   ```

3. Use um IP público e porta aberta para jogar entre redes diferentes.

---
