from flask import Flask, render_template, request, jsonify
import math
from itertools import permutations

app = Flask(__name__)

# This is a standard Haversine formula snippet I found on Stack Overflow for distance calculation between zones and the safety zone
def haversine_distance(a, b):
    """
    Calculate great-circle distance between two points on Earth (in kilometers)
    a and b are dicts with 'lat' and 'lng' in decimal degrees.
    """
    R = 6371.0  
    lat1 = math.radians(a['lat'])
    lon1 = math.radians(a['lng'])
    lat2 = math.radians(b['lat'])
    lon2 = math.radians(b['lng'])

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    sin_dlat = math.sin(dlat / 2.0)
    sin_dlon = math.sin(dlon / 2.0)
    aa = sin_dlat**2 + math.cos(lat1) * math.cos(lat2) * sin_dlon**2
    c = 2 * math.atan2(math.sqrt(aa), math.sqrt(1 - aa))
    return R * c  



def div_zones_by_sev(zones):
    high = []
    low = []
    for z in zones:
        if z.get('severity', 0) >= 5:
            high.append(z)
        else:
            low.append(z)
    return high, low



def backtracking_select(zones, capacity):
    n = len(zones)
    if n == 0:
        return [], 0

    best = {'people': 0, 'subset': []}
    chosen = []

    def dfs(idx, curr_people):
        if idx == n:
            if curr_people > best['people']:
                best['people'] = curr_people
                best['subset'] = chosen.copy()
            return

        remaining = sum(z['population'] for z in zones[idx:])
        if curr_people + remaining <= best['people']:
            return

        dfs(idx + 1, curr_people)

        zone = zones[idx]
        if curr_people + zone['population'] <= capacity:
            chosen.append(zone)
            dfs(idx + 1, curr_people + zone['population'])
            chosen.pop()

    dfs(0, 0)
    return best['subset'], best['people']






def opt_order(selected_zones, safe_zone):
    k = len(selected_zones)
    if k == 0:
        return [], 0.0, []

    best_dist = float('inf')
    best_perm = None
    best_legs = None

    for perm in permutations(selected_zones):
        total = 0.0
        legs = []
        cum = 0.0

        for i in range(len(perm)):
            if i == 0:
                legs.append({
                    'from': None,
                    'to': perm[i],
                    'distance_km': 0.0,
                    'cumulative_km': 0.0
                })
            else:
                d = haversine_distance(perm[i - 1], perm[i])
                total += d
                cum += d
                legs.append({
                    'from': perm[i - 1],
                    'to': perm[i],
                    'distance_km': round(d, 3),
                    'cumulative_km': round(cum, 3)
                })

        last = perm[-1]
        final_leg = haversine_distance(last, safe_zone)
        total += final_leg
        cum += final_leg
        legs.append({
            'from': last,
            'to': {'lat': safe_zone['lat'], 'lng': safe_zone['lng'], 'name': 'Safe Zone'},
            'distance_km': round(final_leg, 3),
            'cumulative_km': round(cum, 3)
        })

        if total < best_dist:
            best_dist = total
            best_perm = perm
            best_legs = legs

    ordered = [{
        'lat': z['lat'],
        'lng': z['lng'],
        'population': z['population'],
        'severity': z['severity']
    } for z in best_perm]

    return ordered, round(best_dist, 3), best_legs








@app.route('/')
def home():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.get_json()

    zones = data.get('zones', [])
    capacity = int(data.get('vehicle_capacity', 0))
    safe_zone = data.get('safe_zone', None)

    if not zones or not safe_zone or capacity <= 0:
        return jsonify({"error": "Invalid input. Prov zones, safe_zone and capacity."}), 400

    zones_sorted = sorted(zones, key=lambda z: z.get('population', 0), reverse=True)
    high_group, low_group = div_zones_by_sev(zones_sorted)

    selected_high, people_high = backtracking_select(high_group, capacity)
    selected_low, people_low = backtracking_select(low_group, capacity - people_high)
    selected = selected_high + selected_low

    if not selected:
        return jsonify({
            'total_people': 0,
            'total_distance_km': 0.0,
            'estimated_time_min': 0.0,
            'final_route': [],
            'legs': [],
            'safe_zone': safe_zone
        })

    ordered_route, total_distance_km, legs = opt_order(selected, safe_zone)

# Here we have taken avg speed as 25kmph
    estimated_time_min = (total_distance_km / 25) * 60

    result = {
        'total_people': sum(z['population'] for z in selected),
        'total_distance_km': total_distance_km,
        'estimated_time_min': round(estimated_time_min, 1),
        'final_route': ordered_route,
        'legs': legs,
        'safe_zone': {'lat': safe_zone['lat'], 'lng': safe_zone['lng']}
    }

    return jsonify(result)



if __name__ == '__main__':
    app.run(debug=True)
