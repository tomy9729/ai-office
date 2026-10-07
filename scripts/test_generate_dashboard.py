"""Synthetic fixtures only; run with python -m unittest discover -s scripts."""
from datetime import date
import json
from pathlib import Path
import tempfile
import unittest

import generate_dashboard as dashboard


class DashboardTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        (self.root / "Reports" / "2026" / "10").mkdir(parents=True)
        (self.root / "Decisions").mkdir()

    def write(self, name, content):
        path = self.root / "Reports" / "2026" / "10" / name
        path.write_text(content, encoding="utf-8")
        return path

    def test_end_to_end_totals_periods_links_and_upsert(self):
        self.write("quoted # report.md", '''---
ticket: AO-example
title: "A: B # C \\"quote\\" </script><img src=x>"
date: 2026-10-07
status: COMPLETED
size: M
estimated_md: 1.5
final_md: 2.0
project: example
type: core
agents:
  - Implementer
  - QA
models:
  - '6.1 Sol'
---
# Body
''')
        self.write("zero.md", '''---
title: zero
date: 2026-10-07
status: PARTIAL
size: S
estimated_md: 0
final_md: 0
agents: []
models: []
---
''')
        self.write("estimated.md", '''---
date: 2026-10-08
size: L
estimated_md: 1
---
# Estimated
''')
        self.write("2026-10-07-legacy.md", "# Legacy\n\n## 状態\nCOMPLETED\n\n## 상태\nBLOCKED — reason\n")
        self.write("undated.md", "# Undated\nmentioned COMPLETED\n")
        self.write("old.md", "---\ndate: 2025-12-31\nfinal_md: 4\n---\n")
        (self.root / "Decisions" / "DECISIONS.md").write_text(
            "# Decisions\n- 2026-10-07 | 결정: first\n## 2026-10-07 - section\n- 결정: second\n- 이유: no count\n- Decision: third\n## 2026-09-01\n- 결정: old\n", encoding="utf-8")
        original = {p: p.read_bytes() for p in self.root.rglob("*.md")}
        data = dashboard.generate(self.root, date(2026, 10, 7), "Asia/Seoul", current_date=date(2026, 10, 7))
        day = data["periods"]["daily"]["summary"]
        self.assertEqual(day["count"], 3)
        self.assertEqual(day["estimated_md"], 1.5)
        self.assertEqual(day["final_md"], 2)
        self.assertEqual(day["average_md"], 1)
        self.assertEqual(day["md_count"], 2)
        self.assertEqual(day["status"]["BLOCKED"], 1)
        self.assertEqual(day["decision_count"], 3)
        self.assertEqual(day["core_count"], 1)
        self.assertEqual(day["size_average_md"]["S"], 0)
        self.assertEqual(day["project_md"], {"UNKNOWN": 0, "example": 2})
        week = data["periods"]["weekly"]["summary"]
        self.assertEqual(week["count"], 4)
        self.assertEqual(week["average_md"], 1)
        self.assertEqual(data["periods"]["current"]["summary"]["count"], 6)
        current = self.root / "Dashboard" / "Current" / "index.html"
        output = current.read_text(encoding="utf-8")
        self.assertNotIn("</script><img", output)
        self.assertIn("\\u003c/script\\u003e", output)
        self.assertIn("quoted%20%23%20report.md", output)
        self.assertNotIn("fetch(", output)
        self.assertIn("Operations Console", output)
        self.assertIn("check_dashboard.cjs", dashboard.TEMPLATE)
        legacy = next(r for r in data["periods"]["daily"]["reports"] if r["title"] == "Legacy")
        self.assertEqual(legacy["content"].splitlines()[0], "# Legacy")
        self.assertEqual(json.loads((current.parent / "data.json").read_text(encoding="utf-8")), data)
        daily = self.root / "Dashboard" / "Archive" / "Daily" / "2026" / "10" / "2026-10-07.html"
        self.assertTrue(daily.exists())
        self.assertIn("../../../../../Reports/", daily.read_text(encoding="utf-8"))
        archive_before = daily.read_bytes()
        dashboard.generate(self.root, date(2026, 10, 8), "Asia/Seoul", current_date=date(2026, 10, 8))
        self.assertEqual(daily.read_bytes(), archive_before)
        self.assertEqual(len(list((self.root / "Dashboard" / "Archive" / "Weekly").rglob("*.html"))), 1)
        self.assertEqual(len(list((self.root / "Dashboard" / "Archive" / "Monthly").rglob("*.html"))), 1)
        self.assertEqual(original, {p: p.read_bytes() for p in self.root.rglob("*.md")})

    def test_invalid_metadata_preserves_current(self):
        self.write("valid.md", "---\ndate: 2026-10-07\n---\n")
        dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))
        current = self.root / "Dashboard" / "Current" / "index.html"
        original = current.read_bytes()
        for malformed in ("estimated_md: NaN", "final_md: -1", "size: XL", "status: DONE", "work_status: DONE",
                          "date: 2026-99-01", "models: requested-model", "date: 2026-10-07\ndate: 2026-10-08",
                          "title: |", "title: unquoted: colon"):
            with self.subTest(malformed=malformed):
                self.write("bad.md", "---\n" + malformed + "\n---\n")
                with self.assertRaises(ValueError):
                    dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))
                self.assertEqual(current.read_bytes(), original)
        self.write("bad.md", "---\ntitle: missing end\n")
        with self.assertRaises(ValueError):
            dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))

    def test_scalar_and_missing_md(self):
        self.assertEqual(dashboard.scalar("'Bob''s # title: value' # comment"), "Bob's # title: value")
        self.assertEqual(dashboard.scalar('"line\\nquoted\\\"" # comment'), 'line\nquoted"')
        self.assertEqual(dashboard.scalar("0.25 # estimate"), "0.25")
        self.write("legacy.md", "# No MD\nTicket: AO-legacy\nDate: 2026-10-07 (Asia/Seoul)\n## 상태\nCOMPLETED\n")
        data = dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))
        summary = data["periods"]["daily"]["summary"]
        self.assertIsNone(summary["average_md"])
        self.assertIsNone(summary["final_md"])
        self.assertIsNone(summary["estimated_md"])
        self.assertEqual(summary["project_md"], {"UNKNOWN": None})
        self.assertEqual(summary["completion_rate"], 100)
        self.assertEqual(summary["work_status"], {"UNKNOWN": 1})
        self.assertEqual(data["schema_version"], 2)
        self.assertEqual(data["periods"]["daily"]["reports"][0]["ticket"], "AO-legacy")
        dashboard.generate(self.root, date(2027, 1, 1), "UTC", current_date=date(2027, 1, 1))
        self.assertTrue((self.root / "Dashboard" / "Archive" / "Weekly" / "2026" / "2026-W53.html").exists())

    def test_work_status_and_failed_generation_preserves_work(self):
        path = self.write("work.md", "---\nstatus: PARTIAL\nwork_status: COMPLETED\n---\n")
        data = dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))
        row = data["periods"]["current"]["reports"][0]
        self.assertEqual((row["status"], row["work_status"]), ("PARTIAL", "COMPLETED"))
        snapshots = {p: p.read_bytes() for p in (self.root / "Dashboard").rglob("*") if p.is_file()}
        self.write("bad.md", "---\nwork_status: DONE\n---\n")
        with self.assertRaises(ValueError):
            dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))
        self.assertEqual(snapshots, {p: p.read_bytes() for p in (self.root / "Dashboard").rglob("*") if p.is_file()})
        self.assertEqual(dashboard.report(self.root, path)["work_status"], "COMPLETED")
        for value in ("COMPLETED", "PARTIAL", "BLOCKED", "null"):
            path = self.write("work.md", "---\nwork_status: " + value + "\n---\n")
            self.assertEqual(dashboard.report(self.root, path)["work_status"], "UNKNOWN" if value == "null" else value)

    def test_operating_docs_allow_missing_display_information(self):
        core = Path(__file__).resolve().parent.parent
        for name in ("SKILL.md", "README.md", "references/templates.md"):
            text = (core / name).read_text(encoding="utf-8")
            self.assertIn("role_action_target", text)
            self.assertNotIn("모델 없는 이름으로 생성하지", text)
            self.assertNotIn("모델 없는 제목으로 생성하지", text)
        self.assertIn("이름 관측 실패", (core / "SKILL.md").read_text(encoding="utf-8"))

    def test_workspace_boundary(self):
        with self.assertRaises(ValueError):
            dashboard.within(self.root, self.root / ".." / "outside")
        with tempfile.TemporaryDirectory() as outside:
            link = self.root / "Reports" / "linked"
            try:
                link.symlink_to(outside, target_is_directory=True)
            except OSError:
                self.skipTest("Platform does not permit symlink creation")
            with self.assertRaises(ValueError):
                dashboard.generate(self.root, date(2026, 10, 7), "UTC", current_date=date(2026, 10, 7))

    def test_historical_archive_does_not_change_current_day(self):
        self.write("now.md", "---\ndate: 2026-10-07\nfinal_md: 2\n---\n")
        self.write("past.md", "---\ndate: 2026-09-01\nfinal_md: 1\n---\n")
        data = dashboard.generate(self.root, date(2026, 9, 1), "UTC", current_date=date(2026, 10, 7))
        self.assertEqual(data["date"], "2026-10-07")
        self.assertEqual(data["today_count"], 1)
        self.assertEqual(data["periods"]["daily"]["summary"]["final_md"], 2)
        past = self.root / "Dashboard" / "Archive" / "Daily" / "2026" / "09" / "2026-09-01.html"
        embedded = past.read_text(encoding="utf-8").split('<script type="application/json" id="data">')[1].split('</script>')[0]
        snapshot = json.loads(embedded)
        self.assertEqual(snapshot["date"], "2026-09-01")
        self.assertEqual(snapshot["periods"]["daily"]["summary"]["final_md"], 1)
        self.assertEqual(snapshot["view"], "daily")
        self.assertEqual(snapshot["periods"]["current"]["summary"]["count"], 1)
        self.assertNotIn("now.md", [r["path"].rsplit("/", 1)[-1] for r in snapshot["periods"]["current"]["reports"]])
        self.assertFalse((self.root / "Dashboard" / "Archive" / "Daily" / "2026" / "10").exists())
        current = self.root / "Dashboard" / "Current" / "data.json"
        self.assertEqual(json.loads(current.read_text(encoding="utf-8")), data)


if __name__ == "__main__":
    unittest.main()
