# Message Forwarder

Um bot Telegram em Go para encaminhar mensagens de conversas privadas para grupos.

## Descrição

Este projeto implementa um bot Telegram que escuta mensagens de uma **conversa privada específica** (como um bot de terceiros que envia notificações) e as reenvia automaticamente para um **grupo de destino**. Perfeito para compartilhar alertas, notificações ou mensagens importantes com uma equipe.

## Funcionalidades

- ✅ Encaminhamento automático de mensagens de **conversa privada** para **grupo**
- ✅ Ideal para bots de terceiros (alertas, notificações, monitoramento)
- ✅ Suporte a múltiplos tipos de mídia (fotos, vídeos, documentos, áudio, etc.)
- ✅ Formatação das mensagens com informações do remetente original
- ✅ Logs detalhados de atividade
- ✅ Configuração via arquivo JSON
- ✅ Mínimas dependências (apenas a biblioteca oficial do Telegram)

## Requisitos

- Go 1.19 ou superior
- Bot Token do Telegram (obtido via @BotFather)
- ID da conversa privada fonte (bot de terceiros)
- ID do grupo de destino

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

### 2. Obter IDs da Conversa e Grupo

**Para obter o ID da conversa privada (bot de terceiros):**

1. Adicione seu bot à conversa com o bot de terceiros (se possível) ou
2. Execute o bot temporariamente com `debug: true`
3. Inicie uma conversa com o bot de terceiros ou aguarde ele enviar uma mensagem
4. O ID da conversa aparecerá nos logs (será um número positivo)

**Para obter o ID do grupo de destino:**

1. Adicione o bot ao grupo de destino
2. Execute o bot temporariamente com `debug: true`
3. Envie uma mensagem no grupo
4. O ID aparecerá nos logs (será um número negativo)

### 3. Arquivo de Configuração

Edite o arquivo `config.json`:

```json
{
  "bot_token": "1234567890:ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghi",
  "source_chat_id": 123456789,
  "target_chat_id": -1234567890,
  "debug": true
}
```

- `bot_token`: Token do seu bot obtido via @BotFather
- `source_chat_id`: ID da conversa privada (bot de terceiros) - **número positivo**
- `target_chat_id`: ID do grupo de destino - **número negativo**
- `debug`: Define se deve mostrar logs detalhados (útil para descobrir IDs)

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
3. Filtra mensagens apenas da conversa privada fonte (bot de terceiros)
4. Verifica se é realmente uma conversa privada (não grupo)
5. Formata a mensagem incluindo informações do remetente original
6. Reenvia a mensagem para o grupo de destino
7. Registra logs da atividade

## Casos de Uso Comuns

- 🚨 **Alertas de monitoramento**: Receber alertas de bots de monitoramento e compartilhar com a equipe
- 📊 **Notificações de sistemas**: Encaminhar notificações de bots de CI/CD, servidores, etc.
- 💰 **Alertas financeiros**: Compartilhar alertas de preços, investimentos ou transações
- 🔔 **Notificações personalizadas**: Qualquer bot que envie notificações importantes

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
- Certifique-se de que o bot tem acesso à conversa privada fonte
- Verifique se os IDs estão corretos (conversa privada = positivo, grupo = negativo)

### Erro de permissão

- O bot precisa conseguir receber mensagens da conversa privada fonte
- O bot precisa ter permissão para enviar mensagens no grupo de destino
- Adicione o bot como administrador do grupo de destino se necessário

### Como obter IDs corretos

1. Defina `debug: true` no config.json
2. Execute o bot
3. Para conversa privada: envie uma mensagem para o bot ou aguarde o bot de terceiros enviar
4. Para grupo: envie uma mensagem no grupo onde o bot está
5. Os IDs aparecerão nos logs

### Diferença entre IDs

- **Conversa privada**: ID positivo (ex: 123456789)
- **Grupo/Canal**: ID negativo (ex: -1234567890)

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
