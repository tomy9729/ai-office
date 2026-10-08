#!/usr/bin/env python3
"""Build file:// dashboards from Markdown, using only the Python standard library.

Frontmatter supports flat scalar values and scalar block lists (agents/models).
Quote strings containing YAML punctuation. Double quotes use JSON escapes; YAML
single quotes escape an apostrophe by doubling it. Nested YAML, anchors, tags and
multiline values are intentionally rejected. Reports without frontmatter remain
visible, with unknown metadata; no historical Size/MD/model is inferred.
"""

import argparse
from collections import Counter, defaultdict
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation
import json
import os
from pathlib import Path
import re
import tempfile
from urllib.parse import quote
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def within(root, path):
    """Reject escaping symlinks/junctions before reading or writing."""
    resolved = path.resolve()
    if not resolved.is_relative_to(root):
        raise ValueError(f"Path escapes workspace: {path.name}")
    return resolved


def scalar(value):
    value = value.strip()
    if not value or value in ("null", "Null", "NULL", "~"):
        return None
    if value.startswith('"'):
        decoder = json.JSONDecoder()
        parsed, end = decoder.raw_decode(value)
        tail = value[end:].strip()
        if not isinstance(parsed, str) or (tail and not tail.startswith("#")):
            raise ValueError("Invalid quoted scalar")
        return parsed
    if value.startswith("'"):
        match = re.fullmatch(r"'((?:[^']|'')*)'\s*(?:#.*)?", value)
        if not match:
            raise ValueError("Invalid single-quoted scalar")
        return match[1].replace("''", "'")
    value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
    if value.startswith(("[", "{", "&", "*", "!", "|", ">", "#")) or re.search(r":\s", value):
        raise ValueError("Unsupported YAML value; use a quoted scalar or block list")
    return value


def frontmatter(text):
    lines = text.lstrip("\ufeff").splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, False
    result = {}
    list_key = None
    for number, line in enumerate(lines[1:], 2):
        if line.strip() == "---":
            return result, True
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = re.fullmatch(r"\s+-\s+(.*)", line)
        if item and list_key:
            result[list_key].append(scalar(item[1]))
            continue
        match = re.fullmatch(r"([a-zA-Z_][\w-]*):(?:\s+(.*))?", line)
        if not match or match[1] in result:
            raise ValueError(f"Invalid or duplicate frontmatter key at line {number}")
        key, value = match[1], match[2]
        list_key = key if key in ("agents", "models") and value in (None, "", "[]") else None
        result[key] = [] if list_key else scalar(value or "")
    raise ValueError("Unclosed frontmatter")


def md_value(value, key):
    if value is None:
        return None
    try:
        number = Decimal(str(value))
    except InvalidOperation as error:
        raise ValueError(f"{key} must be a nonnegative finite number") from error
    if not number.is_finite() or number < 0 or not float(number) < float("inf"):
        raise ValueError(f"{key} must be a nonnegative finite number")
    return float(number)


def report(root, path):
    text = within(root, path).read_text(encoding="utf-8-sig")
    metadata, has_metadata = frontmatter(text)
    for key, value in metadata.items():
        if key not in ("agents", "models") and isinstance(value, list):
            raise ValueError(f"{key} must be a scalar")
    title = metadata.get("title")
    if not title:
        heading = re.search(r"^#\s+(.+)$", text, re.M)
        title = heading[1] if heading else path.stem
    # Explicit legacy labels are evidence; prose mentions are not metadata.
    legacy_ticket = re.search(r"^(?:-\s*)?Ticket:\s*(\S+)\s*$", text, re.M)
    legacy_date = re.search(r"^(?:-\s*)?(?:Date|날짜):\s*(\d{4}-\d{2}-\d{2})(?:\s+\([^\r\n()]+\))?\s*$", text, re.M)
    legacy_status = re.search(r"^##\s+(?:상태|Status)\s*\n\s*(?:-\s*)?(COMPLETED|PARTIAL|BLOCKED)\b", text, re.M)
    date_value = metadata.get("date") or (legacy_date[1] if legacy_date else None)
    if not date_value:
        found = re.search(r"(?<!\d)(\d{4}-\d{2}-\d{2})(?!\d)", path.stem)
        # Ticket filenames contain compact dates; they do not establish report dates.
        date_value = found[1] if found else None
    if date_value:
        date_value = date.fromisoformat(str(date_value)).isoformat()
    status = metadata.get("status") or (legacy_status[1] if legacy_status else "UNKNOWN")
    work_status = metadata.get("work_status") or "UNKNOWN"
    size = metadata.get("size") or "UNKNOWN"
    if status not in ("COMPLETED", "PARTIAL", "BLOCKED", "UNKNOWN"):
        raise ValueError("status must be COMPLETED, PARTIAL, BLOCKED or absent")
    if work_status not in ("COMPLETED", "PARTIAL", "BLOCKED", "UNKNOWN"):
        raise ValueError("work_status must be COMPLETED, PARTIAL, BLOCKED or absent")
    if size not in ("S", "M", "L", "UNKNOWN"):
        raise ValueError("size must be S, M, L or absent")
    lists = {}
    for key in ("agents", "models"):
        values = metadata.get(key) or []
        if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
            raise ValueError(f"{key} must be a scalar block list")
        if key == "models" and any(v.lower() in ("unknown", "unknown model", "model unknown", "모델 미확정", "미확인 모델") for v in values):
            raise ValueError("models must contain confirmed actual models, without placeholders")
        lists[key] = list(dict.fromkeys(values))
    estimated = md_value(metadata.get("estimated_md"), "estimated_md")
    final = md_value(metadata.get("final_md"), "final_md")
    legacy_md = md_value(metadata.get("md"), "md")
    representative = final if final is not None else legacy_md if legacy_md is not None else estimated
    return dict(ticket=metadata.get("ticket") or (legacy_ticket[1] if legacy_ticket else None), title=title, date=date_value, status=status, work_status=work_status,
                recording_issue=(metadata.get("recording_issue") or "").strip() or None,
                size=size, estimated_md=estimated, final_md=final, md=representative,
                project=metadata.get("project") or "UNKNOWN", type=metadata.get("type") or "UNKNOWN",
                path=path.relative_to(root).as_posix(), metadata=has_metadata, content=text, **lists)


