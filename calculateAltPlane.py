import requests
import math
import win32com.client
import ScndSpeedDemo as Ss

# Your location
OBSERVER_LAT = 51.28  # Your latitude
OBSERVER_LON = 4.58   # Your longitude
OBSERVER_ALT = 20     # Your elevation in meters (above sea level)


def fetch_aircraft_data():
    """Fetch aircraft data from OpenSky API."""
    params = {
        'lamin': 51.00,
        'lamax': 51.278831,
        'lomin': 4.00,
        'lomax': 4.70
    }
    response = requests.get('https://opensky-network.org/api/states/all', params=params)

    if response.status_code == 200:
        data = response.json()
        aircraft_list = []

        if "states" in data:
            for aircraft in data["states"]:
                # Extract aircraft data
                callsign = aircraft[1]
                air_lat = aircraft[6]
                air_lon = aircraft[5]
                air_alt = aircraft[7]  # Altitude in meters

                # Skip if no position or altitude data is available
                if air_lat is None or air_lon is None or air_alt is None:
                    continue

                # Calculate the elevation angle
                observer_lat_rad = math.radians(OBSERVER_LAT)
                observer_lon_rad = math.radians(OBSERVER_LON)
                air_lat_rad = math.radians(air_lat)
                air_lon_rad = math.radians(air_lon)

                # Earth's radius in meters
                EARTH_RADIUS = 6371000

                # Calculate the ground distance (great-circle distance)
                delta_lat = air_lat_rad - observer_lat_rad
                delta_lon = air_lon_rad - observer_lon_rad

                a = math.sin(delta_lat / 2)**2 + math.cos(observer_lat_rad) * math.cos(air_lat_rad) * math.sin(delta_lon / 2)**2
                c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
                ground_distance = EARTH_RADIUS * c  # Ground distance in meters

                # Calculate the slant range (hypotenuse)
                slant_range = math.sqrt(ground_distance**2 + (air_alt - OBSERVER_ALT)**2)

                # Calculate the elevation angle
                elevation_angle = math.degrees(math.asin((air_alt - OBSERVER_ALT) / slant_range))

                # Calculate the azimuth angle
                x = math.sin(delta_lon) * math.cos(air_lat_rad)
                y = math.cos(observer_lat_rad) * math.sin(air_lat_rad) - math.sin(observer_lat_rad) * math.cos(air_lat_rad) * math.cos(delta_lon)
                azimuth = math.degrees(math.atan2(x, y))
                if azimuth < 0:
                    azimuth += 360  # Normalize to 0–360 degrees

                # Add to the aircraft list
                aircraft_list.append({
                    "callsign": callsign,
                    "latitude": air_lat,
                    "longitude": air_lon,
                    "altitude": air_alt,
                    "elevation_angle": elevation_angle,
                    "azimuth": azimuth
                })
        return sorted(aircraft_list, key=lambda x: x["elevation_angle"], reverse=True)
    else:
        print(f"Error fetching data: {response.status_code}")
        return []


def track_aircraft(telescope, aircraft):
    """Track a specific aircraft."""
    print(f"Tracking Aircraft: {aircraft['callsign']}")
    print(f"  Latitude: {aircraft['latitude']}")
    print(f"  Longitude: {aircraft['longitude']}")
    print(f"  Altitude: {aircraft['altitude']} m")
    print(f"  Elevation Angle: {aircraft['elevation_angle']:.2f}°")
    print(f"  Azimuth: {aircraft['azimuth']:.2f}°")

    Ss.SlewToAzAlt(aircraft['elevation_angle'], aircraft['azimuth'], telescope, True)


def main():
    """Main program loop."""
    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True

    while True:
        aircraft_list = fetch_aircraft_data()

        if not aircraft_list:
            print("No available aircraft. Press 'r' to retry or 'Enter' to exit.")
            user_input = input("Your choice: ").strip().lower()
            if user_input == "r" or user_input == "":
                continue
            else:
                print("Exiting...")
                break

        if len(aircraft_list) == 1:
            print("Only one aircraft available. Automatically tracking it...")
            track_aircraft(telescope, aircraft_list[0])
        else:
            print("Available Aircraft:")
            for i, aircraft in enumerate(aircraft_list):
                print(f"{i + 1}. {aircraft['callsign']} - Elevation: {aircraft['elevation_angle']:.2f}°, Azimuth: {aircraft['azimuth']:.2f}°")

            choice = int(input("\nEnter the number of the aircraft to track: ")) - 1
            if 0 <= choice < len(aircraft_list):
                track_aircraft(telescope, aircraft_list[choice])
            else:
                print("Invalid selection.")

        print("Tracking complete. Press 'r' to retry or 'Enter' to exit.")
        user_input = input("Your choice: ").strip().lower()
        if user_input == "r" or user_input == "":
            continue
        else:
            print("Exiting...")
            break


if __name__ == "__main__":
    main()
11