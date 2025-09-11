package main

import (
	"encoding/json"
	"os"
)

// Config representa a configuração do bot
type Config struct {
	BotToken       string `json:"bot_token"`
	SourceChatID   int64  `json:"source_chat_id"`
	TargetChatID   int64  `json:"target_chat_id"`
	WebhookMode    bool   `json:"webhook_mode"`
	Debug          bool   `json:"debug"`
}

// LoadConfig carrega a configuração do arquivo config.json
func LoadConfig(filename string) (*Config, error) {
	file, err := os.Open(filename)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	var config Config
	decoder := json.NewDecoder(file)
	err = decoder.Decode(&config)
	if err != nil {
		return nil, err
	}

	return &config, nil
}