def read_decisions(root):
    path = root / "Decisions" / "DECISIONS.md"
    if not path.exists():
        return []
    result, section_date = [], None
    for line in within(root, path).read_text(encoding="utf-8-sig").splitlines():
        heading = re.match(r"^#+\s+(\d{4}-\d{2}-\d{2})\b", line)
        if line.startswith("#"):
            section_date = date.fromisoformat(heading[1]).isoformat() if heading else None
        dated = re.match(r"^-\s+(\d{4}-\d{2}-\d{2})\s*\|", line)
        if "결정:" not in line and "Decision:" not in line:
            continue
        if not line.lstrip().startswith("-"):
            continue
        day = date.fromisoformat(dated[1]).isoformat() if dated else section_date
        result.append(dict(date=day, text=line.lstrip("- "), path="Decisions/DECISIONS.md"))
    return result


def collect(root):
    reports = []
    directory = root / "Reports"
    if directory.exists():
        within(root, directory)
        # os.walk avoids following directory symlinks; reject them rather than hide records.
        for folder, directories, files in os.walk(directory, followlinks=False):
            for name in directories + files:
                within(root, Path(folder) / name)
            for name in sorted(files):
                if name.lower().endswith(".md"):
                    path = Path(folder) / name
                    try:
                        reports.append(report(root, path))
                    except (ValueError, json.JSONDecodeError) as error:
                        raise ValueError(f"{path.relative_to(root).as_posix()}: {error}") from error
    reports.sort(key=lambda row: (row["date"] or "", row["path"]), reverse=True)
    return reports, read_decisions(root)


def summary(reports, decisions):
    def counts(key):
        return dict(sorted(Counter(row[key] for row in reports).items()))
    def average(rows):
        values = [row["md"] for row in rows if row["md"] is not None]
        return round(sum(values) / len(values), 4) if values else None
    def total(key):
        values = [row[key] for row in reports if row[key] is not None]
        return round(sum(values), 4) if values else None
    groups, projects = defaultdict(list), defaultdict(list)
    for row in reports:
        groups[row["size"]].append(row)
        projects[row["project"]].append(row)
    daily, weekly = defaultdict(list), defaultdict(list)
    for row in reports:
        if row["date"]:
            day = date.fromisoformat(row["date"])
            year, week, _ = day.isocalendar()
            daily[row["date"]].append(row)
            weekly[f"{year}-W{week:02d}"].append(row)
    def trend(groups):
        return [dict(label=key, count=len(rows), md=round(sum(r["md"] for r in rows if r["md"] is not None), 4)
                     if any(r["md"] is not None for r in rows) else None) for key, rows in sorted(groups.items())]
    count = len(reports)
    return dict(count=count, status=counts("status"), work_status=counts("work_status"), size=counts("size"), projects=counts("project"),
                project_md={key: round(sum(r["md"] for r in rows if r["md"] is not None), 4)
                            if any(r["md"] is not None for r in rows) else None for key, rows in sorted(projects.items())},
                estimated_md=total("estimated_md"), final_md=total("final_md"), total_md=total("md"),
                average_md=average(reports), md_count=sum(r["md"] is not None for r in reports),
                completion_rate=round(100 * sum(r["status"] == "COMPLETED" for r in reports) / count, 2) if count else None,
                roles=dict(sorted(Counter(v for r in reports for v in r["agents"]).items())),
                models=dict(sorted(Counter(v for r in reports for v in r["models"]).items())),
                size_average_md={key: average(rows) for key, rows in sorted(groups.items())},
                daily_md=trend(daily), weekly_md=trend(weekly), decision_count=len(decisions),
                core_count=sum(r["type"] == "core" for r in reports))


