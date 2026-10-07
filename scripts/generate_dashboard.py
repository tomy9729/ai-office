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
    size = metadata.get("size") or "UNKNOWN"
    if status not in ("COMPLETED", "PARTIAL", "BLOCKED", "UNKNOWN"):
        raise ValueError("status must be COMPLETED, PARTIAL, BLOCKED or absent")
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
    return dict(ticket=metadata.get("ticket") or (legacy_ticket[1] if legacy_ticket else None), title=title, date=date_value, status=status,
                size=size, estimated_md=estimated, final_md=final, md=representative,
                project=metadata.get("project") or "UNKNOWN", type=metadata.get("type") or "UNKNOWN",
                path=path.relative_to(root).as_posix(), metadata=has_metadata, **lists)


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
    return dict(count=count, status=counts("status"), size=counts("size"), projects=counts("project"),
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
    return dict(schema_version=1, date=today.isoformat(), timezone=timezone,
                today_count=periods["daily"]["summary"]["count"], periods=periods)


TEMPLATE = r'''<!doctype html>
<html lang="ko"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>AI Office Dashboard</title>
<style>
:root{color-scheme:light;--ink:#193146;--muted:#586d80;--blue:#1667ac;--line:#d6e0e8}*{box-sizing:border-box}body{margin:0;background:#f3f6fa;color:var(--ink);font:15px/1.5 system-ui,sans-serif}main{max-width:1250px;margin:auto;padding:32px}h1{font-size:32px;margin:0}h2{font-size:19px;margin:0 0 16px}p{color:var(--muted)}a{color:var(--blue)}.cards,.grid{display:grid;gap:16px}.cards{grid-template-columns:repeat(auto-fit,minmax(175px,1fr));margin:24px 0}.grid{grid-template-columns:repeat(auto-fit,minmax(320px,1fr))}.card,section{min-width:0;background:white;border:1px solid var(--line);border-radius:12px;padding:20px}.card b{display:block;font-size:25px;margin-top:8px}.label{color:var(--muted);font-size:13px}.bars{display:grid;gap:10px}.bar{display:grid;grid-template-columns:100px 1fr 100px;gap:10px;align-items:center}.bar span{overflow-wrap:anywhere}.track{background:#e8eef5;height:14px;border-radius:7px;overflow:hidden}.fill{height:100%;background:var(--blue)}.bar small{text-align:right}section.wide{grid-column:1/-1}table{border-collapse:collapse;width:100%;font-size:14px}th,td{text-align:left;padding:11px 8px;border-bottom:1px solid var(--line)}th{color:var(--muted)}.scroll{overflow-x:auto}ul{padding-left:20px}li{margin:8px 0}nav{display:flex;gap:12px;flex-wrap:wrap;margin:16px 0}nav a{padding:6px 10px;border:1px solid var(--line);border-radius:6px;background:white}select{padding:8px;font:inherit}footer{margin-top:24px;color:var(--muted);font-size:13px}@media(max-width:600px){main{padding:16px}.grid{grid-template-columns:1fr}.bar{grid-template-columns:90px 1fr 75px}}
</style>
<main><h1>AI Office Dashboard</h1><p id="subtitle"></p><nav id="navigation"></nav>
<label for="period">집계 기간 </label><select id="period"><option value="current">전체 / 최신</option><option value="daily">일간</option><option value="weekly">주간</option><option value="monthly">월간</option></select>
<div class="cards" id="cards"></div><div class="grid" id="content"></div>
<footer>Markdown Report 기반 스냅샷 · MD는 사람 기준으로 환산한 상대적 업무량 추정치입니다. 실행 시간·Token·인사 평가와 무관합니다. 평균은 Final MD → md → Estimated MD 순으로 존재하는 대표값만 사용합니다. UNKNOWN과 MD 미기록은 추정하지 않습니다.</footer></main>
<script type="application/json" id="data">__DATA__</script>
<script>
const data=JSON.parse(document.getElementById('data').textContent);
const view=data.view, root=document.getElementById('content'), cards=document.getElementById('cards');
const fmt=v=>v===null||v===undefined?'미기록':Number(v).toLocaleString('ko-KR',{maximumFractionDigits:4});
function node(tag,text,parent){const n=document.createElement(tag);if(text!==undefined)n.textContent=text;if(parent)parent.append(n);return n}
function link(text,url,parent){const a=node('a',text,parent);a.href=url;return a}
function section(title,wide=false){const s=node('section',undefined,root);if(wide)s.className='wide';node('h2',title,s);return s}
function bars(title,values,suffix='',ratio=false){const s=section(title), box=node('div',undefined,s);box.className='bars';if(!values.length){node('p','기록 없음',box);return}const max=Math.max(1,...values.map(x=>x[1]??0)),sum=values.reduce((a,x)=>a+(x[1]??0),0);for(const [label,value] of values){const row=node('div',undefined,box);row.className='bar';node('span',label,row);const track=node('div',undefined,row);track.className='track';const fill=node('div',undefined,track);fill.className='fill';fill.style.width=(100*(value??0)/max)+'%';node('small',fmt(value)+(value===null?'':suffix)+(ratio&&sum?' ('+fmt(value/sum*100)+'%)':''),row)}}
function reportTable(title,reports){const s=section(title,true);if(!reports.length){node('p','기록 없음',s);return}const scroll=node('div',undefined,s);scroll.className='scroll';const table=node('table',undefined,scroll),head=node('tr',undefined,node('thead',undefined,table));for(const x of ['날짜 / Ticket','업무','상태','Size','Estimated / Final / 대표 MD','프로젝트'])node('th',x,head);const body=node('tbody',undefined,table);for(const r of reports){const tr=node('tr',undefined,body);node('td',(r.date||'날짜 미기록')+' / '+(r.ticket||'Ticket 없음'),tr);link(r.title,r.url,node('td',undefined,tr));node('td',r.status,tr);node('td',r.size,tr);node('td',[r.estimated_md,r.final_md,r.md].map(fmt).join(' / '),tr);node('td',r.project,tr)}}
function render(key){root.replaceChildren();cards.replaceChildren();const p=data.periods[key],s=p.summary;document.getElementById('subtitle').textContent=data.date+' · '+data.timezone+' · '+(p.start?p.start+' ~ '+p.end+' (종료일 제외)':'전체 기록')+' · 날짜 미기록은 전체에만 포함';const metrics=[['오늘 업무',data.today_count],['기간 업무',s.count],['완료율',s.completion_rate===null?'미기록':fmt(s.completion_rate)+'%'],['Estimated MD',fmt(s.estimated_md)],['Final MD',fmt(s.final_md)],['대표 MD 합계',fmt(s.total_md)],['평균 MD',fmt(s.average_md)],['MD 기록 / 미기록',s.md_count+' / '+(s.count-s.md_count)],['Decision',s.decision_count],['Core 개선',s.core_count]];for(const [label,value]of metrics){const c=node('div',undefined,cards);c.className='card';node('span',label,c).className='label';node('b',value,c)}
bars('상태 분포',Object.entries(s.status));bars('Size 분포',Object.entries(s.size),'',true);bars('Role 참여',Object.entries(s.roles));bars('확인된 Model 사용',Object.entries(s.models));bars('프로젝트 업무 비율',Object.entries(s.projects),'',true);bars('프로젝트별 대표 MD',Object.entries(s.project_md),' MD');bars('Size별 평균 MD',Object.entries(s.size_average_md),' MD');bars('일별 대표 MD',s.daily_md.map(x=>[x.label,x.md]),' MD');bars('주별 대표 MD',s.weekly_md.map(x=>[x.label,x.md]),' MD');bars('주별 업무량',s.weekly_md.map(x=>[x.label,x.count]),'건');bars('Estimated vs Final MD',[['Estimated',s.estimated_md],['Final',s.final_md]],' MD');reportTable(key==='current'?'최근 업무 (최대 30개)':'기간 업무',key==='current'?p.reports.slice(0,30):p.reports);const ds=section('주요 Decision',true);if(!p.decisions.length)node('p','기록 없음',ds);const ul=node('ul',undefined,ds);for(const d of p.decisions.slice(-30).reverse())link((d.date||'날짜 미기록')+' · '+d.text,d.url,node('li',undefined,ul));reportTable('최근 Core 개선 (type: core)',p.reports.filter(r=>r.type==='core').slice(0,20))}
const select=document.getElementById('period');select.value=view;select.addEventListener('change',()=>render(select.value));for(const [label,url]of Object.entries(data.navigation))link(label,url,document.getElementById('navigation'));render(view);
</script></html>'''


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
    outputs = {target: render(root, target, data if view == "current" else archive_data, view, targets)
               for view, target in targets.items()}
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
