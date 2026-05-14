from pathlib import Path
import unittest

from autofusion_bench.exp001.costs import build_budget_profile, load_cost_table
from autofusion_bench.exp001.runner import run_exp001


ROOT = Path(__file__).resolve().parents[1]
EXP_DIR = ROOT / "experiments" / "exp-001-decision-surface-pilot"
FIXTURES = EXP_DIR / "fixtures"


class Exp001ProtocolTests(unittest.TestCase):
    def test_budget_profile_keeps_tav_illegal_under_tight(self) -> None:
        costs = load_cost_table(FIXTURES / "cost_table.csv")
        profile = build_budget_profile(costs)
        self.assertGreaterEqual(profile.spread_ratio, 1.5)
        self.assertIn("AV", profile.legal_by_budget["tight"])
        self.assertNotIn("TAV", profile.legal_by_budget["tight"])

    def test_fixture_smoke_passes_protocol_and_signal_gates(self) -> None:
        summary = run_exp001(
            config_path=EXP_DIR / "config.yaml",
            cost_table_path=FIXTURES / "cost_table.csv",
            outcome_table_path=FIXTURES / "outcome_table.csv",
            q_policy_map_path=FIXTURES / "q_policy_map.csv",
            q_proxy_table_path=FIXTURES / "q_proxy_table.csv",
            q_diagnostics_path=FIXTURES / "q_diagnostics.csv",
            corruption_manifest_path=FIXTURES / "corruption_manifest.csv",
            output_dir=EXP_DIR / "outputs" / "unittest-smoke",
        )
        metrics = summary["metrics"]
        self.assertTrue(summary["status"]["protocol_passed"])
        self.assertTrue(summary["status"]["benchmark_signal_passed"])
        self.assertGreaterEqual(metrics["best_single_axis_oracle_regret_dt"], 3.0)
        self.assertGreaterEqual(metrics["joint_gap_closure"], 0.3)


if __name__ == "__main__":
    unittest.main()

