from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from exports.export_scenario_xlsx import (
    build_workbook,
    calculate_unit_results,
    extract_goal_outcome,
)
from analysis.scenario_classifier import SCENARIO_NAMES


RED_MESSAGE = """
📣 Alerta Estratégia: mapa-de-calor 📣
🏟 Jogo: La Luz (6º) x (13º) Paysandu FC
🏆 Competição: Uruguay Segunda Division
🕛 Tempo: 70 '
⚽ Resultado: 1 x 2 (0 x 0 Intervalo)
📈 Odds 1x2 Pre-live: 1.8 / 3.2 / 4

https://cornerprobet.com/analysis/rpam7

⚽: ❌

https://cornerprobet.com
"""


GREEN_MESSAGE = """
📣 Alerta Estratégia: mapa-de-calor 📣
🏟 Jogo: Olympique Akbou (6º) x (9º) ES Ben Aknoun
🏆 Competição: Algeria Ligue 1
🕛 Tempo: 71 '
⚽ Resultado: 1 x 0 (0 x 0 Intervalo)
📈 Odds 1x2 Pre-live: 2.62 / 2.9 / 2.5

https://cornerprobet.com/analysis/rn85s

⚽ 77' (ES Ben Aknoun)

https://cornerprobet.com
"""


class ExportScenarioXlsxTest(unittest.TestCase):
    def test_detects_red_goal_line(self):
        self.assertFalse(extract_goal_outcome(RED_MESSAGE))

    def test_detects_green_goal_line(self):
        self.assertTrue(extract_goal_outcome(GREEN_MESSAGE))

    def test_calculates_simple_units(self):
        results = calculate_unit_results([True, False, False, True])

        self.assertEqual([result.simple_unit for result in results], [1, -1, -1, 1])
        self.assertEqual([result.simple_balance for result in results], [1, 0, -1, 0])

    def test_calculates_recovery_martingale_after_second_red(self):
        results = calculate_unit_results([True, False, False, True])

        self.assertEqual([result.martingale_unit for result in results], [1, -1, -1, 2])
        self.assertEqual(results[-1].martingale_balance, 1)

    def test_builds_all_24_scenario_sheets_even_without_rows(self):
        workbook = build_workbook({scenario: [] for scenario in SCENARIO_NAMES})

        self.assertEqual(len(workbook.worksheets), len(SCENARIO_NAMES))
        self.assertEqual(len(workbook.worksheets), 24)
        self.assertTrue(workbook.worksheets[0]["A1"].value.startswith("Cenario: "))


if __name__ == "__main__":
    unittest.main()
