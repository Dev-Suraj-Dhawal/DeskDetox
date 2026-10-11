#!/usr/bin/env python3
"""DeskDetox - AI-powered Outdoor Micro-Adventure Guide.

Challenge: Touch Grass (Hackathon)
Gets remote workers off screens and outdoors during their breaks.

Usage:
    python main.py
    python main.py --minutes 20
    python main.py --test-tools
"""

import sys
import asyncio
import argparse
import logging  # <-- ADDED
from typing import Optional

# <-- ADDED: Mute standard warnings so they don't ruin the CLI UI during API retries -->
logging.getLogger().setLevel(logging.ERROR)

# Ensure Windows terminals handle UTF-8 cleanly
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from deskdetox.cli import interactive_loop, run_mission_flow, print_banner, check_api_key_or_warn, console
from deskdetox.tools import get_location, get_weather, get_nearby_nature


def run_diagnostics() -> None:
    """Smoke test and print diagnostics for the three open data tools."""
    from rich.table import Table
    from rich.panel import Panel

    console.print("\n[bold green]🛠️  DeskDetox Sensory Data Tools Diagnostic[/bold green]\n")

    # 1. Test Location Tool
    console.print("[cyan]1. Testing get_location()...[/cyan]")
    loc = get_location()
    loc_table = Table(title="Detected Geolocation (IP-based)", show_header=True)
    loc_table.add_column("Property", style="bold yellow")
    loc_table.add_column("Value", style="white")
    for k, v in loc.items():
        loc_table.add_row(k, str(v))
    console.print(loc_table)
    console.print()

    lat = loc.get("latitude", 40.7850)
    lon = loc.get("longitude", -73.9682)

    # 2. Test Weather Tool
    console.print(f"[cyan]2. Testing get_weather({lat}, {lon})...[/cyan]")
    weather = get_weather(lat, lon)
    weather_table = Table(title="Open-Meteo Current Weather", show_header=True)
    weather_table.add_column("Metric", style="bold yellow")
    weather_table.add_column("Reading", style="white")
    for k, v in weather.items():
        weather_table.add_row(k, str(v))
    console.print(weather_table)
    console.print()

    # 3. Test Overpass Nature Tool
    console.print(f"[cyan]3. Testing get_nearby_nature({lat}, {lon}, radius=1500)...[/cyan]")
    nature = get_nearby_nature(lat, lon, radius=1500)
    spaces = nature.get("green_spaces", [])
    nature_table = Table(title=f"Nearby Green Spaces ({len(spaces)} found)", show_header=True)
    nature_table.add_column("Name", style="bold green")
    nature_table.add_column("Type", style="white")
    for s in spaces:
        nature_table.add_row(s.get("name", "Unknown"), s.get("type", "Green Space"))
    if not spaces and nature.get("note"):
        nature_table.add_row("Notice", nature.get("note", ""))
    console.print(nature_table)
    console.print()

    console.print(
        Panel(
            "[bold green]✅ All 3 Open Data Tools executed successfully![/bold green]\n"
            "The Antigravity Agent can use these tools to craft localized, weather-aware missions.",
            border_style="green",
        )
    )


def parse_args() -> argparse.Namespace:
    """Parse command line flags."""
    parser = argparse.ArgumentParser(
        description="DeskDetox - AI-powered Outdoor Micro-Adventure Guide for Remote Workers",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-m",
        "--minutes",
        type=str,
        default=None,
        help="Minutes available for break (e.g. 15). If omitted, runs in interactive mode.",
    )
    parser.add_argument(
        "--test-tools",
        action="store_true",
        help="Run live verification of open data sensory tools (Location, Weather, OpenStreetMap).",
    )
    return parser.parse_args()


async def main_async(args: argparse.Namespace) -> None:
    """Asynchronous entrypoint."""
    if args.test_tools:
        run_diagnostics()
        return

    if args.minutes:
        print_banner()
        if not check_api_key_or_warn():
            sys.exit(1)
        clean_minutes = "".join(filter(str.isdigit, args.minutes)) or "15"
        await run_mission_flow(clean_minutes)
    else:
        await interactive_loop()


def main() -> None:
    """Application entrypoint."""
    args = parse_args()
    try:
        asyncio.run(main_async(args))
    except KeyboardInterrupt:
        print("\nExiting DeskDetox. Enjoy the outdoors!")
        sys.exit(0)


if __name__ == "__main__":
    main()
