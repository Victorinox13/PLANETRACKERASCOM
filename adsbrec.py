import socket
import time

# Dump1090 TCP settings
HOST = "localhost"  # Adjust if dump1090 is on another machine
PORT = 30003        # Default SBS-1/BaseStation port

# Store current aircraft data
flights = {}  # Key: hex ID, Value: flight identifier
last_seen = {}  # Key: hex ID, Value: last update time
detected_hexes = set()  # Track all hex IDs seen

def parse_sbs1(message):
    """Parse an SBS-1 message and return hex ID and flight identifier if available."""
    fields = message.split(",")
    if len(fields) < 5 or fields[0] != "MSG":
        return None

    msg_type = fields[1]
    hex_id = fields[3].strip()
    flight = fields[4].strip()

    # Add hex ID to detected set
    if hex_id:
        detected_hexes.add(hex_id)

    # Extract flight identifier from MSG,1
    if msg_type == "1" and hex_id and flight:
        return {"hex": hex_id, "flight": flight}
    return {"hex": hex_id}  # Return hex ID only

def print_flight_list():
    """Print the current list of detected flights and hex IDs."""
    print("\nDetected Hex IDs:")
    print("----------------")
    for hex_id in sorted(detected_hexes):
        print(hex_id)
    print("----------------")

    if not flights:
        print("No flight identifiers detected")
    else:
        print("\nFlight List:")
        print("-----------")
        for flight in sorted(flights.values()):
            print(flight)
        print("-----------")

def main():
    # TCP socket setup
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))

    buffer = ""
    try:
        while True:
            # Read data from socket
            data = sock.recv(1024).decode("utf-8", errors="ignore")
            if not data:
                continue

            # Append to buffer and process line by line
            buffer += data
            lines = buffer.split("\n")
            buffer = lines[-1]  # Keep incomplete line in buffer
            current_time = time.time()

            # Print raw messages
            for line in lines[:-1]:
                print(f"Raw message: {line.strip()}")

                # Parse the message
                parsed = parse_sbs1(line.strip())
                if parsed:
                    hex_id = parsed["hex"]
                    flight = parsed.get("flight")

                    # Add or update the flight if available
                    if flight:
                        flights[hex_id] = flight
                        last_seen[hex_id] = current_time
                        print(f"Detected flight: {flight} (Hex: {hex_id})")
                    else:
                        # Only update last seen time if no flight identifier
                        last_seen[hex_id] = current_time

            # Remove aircraft not detected anymore (timeout after 30 seconds)
            timeout = 30  # seconds
            to_remove = [hex_id for hex_id, last_time in last_seen.items()
                         if current_time - last_time > timeout]
            for hex_id in to_remove:
                removed_flight = flights.pop(hex_id, None)
                last_seen.pop(hex_id, None)
                detected_hexes.discard(hex_id)
                if removed_flight:
                    print(f"Removed flight: {removed_flight} (Hex: {hex_id}) - No updates for {timeout} seconds")
                else:
                    print(f"Removed hex ID: {hex_id} - No updates for {timeout} seconds")

            # Print the current flight list and hex IDs
            print_flight_list()

            # Delay for 0.5 seconds
            time.sleep(0.5)

    except KeyboardInterrupt:
        print("Stopped by user")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()

if __name__ == "__main__":
    main()