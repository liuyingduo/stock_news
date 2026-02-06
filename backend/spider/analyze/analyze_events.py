"""
Batch AI analysis for events.
"""

import argparse
import asyncio
import os
import sys
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, backend_dir)

from app.core.database import close_mongo_connection, connect_to_mongo
from app.models import EventUpdate
from app.services.ai_service import get_ai_service
from app.services.database_service import db_service


class EventAnalyzer:
    def __init__(self, concurrency: int = 10):
        self.concurrency = max(1, concurrency)
        self.ai_service = None
        self.ok = 0
        self.fail = 0
        self.start_ts = 0.0
        self.lock = asyncio.Lock()

    async def get_candidate_events(
        self,
        limit: int,
        days: Optional[int],
        category: Optional[str],
        event_type: Optional[str],
        force: bool,
    ) -> List[Dict[str, Any]]:
        start_date = None
        if days is not None:
            start_date = datetime.utcnow() - timedelta(days=days)

        events, _ = await db_service.get_events(
            skip=0,
            limit=limit,
            category=category,
            event_type=event_type,
            start_date=start_date,
        )

        if force:
            return events
        return [evt for evt in events if not evt.get("ai_analysis")]

    async def _analyze_one(self, event: Dict[str, Any]) -> bool:
        try:
            result = await self.ai_service.analyze_and_classify(
                event_title=event["title"],
                event_content=event["content"],
                needs_classification=True,
            )
            ai_analysis = result["ai_analysis"]

            update = EventUpdate(
                ai_analysis=ai_analysis,
                event_category=result.get("event_category"),
                event_types=result.get("event_types"),
            )
            await db_service.update_event(event["id"], update)

            for sector in ai_analysis.affected_sectors or []:
                await db_service.create_or_update_sector(
                    name=sector.name,
                    code=sector.code or f"SECTOR_{sector.name}",
                )
            for stock in ai_analysis.affected_stocks or []:
                await db_service.create_or_update_stock(
                    name=stock.name,
                    code=stock.code or f"STOCK_{stock.name}",
                )
            return True
        except Exception as exc:
            print(f"\nFailed to analyze event {event.get('id')}: {exc}")
            return False

    async def _run_one(self, semaphore: asyncio.Semaphore, event: Dict[str, Any], total: int) -> None:
        async with semaphore:
            success = await self._analyze_one(event)
            async with self.lock:
                if success:
                    self.ok += 1
                else:
                    self.fail += 1
                done = self.ok + self.fail
                elapsed = max(time.time() - self.start_ts, 0.001)
                speed = done / elapsed
                eta = (total - done) / speed if speed > 0 else 0
                print(
                    f"\r[{done}/{total}] ok={self.ok} fail={self.fail} speed={speed:.2f}/s eta={eta:.0f}s",
                    end="",
                    flush=True,
                )

    async def run(
        self,
        limit: int,
        days: Optional[int],
        category: Optional[str],
        event_type: Optional[str],
        force: bool,
    ) -> None:
        self.ai_service = get_ai_service()
        if not self.ai_service:
            raise RuntimeError("AI service unavailable. Set ZHIPU_API_KEY first.")

        candidates = await self.get_candidate_events(limit, days, category, event_type, force)
        total = len(candidates)
        if total == 0:
            print("No events require analysis.")
            return

        print(f"Events to analyze: {total}, concurrency: {self.concurrency}")
        self.start_ts = time.time()
        sem = asyncio.Semaphore(self.concurrency)
        await asyncio.gather(*(self._run_one(sem, evt, total) for evt in candidates))
        print()
        print(f"Done. ok={self.ok}, fail={self.fail}, total={total}")


async def _main() -> None:
    parser = argparse.ArgumentParser(description="Batch AI analyze events")
    parser.add_argument("--limit", type=int, default=500, help="max events to read")
    parser.add_argument("--days", type=int, default=None, help="only analyze latest N days")
    parser.add_argument(
        "--category",
        type=str,
        default=None,
        choices=["global_macro", "policy", "industry", "company"],
    )
    parser.add_argument("--event-type", type=str, default=None)
    parser.add_argument("--concurrency", "-c", type=int, default=10)
    parser.add_argument("--force", action="store_true", help="reanalyze even when ai_analysis exists")
    args = parser.parse_args()

    await connect_to_mongo()
    try:
        analyzer = EventAnalyzer(concurrency=args.concurrency)
        await analyzer.run(
            limit=args.limit,
            days=args.days,
            category=args.category,
            event_type=args.event_type,
            force=args.force,
        )
    finally:
        await close_mongo_connection()


if __name__ == "__main__":
    asyncio.run(_main())
