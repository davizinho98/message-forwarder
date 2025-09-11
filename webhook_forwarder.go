package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"time"

	tgbotapi "github.com/go-telegram-bot-api/telegram-bot-api/v5"
)

// WebhookMessage representa uma mensagem recebida via webhook
type WebhookMessage struct {
	Text      string    `json:"text"`
	From      string    `json:"from"`
	Timestamp time.Time `json:"timestamp"`
}

// WebhookForwarder encaminha mensagens recebidas via webhook
type WebhookForwarder struct {
	bot          *tgbotapi.BotAPI
	targetChatID int64
}

// NewWebhookForwarder cria um novo forwarder webhook
func NewWebhookForwarder(botToken string, targetChatID int64) (*WebhookForwarder, error) {
	bot, err := tgbotapi.NewBotAPI(botToken)
	if err != nil {
		return nil, err
	}

	return &WebhookForwarder{
		bot:          bot,
		targetChatID: targetChatID,
	}, nil
}

// StartWebhookServer inicia o servidor webhook
func (w *WebhookForwarder) StartWebhookServer(port string) {
	http.HandleFunc("/webhook", w.handleWebhook)
	http.HandleFunc("/health", w.handleHealth)

	log.Printf("🌐 Servidor webhook iniciado na porta %s", port)
	log.Printf("📡 Endpoint: http://localhost:%s/webhook", port)
	log.Printf("💊 Health check: http://localhost:%s/health", port)

	if err := http.ListenAndServe(":"+port, nil); err != nil {
		log.Fatalf("❌ Erro ao iniciar servidor: %v", err)
	}
}

// handleWebhook processa mensagens recebidas via webhook
func (w *WebhookForwarder) handleWebhook(writer http.ResponseWriter, request *http.Request) {
	if request.Method != http.MethodPost {
		http.Error(writer, "Método não permitido", http.StatusMethodNotAllowed)
		return
	}

	var message WebhookMessage
	if err := json.NewDecoder(request.Body).Decode(&message); err != nil {
		log.Printf("❌ Erro ao decodificar JSON: %v", err)
		http.Error(writer, "JSON inválido", http.StatusBadRequest)
		return
	}

	log.Printf("📨 Mensagem recebida via webhook: %s", truncateString(message.Text, 50))

	// Formata e envia para o grupo
	formattedText := fmt.Sprintf("🤖 **Alerta CornerProBot2:**\n\n%s", message.Text)
	
	msg := tgbotapi.NewMessage(w.targetChatID, formattedText)
	msg.ParseMode = "Markdown"

	if _, err := w.bot.Send(msg); err != nil {
		log.Printf("❌ Erro ao enviar mensagem: %v", err)
		http.Error(writer, "Erro ao enviar mensagem", http.StatusInternalServerError)
		return
	}

	log.Printf("✅ Mensagem encaminhada automaticamente!")
	
	// Resposta de sucesso
	response := map[string]string{"status": "success", "message": "Mensagem encaminhada"}
	writer.Header().Set("Content-Type", "application/json")
	json.NewEncoder(writer).Encode(response)
}

// handleHealth endpoint de saúde
func (w *WebhookForwarder) handleHealth(writer http.ResponseWriter, request *http.Request) {
	response := map[string]string{
		"status":    "healthy",
		"timestamp": time.Now().Format(time.RFC3339),
		"service":   "message-forwarder",
	}
	
	writer.Header().Set("Content-Type", "application/json")
	json.NewEncoder(writer).Encode(response)
}
