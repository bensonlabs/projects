##### Made by Google Antigravy with Gemini 3.5 Flash (medium)
# GRAVITAS: Stellar Sandbox & Gravity Simulator

An interactive, high-fidelity N-body gravity simulator built for the browser. Featuring real-time orbital projection, procedural ambient audio synthesis, a glassmorphic dashboard, and live telemetry tracking.

---

## Key Features

*   **Symplectic Euler Physics Engine**: Real-time gravitation calculation with numerical softening to ensure simulation stability even during close-body flybys.
*   **Euler Trajectory Forecasts**: Calculates and draws projected orbital paths in real-time, showing where planets will go before you launch them.
*   **Procedural Web Audio Synthesizer**: Generates ambient space drones using low-pass filters and LFOs, and synthesizes dynamic chimes, sweep sounds, and explosions on cosmic events (collisions, merges, and singularities).
*   **Interactive Spawner Lab**: Launch custom-mass asteroids, planets, stars, pulsars, or black holes.
*   **Two Launch Modes**:
    *   **Custom Vector**: Slingshot launch bodies with drag-and-shoot vector control.
    *   **Auto-Orbit**: Automatically calculates stable Keplerian velocities around the nearest heavy body for instant stable orbits.
*   **Dynamic Collision Behaviors**: Accretion (merging), elastic bounces, or absolute stellar disintegration into glowing space dust.
*   **Telemetry Dashboard**: Track live physical properties including Active Bodies, Total Mass, FPS, and Cosmic Age.
*   **Cosmic Energy Conservation Graph**: A secondary canvas plots Kinetic (Ek), Potential (Ep), and Total Energy (Et) to visualize laws of thermodynamics in action.

---

## Controls

*   **Left Click & Drag (Custom Vector Mode)**: Draw slingshot vector guidelines to shoot objects.
*   **Left Click (Auto-Orbit Mode)**: Drop bodies directly into stable circular orbits.
*   **Right Click & Drag**: Pan the viewport camera.
*   **Scroll Wheel**: Zoom in/out (centered directly on your mouse cursor).

On narrow screens, use **Controls** or **Telemetry** below the site header to open a sidebar. Tap the same button again to close it and return to the simulation, or press **Escape**. Only one drawer opens at a time; its contents scroll independently. On tablet widths, Controls stays visible and Telemetry uses a drawer.

---

## Cosmos Presets

1.  **Solar System**: A stable solar system configuration with a sun, orbiting planets, and a co-orbiting moon.
2.  **Binary Stars**: Two equal-mass stars co-orbiting their barycenter with planets negotiating chaotic figure-8 orbits.
3.  **Black Hole**: A supermassive black hole with gravitational lensing devouring a swirling accretion disk of 75 asteroids.
4.  **Three-Body Chaos**: An unstable, chaotic dance of three stars demonstrating N-body unpredictability.
5.  **Stellar Collision**: A high-speed merger of two heavy objects colliding to form a black hole and debris shower.

---

## Installation & Running Locally

The simulator uses vanilla JavaScript modules. `index.html` is a Jekyll page (`layout: project`, with its head in the front matter). On bensonlabs.org the blog renders it with the site header, from the release this repo (bensonlabs/projects) publishes; the blog's own build only uses pinned releases, so it can't show a change you haven't released.

Preview it with this repo's pack, as its README describes under "Working on it":

1.  From the repository root, with Python 3: `python3 tools/pack.py` (on Windows, `py tools/pack.py`).
2.  Serve the pack: `python3 -m http.server -d dist`.
3.  Open `http://localhost:8000/projects/gravitas/` in your web browser.

A static server doesn't process Jekyll: the front matter ends up in the page as plain text, and there's no site header. The page as visitors see it appears only on bensonlabs.org, once the release is pinned.

---

## Tech Stack

*   **Core**: HTML5, JavaScript (ES6 Modules)
*   **Visuals**: Canvas API, CSS3 Glassmorphism
*   **Audio**: Web Audio API (procedural synthesis)
*   **Icons**: FontAwesome CDN

