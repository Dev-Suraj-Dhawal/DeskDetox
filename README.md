Markdown
# 🌿 DeskDetox: Outdoor Micro-Adventure Guide

> **Hackathon Challenge:** "Touch Grass" — Building AI that gets people off screens and outdoors.  
> **Powered by:** `google.antigravity` SDK • Google AI Studio (`gemini-1.5-flash`) • Open Data Ecosystem

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Google Antigravity SDK](https://img.shields.io/badge/Google-Antigravity%20SDK-4285F4.svg)](https://pypi.org/project/google-antigravity/)
[![Gemini 1.5 Flash](https://img.shields.io/badge/AI-Gemini%201.5%20Flash-orange.svg)](https://aistudio.google.com/)
[![Open-Meteo](https://img.shields.io/badge/Weather-Open--Meteo-brightgreen.svg)](https://open-meteo.com/)
[![OpenStreetMap](https://img.shields.io/badge/Map%20Data-OpenStreetMap%20Overpass-7EB35B.svg)](https://www.openstreetmap.org/)

---

## 🧭 Overview

Remote work has trapped millions in front of glowing rectangles. Even when we take a "break," we often pivot straight from Slack to doomscrolling Twitter, Reddit, or TikTok on our phones.

**DeskDetox** is an autonomous, localized AI assistant designed to break that cycle. Tell DeskDetox how many minutes you have (e.g., 5, 15, or 30 minutes), and the **Google Antigravity Agent** immediately senses your physical surroundings through open data APIs:
1. **Pins your approximate coordinates** without asking you to type them.
2. **Checks real-time weather & daylight** at your exact location.
3. **Discovers nearby green spaces, parks, trails, or bodies of water** via OpenStreetMap.

It then crafts a **highly specific, 2-sentence outdoor mission** tailored to your time window and the local elements—commanding you to leave your phone on the desk and go outside right now.

---

## 🏗️ Architecture & Tech Stack

```text
                     ┌─────────────────────────────────────────┐
                     │            User in Terminal             │
                     │  "🌿 How many minutes do you have?"     │
                     └────────────────────┬────────────────────┘
                                          │ Break Duration
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │         Google Antigravity Agent        │
                     │           (gemini-1.5-flash)            │
                     └───────┬────────────┬────────────┬───────┘
                             │            │            │
            ┌────────────────┘            │            └────────────────┐
            ▼                             ▼                             ▼
   ┌──────────────────┐          ┌──────────────────┐          ┌──────────────────┐
   │  get_location()  │          │  get_weather()   │          │get_nearby_nature │
   │                  │          │                  │          │                  │
   │  IP Geolocation  │          │  Open-Meteo API  │          │   OSM Overpass   │
   │ (geocoder/ip-api)│          │ Temp & Daylight  │          │ Parks & Trails   │
   └──────────────────┘          └──────────────────┘          └──────────────────┘
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │        Streaming Token Response         │
                     │          (async for token...)           │
                     └────────────────────┬────────────────────┘
                                          ▼
                     ┌─────────────────────────────────────────┐
                     │            Rich Terminal UI             │
                     │    🌲 Actionable Outdoor Mission        │
                     │    📵 Phone-Free Screen Detachment      │
                     └─────────────────────────────────────────┘
Framework: google.antigravity SDK (Agent, LocalAgentConfig).

AI Model: Google AI Studio API (gemini-1.5-flash).

Sensory Open Data Tools:

get_location(): Resolves local city, latitude, and longitude via IP (geocoder + ip-api.com fallback).

get_weather(lat, lon): Fetches real-time temperature, condition (WMO code), apparent temperature, wind speed, and daylight status from Open-Meteo.

get_nearby_nature(lat, lon, radius): Queries OpenStreetMap Overpass API for parks, nature reserves, gardens, viewpoints, and trails within walking distance.

Terminal UI: rich with custom theme, live spinners, bordered mission panels, and native asynchronous token streaming (async for token in response:).

📁 Repository Structure
Plaintext
DeskDetox/
├── deskdetox/
│   ├── __init__.py          # Package initialization
│   ├── agent.py             # Antigravity LocalAgentConfig & system instructions
│   ├── cli.py               # Rich UI, prompt loop, and async stream handler
│   └── tools.py             # Open data tools (Location, Weather, OpenStreetMap)
├── main.py                  # Application entry point with CLI argument flags
├── pyproject.toml           # Python package configuration
├── requirements.txt         # Project dependencies
├── .env.example             # Template for API keys
├── .env                     # Your local API key configuration
└── README.md                # Project documentation
🚀 Installation & Setup
1. Prerequisites
Python 3.10+ (Tested on Python 3.12).

A free Google AI Studio API key from aistudio.google.com.

2. Clone and Setup Environment
Bash
# Clone the repository
git clone [https://github.com/your-username/DeskDetox.git](https://github.com/your-username/DeskDetox.git)
cd DeskDetox

# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
# On macOS / Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
3. Configure API Key
Copy .env.example to .env and insert your Gemini API key:

Bash
cp .env.example .env
Edit .env:

Code snippet
GEMINI_API_KEY=your_actual_gemini_api_key_here
4. Install Globally (Optional)
Because this project is packaged with pyproject.toml, you can install it globally on your machine:

Bash
pip install -e .
Now you can run the app from anywhere in your terminal just by typing:

Bash
deskdetox
🏃 How to Run
Mode 1: Interactive Break Planner (Default)
Launch the interactive CLI:

Bash
deskdetox
Example Session:

Plaintext
🌿 DESKDETOX 🌿
Screen-Free Micro-Adventures • Touch Grass Hackathon
Powered by Google Antigravity & Open Data

🌿 How many minutes do you have for a break? [15]: 15
🔍 Planning a 15-minute outdoor escape...
⠋ Fetching local coordinates, checking sky conditions & discovering green spaces...

🌲 YOUR OUTDOOR MISSION:
────────────────────────────────────────────────────────────────────────
Walk two blocks north to Pushpa Lal Park and spend seven minutes doing a barefoot 
sensory stroll on the grass while taking ten deep breaths in the 21°C evening air. 
Turn your face toward the open sky to count three visible stars before walking back, 
leaving your phone resting safely on your desk.
────────────────────────────────────────────────────────────────────────

╭──────────────────────────────────────────────────────────────╮
│ 📵 Leave your phone on the desk.                             │
│ Step outside, feel the breeze, and touch grass. See you back │
│ in 15 minutes!                                               │
╰──────────────────────────────────────────────────────────────╯
Mode 2: Quick Command-Line Mission
Specify the minutes directly via the --minutes (-m) argument:

Bash
deskdetox --minutes 10
deskdetox -m 20
Mode 3: Sensory Open Data Diagnostic Test
You can verify that all 3 open data sensory tools (get_location(), get_weather(), and get_nearby_nature()) are working correctly on your machine without invoking the LLM:

Bash
deskdetox --test-tools
Diagnostic Output:

Plaintext
🛠️  DeskDetox Sensory Data Tools Diagnostic

1. Testing get_location()...
Detected Geolocation (IP-based) 
┏━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━┓
┃ Property  ┃ Value            ┃
┡━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━┩
│ city      │ Butwāl           │
│ latitude  │ 27.6912          │
│ longitude │ 83.4525          │
│ region    │ Lumbini Province │
│ country   │ NP               │
│ source    │ geocoder         │
└───────────┴──────────────────┘

2. Testing get_weather(27.6912, 83.4525)...
    Open-Meteo Current Weather     
┏━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━┓
┃ Metric          ┃ Reading       ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━┩
│ temperature_c   │ 20.8          │
│ temperature_f   │ 69.4          │
│ condition       │ Partly cloudy │
│ daylight_status │ Nighttime 🌙  │
│ status          │ success       │
└─────────────────┴───────────────┘

3. Testing get_nearby_nature(27.6912, 83.4525, radius=1500)...
  Nearby Green Spaces (2 found)   
┏━━━━━━━━━━━━━━━━━┳━━━━━━┓
┃ Name            ┃ Type ┃
┡━━━━━━━━━━━━━━━━━╇━━━━━━┩
│ Pushpa Lal Park │ Park │
│ Butwal Bus Park │ Park │
└─────────────────┴──────┘

✅ All 3 Open Data Tools executed successfully!
🛠️ The Antigravity Agent Configuration
DeskDetox leverages the google.antigravity framework. We dynamically calculate the walking radius based on the user's available time constraints:

Python
from google.antigravity import Agent, LocalAgentConfig
from deskdetox.tools import get_location, get_weather, get_nearby_nature

SYSTEM_INSTRUCTIONS = (
    "You are an outdoor micro-adventure guide. Your goal is to get the user away from all screens. "
    "Use your tools to find their location, weather, and nearby green spaces. Based on how much time they have, "
    "generate a highly specific, actionable 2-sentence mission for them to go outside RIGHT NOW. "
    "The mission must be phone-free. Do not output fluff, just the mission."
)

config = LocalAgentConfig(
    system_instructions=SYSTEM_INSTRUCTIONS,
    tools=[get_location, get_weather, get_nearby_nature],
    model="gemini-1.5-flash",
    api_key="...",
)

minutes = 15
user_prompt = (
    f"I have exactly {minutes} minutes for a break right now. "
    f"This means I can only walk {int(minutes)/2} minutes away before turning back. "
    "Check the current weather. Find the nearest green space within this specific walking radius. "
    "Give me a highly specific, 2-sentence phone-free outdoor mission."
)

async with Agent(config) as agent:
    response = await agent.chat(user_prompt)
    async for token in response:
        print(token, end="")
🌍 Hackathon Impact: "Touch Grass"
Zero Friction: Remote workers don't have to look up their weather, search Google Maps for parks, or think about what to do outside. The agent does the physical sensing in seconds.

Strictly Screen-Free: Unlike traditional productivity apps that keep users checking checklists on a mobile app, DeskDetox emphasizes leaving all devices at the desk.

Open Data First: Relies exclusively on free, open public APIs (OpenStreetMap & Open-Meteo), requiring zero commercial mapping credentials or paid subscription tiers.

📜 License
MIT License. Built for the Touch Grass Hackathon with Google Antigravity & Google AI Studio.