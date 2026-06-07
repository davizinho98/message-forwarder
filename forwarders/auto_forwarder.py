#!/usr/bin/env python3
"""
Message Forwarder Automático - Versão Python
Monitora mensagens de um bot específico e encaminha automaticamente para um grupo.
"""

import asyncio
import json
import logging
import os
import re
import requests
import sys
from datetime import datetime
from pathlib import Path
from unidecode import unidecode
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from data import invalid_leagues, nationality_countries

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def normalize_text(text):
    """
    Normaliza texto removendo acentos, convertendo para minúsculo e removendo espaços extras
    """
    if not text:
        return ""
    return unidecode(text.lower().strip())

# Diretórios
BASE_DIR = ROOT_DIR
MATCHDAY_DATA_DIR = BASE_DIR / "matchday_data"
ANALYSIS_HTML_DIR = BASE_DIR / "analysis_html"
EQUIVALENCES_DIR = BASE_DIR / "equivalences"
ANALYSIS_HTML_DIR.mkdir(exist_ok=True)
EQUIVALENCES_DIR.mkdir(exist_ok=True)

class LeagueEquivalenceCache:
    """Gerencia o cache de equivalências entre nomes de ligas"""
    
    def __init__(self):
        self.cache_file = EQUIVALENCES_DIR / "league_equivalences.json"
        self.equivalences = self._load_cache()
    
    def _load_cache(self):
        """Carrega o cache de equivalências do arquivo"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Erro ao carregar cache de ligas: {e}")
        return {}
    
    def _save_cache(self):
        """Salva o cache de equivalências no arquivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.equivalences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache de ligas: {e}")
    
    def add_equivalence(self, message_league, json_league):
        """Adiciona uma nova equivalência entre liga da mensagem e do JSON"""
        message_key = normalize_text(message_league)
        if message_key not in self.equivalences:
            self.equivalences[message_key] = json_league
            self._save_cache()
            logger.info(f"💾 Nova equivalência de liga salva: '{message_league}' → '{json_league}'")
    
    def get_equivalent(self, message_league):
        """Busca a equivalência de uma liga da mensagem"""
        message_key = normalize_text(message_league)
        return self.equivalences.get(message_key)

