#!/usr/bin/env python3
"""
Parsing and classification helpers for scenario-based Telegram alerts.
"""

from dataclasses import dataclass
import re
from typing import Optional, Tuple


SCENARIO_NAMES = [
    "casa favorito perdendo com um gol de diferença",
    "casa favorito ganhando com um gol de diferença",
    "fora favorito perdendo com um gol de diferença",
    "fora favorito ganhando com um gol de diferença",
    "casa favorito perdendo com dois gols de diferença",
    "casa favorito ganhando com dois gols de diferença",
    "fora favorito perdendo com dois gols de diferença",
    "fora favorito ganhando com dois gols de diferença",
    "casa favorito perdendo com mais de dois gols de diferença",
    "casa favorito ganhando com mais de dois gols de diferença",
    "fora favorito perdendo com mais de dois gols de diferença",
    "fora favorito ganhando com mais de dois gols de diferença",
    "casa favorito empatando com gols",
    "fora favorito empatando com gols",
    "casa favorito empatando sem gols",
    "fora favorito empatando sem gols",
    "casa parelho perdendo com um gol de diferença",
    "fora parelho perdendo com um gol de diferença",
    "casa parelho perdendo com dois gols de diferença",
    "fora parelho perdendo com dois gols de diferença",
    "casa parelho perdendo com mais de dois gols de diferença",
    "fora parelho perdendo com mais de dois gols de diferença",
    "parelho empatando com gols",
    "parelho empatando sem gols",
]

GENERAL_SCENARIOS = [
    "favorito perdendo",
    "favorito ganhando",
    "favorito empatando",
    "parelho perdendo",
    "parelho empatando",
]


@dataclass(frozen=True)
class AlertData:
    strategy: str
    home_team: str
    home_position: int
    away_team: str
    away_position: int
    league: str
    game_time: str
    home_goals: int
    away_goals: int
    halftime_home_goals: int
    halftime_away_goals: int
    home_odd: float
    draw_odd: float
    away_odd: float
    match_url: str


@dataclass(frozen=True)
class ScenarioResult:
    scenario: str
    general_scenario: str
    favorite_side: Optional[str]
    is_even_match: bool
    goal_difference: int


