#!/usr/bin/env python3
"""
Script para buscar dados de matchday diariamente às 05:10
Salva os últimos 10 dias de dados em formato JSON
"""

import requests
import json
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import pytz

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Timezone de Brasília
BRASILIA_TZ = pytz.timezone('America/Sao_Paulo')

# Diretório para salvar os arquivos JSON
DATA_DIR = Path(__file__).parent / "matchday_data"
DATA_DIR.mkdir(exist_ok=True)

def fetch_matchday():
    """Busca dados do matchday da API"""
    url = 'https://classic.cornerprobet.com/actions/games/getMatchday.php'
    
    headers = {
        'Accept': '*/*',
        'Accept-Language': 'pt-BR,pt;q=0.9',
        'Connection': 'keep-alive',
        'Content-Type': 'application/json',
        'Origin': 'https://classic.cornerprobet.com',
        'Referer': 'https://classic.cornerprobet.com/pt/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'X-Limit-Remaining': '0.9695707908197733',
        'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"'
    }
    
    cookies = {
        'PHPSESSID': 'osl039a36pg6ff06u4ngfusqc7',
        '_fbp': 'fb.1.1761357809122.54146310124754963',
        '_gcl_au': '1.1.247902595.1761358273',
        '_gid': 'GA1.2.1161563047.1761358274',
        '_ga_ZEJ7MW3BNF': 'GS2.1.s1761358272$o1$g1$t1761359634$j60$l0$h0',
        '_ga': 'GA1.2.1588281631.1761358273'
    }
    
    payload = {
        "day": 0,
        "token": "282563_86e802e137"
    }
    
    try:
        logger.info("🔄 Iniciando busca de dados do matchday...")
        response = requests.post(url, headers=headers, cookies=cookies, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        logger.info("✅ Dados recebidos com sucesso!")
        return data
        
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Erro ao buscar dados: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"❌ Erro ao decodificar JSON: {e}")
        return None

def save_matchday_data(data):
    """Salva os dados em arquivo JSON com nome baseado na data de Brasília"""
    if not data:
        logger.warning("⚠️  Nenhum dado para salvar")
        return
    
    # Obtém data/hora atual no timezone de Brasília
    now = datetime.now(BRASILIA_TZ)
    filename = now.strftime("%d-%m-%Y.json")
    filepath = DATA_DIR / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Dados salvos em: {filepath}")
        
        # Limpar arquivos antigos (manter apenas últimos 10 dias)
        cleanup_old_files()
        
    except Exception as e:
        logger.error(f"❌ Erro ao salvar arquivo: {e}")

def cleanup_old_files():
    """Remove arquivos mais antigos que 10 dias"""
    try:
        now = datetime.now(BRASILIA_TZ)
        cutoff_date = now - timedelta(days=10)
        
        deleted_count = 0
        for filepath in DATA_DIR.glob("*.json"):
            try:
                # Extrai data do nome do arquivo (formato: dd-mm-yyyy.json)
                filename = filepath.stem  # Remove .json
                file_date = datetime.strptime(filename, "%d-%m-%Y")
                # Adiciona timezone de Brasília
                file_date = BRASILIA_TZ.localize(file_date)
                
                if file_date < cutoff_date:
                    filepath.unlink()
                    deleted_count += 1
                    logger.info(f"🗑️  Arquivo antigo removido: {filepath.name}")
                    
            except ValueError:
                # Ignora arquivos com nome inválido
                logger.warning(f"⚠️  Arquivo com nome inválido ignorado: {filepath.name}")
                continue
        
        if deleted_count > 0:
            logger.info(f"✅ {deleted_count} arquivo(s) antigo(s) removido(s)")
        else:
            logger.info("✅ Nenhum arquivo antigo para remover")
            
    except Exception as e:
        logger.error(f"❌ Erro ao limpar arquivos antigos: {e}")

def run_daily_task():
    """Executa a tarefa diária"""
    logger.info("=" * 80)
    logger.info("🚀 EXECUTANDO TAREFA DIÁRIA - BUSCA DE MATCHDAY")
    logger.info("=" * 80)
    
    # Busca os dados
    data = fetch_matchday()
    
    # Salva os dados
    if data:
        save_matchday_data(data)
    
    logger.info("=" * 80)
    logger.info("✅ TAREFA DIÁRIA CONCLUÍDA")
    logger.info("=" * 80)

def main():
    """Função principal - agenda e executa as tarefas"""
    logger.info("🤖 Iniciando Daily Matchday Fetcher...")
    logger.info(f"📁 Diretório de dados: {DATA_DIR}")
    logger.info(f"🕐 Horário agendado: 05:10 (Brasília)")
    logger.info(f"📅 Mantendo últimos 10 dias de dados")
    
    # Agenda a tarefa para 05:10 todos os dias
    schedule.every().day.at("05:10").do(run_daily_task)
    
    logger.info("✅ Tarefa agendada com sucesso!")
    logger.info("👂 Aguardando horário de execução... (Pressione Ctrl+C para parar)")
    
    # Executa uma vez imediatamente para teste (opcional)
    # Comente a linha abaixo se não quiser executar imediatamente
    logger.info("\n🧪 EXECUTANDO TESTE INICIAL...")
    run_daily_task()
    
    # Loop principal
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Verifica a cada minuto
    except KeyboardInterrupt:
        logger.info("\n🛑 Parando Daily Matchday Fetcher...")

if __name__ == "__main__":
    main()

