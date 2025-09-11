# Message Forwarder

Um bot Telegram em Go para encaminhar mensagens automaticamente entre grupos.

## Descrição

Este projeto implementa um bot Telegram que escuta mensagens de um grupo específico e as reenvia automaticamente para outro grupo. O bot suporta diferentes tipos de mensagem incluindo texto, fotos, vídeos, documentos, áudio, mensagens de voz e stickers.

## Funcionalidades

- ✅ Encaminhamento automático de mensagens entre grupos
- ✅ Suporte a múltiplos tipos de mídia (fotos, vídeos, documentos, áudio, etc.)
- ✅ Formatação das mensagens com informações do remetente original
- ✅ Logs detalhados de atividade
- ✅ Configuração via arquivo JSON
- ✅ Mínimas dependências (apenas a biblioteca oficial do Telegram)

## Requisitos

- Go 1.19 ou superior
- Bot Token do Telegram (obtido via @BotFather)
- IDs dos grupos fonte e destino

## Instalação

1. Clone o repositório:
```bash
git clone <url-do-repositorio>
cd message-forwarder
```

2. Instale as dependências:
```bash
go mod download
```

3. Configure o bot:
```bash
cp config.example.json config.json
# Edite config.json com suas configurações
```

## Configuração

### 1. Criar Bot no Telegram

1. Abra o Telegram e procure por `@BotFather`
2. Digite `/newbot` e siga as instruções
3. Copie o token fornecido

### 2. Obter IDs dos Grupos

Para obter o ID de um grupo:

1. Adicione o bot ao grupo
2. Execute o bot temporariamente com `debug: true`
3. Envie uma mensagem no grupo
4. O ID aparecerá nos logs

### 3. Arquivo de Configuração

Edite o arquivo `config.json`:

```json
{
  "bot_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
  "source_chat_id": -1234567890,
  "target_chat_id": -9876543210,
  "debug": false
}
```

- `bot_token`: Token do seu bot obtido via @BotFather
- `source_chat_id`: ID do grupo de onde as mensagens serão copiadas
- `target_chat_id`: ID do grupo para onde as mensagens serão enviadas
- `debug`: Define se deve mostrar logs detalhados

## Execução

Para executar o bot:

```bash
go run main.go config.go
```

Para compilar:

```bash
go build -o message-forwarder *.go
./message-forwarder
```

## Estrutura do Projeto

```
message-forwarder/
├── main.go              # Arquivo principal com lógica do bot
├── config.go            # Gerenciamento de configuração
├── config.example.json  # Exemplo de configuração
├── config.json          # Sua configuração (criado por você)
├── go.mod               # Dependências do Go
├── .gitignore           # Arquivos ignorados pelo Git
└── README.md            # Este arquivo
```

## Como Funciona

1. O bot conecta-se ao Telegram usando o token fornecido
2. Escuta continuamente por novas mensagens
3. Filtra mensagens apenas do grupo fonte configurado
4. Formata a mensagem incluindo informações do remetente original
5. Reenvia a mensagem para o grupo destino
6. Registra logs da atividade

## Tipos de Mensagem Suportados

- ✅ Texto simples
- ✅ Fotos
- ✅ Vídeos
- ✅ Documentos
- ✅ Arquivos de áudio
- ✅ Mensagens de voz
- ✅ Stickers
- ✅ Mensagens com legenda

## Segurança

- Mantenha seu `config.json` seguro e nunca o compartilhe
- O arquivo `config.json` está no `.gitignore` para evitar commits acidentais
- Use o arquivo `config.example.json` como template

## Dependências

Este projeto usa apenas uma dependência externa:

- `github.com/go-telegram-bot-api/telegram-bot-api/v5` - Biblioteca oficial do Telegram Bot API

## Troubleshooting

### Bot não responde
- Verifique se o token está correto
- Certifique-se de que o bot foi adicionado aos grupos
- Verifique se os IDs dos grupos estão corretos

### Erro de permissão
- O bot precisa ter permissão para ler mensagens no grupo fonte
- O bot precisa ter permissão para enviar mensagens no grupo destino

### Como obter IDs dos grupos
1. Defina `debug: true` no config.json
2. Execute o bot
3. Envie uma mensagem em qualquer grupo onde o bot está
4. O ID aparecerá nos logs

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