class TeamEquivalenceCache:
    """Gerencia o cache de equivalências entre nomes de equipes"""
    
    def __init__(self):
        self.cache_file = EQUIVALENCES_DIR / "team_equivalences.json"
        self.equivalences = self._load_cache()
    
    def _load_cache(self):
        """Carrega o cache de equivalências do arquivo"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"⚠️  Erro ao carregar cache de equipes: {e}")
        return {}
    
    def _save_cache(self):
        """Salva o cache de equivalências no arquivo"""
        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.equivalences, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"❌ Erro ao salvar cache de equipes: {e}")
    
    def add_equivalence(self, message_team, json_team):
        """Adiciona uma nova equivalência entre equipe da mensagem e do JSON"""
        message_key = normalize_text(message_team)
        if message_key not in self.equivalences:
            self.equivalences[message_key] = json_team
            self._save_cache()
            logger.info(f"💾 Nova equivalência de equipe salva: '{message_team}' → '{json_team}'")
    
    def get_equivalent(self, message_team):
        """Busca a equivalência de uma equipe da mensagem"""
        message_key = normalize_text(message_team)
        return self.equivalences.get(message_key)

# Instâncias globais dos caches
league_cache = LeagueEquivalenceCache()
team_cache = TeamEquivalenceCache()

def clean_team_name(nome):
    """
    Limpa o nome da equipe conforme as regras:
    - Remove acentos
    - Substitui espaços por traços
    - Remove caracteres especiais que não sejam letras
    """
    # Remove acentos
    nome_sem_acento = unidecode(nome)
    
    # Remove caracteres especiais que não sejam letras, números ou espaços
    nome_limpo = re.sub(r'[^a-zA-Z0-9\s]', '', nome_sem_acento)
    
    # Substitui espaços por traços
    nome_final = nome_limpo.replace(' ', '-')
    
    return nome_final

def extract_league_and_teams(message_text):
    """
    Extrai a liga e os times da mensagem.
    Formato esperado:
    Linha 3: 🏆 League Name
    Linha 4: ⚽ Home Team Name vs Away Team Name
    """
    if not message_text:
        return None, None, None
    
    lines = message_text.split('\n')
    
    if len(lines) < 4:
        return None, None, None
    
    # Linha 3 (índice 2): Liga
    league_line = lines[2].strip()
    league = league_line.replace('🏆', '').strip()
    
    # Linha 4 (índice 3): Times
    teams_line = lines[3].strip()
    teams_line = teams_line.replace('⚽', '').strip()
    
    # Separar times por "vs"
    if ' vs ' in teams_line:
        parts = teams_line.split(' vs ')
        home_team = parts[0].strip()
        away_team = parts[1].strip()
        return league, home_team, away_team
    
    return None, None, None

def convert_league_name(league_name):
    """
    Converte o nome da liga usando o dicionário nationality_countries.
    Pega a primeira palavra da liga e procura no dicionário.
    Se encontrar, substitui pela versão do dicionário.
    
    Retorna: (league_convertida, emoji_validade)
    """
    if not league_name:
        return league_name, "❌"
    
    # Pegar a primeira palavra da liga
    first_word = league_name.split()[0]
    
    # Procurar no dicionário nationality_countries
    converted_league = league_name
    if first_word in nationality_countries.NACIONALITY_COUNTRIES:
        # Substituir a primeira palavra pela versão do dicionário
        converted_first_word = nationality_countries.NACIONALITY_COUNTRIES[first_word]
        words = league_name.split()
        words[0] = converted_first_word
        converted_league = " ".join(words)
        logger.info(f"🔄 Liga convertida: '{league_name}' → '{converted_league}'")
    
    # Verificar se a liga original é inválida (usando a liga original, não convertida)
    if first_word in invalid_leagues.INVALID_LEAGUES or league_name in invalid_leagues.INVALID_LEAGUES:
        emoji_validade = "❌"
        logger.info(f"❌ Liga inválida detectada: '{league_name}'")
    else:
        emoji_validade = "✅"
        logger.info(f"✅ Liga válida: '{league_name}'")
    
    return converted_league, emoji_validade

def get_country_from_league(league):
    """
    Extrai o nome do país da liga (primeira palavra)
    """
    if not league:
        return ""
    return league.split()[0]

def get_country_variations(country):
    """
    Retorna variações do nome do país para melhorar a busca
    """
    country_mappings = {
        'spanish': ['spain', 'spanish'],
        'spain': ['spain', 'spanish'],
        'brazilian': ['brazil', 'brazilian'],
        'brazil': ['brazil', 'brazilian'],
        'argentinian': ['argentina', 'argentinian'],
        'argentina': ['argentina', 'argentinian'],
        'german': ['germany', 'german'],
        'germany': ['germany', 'german'],
        'french': ['france', 'french'],
        'france': ['france', 'french'],
        'italian': ['italy', 'italian'],
        'italy': ['italy', 'italian'],
        'english': ['england', 'english'],
        'england': ['england', 'english'],
    }
    
    country_norm = normalize_text(country)
    return country_mappings.get(country_norm, [country_norm])

def has_youth_category(text):
    """
    Verifica se o texto contém indicadores de categorias de base.
    Ex: U19, U20, U21, U23, Sub-19, Sub-20, etc.
    """
    if not text:
        return False
    text_lower = text.lower()
    # Padrões de categorias de base
    youth_patterns = [
        r'\bu\d{2}\b',  # U19, U20, U21, U23, etc.
        r'\bsub[- ]?\d{2}\b',  # Sub-19, Sub 19, Sub19
        r'\bjunior\b',
        r'\bjuniores\b',
        r'\breservas?\b',
        r'\byouth\b',
        r'\bacademy\b',
        r'\bii\b',  # Time II (reserva)
        r'\bb\b',  # Time B
    ]
    for pattern in youth_patterns:
        if re.search(pattern, text_lower):
            return True
    return False


def find_game_in_matchday(league, home_team, away_team):
    """
    Busca o jogo no arquivo JSON do matchday com estratégias de busca melhoradas.
    
    Estratégias de busca:
    1. Busca direta por nome da liga
    2. Busca por país (primeira palavra da liga)
    3. Para equipes: nome completo, depois primeiro nome
    4. Normalização com remoção de acentos
    5. Prioriza jogos de equipes principais sobre categorias de base (U19, U20, etc.)
    
    Retorna: (home_name, away_name, game_id) ou (None, None, None)
    """
    try:
        # Encontrar o arquivo JSON mais recente
        json_files = list(MATCHDAY_DATA_DIR.glob("*.json"))
        if not json_files:
            logger.warning("⚠️  Nenhum arquivo JSON encontrado em matchday_data/")
            return None, None, None
        
        # Pegar o arquivo mais recente
        latest_json = max(json_files, key=lambda p: p.stat().st_mtime)
        logger.info(f"📄 Lendo arquivo: {latest_json.name}")
        
        with open(latest_json, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Navegar na estrutura: data -> horários -> ligas -> games
        if 'data' not in data:
            logger.warning("⚠️  Chave 'data' não encontrada no JSON")
            return None, None, None
        
        # Normalizar nomes para comparação
        league_normalized = normalize_text(league)
        home_normalized = normalize_text(home_team)
        away_normalized = normalize_text(away_team)
        
        # Preparar variações dos nomes das equipes
        home_words = home_team.split() if home_team else []
        away_words = away_team.split() if away_team else []
        
        home_first_word = home_words[0] if len(home_words) > 0 else ""
        home_second_word = home_words[1] if len(home_words) > 1 else ""
        away_first_word = away_words[0] if len(away_words) > 0 else ""
        away_second_word = away_words[1] if len(away_words) > 1 else ""
        
        home_first_normalized = normalize_text(home_first_word)
        home_second_normalized = normalize_text(home_second_word)
        away_first_normalized = normalize_text(away_first_word)
        away_second_normalized = normalize_text(away_second_word)
        
        # Extrair país da liga para busca alternativa
        country = get_country_from_league(league)
        country_normalized = normalize_text(country)
        
        logger.info(f"🔍 Buscando jogo:")
        logger.info(f"   Liga: '{league}' (normalizada: '{league_normalized}')")
        logger.info(f"   País: '{country}' (normalizado: '{country_normalized}')")
        logger.info(f"   Casa: '{home_team}' (normalizada: '{home_normalized}')")
        logger.info(f"     Primeiro: '{home_first_word}' (normalizado: '{home_first_normalized}')")
        logger.info(f"     Segundo: '{home_second_word}' (normalizado: '{home_second_normalized}')")
        logger.info(f"   Fora: '{away_team}' (normalizada: '{away_normalized}')")
        logger.info(f"     Primeiro: '{away_first_word}' (normalizado: '{away_first_normalized}')")
        logger.info(f"     Segundo: '{away_second_word}' (normalizado: '{away_second_normalized}')")
        
        def check_team_match(game_home, game_away, home_target, away_target):
            """Verifica se as equipes correspondem com busca exata"""
            game_home_norm = normalize_text(game_home)
            game_away_norm = normalize_text(game_away)
            
            return (game_home_norm == normalize_text(home_target) and 
                    game_away_norm == normalize_text(away_target))
        
        def check_team_match_flexible(game_home, game_away, home_target, away_target):
            """Verifica se as equipes correspondem com busca flexível mais rigorosa"""
            if not home_target or not away_target:
                return False
                
            game_home_norm = normalize_text(game_home)
            game_away_norm = normalize_text(game_away)
            home_target_norm = normalize_text(home_target)
            away_target_norm = normalize_text(away_target)
            
            # Rejeitar se os nomes forem muito curtos (evita falsos positivos como "CA")
            MIN_LENGTH = 3
            if len(home_target_norm) < MIN_LENGTH or len(away_target_norm) < MIN_LENGTH:
                return False
            
            # Busca bidirecional: se o target está contido no game OU se o game está contido no target
            home_match = (home_target_norm in game_home_norm or game_home_norm in home_target_norm)
            away_match = (away_target_norm in game_away_norm or game_away_norm in away_target_norm)
            
            return home_match and away_match
        
        def is_reasonable_match(game_home, game_away, home_target, away_target, strategy_name, game_league=None):
            """Verifica se o match encontrado é razoável (evita falsos positivos)"""
            # Para busca geral (fallback), ser mais rigoroso
            if strategy_name == "busca geral":
                game_home_norm = normalize_text(game_home)
                game_away_norm = normalize_text(game_away)
                home_target_norm = normalize_text(home_target)
                away_target_norm = normalize_text(away_target)
                
                # Calcular similaridade básica (quantos caracteres coincidem)
                home_similarity = len(set(home_target_norm) & set(game_home_norm)) / max(len(home_target_norm), len(game_home_norm))
                away_similarity = len(set(away_target_norm) & set(game_away_norm)) / max(len(away_target_norm), len(game_away_norm))
                
                # Requerer pelo menos 50% de similaridade para busca geral
                MIN_SIMILARITY = 0.5
                if home_similarity < MIN_SIMILARITY or away_similarity < MIN_SIMILARITY:
                    logger.debug(f"🚫 Match rejeitado por baixa similaridade: {home_similarity:.2f}, {away_similarity:.2f}")
                    return False
                
                # Validação adicional: verificar se a liga do jogo não está em um país completamente diferente
                if game_league:
                    league_words = normalize_text(league).split()
                    game_league_words = normalize_text(game_league).split()
                    
                    # Se a liga original tem indicação de país, verificar compatibilidade
                    if len(league_words) > 0 and len(game_league_words) > 0:
                        original_country = league_words[0]  # Primeira palavra da liga original
                        
                        # Usar NACIONALITY_COUNTRIES para obter países conhecidos
                        known_countries = set([normalize_text(c) for c in nationality_countries.NACIONALITY_COUNTRIES.values()])
                        known_nationalities = set([normalize_text(n) for n in nationality_countries.NACIONALITY_COUNTRIES.keys()])
                        all_known = known_countries | known_nationalities
                        
                        # Se o país original é conhecido e a liga do jogo não contém referência compatível
                        if original_country in all_known:
                            # Verificar se há alguma compatibilidade entre os países
                            has_country_match = False
                            for word in game_league_words:
                                if word in all_known:
                                    has_country_match = True
                                    break
                            
                            if not has_country_match:
                                logger.debug(f"🚫 Match rejeitado por incompatibilidade de país: '{league}' vs '{game_league}'")
                                return False
            
            return True
        
        def try_all_team_combinations(game_home, game_away, strategy_name, game_league=None):
            """
            Tenta todas as combinações de nomes das equipes
            Primeiro tenta busca exata, depois busca flexível
            Retorna: (success, match_description) ou (False, "")
            """
            combinations = [
                (home_team, away_team, "nomes completos"),
                (home_first_word, away_first_word, "primeiros nomes"),
                (home_first_word, away_second_word, "primeiro casa + segundo fora"),
                (home_second_word, away_second_word, "segundos nomes"),
                (home_second_word, away_first_word, "segundo casa + primeiro fora"),
            ]
            
            # Primeiro: tentativa com busca exata
            for home_target, away_target, desc in combinations:
                if home_target and away_target:
                    if check_team_match(game_home, game_away, home_target, away_target):
                        return True, f"{desc} (exata)"
            
            # Segundo: tentativa com busca flexível (substring)
            for home_target, away_target, desc in combinations:
                if home_target and away_target:
                    if check_team_match_flexible(game_home, game_away, home_target, away_target):
                        # Validar se é um match razoável
                        if is_reasonable_match(game_home, game_away, home_target, away_target, strategy_name, game_league):
                            return True, f"{desc} (flexível)"
                        else:
                            logger.debug(f"🚫 Match flexível rejeitado: {game_home} vs {game_away}")
                            continue
            
            return False, ""
        
        def select_best_match(matches, search_has_youth):
            """
            Seleciona o melhor match dentre os encontrados.
            Prioriza jogos de equipes principais se a busca não especifica categoria de base.
            
            Args:
                matches: lista de tuplas (game_home, game_away, game_id, match_desc, league_name)
                search_has_youth: se a busca original contém indicador de categoria de base
            
            Retorna: (game_home, game_away, game_id, match_desc, league_name) ou None
            """
            if not matches:
                return None
            
            if len(matches) == 1:
                return matches[0]
            
            # Separar jogos por categoria
            main_team_matches = []
            youth_team_matches = []
            
            for match in matches:
                game_home, game_away, game_id, match_desc, league_name = match
                game_is_youth = has_youth_category(game_home) or has_youth_category(game_away)
                
                if game_is_youth:
                    youth_team_matches.append(match)
                else:
                    main_team_matches.append(match)
            
            logger.info(f"📊 Encontrados {len(matches)} jogos correspondentes:")
            logger.info(f"   - Times principais: {len(main_team_matches)}")
            logger.info(f"   - Categorias de base: {len(youth_team_matches)}")
            
            # Se a busca especifica categoria de base, priorizar youth
            if search_has_youth:
                logger.info(f"🎯 Busca especifica categoria de base, priorizando jogos U19/U20/etc.")
                if youth_team_matches:
                    return youth_team_matches[0]
                return main_team_matches[0] if main_team_matches else matches[0]
            else:
                # Busca NÃO especifica categoria de base, priorizar time principal
                logger.info(f"🎯 Busca NÃO especifica categoria de base, priorizando times principais")
                if main_team_matches:
                    return main_team_matches[0]
                # Se só tem jogos de base, retornar mesmo assim (pode ser o que o usuário quer)
                return youth_team_matches[0] if youth_team_matches else matches[0]
        
        # Verificar se a busca original contém indicadores de categoria de base
        search_has_youth = has_youth_category(home_team) or has_youth_category(away_team) or has_youth_category(league)
        
        # ESTRATÉGIA 0: Busca usando cache de equivalências
        logger.info(f"📋 Verificando cache de equivalências...")
        
        # Verificar cache de liga
        cached_league = league_cache.get_equivalent(league)
        if cached_league:
            logger.info(f"💾 Liga encontrada no cache: '{league}' → '{cached_league}'")
            
            # Coletar todos os jogos correspondentes no cache
            cache_matches = []
            
            # Buscar a liga equivalente no JSON
            for time_slot, leagues in data['data'].items():
                for league_name, league_data in leagues.items():
                    if normalize_text(league_name) == normalize_text(cached_league):
                        logger.info(f"🎯 Liga do cache encontrada no JSON: '{league_name}'")
                        
                        if 'games' in league_data:
                            for game in league_data['games']:
                                game_home = game.get('home_name', '')
                                game_away = game.get('away_name', '')
                                
                                # Verificar cache de equipes primeiro
                                cached_home = team_cache.get_equivalent(home_team)
                                cached_away = team_cache.get_equivalent(away_team)
                                
                                if cached_home and cached_away:
                                    if (normalize_text(game_home) == normalize_text(cached_home) and 
                                        normalize_text(game_away) == normalize_text(cached_away)):
                                        cache_matches.append((game_home, game_away, game['id'], "cache completo", league_name))
                                
                                # Se não tem cache completo de equipes, tentar combinações normais
                                success, match_desc = try_all_team_combinations(game_home, game_away, "cache de liga", league_name)
                                if success:
                                    cache_matches.append((game_home, game_away, game['id'], f"cache de liga, {match_desc}", league_name))
            
            # Selecionar o melhor match
            if cache_matches:
                best_match = select_best_match(cache_matches, search_has_youth)
                if best_match:
                    game_home, game_away, game_id, match_desc, league_name = best_match
                    logger.info(f"✅ Jogo selecionado ({match_desc}): {game_home} vs {game_away} (ID: {game_id})")
                    # Salvar equivalências de equipes descobertas
                    team_cache.add_equivalence(home_team, game_home)
                    team_cache.add_equivalence(away_team, game_away)
                    return game_home, game_away, game_id
        
        # Coletar todos os matches das estratégias 1 e 2
        all_matches = []
        
        # Percorrer todos os horários
        for time_slot, leagues in data['data'].items():
            # Percorrer todas as ligas nesse horário
            for league_name, league_data in leagues.items():
                league_name_normalized = normalize_text(league_name)
                
                # ESTRATÉGIA 1: Busca direta por nome da liga
                if league_name_normalized == league_normalized:
                    logger.info(f"🎯 Liga encontrada diretamente: '{league_name}'")
                    
                    if 'games' in league_data:
                        for game in league_data['games']:
                            game_home = game.get('home_name', '')
                            game_away = game.get('away_name', '')
                            
                            # Tentar todas as combinações de nomes
                            success, match_desc = try_all_team_combinations(game_home, game_away, "liga direta", league_name)
                            if success:
                                all_matches.append((game_home, game_away, game['id'], f"liga direta, {match_desc}", league_name))
                
                # ESTRATÉGIA 2: Busca por país (primeira palavra da liga)
                else:
                    # Verificar se a liga corresponde a alguma variação do país
                    country_variations = get_country_variations(country)
                    country_match = False
                    matched_variation = ""
                    
                    for country_var in country_variations:
                        if league_name_normalized.startswith(normalize_text(country_var)):
                            country_match = True
                            matched_variation = country_var
                            break
                    
                    if country_match:
                        logger.info(f"🌍 Liga com país correspondente encontrada: '{league_name}' (país: '{country}' → '{matched_variation}')")
                        
                        if 'games' in league_data:
                            for game in league_data['games']:
                                game_home = game.get('home_name', '')
                                game_away = game.get('away_name', '')
                                
                                # Tentar todas as combinações de nomes
                                success, match_desc = try_all_team_combinations(game_home, game_away, "busca por país", league_name)
                                if success:
                                    all_matches.append((game_home, game_away, game['id'], f"busca por país, {match_desc}", league_name))
        
        # Selecionar o melhor match das estratégias 1 e 2
        if all_matches:
            best_match = select_best_match(all_matches, search_has_youth)
            if best_match:
                game_home, game_away, game_id, match_desc, league_name = best_match
                logger.info(f"✅ Jogo selecionado ({match_desc}): {game_home} vs {game_away} (ID: {game_id})")
                # Salvar equivalências descobertas
                league_cache.add_equivalence(league, league_name)
                team_cache.add_equivalence(home_team, game_home)
                team_cache.add_equivalence(away_team, game_away)
                return game_home, game_away, game_id
        
        # ESTRATÉGIA 3: Busca apenas pelas equipes em todas as ligas (fallback)
        logger.info(f"🔄 Tentando busca geral pelas equipes em todas as ligas...")
        fallback_matches = []
        
        for time_slot, leagues in data['data'].items():
            for league_name, league_data in leagues.items():
                if 'games' in league_data:
                    for game in league_data['games']:
                        game_home = game.get('home_name', '')
                        game_away = game.get('away_name', '')
                        
                        # Tentar todas as combinações de nomes
                        success, match_desc = try_all_team_combinations(game_home, game_away, "busca geral", league_name)
                        if success:
                            fallback_matches.append((game_home, game_away, game['id'], f"busca geral, {match_desc}", league_name))
        
        # Selecionar o melhor match do fallback
        if fallback_matches:
            best_match = select_best_match(fallback_matches, search_has_youth)
            if best_match:
                game_home, game_away, game_id, match_desc, league_name = best_match
                logger.info(f"✅ Jogo selecionado ({match_desc}) na liga '{league_name}': {game_home} vs {game_away} (ID: {game_id})")
                # Salvar equivalências descobertas
                league_cache.add_equivalence(league, league_name)
                team_cache.add_equivalence(home_team, game_home)
                team_cache.add_equivalence(away_team, game_away)
                return game_home, game_away, game_id
        
        logger.warning(f"⚠️  Jogo não encontrado após busca extensiva: {league} - {home_team} vs {away_team}")
        return None, None, None
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar jogo no matchday: {e}")
        return None, None, None

def extract_stats_from_html(html_content):
    """
    Extrai estatísticas do HTML da análise.
    Retorna: (ppj_fav, media_gm_casa, media_gs_fora) ou (None, None, None)
    """
    try:
        soup = BeautifulSoup(html_content, 'lxml')
        
        # 1. Extrair PPJ Fav (p com classe ppg que vem logo após div com classe home_form)
        ppj_fav = None
        home_form_divs = soup.find_all('div', class_='home_form')
        for home_form in home_form_divs:
            # Procurar o próximo elemento p com classe ppg após esta div
            next_p = home_form.find_next_sibling('p', class_='ppg')
            if next_p:
                ppj_text = next_p.get_text(strip=True)
                # Pegar apenas os números antes de "PPJ"
                ppj_match = re.search(r'([\d.]+)', ppj_text)
                if ppj_match:
                    ppj_fav = ppj_match.group(1)
                    break
        
        # 2. Extrair Média Golos Marcados (casa) - primeiro td do tr com background #1c4252 e texto "Média Golos Marcados"
        media_gm_casa = None
        for tr in soup.find_all('tr'):
            style = tr.get('style', '')
            if '#1c4252' in style and 'Média Golos Marcados' in tr.get_text():
                td_elements = tr.find_all('td')
                if len(td_elements) >= 1:
                    media_gm_casa = td_elements[0].get_text(strip=True)
                    break
        
        # 3. Extrair Média Golos Sofridos (fora) - terceiro td do tr com "Média Golos Sofridos"
        media_gs_fora = None
        for tr in soup.find_all('tr'):
            if 'Média Golos Sofridos' in tr.get_text():
                td_elements = tr.find_all('td')
                if len(td_elements) >= 3:
                    # Terceiro valor (índice 2) é o do time visitante (fora)
                    media_gs_fora = td_elements[2].get_text(strip=True)
                    break
        
        logger.info(f"📊 Estatísticas extraídas:")
        logger.info(f"   PPJ Fav: {ppj_fav}")
        logger.info(f"   Média G.M Casa: {media_gm_casa}")
        logger.info(f"   Média G.S Fora: {media_gs_fora}")
        
        return ppj_fav, media_gm_casa, media_gs_fora
        
    except Exception as e:
        logger.error(f"❌ Erro ao extrair estatísticas do HTML: {e}")
        return None, None, None


def fetch_game_analysis(home_name, away_name, game_id):
    """
    Busca a página de análise do jogo e extrai estatísticas.
    Retorna: (ppj_fav, media_gm_casa, media_gs_fora) ou (None, None, None)
    """
    try:
        # Limpar nomes das equipes
        home_clean = clean_team_name(home_name)
        away_clean = clean_team_name(away_name)
        
        # Construir URL
        url = f"https://cornerprobet.com/pt/analysis/{home_clean}-{away_clean}/{game_id}"
        
        logger.info(f"🔍 Buscando análise: {url}")
        
        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7,es-BR;q=0.6,es;q=0.5',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Referer': 'https://classic.cornerprobet.com/pt/',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-User': '?1',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
            'sec-ch-ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"'
        }
        
        cookies = {
            'cf_clearance': 'Wm6RQ7Nzct7GiGTXfL41S2MHxZFwj6BO9.LgtyJgb.E-1756481292-1.2.1.1-6DsNhXG3ovfc2qv3HqeHG1G6UEGhYFSzRvoTd1YzL7vESDzwQu5QN7Aes4knLjjMMsh3FneOq4aGcfA_Ff2wDFTOuRR7xNmedEfHKrOKkABUktTG.GUPcB4FgyBh1hoYMFPXM7ABVyHGA1c47nwsnhUqje4pmYFytFUxcMuObKNDrv6dgyLTXGDSMONamGw3v612f_BVgtBDnByf3Tiu_hSDYQ4qfDuOJtrlX3BTYfo',
            '_gcl_au': '1.1.280675726.1760124239',
            '_gid': 'GA1.2.1064458828.1760648319',
            '_ga': 'GA1.2.2007463621.1752198586',
            '_clck': '1qdf3kl%5E2%5Eg0h%5E0%5E2122',
            '_clsk': '1nv3cu1%5E1761442277835%5E1%5E1%5Ek.clarity.ms%2Fcollect',
            '_ga_ZEJ7MW3BNF': 'GS2.1.s1761442276$o164$g0$t1761442281$j55$l0$h0',
            'PHPSESSID': 'kpls2s1p7bgqpdr14hjs276jdd'
        }
        
        response = requests.get(url, headers=headers, cookies=cookies, timeout=30)
        response.raise_for_status()
        #  write html
        # html_file_path = ANALYSIS_HTML_DIR / f"analysis_{game_id}.html"
        # with open(html_file_path, 'w', encoding='utf-8') as html_file:
        #     html_file.write(response.text)
        
        # Extrair estatísticas do HTML
        ppj_fav, media_gm_casa, media_gs_fora = extract_stats_from_html(response.text)
        
        return ppj_fav, media_gm_casa, media_gs_fora, url
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar análise do jogo: {e}")
        return None, None, None, None

class AutoMessageForwarder:
    def __init__(self, config_path="client_config.json"):
        """Inicializa o forwarder automático"""
        self.config = self.load_config(config_path)
        
        # Modo híbrido: Usuário lê, Bot envia
        if self.config.get("bot_token") and self.config.get("phone_number"):
            logger.info("🔄 Modo HÍBRIDO ativado: Usuário lê + Bot envia")
            
            # Cliente USUÁRIO para ler mensagens
            self.user_app = Client(
                name="multi_forwarder_user",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                phone_number=self.config["phone_number"]
            )
            
            # Cliente BOT para enviar mensagens
            self.bot_app = Client(
                name="multi_forwarder_bot",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                bot_token=self.config["bot_token"]
            )
            
            # App principal é o usuário (para handlers)
            self.app = self.user_app
            self.send_app = self.bot_app  # App para enviar mensagens
            self.hybrid_mode = True
            
        elif self.config.get("bot_token"):
            # Modo BOT puro (apenas bot)
            logger.info("🤖 Modo BOT puro ativado")
            self.app = Client(
                name="multi_forwarder_bot",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                bot_token=self.config["bot_token"]
            )
            self.send_app = self.app
            self.hybrid_mode = False
            
        else:
            # Modo USUÁRIO puro (compatibilidade com versão antiga)
            logger.info("👤 Modo USUÁRIO puro ativado")
            self.app = Client(
                name="multi_forwarder",
                api_id=self.config["api_id"],
                api_hash=self.config["api_hash"],
                phone_number=self.config["phone_number"]
            )
            self.send_app = self.app
            self.hybrid_mode = False
        
        # Registra o handler de mensagens
        self.register_handlers()
    
    def load_config(self, config_path):
        """Carrega a configuração do arquivo JSON ou variáveis de ambiente"""
        
        # Primeiro tenta variáveis de ambiente (para deploy em nuvem)
        if os.getenv('API_ID'):
            logger.info("📡 Usando configuração via variáveis de ambiente")
            config = {
                "api_id": int(os.getenv('API_ID')),
                "api_hash": os.getenv('API_HASH'),
                "debug": os.getenv('DEBUG', 'true').lower() == 'true',
            }
            
            # Suporte para bot_token ou phone_number
            if os.getenv('BOT_TOKEN'):
                config["bot_token"] = os.getenv('BOT_TOKEN')
            else:
                config["phone_number"] = os.getenv('PHONE_NUMBER')
            
            # Suporte para configuração antiga (backwards compatibility)
            if os.getenv('SOURCE_USER_ID') and os.getenv('TARGET_CHAT_ID'):
                config["forwarders"] = [{
                    "source_user_id": int(os.getenv('SOURCE_USER_ID')),
                    "target_chat_id": int(os.getenv('TARGET_CHAT_ID')),
                    "strategy_filters": {
                        "enabled": os.getenv('STRATEGY_FILTERS_ENABLED', 'false').lower() == 'true',
                        "mode": os.getenv('STRATEGY_FILTERS_MODE', 'whitelist'),
                        "strategies": os.getenv('STRATEGY_FILTERS_STRATEGIES', '').split(',') if os.getenv('STRATEGY_FILTERS_STRATEGIES') else []
                    }
                }]
        else:
            # Senão usa arquivo JSON (desenvolvimento local)
            try:
                logger.info("📄 Usando configuração via arquivo JSON")
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except FileNotFoundError:
                logger.error(f"❌ Arquivo {config_path} não encontrado e variáveis de ambiente não configuradas")
                logger.error("💡 Configure as variáveis: API_ID, API_HASH, PHONE_NUMBER")
                raise
            except json.JSONDecodeError:
                logger.error(f"❌ Erro ao decodificar JSON do arquivo {config_path}")
                raise
        
        # Converte configuração antiga para nova estrutura se necessário
        if "source_user_id" in config and "target_chat_id" in config:
            logger.info("🔄 Convertendo configuração antiga para nova estrutura multi-fonte")
            old_config = {
                "source_user_id": config.pop("source_user_id"),
                "target_chat_id": config.pop("target_chat_id"),
                "strategy_filters": config.pop("strategy_filters", {
                    "enabled": False,
                    "mode": "whitelist",
                    "strategies": []
                })
            }
            config["forwarders"] = [old_config]
        
        # Valida configurações obrigatórias
        required_fields = ["api_id", "api_hash"]
        for field in required_fields:
            if field not in config or config[field] is None:
                raise ValueError(f"Campo obrigatório '{field}' não encontrado na configuração")
        
        # Valida que tem bot_token OU phone_number (ou ambos para modo híbrido)
        if not config.get("bot_token") and not config.get("phone_number"):
            raise ValueError("É necessário configurar 'bot_token' (para bot) ou 'phone_number' (para usuário) ou ambos (modo híbrido)")
        
        # Valida estrutura de forwarders
        if "forwarders" not in config or not config["forwarders"]:
            raise ValueError("Campo 'forwarders' não encontrado ou vazio na configuração")
        
        # Configura filtros padrão para cada forwarder se necessário
        for i, forwarder in enumerate(config["forwarders"]):
            if "strategy_filters" not in forwarder:
                forwarder["strategy_filters"] = {
                    "enabled": False,
                    "mode": "whitelist",
                    "strategies": []
                }
            
            # Log da configuração de cada forwarder
            strategy_config = forwarder["strategy_filters"]
            source_id = forwarder["source_user_id"]
            target_id = forwarder["target_chat_id"]
            
            if strategy_config.get("enabled", False):
                mode = strategy_config.get("mode", "whitelist")
                strategies = strategy_config.get("strategies", [])
                logger.info(f"🎯 Forwarder {i+1} ({source_id} → {target_id}): Filtros HABILITADOS ({mode}): {', '.join(strategies)}")
            else:
                logger.info(f"🎯 Forwarder {i+1} ({source_id} → {target_id}): Filtros DESABILITADOS")
                
        return config
    
    def register_handlers(self):
        """Registra os handlers de mensagens para todas as fontes configuradas"""
        
        # Separar fontes por tipo (usuários/bots vs grupos/canais)
        user_sources = []
        chat_sources = []
        
        for forwarder in self.config["forwarders"]:
            source_id = forwarder["source_user_id"]
            if source_id > 0:
                # ID positivo = usuário/bot
                user_sources.append(source_id)
            else:
                # ID negativo = grupo/canal
                chat_sources.append(source_id)
        
        # Handler para mensagens privadas de usuários/bots
        if user_sources:
            @self.app.on_message(
                filters.user(user_sources) & 
                filters.private
            )
            async def handle_user_message(client: Client, message: Message):
                """Handler para mensagens de usuários/bots"""
                await self.forward_message(client, message)
        
        # Handler para mensagens de grupos/canais
        if chat_sources:
            @self.app.on_message(
                filters.chat(chat_sources)
            )
            async def handle_chat_message(client: Client, message: Message):
                """Handler para mensagens de grupos/canais"""
                await self.forward_message(client, message)
    
    def should_forward_message(self, message_text: str, forwarder_config: dict) -> bool:
        """Verifica se a mensagem deve ser encaminhada baseado nos filtros de estratégia"""
        
        # Se filtros não estão habilitados, encaminhar tudo
        strategy_config = forwarder_config.get("strategy_filters", {})
        if not strategy_config.get("enabled", False):
            return True
        
        # Se não há texto, não encaminhar
        if not message_text:
            return False
        
        # Extrair primeira e segunda linha (onde está a estratégia)
        first_line = message_text.split('\n')[0].lower().strip()
        second_line = message_text.split('\n')[1].lower().strip() if len(message_text.split('\n')) > 1 else ""
        
        if self.config.get("debug", False):
            source_id = forwarder_config["source_user_id"]
            logger.info(f"🔍 [{source_id}] Analisando primeira linha: '{first_line}'\n Segunda linha: '{second_line}'")
        
        # Lista de estratégias configuradas
        strategies = strategy_config.get("strategies", [])
        mode = strategy_config.get("mode", "whitelist")
        
        # Verificar se alguma estratégia está presente na primeira linha
        strategy_found = False
        matched_strategy = None
        
        for strategy in strategies:
            if strategy.lower() in first_line.lower():
                strategy_found = True
                matched_strategy = strategy
                break
            if strategy.lower() in second_line.lower():
                strategy_found = True
                matched_strategy = strategy
                break
        
        # Aplicar lógica de whitelist ou blacklist
        if mode == "whitelist":
            # Whitelist: só encaminhar se a estratégia estiver na lista
            should_forward = strategy_found
        else:
            # Blacklist: encaminhar tudo EXCETO se a estratégia estiver na lista
            should_forward = not strategy_found
        
        if self.config.get("debug", False):
            source_id = forwarder_config["source_user_id"]
            status = "✅ APROVADA" if should_forward else "❌ BLOQUEADA"
            if matched_strategy:
                logger.info(f"🎯 [{source_id}] Estratégia encontrada: '{matched_strategy}' - {status}")
            else:
                logger.info(f"🎯 [{source_id}] Nenhuma estratégia reconhecida - {status}")
        
        return should_forward
    
    def get_forwarder_config(self, source_user_id: int) -> list:
        """Encontra todas as configurações de forwarders para um source_user_id específico"""
        matching_forwarders = []
        for forwarder in self.config["forwarders"]:
            if forwarder["source_user_id"] == source_user_id:
                matching_forwarders.append(forwarder)
        return matching_forwarders
    
    async def forward_message(self, client: Client, message: Message):
        """Encaminha uma mensagem para todos os grupos de destino configurados"""
        try:
            # Determinar ID da fonte baseado no tipo de mensagem
            source_id = message.chat.id

            logger.debug(f"📩 Mensagem recebida de {source_id}: {message.text or '[Mídia]'}")
            
            # Encontrar todas as configurações de forwarder para esta fonte
            forwarder_configs = self.get_forwarder_config(source_id)
            if not forwarder_configs:
                logger.warning(f"⚠️  Nenhuma configuração encontrada para source_id: {source_id}")
                return
            
            # Log da mensagem recebida
            text_preview = (message.text[:50] + "...") if message.text and len(message.text) > 50 else (message.text or "[Mídia]")
            logger.info(f"📨 [{source_id}] Nova mensagem recebida: {text_preview}")
            logger.info(f"🎯 [{source_id}] Processando {len(forwarder_configs)} destino(s)")
            
            # Processar cada forwarder configurado para esta fonte
            for forwarder_config in forwarder_configs:
                target_id = forwarder_config["target_chat_id"]
                
                try:
                    # Verificar filtros de estratégia para este forwarder específico
                    if not self.should_forward_message(message.text, forwarder_config):
                        logger.info(f"🚫 [{source_id}→{target_id}] Mensagem bloqueada pelos filtros de estratégia")
                        continue
                    
                    # Verificar se é estratégia "Lay 0x1" para buscar análise
                    stats_text = ""
                    if message.text:
                        first_line = message.text.split('\n')[0].lower().strip() if message.text else ""
                        second_line = message.text.split('\n')[1].lower().strip() if len(message.text.split('\n')) > 1 else ""
                        
                        # Verificar se contém "Lay 0x1" na primeira ou segunda linha
                        if ("lay 0x1" in first_line or "lay 0x1" in second_line or "lay 1x2" in first_line or "lay 1x2" in second_line):                            
                            # Extrair liga e times da mensagem
                            league, home_team, away_team = extract_league_and_teams(message.text)
                            
                            if league and home_team and away_team:
                                # logger.info(f"📊 Liga original: {league}")
                                # logger.info(f"🏠 Casa: {home_team}")
                                # logger.info(f"✈️  Fora: {away_team}")
                                
                                # Converter nome da liga e verificar validade
                                converted_league, league_validity_emoji = convert_league_name(league)
                                # logger.info(f"📊 Liga convertida: {converted_league}")
                                
                                # Buscar jogo no matchday JSON usando a liga convertida
                                home_name, away_name, game_id = find_game_in_matchday(converted_league, home_team, away_team)
                                
                                if home_name and away_name and game_id:
                                    # Buscar análise do jogo e extrair estatísticas
                                    ppj_fav, media_gm_casa, media_gs_fora, url = fetch_game_analysis(home_name, away_name, game_id)
                                    
                                    # if ppj_fav or media_gm_casa or media_gs_fora:
                                    #     logger.info(f"✅ Estatísticas extraídas com sucesso!")
                                        
                                    #     # Montar texto com estatísticas
                                    #     stats_text = "\n\n📊 Critérios:"
                                    #     # Adicionar critério de liga válida/inválida
                                    #     # stats_text += f"\n🏆 Liga Válida: {league_validity_emoji}"
                                    #     if ppj_fav:
                                    #       if float(ppj_fav) < 1.2:
                                    #         stats_text += f"\n🎯 PPJ Fav: {ppj_fav} ❌"
                                    #       else:
                                    #         stats_text += f"\n🎯 PPJ Fav: {ppj_fav} ✅"
                                    #     if media_gm_casa:
                                    #         if float(media_gm_casa) < 1:
                                    #             stats_text += f"\n⚽ Média G.M Casa: {media_gm_casa} ❌"
                                    #         else:
                                    #             stats_text += f"\n⚽ Média G.M Casa: {media_gm_casa} ✅"
                                    #     if media_gs_fora:
                                    #         if float(media_gs_fora) < 0.8:
                                    #             stats_text += f"\n🛡️ Média G.S Fora: {media_gs_fora} ❌"
                                    #         else:
                                    #             stats_text += f"\n🛡️ Média G.S Fora: {media_gs_fora} ✅"
                                    #     stats_text += f"\n\n{url}"
                                    # else:
                                    #     # Mesmo sem dados da partida, mostrar critério da liga
                                    #     stats_text = f"\n\n📊 Critérios:\n🏆 Liga Válida: {league_validity_emoji}"
                                    #     stats_text += f"\n\n{url}"
                                    #     logger.warning(f"⚠️  Não foi possível extrair estatísticas ({url})")
                                    stats_text += f"\n\n{url}"
                                # else:
                                #   # Mesmo sem encontrar o jogo, mostrar critério da liga
                                #   stats_text = f"\n\n📊 Critérios:\n🏆 Liga Válida: {league_validity_emoji}"
                                #   stats_text += f"\n\nDados da partida não encontrados"
                                #   logger.warning(f"⚠️  Jogo não encontrado no matchday")
                            # else:
                            #   stats_text += f"\n\nDados da partida não encontrados"
                            #   logger.warning(f"⚠️  Não foi possível extrair liga/times da mensagem")
                    
                    # Formata a mensagem com estatísticas (se houver)
                    if message.text:
                        formatted_message = f"{message.text}{stats_text}"
                    else:
                        formatted_message = "[Mensagem com mídia]"
                    
                    # Encaminha para o grupo de destino específico usando o cliente apropriado
                    await self.send_app.send_message(
                        chat_id=target_id,
                        text=formatted_message
                    )
                    
                    logger.info(f"✅ [{source_id}→{target_id}] Mensagem encaminhada automaticamente!")
                    
                except Exception as e:
                    logger.error(f"❌ [{source_id}→{target_id}] Erro ao encaminhar mensagem: {e}")
                    # Continua para os próximos destinos mesmo se um falhar
                    continue
            
        except Exception as e:
            logger.error(f"❌ Erro geral ao processar mensagem: {e}")
    
    async def start(self):
        """Inicia o cliente e o monitoramento"""
        logger.info("🚀 Iniciando Message Forwarder Automático Multi-Fonte...")
        
        # No modo híbrido, precisamos iniciar ambos os clientes
        if self.hybrid_mode:
            async with self.user_app, self.bot_app:
                # Obtém informações do usuário (para leitura)
                me_user = await self.user_app.get_me()
                logger.info(f"👤 Usuário (leitura): {me_user.first_name} {me_user.last_name or ''} (@{me_user.username or 'sem_username'})")
                
                # Obtém informações do bot (para envio)
                me_bot = await self.bot_app.get_me()
                logger.info(f"🤖 Bot (envio): {me_bot.first_name} (@{me_bot.username or 'sem_username'})")
                
                # Carregar diálogos para popular cache de peers (usuário)
                logger.info("🔄 Carregando cache de diálogos do usuário...")
                user_dialog_count = 0
                async for dialog in self.user_app.get_dialogs(limit=100):
                    user_dialog_count += 1
                logger.info(f"✅ Cache do usuário carregado com {user_dialog_count} diálogos")
                
                # Para o bot, carregar o cache dos destinos configurados
                logger.info("🔄 Carregando cache de destinos do bot...")
                for forwarder in self.config["forwarders"]:
                    target_id = forwarder["target_chat_id"]
                    try:
                        # Tentar acessar o chat para popular o cache do bot
                        chat = await self.bot_app.get_chat(target_id)
                        logger.info(f"✅ Bot: cache carregado para destino '{getattr(chat, 'title', target_id)}'")
                    except Exception as e:
                        logger.warning(f"⚠️  Bot: não conseguiu carregar cache para destino {target_id}: {e}")
                
                await self._verify_forwarders()
                
                logger.info("👂 Aguardando mensagens de todas as fontes configuradas... (Pressione Ctrl+C para parar)")
                
                # Mantém o cliente rodando
                await asyncio.Event().wait()
        else:
            # Modo normal (apenas um cliente)
            async with self.app:
                # Obtém informações do usuário/bot
                me = await self.app.get_me()
                logger.info(f"👤 Logado como: {me.first_name} {me.last_name or ''} (@{me.username or 'sem_username'})")
                
                # Carregar diálogos para popular cache de peers
                logger.info("🔄 Carregando cache de diálogos...")
                dialog_count = 0
                async for dialog in self.app.get_dialogs(limit=100):
                    dialog_count += 1
                logger.info(f"✅ Cache carregado com {dialog_count} diálogos")
                
                await self._verify_forwarders()
                
                logger.info("👂 Aguardando mensagens de todas as fontes configuradas... (Pressione Ctrl+C para parar)")
                
                # Mantém o cliente rodando
                await asyncio.Event().wait()
    
    async def _verify_forwarders(self):
        """Verifica as configurações de forwarders"""
        logger.info(f"📋 Configurados {len(self.config['forwarders'])} forwarder(s):")
        
        # Verifica cada configuração de forwarder
        for i, forwarder in enumerate(self.config["forwarders"], 1):
            source_id = forwarder["source_user_id"]
            target_id = forwarder["target_chat_id"]
            
            logger.info(f"🔄 Verificando Forwarder {i}: {source_id} → {target_id}")
            
            # Verifica se o usuário fonte existe
            try:
                if source_id == 779230055:  # CornerProBot2
                    try:
                        source_user = await self.app.get_users('@cornerpro2_bot')
                        logger.info(f"✅ Fonte {i}: {source_user.first_name} (@{source_user.username})")
                    except:
                        source_user = await self.app.get_chat(source_id)
                        logger.info(f"✅ Fonte {i}: {source_user.first_name} (ID: {source_id})")
                else:
                    source_user = await self.app.get_chat(source_id)
                    source_name = getattr(source_user, 'title', None) or getattr(source_user, 'first_name', f'ID:{source_id}')
                    logger.info(f"✅ Fonte {i}: {source_name} (ID: {source_id})")
                    

            except Exception as e:
                logger.error(f"❌ Erro ao verificar fonte {i} (ID: {source_id}): {e}")
                logger.error(f"💡 Certifique-se de estar no chat/canal ou ter conversado com o usuário")
                continue
            
            # Verifica se o chat de destino existe (usando send_app para verificar permissões)
            try:
                target_chat = await self.send_app.get_chat(target_id)
                target_name = getattr(target_chat, 'title', f'ID:{target_id}')
                logger.info(f"✅ Destino {i}: {target_name} (ID: {target_id})")
            except Exception as e:
                logger.error(f"❌ Erro ao verificar destino {i} (ID: {target_id}): {e}")
                logger.error(f"💡 Certifique-se de que o bot está no grupo/canal de destino com permissões")
                continue
              

async def main():
    """Função principal"""
    try:
        forwarder = AutoMessageForwarder()
        await forwarder.start()
    except KeyboardInterrupt:
        logger.info("🛑 Parando o Message Forwarder...")
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")

if __name__ == "__main__":
    asyncio.run(main())
