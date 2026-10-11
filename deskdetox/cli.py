"""Command Line Interface for DeskDetox.

Provides a rich, interactive terminal experience that prompts remote workers
for their break time, invokes the Antigravity Agent, and streams actionable
outdoor micro-adventures to break free from screens.
"""

import sys
import asyncio
from typing import Optional

# Ensure Windows terminal handles UTF-8 output for emojis and formatting
if sys.platform == "win32":
    try:
        if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
            sys.stdout.reconfigure(encoding="utf-8")
        if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
            sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.text import Text
from rich.rule import Rule
from rich.theme import Theme
from rich.status import Status

from deskdetox.agent import build_agent_config, get_api_key

# Custom color palette for nature-inspired CLI
custom_theme = Theme({
    "info": "dim cyan",
    "warning": "yellow",
    "danger": "bold red",
    "nature": "bold green",
    "mission": "bold bright_green",
    "accent": "bold magenta",
})

console = Console(theme=custom_theme, legacy_windows=False)


def print_banner() -> None:
    """Render the application banner and mission statement."""
    title = Text("🌿 DESKDETOX 🌿", style="bold green", justify="center")
    subtitle = Text(
        "Screen-Free Micro-Adventures • Touch Grass Hackathon\nPowered by Google Antigravity & Open Data",
        style="italic dim white",
        justify="center",
    )
    banner_content = Text.assemble(title, "\n", subtitle)
    console.print()
    console.print(
        Panel(
            banner_content,
            border_style="green",
            padding=(1, 2),
            subtitle="[bold dim]Step away from the screen[/bold dim]",
        )
    )
    console.print()


def check_api_key_or_warn() -> bool:
    """Verify that an API key is present; display instructions if missing."""
    api_key = get_api_key()
    if not api_key:
        console.print(
            Panel(
                "[bold yellow]⚠️ No Google Studio / Gemini API Key Detected![/bold yellow]\n\n"
                "To run the Antigravity Agent, please create a [bold].env[/bold] file with your key:\n"
                "  [cyan]GEMINI_API_KEY=your_gemini_api_key_here[/cyan]\n\n"
                "Get a free API key at: [bold link=https://aistudio.google.com/]https://aistudio.google.com/[/bold link]\n\n"
                "[dim]You can copy .env.example to .env and paste your key.[/dim]",
                title="[bold red]Configuration Required[/bold red]",
                border_style="yellow",
            )
        )
        return False
    return True


async def run_mission_flow(minutes: str) -> None:
    """Execute a single outdoor adventure generation session.

    Args:
        minutes: The duration of the break in minutes.
    """
    from google.antigravity import Agent

    # Prepare prompt
    user_prompt = (
        f"I have {minutes} minutes for a break right now. "
        "Find my location, local weather, and nearby green spaces, "
        "and give me my 2-sentence phone-free outdoor mission immediately."
    )

    config = build_agent_config()

    console.print(Rule(style="dim green"))
    console.print(f"[bold cyan]🔍 Planning a {minutes}-minute outdoor escape...[/bold cyan]")

    status = Status(
        "[bold green]Fetching local coordinates, checking sky conditions & discovering green spaces...[/bold green]",
        spinner="earth",
        console=console,
    )
    status.start()

    try:
        async with Agent(config) as agent:
            # Send prompt to the Antigravity agent
            response = await agent.chat(user_prompt)

            # Stop the status spinner once response stream begins
            status.stop()

            console.print()
            console.print("[bold green]🌲 YOUR OUTDOOR MISSION:[/bold green]")
            console.print(Rule(style="green"))

            # Native async streaming using Antigravity SDK
            collected_text = []
            async for token in response:
                console.print(token, end="", style="bold white")
                collected_text.append(token)
                # Flush stdout to ensure smooth live typing feel
                sys.stdout.flush()

            console.print()
            console.print(Rule(style="green"))

            # Encouraging footer
            mission_body = "".join(collected_text).strip()
            if not mission_body:
                # In case response object already resolved full text
                mission_body = getattr(response, "text", "") or "Step outside, breathe in the fresh air, and look up at the sky."
                console.print(f"[bold white]{mission_body}[/bold white]\n")

            console.print(
                Panel(
                    "[bold bright_green]📵 Leave your phone on the desk.[/bold bright_green]\n"
                    "[italic dim]Step outside, feel the breeze, and touch grass. See you back in "
                    f"{minutes} minutes![/italic dim]",
                    border_style="bright_green",
                    padding=(0, 2),
                )
            )
            console.print()

    except Exception as exc:
        status.stop()
        console.print(
            Panel(
                f"[bold red]Error running agent mission:[/bold red] {exc}\n\n"
                "[dim]Make sure your GEMINI_API_KEY is valid and network connectivity is active.[/dim]",
                border_style="red",
                title="Execution Notice",
            )
        )


async def interactive_loop() -> None:
    """Main interactive terminal loop for DeskDetox."""
    print_banner()

    if not check_api_key_or_warn():
        return

    while True:
        try:
            # Prompt the user for break duration
            minutes_input = Prompt.ask(
                "[bold green]🌿 How many minutes do you have for a break?[/bold green]",
                default="15",
            ).strip()

            if minutes_input.lower() in ("exit", "quit", "q"):
                console.print("\n[dim green]Stay grounded and take care! 👋[/dim green]\n")
                break

            # Validate input or default to 15
            clean_minutes = "".join(filter(str.isdigit, minutes_input))
            if not clean_minutes:
                clean_minutes = "15"

            await run_mission_flow(clean_minutes)

            # Ask if user wants another mission or to quit
            again = Prompt.ask(
                "[dim]Generate another mission or plan a different break? (y/n)[/dim]",
                choices=["y", "n"],
                default="n",
            )
            if again.lower() != "y":
                console.print("\n[bold green]Enjoy the outdoors! Shut your laptop and go. 🌲✨[/bold green]\n")
                break

        except (KeyboardInterrupt, EOFError):
            console.print("\n\n[bold green]Heading outside? Enjoy your break! 🍃[/bold green]\n")
            break
