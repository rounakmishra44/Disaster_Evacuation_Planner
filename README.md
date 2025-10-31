# Disaster_Evacuation_Planner


This project demonstrates how **Divide & Conquer** and **Backtracking** algorithms can be applied to real-world scenarios — specifically, to plan optimal evacuation routes during a disaster situation.  
It combines **Flask (Python)** for backend logic and **Leaflet.js** for an interactive frontend map.

---

## Overview

The system simulates a disaster evacuation scenario where multiple affected zones must be evacuated to a safe zone.  
Each zone has:
- A population count
- A severity level (1–10)

A vehicle with limited capacity must evacuate as many people as possible while minimizing total travel distance.

---

## Key Features

1. **Interactive Map Interface**
   - Users can click on the map to add disaster zones.
   - Each zone can have its own population and severity level.
   - A safe zone can be set by clicking the “Set Safe Zone” button.

2. **Vehicle Capacity Input**
   - The user specifies how many people the evacuation vehicle can carry.

3. **Algorithmic Optimization**
   - **Divide & Conquer**: Splits zones into high and low severity groups.
   - **Backtracking**: Selects the subset of zones that maximizes total people evacuated under capacity constraints.
   - **Permutation (Brute Force)**: Finds the shortest route (minimum total distance) among selected zones and the safe zone.

4. **Results Display**
   - Total people evacuated
   - Total distance covered (in kilometers)
   - Ordered route with stepwise distances

5. **Visualization**
   - The best evacuation route is drawn on the map using Leaflet.js.

---

## Technologies Used

### Backend
- **Python 3**
- **Flask Framework**

### Frontend
- **HTML5**



