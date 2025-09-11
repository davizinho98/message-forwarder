package main

import (
	"log"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

func main() {
	log.Println("🚀 Message Forwarder - Iniciando...")

	// Carrega a configuração
	config, err := LoadConfig("config.json")
	if err != nil {
		log.Fatalf("❌ Erro ao carregar configuração: %v", err)
	}

	// Verifica se deve usar modo webhook
	if config.WebhookMode {
		log.Println("🌐 Modo Webhook ativado")
		
		// Cria o forwarder webhook
		forwarder, err := NewWebhookForwarder(config.BotToken, config.TargetChatID)
		if err != nil {
			log.Fatalf("❌ Erro ao criar webhook forwarder: %v", err)
		}

		log.Printf("🎯 Encaminhando para grupo: %d", config.TargetChatID)
		log.Println("📋 Configure o CornerProBot2 para enviar webhook para:")
		log.Printf("   http://seu_ip:8080/webhook")
		
		// Inicia servidor webhook
		forwarder.StartWebhookServer("8080")
		return
	}

	// Modo bot tradicional
	log.Println("🤖 Modo Bot ativado")
	
	// Cria o bot
	bot, err := tgbotapi.NewBotAPI(config.BotToken)
	if err != nil {
		log.Fatalf("❌ Erro ao criar bot: %v", err)
	}

	bot.Debug = config.Debug
	log.Printf("✅ Bot autorizado como %s", bot.Self.UserName)

	// Inicia o message forwarder
	startMessageForwarder(bot, config)
}

// startMessageForwarder inicia o processo de escuta e reenvio de mensagens
func startMessageForwarder(bot *tgbotapi.BotAPI, config *Config) {
	log.Printf("👂 Aguardando mensagens enviadas para o bot (de qualquer usuário/bot) para reenviar para o grupo (ID: %d)", 
		config.TargetChatID)

	// Configura updates
	u := tgbotapi.NewUpdate(0)
	u.Timeout = 60

	updates := bot.GetUpdatesChan(u)

	for update := range updates {
		if config.Debug {
			log.Printf("🔔 Update recebido: %+v", update)
		}
		if update.Message == nil {
			continue
		}

		message := update.Message

		// Se source_chat_id for 0, aceita qualquer conversa privada
		// Senão, filtra por ID específico
		if config.SourceChatID != 0 {
			if message.Chat.ID != config.SourceChatID {
				if config.Debug {
					log.Printf("🔍 Mensagem ignorada - Chat ID: %d (esperado: %d)", 
						message.Chat.ID, config.SourceChatID)
				}
				continue
			}
		}

		// Verifica se é realmente uma conversa privada (não grupo)
		if !message.Chat.IsPrivate() {
			if config.Debug {
				log.Printf("⚠️ Mensagem ignorada - Não é conversa privada (Chat ID: %d)", message.Chat.ID)
			}
			continue
		}

		// Se chegou até aqui, mostra informações do chat para descobrir IDs
		if config.Debug {
			log.Printf("📍 Chat encontrado - ID: %d, Tipo: %s, Username: %s, Nome: %s %s", 
				message.Chat.ID, message.Chat.Type, message.Chat.UserName, 
				message.Chat.FirstName, message.Chat.LastName)
		}

		// Log da mensagem recebida
		log.Printf("📨 Nova mensagem de %s: %s", 
			message.From.UserName, truncateString(message.Text, 50))

		// Reenvia a mensagem
		forwardErr := forwardMessage(bot, message, config.TargetChatID)
		if forwardErr != nil {
			log.Printf("❌ Erro ao reenviar mensagem: %v", forwardErr)
		} else {
			log.Printf("✅ Mensagem reenviada com sucesso")
		}
		err := forwardMessage(bot, message, config.TargetChatID)
		if err != nil {
			log.Printf("❌ Erro ao reenviar mensagem: %v", err)
		} else {
			log.Printf("✅ Mensagem reenviada com sucesso")
		}
	}
}

// forwardMessage reenvia uma mensagem para o chat de destino
func forwardMessage(bot *tgbotapi.BotAPI, originalMessage *tgbotapi.Message, targetChatID int64) error {
	var msg tgbotapi.Chattable

	// Determina o tipo de mensagem e cria a mensagem apropriada
	switch {
	case originalMessage.Text != "":
		// Mensagem de texto
		text := formatMessage(originalMessage)
		msg = tgbotapi.NewMessage(targetChatID, text)
		
	case originalMessage.Photo != nil:
		// Foto
		photos := originalMessage.Photo
		if len(photos) > 0 {
			// Pega a foto de maior qualidade
			photo := photos[len(photos)-1]
			photoMsg := tgbotapi.NewPhoto(targetChatID, tgbotapi.FileID(photo.FileID))
			photoMsg.Caption = formatMessage(originalMessage)
			msg = photoMsg
		}
		
	case originalMessage.Document != nil:
		// Documento
		docMsg := tgbotapi.NewDocument(targetChatID, tgbotapi.FileID(originalMessage.Document.FileID))
		docMsg.Caption = formatMessage(originalMessage)
		msg = docMsg
		
	case originalMessage.Video != nil:
		// Vídeo
		videoMsg := tgbotapi.NewVideo(targetChatID, tgbotapi.FileID(originalMessage.Video.FileID))
		videoMsg.Caption = formatMessage(originalMessage)
		msg = videoMsg
		
	case originalMessage.Audio != nil:
		// Áudio
		audioMsg := tgbotapi.NewAudio(targetChatID, tgbotapi.FileID(originalMessage.Audio.FileID))
		audioMsg.Caption = formatMessage(originalMessage)
		msg = audioMsg
		
	case originalMessage.Voice != nil:
		// Mensagem de voz
		voiceMsg := tgbotapi.NewVoice(targetChatID, tgbotapi.FileID(originalMessage.Voice.FileID))
		msg = voiceMsg
		
	case originalMessage.Sticker != nil:
		// Sticker
		stickerMsg := tgbotapi.NewSticker(targetChatID, tgbotapi.FileID(originalMessage.Sticker.FileID))
		msg = stickerMsg
		
	default:
		// Tipo de mensagem não suportado
		text := formatMessage(originalMessage)
		if text == "" {
			text = "📎 Mensagem de tipo não suportado"
		}
		msg = tgbotapi.NewMessage(targetChatID, text)
	}

	_, err := bot.Send(msg)
	return err
}

// formatMessage formata a mensagem com informações do remetente
func formatMessage(message *tgbotapi.Message) string {
	var username string
	if message.From.UserName != "" {
		username = "@" + message.From.UserName
	} else {
		username = message.From.FirstName
		if message.From.LastName != "" {
			username += " " + message.From.LastName
		}
	}

	var text string
	if message.Text != "" {
		text = message.Text
	} else if message.Caption != "" {
		text = message.Caption
	}

	if text != "" {
		return "👤 " + username + ":\n" + text
	}
	
	return "👤 " + username
}

// truncateString trunca uma string se ela for muito longa
func truncateString(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen] + "..."
}
