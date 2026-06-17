#!/usr/bin/env python3
"""
astra-sre triage.py — Phase 2-⑤: Symptom → Incident Matcher
Search sre_incidents knowledge base for similar past incidents.

Usage:
    ./triage.py "E2EE 无法解密 消息"
    ./triage.py "Gateway sync error 离线" --top 3
    ./triage.py --list                # List all incidents
    ./triage.py --tag P1              # Filter by severity tag
"""
import argparse
import json
import sys

from kb_access import search_kb, list_all, parse_tags

INCIDENTS_KB = "sre_incidents"


# ── Helpers ───────────────────────────────────────────────────
def severity_from_tags(tags: list[str]) -> str:
    """Extract severity from tags."""
    for t in tags:
        t = t.strip().lower()
        if t in ("p1", "p2", "p3", "p0"):
            return t.upper()
    return "N/A"


def severity_emoji(sev: str) -> str:
    return {"P1": "🔴", "P2": "🟠", "P3": "🟡"}.get(sev, "⚪")


def snippet(text: str, max_len: int = 300) -> str:
    txt = text.replace("\n", " ").strip()
    return txt[:max_len] + ("…" if len(txt) > max_len else "")


# ── Main ─────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="🔍 astra-sre triage — 诊断时自动搜 sre_incidents 找相似案例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  %(prog)s \"E2EE 无法解密\"\n"
               "  %(prog)s \"Gateway sync error\" --top 5\n"
               "  %(prog)s --list\n"
               "  %(prog)s --tag P1",
    )
    parser.add_argument("query", nargs="?", help="症状描述（自然语言）")
    parser.add_argument("--top", type=int, default=5, help="最多返回几条 (default: 5)")
    parser.add_argument("--list", action="store_true", help="列出所有已记录的事故")
    parser.add_argument("--tag", help="按严重度标签过滤 (P1/P2/P3)")
    parser.add_argument("--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    # ── List mode ──
    if args.list:
        incidents = list_all(INCIDENTS_KB)
        if not incidents:
            print("📭 sre_incidents 知识库为空")
            return

        # Deduplicate by title
        seen = set()
        unique = []
        for inc in incidents:
            if inc["title"] not in seen:
                seen.add(inc["title"])
                unique.append(inc)

        if args.tag:
            tag_filter = args.tag.upper()
            unique = [
                i for i in unique
                if tag_filter in [t.upper().strip() for t in parse_tags(i.get("tags", "[]"))]
            ]

        print(f"\n📚 sre_incidents — {len(unique)} 条事故记录\n")
        for i, inc in enumerate(unique, 1):
            tags = parse_tags(inc.get("tags", "[]"))
            sev = severity_from_tags(tags)
            tags_str = ", ".join(tags)
            print(f"  {i}. {sev} {inc['title']}")
            print(f"     Tags: {tags_str}")
            print()
        return

    # ── Search mode ──
    if not args.query:
        parser.print_help()
        sys.exit(1)

    matches = search_kb(INCIDENTS_KB, args.query, args.top)

    if args.tag:
        tag_filter = args.tag.upper()
        matches = [
            m for m in matches
            if tag_filter in [t.upper().strip() for t in parse_tags(m.get("tags", "[]"))]
        ]

    if args.json:
        print(json.dumps([
            {
                "title": m["title"],
                "score": m["score"],
                "severity": severity_from_tags(parse_tags(m.get("tags", "[]"))),
                "tags": parse_tags(m.get("tags", "[]")),
                "snippet": snippet(m.get("content", ""), 300),
                "full_content": m.get("content", ""),
            }
            for m in matches
        ], ensure_ascii=False, indent=2))
        return

    # Markdown output
    if not matches:
        print(f"\n🔍 未在 sre_incidents 中找到与「{args.query}」匹配的案例\n")
        return

    print(f"\n🔍 搜索「{args.query}」— 找到 {len(matches)} 个匹配案例\n")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
    for i, m in enumerate(matches, 1):
        tags = parse_tags(m.get("tags", "[]"))
        sev = severity_from_tags(tags)
        print(f"### {i}. {sev} {m['title']}")
        print(f"**相似度**: {m['score']:.3f}")
        print(f"**标签**: {', '.join(tags)}")
        print(f"**摘要**: {snippet(m.get('content', ''), 200)}")
        print()

    print(f"ℹ️  完整 incident 内容可通过 kb_search('sre_incidents', '{args.query}') 获取\n")


if __name__ == "__main__":
    main()
