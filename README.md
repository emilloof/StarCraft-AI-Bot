# StarCraft AI Bot 🎮🤖

This repository houses a custom StarCraft II Artificial Intelligence bot written in Python. 

**👥 Team Context:** This project was developed collaboratively by a 7-person team. While the `main` branch contains our combined final release, **my personal contributions to the project are isolated and showcased on the `micromanagent-emil` branch.**

## 🎯 My Contributions: The `micromanagent-emil` Branch
My role within the 7-person team focused heavily on **Micromanagement**—the intricate, moment-to-moment control of individual units during combat and navigation. If you are an employer or collaborator reviewing my work, please check out the `micromanagent-emil` branch to see my specific code. 

My work interacts heavily with the underlying systems to ensure units move efficiently, engage targets optimally, and survive longer in battles.

## ⚙️ Core Architecture & Features

The bot is built using a highly modular, task-driven architecture:

*   **Task Management System:** The AI distributes discrete tasks to units via a robust manager (`task_manager.py`). Tasks are compartmentalized into distinct scripts such as `attack.py`, `build.py`, `scout.py`, and `gather_minerals.py`.
*   **Advanced Pathfinding:** Implements custom navigation algorithms, including A* (`astar_temp.py`) and Dijkstra (`dijkstra.py`) to navigate the complex SC2 maps.
*   **Potential Flow Fields:** Utilizes a potential flow system (`modules/potential_flow/`) to smoothly guide units around obstacles and enemies, preventing clumping and improving swarm movement.
*   **Visual Debugger:** Includes a custom debugging suite (`visualdebugger/`) capable of rendering heat maps, flow vectors, and path overlays directly over the game map to analyze AI decision-making in real-time.
*   **Data-Driven Logic:** Relies on JSON-based data configurations for map regions, chokepoints, and tech trees (`regions.json`, `chokepoints.json`, `techtree.json`) to maintain strategic awareness.

## 🚀 Getting Started

### Prerequisites
*   Python 3.x
*   StarCraft II installed on your local machine.
*   Required Python packages (install via `requirements.txt`).

### Running the Bot
1. Clone the repository to your local machine.
2. Ensure you are on the correct branch to view specific features (e.g., `git checkout micromanagent-emil` to see my unit control logic).
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