def parse_alert_message(message_text: str) -> Optional[AlertData]:
    """Extract all structured fields from a CornerPro strategy alert."""
    if not message_text:
        return None

    strategy_match = re.search(
        r"^\s*📣\s*Alerta\s+Estratégia:\s*(?P<strategy>.*?)\s*📣\s*$",
        message_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    game_match = re.search(
        r"^\s*🏟\s*Jogo:\s*(?P<home>.+?)\s*\((?P<home_pos>\d+)º\)\s*x\s*"
        r"\((?P<away_pos>\d+)º\)\s*(?P<away>.+?)\s*$",
        message_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    league_match = re.search(
        r"^\s*🏆\s*Competição:\s*(?P<league>.+?)\s*$",
        message_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    time_match = re.search(
        r"^\s*🕛\s*Tempo:\s*(?P<time>.+?)\s*'\s*$",
        message_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    result_match = re.search(
        r"^\s*⚽\s*Resultado:\s*(?P<home_goals>\d+)\s*x\s*(?P<away_goals>\d+)\s*"
        r"\((?P<ht_home>\d+)\s*x\s*(?P<ht_away>\d+)\s*Intervalo\)\s*$",
        message_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    odds_match = re.search(
        r"^\s*📈\s*Odds\s+1x2\s+Pre-live:\s*(?P<home_odd>[\d.,]+)\s*/\s*"
        r"(?P<draw_odd>[\d.,]+)\s*/\s*(?P<away_odd>[\d.,]+)\s*$",
        message_text,
        flags=re.IGNORECASE | re.MULTILINE,
    )
    url_match = re.search(r"https?://\S+", message_text)

    if not all([
        strategy_match,
        game_match,
        league_match,
        time_match,
        result_match,
        odds_match,
        url_match,
    ]):
        return None

    try:
        return AlertData(
            strategy=strategy_match.group("strategy").strip(),
            home_team=game_match.group("home").strip(),
            home_position=int(game_match.group("home_pos")),
            away_team=game_match.group("away").strip(),
            away_position=int(game_match.group("away_pos")),
            league=league_match.group("league").strip(),
            game_time=time_match.group("time").strip(),
            home_goals=int(result_match.group("home_goals")),
            away_goals=int(result_match.group("away_goals")),
            halftime_home_goals=int(result_match.group("ht_home")),
            halftime_away_goals=int(result_match.group("ht_away")),
            home_odd=_parse_odd(odds_match.group("home_odd")),
            draw_odd=_parse_odd(odds_match.group("draw_odd")),
            away_odd=_parse_odd(odds_match.group("away_odd")),
            match_url=url_match.group(0).strip(),
        )
    except (TypeError, ValueError):
        return None


def classify_alert(alert: AlertData) -> ScenarioResult:
    """Classify an alert into one detailed scenario and one general scenario."""
    odd_difference = abs(alert.home_odd - alert.away_odd)
    score_difference = alert.home_goals - alert.away_goals
    goal_difference = abs(score_difference)

    if odd_difference > 0.2:
        favorite_side = "casa" if alert.home_odd < alert.away_odd else "fora"

        if score_difference == 0:
            goals_label = "com gols" if alert.home_goals > 0 else "sem gols"
            return ScenarioResult(
                scenario=f"{favorite_side} favorito empatando {goals_label}",
                general_scenario="favorito empatando",
                favorite_side=favorite_side,
                is_even_match=False,
                goal_difference=0,
            )

        favorite_score_difference = score_difference if favorite_side == "casa" else -score_difference
        status = "ganhando" if favorite_score_difference > 0 else "perdendo"
        scenario = f"{favorite_side} favorito {status} {_goal_difference_label(abs(favorite_score_difference))}"

        return ScenarioResult(
            scenario=scenario,
            general_scenario=f"favorito {status}",
            favorite_side=favorite_side,
            is_even_match=False,
            goal_difference=goal_difference,
        )

    if score_difference == 0:
        goals_label = "com gols" if alert.home_goals > 0 else "sem gols"
        return ScenarioResult(
            scenario=f"parelho empatando {goals_label}",
            general_scenario="parelho empatando",
            favorite_side=None,
            is_even_match=True,
            goal_difference=0,
        )

    losing_side = "casa" if score_difference < 0 else "fora"
    return ScenarioResult(
        scenario=f"{losing_side} parelho perdendo {_goal_difference_label(goal_difference)}",
        general_scenario="parelho perdendo",
        favorite_side=None,
        is_even_match=True,
        goal_difference=goal_difference,
    )


def parse_and_classify(message_text: str) -> Optional[Tuple[AlertData, ScenarioResult]]:
    alert = parse_alert_message(message_text)
    if not alert:
        return None
    return alert, classify_alert(alert)


def should_forward_strategy(alert_strategy: str, strategy_config: dict) -> bool:
    """Apply whitelist/blacklist strategy filters to the extracted strategy."""
    if not strategy_config or not strategy_config.get("enabled", False):
        return True

    strategies = strategy_config.get("strategies", [])
    mode = strategy_config.get("mode", "whitelist")
    normalized_strategy = alert_strategy.lower().strip()

    strategy_found = any(
        configured.lower().strip() in normalized_strategy
        for configured in strategies
        if configured
    )

    if mode == "blacklist":
        return not strategy_found
    return strategy_found


def _parse_odd(raw_odd: str) -> float:
    return float(raw_odd.replace(",", "."))


def _goal_difference_label(goal_difference: int) -> str:
    if goal_difference == 1:
        return "com um gol de diferença"
    if goal_difference == 2:
        return "com dois gols de diferença"
    return "com mais de dois gols de diferença"
