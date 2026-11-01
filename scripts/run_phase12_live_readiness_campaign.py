"""CLI to run Phase 12 live readiness campaign."""
from src.execution.phase12_campaign import Phase12Campaign


def main():
    camp = Phase12Campaign(symbols=("BTC", "ETH"), seed=42, venues=("deribit", "okx", "binance"), paper_only=True)
    res = camp.run()
    print("PHASE12_DONE")
    for a in res["artifacts"]:
        print(a)


if __name__ == "__main__":
    main()
