from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from analysis.scenario_classifier import (
    SCENARIO_NAMES,
    classify_alert,
    parse_alert_message,
    parse_and_classify,
    should_forward_strategy,
)


def build_message(
    strategy="mapa-de-calor",
    home_team="Lauterach",
    home_position=17,
    away_team="Kuchl",
    away_position=2,
    league="Austria Regionalliga: West",
    game_time="70",
    score=(0, 2),
    halftime_score=(0, 0),
    odds=(6.5, 6.5, 1.22),
    url="https://cornerprobet.com/analysis/re8qc",
    blank_lines_before_url=2,
):
    separator = "\n" * (blank_lines_before_url + 1)
    return (
        f"📣 Alerta Estratégia: {strategy} 📣\n"
        f"🏟 Jogo: {home_team} ({home_position}º) x ({away_position}º) {away_team}\n"
        f"🏆 Competição: {league}\n"
        f"🕛 Tempo: {game_time} '\n"
        f"⚽ Resultado: {score[0]} x {score[1]} ({halftime_score[0]} x {halftime_score[1]} Intervalo)\n"
        f"📈 Odds 1x2 Pre-live: {odds[0]} / {odds[1]} / {odds[2]}"
        f"{separator}{url}"
    )


class ScenarioClassifierTest(unittest.TestCase):
    def test_parse_example_message(self):
        alert = parse_alert_message(build_message())

        self.assertIsNotNone(alert)
        self.assertEqual(alert.strategy, "mapa-de-calor")
        self.assertEqual(alert.home_team, "Lauterach")
        self.assertEqual(alert.home_position, 17)
        self.assertEqual(alert.away_team, "Kuchl")
        self.assertEqual(alert.away_position, 2)
        self.assertEqual(alert.league, "Austria Regionalliga: West")
        self.assertEqual(alert.game_time, "70")
        self.assertEqual(alert.home_goals, 0)
        self.assertEqual(alert.away_goals, 2)
        self.assertEqual(alert.halftime_home_goals, 0)
        self.assertEqual(alert.halftime_away_goals, 0)
        self.assertEqual(alert.home_odd, 6.5)
        self.assertEqual(alert.draw_odd, 6.5)
        self.assertEqual(alert.away_odd, 1.22)
        self.assertEqual(alert.match_url, "https://cornerprobet.com/analysis/re8qc")

    def test_classifies_example_as_away_favorite_winning_by_two(self):
        alert, result = parse_and_classify(build_message())

        self.assertEqual(result.scenario, "fora favorito ganhando com dois gols de diferença")
        self.assertEqual(result.general_scenario, "favorito ganhando")
        self.assertEqual(result.favorite_side, "fora")
        self.assertFalse(result.is_even_match)

    def test_url_can_be_after_blank_lines(self):
        alert = parse_alert_message(build_message(blank_lines_before_url=4))

        self.assertIsNotNone(alert)
        self.assertEqual(alert.match_url, "https://cornerprobet.com/analysis/re8qc")

    def test_accepts_comma_decimal_odds(self):
        alert = parse_alert_message(build_message(odds=("1,80", "3,20", "2,10")))

        self.assertIsNotNone(alert)
        self.assertEqual(alert.home_odd, 1.8)
        self.assertEqual(alert.draw_odd, 3.2)
        self.assertEqual(alert.away_odd, 2.1)

    def test_strategy_whitelist_and_blacklist(self):
        self.assertTrue(should_forward_strategy(
            "mapa-de-calor",
            {"enabled": True, "mode": "whitelist", "strategies": ["mapa"]},
        ))
        self.assertFalse(should_forward_strategy(
            "mapa-de-calor",
            {"enabled": True, "mode": "whitelist", "strategies": ["lay"]},
        ))
        self.assertFalse(should_forward_strategy(
            "mapa-de-calor",
            {"enabled": True, "mode": "blacklist", "strategies": ["calor"]},
        ))
        self.assertTrue(should_forward_strategy(
            "mapa-de-calor",
            {"enabled": False, "mode": "whitelist", "strategies": []},
        ))

    def test_invalid_or_incomplete_messages_do_not_parse(self):
        self.assertIsNone(parse_alert_message(""))
        self.assertIsNone(parse_and_classify("📣 Alerta Estratégia: mapa-de-calor 📣"))

    def test_tied_scores_with_and_without_goals(self):
        home_favorite_with_goals = classify_alert(parse_alert_message(
            build_message(score=(1, 1), odds=(1.5, 3.2, 2.2))
        ))
        even_without_goals = classify_alert(parse_alert_message(
            build_message(score=(0, 0), odds=(1.9, 3.2, 2.0))
        ))

        self.assertEqual(home_favorite_with_goals.scenario, "casa favorito empatando com gols")
        self.assertEqual(even_without_goals.scenario, "parelho empatando sem gols")

    def test_all_24_detailed_scenarios(self):
        cases = {
            "casa favorito perdendo com um gol de diferença": ((0, 1), (1.5, 3.2, 2.2)),
            "casa favorito ganhando com um gol de diferença": ((1, 0), (1.5, 3.2, 2.2)),
            "fora favorito perdendo com um gol de diferença": ((1, 0), (2.2, 3.2, 1.5)),
            "fora favorito ganhando com um gol de diferença": ((0, 1), (2.2, 3.2, 1.5)),
            "casa favorito perdendo com dois gols de diferença": ((0, 2), (1.5, 3.2, 2.2)),
            "casa favorito ganhando com dois gols de diferença": ((2, 0), (1.5, 3.2, 2.2)),
            "fora favorito perdendo com dois gols de diferença": ((2, 0), (2.2, 3.2, 1.5)),
            "fora favorito ganhando com dois gols de diferença": ((0, 2), (2.2, 3.2, 1.5)),
            "casa favorito perdendo com mais de dois gols de diferença": ((0, 3), (1.5, 3.2, 2.2)),
            "casa favorito ganhando com mais de dois gols de diferença": ((3, 0), (1.5, 3.2, 2.2)),
            "fora favorito perdendo com mais de dois gols de diferença": ((3, 0), (2.2, 3.2, 1.5)),
            "fora favorito ganhando com mais de dois gols de diferença": ((0, 3), (2.2, 3.2, 1.5)),
            "casa favorito empatando com gols": ((1, 1), (1.5, 3.2, 2.2)),
            "fora favorito empatando com gols": ((1, 1), (2.2, 3.2, 1.5)),
            "casa favorito empatando sem gols": ((0, 0), (1.5, 3.2, 2.2)),
            "fora favorito empatando sem gols": ((0, 0), (2.2, 3.2, 1.5)),
            "casa parelho perdendo com um gol de diferença": ((0, 1), (1.9, 3.2, 2.0)),
            "fora parelho perdendo com um gol de diferença": ((1, 0), (1.9, 3.2, 2.0)),
            "casa parelho perdendo com dois gols de diferença": ((0, 2), (1.9, 3.2, 2.0)),
            "fora parelho perdendo com dois gols de diferença": ((2, 0), (1.9, 3.2, 2.0)),
            "casa parelho perdendo com mais de dois gols de diferença": ((0, 3), (1.9, 3.2, 2.0)),
            "fora parelho perdendo com mais de dois gols de diferença": ((3, 0), (1.9, 3.2, 2.0)),
            "parelho empatando com gols": ((1, 1), (1.9, 3.2, 2.0)),
            "parelho empatando sem gols": ((0, 0), (1.9, 3.2, 2.0)),
        }

        self.assertEqual(set(cases.keys()), set(SCENARIO_NAMES))

        for expected_scenario, (score, odds) in cases.items():
            with self.subTest(expected_scenario=expected_scenario):
                alert = parse_alert_message(build_message(score=score, odds=odds))
                result = classify_alert(alert)
                self.assertEqual(result.scenario, expected_scenario)


if __name__ == "__main__":
    unittest.main()