def dataset(reports, decisions, today, timezone):
    monday = today - timedelta(days=today.weekday())
    month = today.replace(day=1)
    next_month = (month.replace(day=28) + timedelta(days=4)).replace(day=1)
    ranges = {"current": (None, None), "daily": (today, today + timedelta(days=1)),
              "weekly": (monday, monday + timedelta(days=7)), "monthly": (month, next_month)}
    periods = {}
    for key, (start, end) in ranges.items():
        def includes(row):
            return start is None or row["date"] is not None and start.isoformat() <= row["date"] < end.isoformat()
        rows = [r for r in reports if includes(r)]
        choices = [d for d in decisions if includes(d)]
        periods[key] = dict(reports=rows, decisions=choices, summary=summary(rows, choices),
                            start=start.isoformat() if start else None, end=end.isoformat() if end else None)
    return dict(schema_version=2, date=today.isoformat(), timezone=timezone,
                today_count=periods["daily"]["summary"]["count"], periods=periods)


TEMPLATE = Path(__file__).with_name('dashboard.html').read_text(encoding='utf-8')


def relative_url(root, source, target):
    within(root, target)
    relative = os.path.relpath(target, source.parent).replace(os.sep, "/")
    return "/".join(quote(part, safe="") for part in relative.split("/"))


def render(root, target, data, view, targets):
    snapshot = json.loads(json.dumps(data, ensure_ascii=False, allow_nan=False))
    snapshot["view"] = view
    snapshot["navigation"] = {key: relative_url(root, target, path) for key, path in targets.items()}
    for period in snapshot["periods"].values():
        for row in period["reports"] + period["decisions"]:
            row["url"] = relative_url(root, target, root / row["path"])
    encoded = json.dumps(snapshot, ensure_ascii=False, allow_nan=False).replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return TEMPLATE.replace("__DATA__", encoded)


def generate(workspace, today, timezone, *, current_date=None):
    root = Path(workspace).resolve(strict=True)
    if not root.is_dir():
        raise ValueError("Workspace must be a directory")
    reports, decisions = collect(root)
    current_date = current_date or datetime.now(ZoneInfo(timezone)).date()
    data = dataset(reports, decisions, current_date, timezone)
    archive_data = data if today == current_date else dataset(reports, decisions, today, timezone)
    year, week, _ = today.isocalendar()
    dashboard = root / "Dashboard"
    targets = {"current": dashboard / "Current" / "index.html",
               "daily": dashboard / "Archive" / "Daily" / str(today.year) / f"{today.month:02d}" / f"{today.isoformat()}.html",
               "weekly": dashboard / "Archive" / "Weekly" / str(year) / f"{year}-W{week:02d}.html",
               "monthly": dashboard / "Archive" / "Monthly" / str(today.year) / f"{today:%Y-%m}.html"}
    # Parse and render everything before touching existing snapshots.
    outputs = {}
    for view, target in targets.items():
        snapshot = data
        if view != "current":
            # Archive exploration cannot include dated records after its period.
            end = archive_data["periods"][view]["end"]
            rows = [r for r in reports if r["date"] is None or r["date"] < end]
            choices = [d for d in decisions if d["date"] is None or d["date"] < end]
            snapshot = dataset(rows, choices, today, timezone)
        outputs[target] = render(root, target, snapshot, view, targets)
    outputs[dashboard / "Current" / "data.json"] = json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    temporary = []
    try:
        for target, content in outputs.items():
            within(root, target)
            target.parent.mkdir(parents=True, exist_ok=True)
            within(root, target.parent)
            fd, name = tempfile.mkstemp(prefix=".dashboard-", suffix=".tmp", dir=target.parent)
            temporary.append((Path(name), target))
            with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                stream.write(content)
        for staged, target in temporary:
            within(root, target)
            os.replace(staged, target)
    finally:
        for staged, _ in temporary:
            staged.unlink(missing_ok=True)
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", required=True, type=Path)
    parser.add_argument("--timezone", default="UTC")
    parser.add_argument("--date", type=date.fromisoformat, help="Archive date (default: today in timezone); Current always uses today")
    args = parser.parse_args()
    try:
        zone = ZoneInfo(args.timezone)
        today = args.date or datetime.now(zone).date()
        data = generate(args.workspace, today, args.timezone)
    except (OSError, ValueError, ZoneInfoNotFoundError) as error:
        parser.exit(1, f"Dashboard generation failed: {error}\n")
    print(f"Dashboard generated: Current {data['date']}, Archive {today} ({data['periods']['current']['summary']['count']} reports)")


if __name__ == "__main__":
    main()
