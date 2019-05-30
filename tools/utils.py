from geopy.distance import geodesic


def calculate_distance(sender, receiver):
    distance = geodesic(sender, receiver).km
    return distance


def calculate_price(distance, weight):
    weight = int(weight)
    premium = 2 * (weight - 5)
    if distance <= 2 and weight <= 5:
        return 10
    if distance <= 2 and weight > 5:
        return 10 + 2 * (weight - 5)
    if 2 < distance <= 4 and weight <= 5:
        return 10 + (distance - 2)
    if 2 < distance <= 4 and weight > 5:
        return 10 + (distance - 2) + premium
    if 4 < distance <= 10 and weight <= 5:
        return 10 + 2 * (distance - 2)
    if 4 < distance <= 10 and weight > 5:
        return 10 + 2 * (distance - 2) + premium
    if 10 < distance <= 16 and weight <= 5:
        return 10 + 5 * (distance - 2)/3
    if 10 < distance <= 16 and weight > 5:
        return 10 + 5 * (distance - 2)/3 + premium
    if distance > 16 and weight <= 5:
        return 10 + 6 * (distance - 2)/3
    if distance > 16 and weight > 5:
        return 10 + 6 * (distance - 2)/3 + premium
