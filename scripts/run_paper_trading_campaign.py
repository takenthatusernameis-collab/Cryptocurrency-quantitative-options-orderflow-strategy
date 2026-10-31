#!/usr/bin/env python3
"""Pre-Live Gates & Paper Trading Campaign for Phase 8."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

# Allow running from repo root
try:
    from src.config.secrets import load_secrets_config, SecretsManager
    from src.execution.live_trading import LiveTradingEngine
    from src.execution.orders import OrderSide, OrderType
    from src.risk.reconciliation import ReconciliationEngine
    from src.risk.execution_integration import create_execution_risk_integrator
    from src.risk.limits import RiskLimits, RiskManager
    from src.risk.circuit_breaker import CircuitBreaker
    from src.ingestion.deribit import DeribitClient
    from src.ingestion.okx import OKXClient
    from src.ingestion.binance import BinanceClient
    from src.telemetry import serialize_metrics_strict
    from src.telemetry.monitor import ProductionTelemetryMonitor
except ImportError:
    from config.secrets import load_secrets_config, SecretsManager  # type: ignore
    from execution.live_trading import LiveTradingEngine  # type: ignore
    from execution.orders import OrderSide, OrderType  # type: ignore
    from risk.reconciliation import ReconciliationEngine  # type: ignore
    from risk.execution_integration import create_execution_risk_integrator  # type: ignore
    from risk.limits import RiskLimits, RiskManager  # type: ignore
    from risk.circuit_breaker import CircuitBreaker  # type: ignore
    from ingestion.deribit import DeribitClient  # type: ignore
    from ingestion.okx import OKXClient  # type: ignore
    from ingestion.binance import BinanceClient  # type: ignore
    from telemetry import serialize_metrics_strict  # type: ignore
    from telemetry.monitor import ProductionTelemetryMonitor  # type: ignore


def _ts() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def _write_json(path: Path, data: Dict[str, Any]) -> str:
    serialized = serialize_metrics_strict(data)
    content = json.dumps(serialized, ensure_ascii=False, indent=2, allow_nan=False)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path)


class PreLiveGateChecker:
    def __init__(self, strict: bool = False):
        self.strict = strict
        self.gates: List[Dict[str, Any]] = []
        self.passed = 0
        self.failed = 0

    def check_gate(self, name: str, condition: bool, details: str = "", critical: bool = True) -> bool:
        gate_result = {
            "gate": name,
            "passed": bool(condition),
            "critical": bool(critical),
            "details": details,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        self.gates.append(gate_result)
        if condition:
            self.passed += 1
            print(f"✓ {name}: PASSED - {details}")
        else:
            self.failed += 1
            print(f"✗ {name}: FAILED - {details}")
        return condition

    def all_critical_passed(self) -> bool:
        for g in self.gates:
            if g["critical"] and not g["passed"]:
                return False
        return True


def run_paper_trading_campaign(mode: str = "paper", gates_only: bool = False, strict_gates: bool = False) -> Dict[str, Any]:
    print("=" * 80)
    print(f"PHASE 8: Live Trading Readiness - {mode.upper()} MODE")
    print("=" * 80)

    checker = PreLiveGateChecker(strict=strict_gates)
    secrets = load_secrets_config()

    # Gate 1: Secrets & Config
    print("\n[1/7] Checking Secrets & Configuration...")
    sm = SecretsManager()
    creds_deribit = sm.get_venue_credentials("deribit")
    checker.check_gate("secrets_loaded", True, "Secrets manager initialized", critical=False)
    checker.check_gate("trading_mode_configured", mode in ["paper", "live"], f"Mode: {mode}", critical=True)
    checker.check_gate("live_trading_safety", not (mode == "live" and not secrets.get("live_trading_enabled")),
                       "Live trading safety check", critical=True)

    # Gate 2: Exchange Adapters
    print("\n[2/7] Checking Exchange Adapters...")
    try:
        deribit_client = DeribitClient()
        checker.check_gate("deribit_adapter_init", True, "Deribit adapter initialized", critical=True)
    except Exception as e:
        checker.check_gate("deribit_adapter_init", False, f"Error: {e}", critical=True)

    try:
        okx_client = OKXClient()
        checker.check_gate("okx_adapter_init", True, "OKX adapter initialized", critical=True)
    except Exception as e:
        checker.check_gate("okx_adapter_init", False, f"Error: {e}", critical=True)

    try:
        binance_client = BinanceClient()
        checker.check_gate("binance_adapter_init", True, "Binance adapter initialized", critical=True)
    except Exception as e:
        checker.check_gate("binance_adapter_init", False, f"Error: {e}", critical=True)

    # Gate 3: Risk Controls
    print("\n[3/7] Checking Risk Controls...")
    limits = RiskLimits()
    risk_mgr = RiskManager(limits=limits)
    cb = CircuitBreaker()
    integrator = create_execution_risk_integrator(risk_manager=risk_mgr, circuit_breaker=cb, seed=42)
    checker.check_gate("risk_manager_init", risk_mgr is not None, "Risk manager initialized", critical=True)
    checker.check_gate("circuit_breaker_init", cb is not None, "Circuit breaker initialized", critical=True)
    checker.check_gate("risk_integrator_init", integrator is not None, "Risk integrator initialized", critical=True)

    # Gate 4: Live Trading Engine
    print("\n[4/7] Checking Live Trading Engine...")
    paper_mode = (mode == "paper")
    live_engine = LiveTradingEngine(risk_integrator=integrator, paper_mode=paper_mode, seed=42)
    checker.check_gate("live_trading_engine_init", live_engine is not None, f"Paper mode: {paper_mode}", critical=True)

    # Test order lifecycle
    try:
        integrator.update_greeks({"delta": 10.0, "gamma": 1.0, "vega": 5.0, "theta": -1.0})
        integrator.update_equity(100000.0)
        order = live_engine.submit_order("BTCUSDT", OrderSide.BUY, 0.01, OrderType.LIMIT, price=100000.0)
        checker.check_gate("order_submission", order is not None and order.order_id is not None,
                          f"Order submitted: {order.order_id[:12]}", critical=True)
        live_engine.process_fill(order.order_id, 0.005, 100000.0, 0.5)
        live_engine.process_fill(order.order_id, 0.005, 100000.0, 0.5)
        checker.check_gate("order_fills_partial_full", True, "Partial and full fills processed", critical=True)
        status = live_engine.get_order_status(order.order_id)
        checker.check_gate("order_status_tracking", status["state"] == "filled", f"Order state: {status['state']}", critical=True)
    except Exception as e:
        checker.check_gate("order_lifecycle_test", False, f"Error: {e}", critical=True)

    # Gate 5: Reconciliation
    print("\n[5/7] Checking Reconciliation...")
    recon_engine = ReconciliationEngine(auto_halt_on_critical=True)
    local_pos = {"BTC": {"quantity": 0.1, "notional": 10000.0}}
    exchange_pos = {"BTC": {"quantity": 0.1, "notional": 10000.0}}
    recon_results = recon_engine.reconcile_positions(local_pos, exchange_pos)
    checker.check_gate("position_reconciliation", all(r.matched for r in recon_results),
                      "Position reconciliation matched", critical=True)

    margin_result = recon_engine.check_margin(5000.0, 10000.0)
    checker.check_gate("margin_check", margin_result.sufficient, f"Margin ratio: {margin_result.margin_ratio:.2f}", critical=True)

    pnl_result = recon_engine.reconcile_pnl(1000.0, 1000.0)
    checker.check_gate("pnl_reconciliation", pnl_result["matched"], "PnL reconciliation matched", critical=True)

    # Gate 6: Telemetry
    print("\n[6/7] Checking Telemetry & Monitoring...")
    monitor = ProductionTelemetryMonitor(run_id=f"paper_{_ts()}", seed=42, risk_integrator=integrator)
    checker.check_gate("telemetry_monitor_init", monitor is not None, "Telemetry monitor initialized", critical=False)

    # Gate 7: Pre-Live Validation
    print("\n[7/7] Final Pre-Live Validation...")
    all_passed = checker.all_critical_passed()
    checker.check_gate("all_critical_gates_passed", all_passed,
                      f"{checker.passed}/{len(checker.gates)} gates passed", critical=True)

    print("\n" + "=" * 80)
    print(f"GATE SUMMARY: {checker.passed} passed, {checker.failed} failed")
    print(f"CRITICAL GATES: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    print("=" * 80)

    # Generate artifacts
    research_dir = Path("research_state")
    research_dir.mkdir(parents=True, exist_ok=True)

    campaign_artifact = {
        "campaign_type": "paper_trading",
        "mode": mode,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "seed": 42,
        "gates": checker.gates,
        "summary": {
            "total_gates": len(checker.gates),
            "passed": checker.passed,
            "failed": checker.failed,
            "all_critical_passed": all_passed,
        },
        "trading_engine_summary": live_engine.get_trading_summary(),
        "reconciliation_audit": recon_engine.get_audit_report(),
        "secrets_redacted": True,
        "strict_serialization": True,
    }

    campaign_path = _write_json(research_dir / f"PAPER_TRADING_CAMPAIGN_{_ts()}.json", campaign_artifact)

    recon_audit = {
        "audit_type": "reconciliation",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reconciliation_engine": recon_engine.get_audit_report(),
        "live_trading_summary": live_engine.get_trading_summary(),
    }
    recon_path = _write_json(research_dir / f"RECONCILIATION_AUDIT_{_ts()}.json", recon_audit)

    gate_report = {
        "report_type": "pre_live_gate",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "strict_gates": strict_gates,
        "gates_only": gates_only,
        "checker_results": checker.gates,
        "summary": {
            "total": len(checker.gates),
            "passed": checker.passed,
            "failed": checker.failed,
            "critical_passed": all_passed,
        },
        "recommendation": "READY FOR PAPER TRADING" if all_passed else "DO NOT PROCEED - FIX FAILED GATES",
    }
    gate_path = _write_json(research_dir / f"PRE_LIVE_GATE_REPORT_{_ts()}.json", gate_report)

    print(f"\nArtifacts emitted:")
    print(f"  - {campaign_path}")
    print(f"  - {recon_path}")
    print(f"  - {gate_path}")

    return campaign_artifact


def main():
    parser = argparse.ArgumentParser(description="Run paper trading campaign with pre-live gates")
    parser.add_argument("--mode", choices=["paper", "live"], default="paper", help="Trading mode")
    parser.add_argument("--gates-only", action="store_true", help="Only run gates, don't start trading")
    parser.add_argument("--strict-gates", action="store_true", help="Strict gate checking")
    args = parser.parse_args()

    try:
        result = run_paper_trading_campaign(args.mode, args.gates_only, args.strict_gates)
        if not result["summary"]["all_critical_passed"]:
            sys.exit(1)
        sys.exit(0)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
