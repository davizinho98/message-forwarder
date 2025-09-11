# Message Forwarder

Um projeto Go para encaminhamento de mensagens.

## Descrição

Este é um projeto inicial em Go configurado com Git. O projeto serve como base para desenvolvimento de um sistema de encaminhamento de mensagens.

## Requisitos

- Go 1.19 ou superior
- Git

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

## Execução

Para executar o projeto:

```bash
go run main.go
```

Para compilar o projeto:

```bash
go build -o message-forwarder main.go
```

## Estrutura do Projeto

```
message-forwarder/
├── main.go          # Arquivo principal da aplicação
├── go.mod           # Arquivo de módulo Go
├── .gitignore       # Arquivos ignorados pelo Git
└── README.md        # Este arquivo
```

## Desenvolvimento

Este projeto está em desenvolvimento inicial. Funcionalidades planejadas:

- [ ] Sistema de encaminhamento de mensagens
- [ ] Configuração via arquivos
- [ ] Logging estruturado
- [ ] Testes unitários

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
