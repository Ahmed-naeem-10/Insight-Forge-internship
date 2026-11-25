import time
import argparse
import schedule
from tracker import run_tracker_cycle, logger


def main():
    parser = argparse.ArgumentParser(description="Automated Price Tracker & Alert Engine (Project 4)")
    parser.add_argument("--once", action="store_true", help="Run a single tracking cycle immediately and exit")
    parser.add_argument("--demo-alert", action="store_true", help="Demonstrate price drop alert detection with simulated discount")
    parser.add_argument("--interval", type=int, default=15, help="Scheduling interval in minutes for continuous background monitoring")
    parser.add_argument("--pages", type=int, default=2, help="Number of pages to scrape per cycle (default: 2)")

    args = parser.parse_args()

    if args.demo_alert:
        print("\n" + "=" * 65)
        print("🧪 RUNNING DEMONSTRATION CYCLE (SIMULATING 15% PRICE DROP)")
        print("=" * 65)
        # Seed an initial baseline first if empty
        run_tracker_cycle(max_pages=args.pages, simulated_price_drop=False)
        # Run second cycle with simulated price drop to trigger the alert
        result = run_tracker_cycle(max_pages=args.pages, simulated_price_drop=True)
        print(f"\n✓ Demo completed. Alerts triggered: {result['alerts_count']}")
        return

    if args.once:
        print("\n" + "=" * 65)
        print("🚀 EXECUTING SINGLE AUTOMATED MONITORING RUN")
        print("=" * 65)
        run_tracker_cycle(max_pages=args.pages)
        return

    # Continuous Local Scheduler Loop (Step 3)
    logger.info(f"Starting continuous local scheduler (Interval: every {args.interval} minutes)...")
    logger.info("Press CTRL+C to terminate.")

    # Run once immediately on startup
    run_tracker_cycle(max_pages=args.pages)

    # Schedule subsequent runs
    schedule.every(args.interval).minutes.do(run_tracker_cycle, max_pages=args.pages)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user.")


if __name__ == "__main__":
    main()
