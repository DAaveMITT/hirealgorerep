import json

# Load your JSON data
with open('consolidated_output.json', 'r') as f:
    vehicles = json.load(f)

# Function to consolidate features by group title
def consolidate_features(vehicle):
    # Extract core vehicle details
    consolidated_vehicle = {
        "Stock": vehicle.get("Stock"),
        "Year": vehicle.get("Year"),
        "Make": vehicle.get("Make"),
        "Length": vehicle.get("Length"),
        "Engine": vehicle.get("Engine"),
        "Capacity": vehicle.get("Capacity"),
        "CoPilotSeat": vehicle.get("Co-Pilot Seat"),
        "RearStorageWithWall": vehicle.get("RearStorageWithWall"),
        "RearStorageNoWall": vehicle.get("RearStorageNoWall"),
        "LuggageRack": vehicle.get("LuggageRack"),
        "Economy": vehicle.get("Economy"),
        "RemovableRearRow": vehicle.get("RemovableRearRow"),
        "RearRampWithKneelingSystem": vehicle.get("RearRampWithKneelingSystem"),
        "WheelChairStation": vehicle.get("WheelChairStation"),
        "Mileage": vehicle.get("Mileage"),
        "Status": vehicle.get("Status"),
        "Category": vehicle.get("Category"),
    }

    # Consolidate features by group title
    group_features = {}
    
    for feature in vehicle.get('Features', []):
        group_title = feature.get('GroupTitle')
        feature_value = feature.get('Feature')
        
        if group_title in group_features:
            group_features[group_title].append(feature_value)
        else:
            group_features[group_title] = [feature_value]
    
    # Flatten the consolidated features
    for idx, (group_title, features) in enumerate(group_features.items(), start=1):
        consolidated_vehicle[f'group_title_{idx}'] = group_title
        consolidated_vehicle[f'features_{idx}'] = features
    
    return consolidated_vehicle

# Consolidate the features for each vehicle
consolidated_vehicles = [consolidate_features(vehicle) for vehicle in vehicles]

# Save the updated JSON
with open('consolidated_vehicles.json', 'w') as f:
    json.dump(consolidated_vehicles, f, indent=4)

print("Consolidated data has been saved to 'consolidated_vehicles.json'")
