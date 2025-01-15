import win32com.client
import time
import tkinter as tk
from datetime import datetime, timezone
from astropy.coordinates import AltAz, EarthLocation, get_sun, get_body, SkyCoord
from astropy.time import Time
from astropy.coordinates.name_resolve import NameResolveError
import SideFunctions.eqMath as eq
import SideFunctions.UserSettings as UsS

# BASIS INSTELLINGEN
target_ra = 0.00
target_dec = 0.00
hasClicked = False

# Function to generate visible objects
def get_visible_objects(location, time, alt_min, alt_max, az_min, az_max):
    objects = []
    try:
        # Sun
        sun = get_sun(time).transform_to(AltAz(obstime=time, location=location))
        if alt_min <= sun.alt.degree <= alt_max and az_min <= sun.az.degree <= az_max:
            objects.append(("Sun", sun.alt.degree, sun.az.degree))

        solarsys = ["moon", "jupiter", "saturn", "venus", "mars"]
        for object_name in solarsys:
            try:
                body = get_body(object_name, time).transform_to(AltAz(obstime=time, location=location))
                if alt_min <= body.alt.degree <= alt_max and az_min <= body.az.degree <= az_max:
                    objects.append((object_name.capitalize(), body.alt.degree, body.az.degree))
            except Exception as e:
                print(f"Could not calculate {object_name}: {e}")
        
        stars = ["Sirius", "Canopus", "Arcturus", "Vega", "Rigel"]
        for star_name in stars:
            try:
                star = SkyCoord.from_name(star_name).transform_to(AltAz(obstime=time, location=location))
                if alt_min <= star.alt.degree <= alt_max and az_min <= star.az.degree <= az_max:
                    objects.append((star_name, star.alt.degree, star.az.degree))
            except NameResolveError:
                pass  # Skip stars that cannot be resolved
    except Exception as e:
        print(f"Error calculating visible objects: {e}")

    return objects

# Function to draw stars and planets on the canvas
def draw_objects_on_canvas(objects):
    canvas.delete("object")  # Clear previous objects
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    for obj_name, alt, az in objects:
        x = int((az - 130) / (200 - 130) * width)
        y = int(height - (alt - 10) / (80 - 10) * height)
        canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white", tags="object")
        canvas.create_text(x + 10, y, text=obj_name, fill="white", font=("Arial", 8), tags="object")

# Update visible objects dynamically
def update_visible_objects():
    location = EarthLocation(lat=UsS.LATITUDE, lon=UsS.LONGITUDE, height=UsS.ELEVATION)
    time = Time(datetime.now(timezone.utc))
    visible_objects = get_visible_objects(location, time, 10, 80, 130, 200)
    draw_objects_on_canvas(visible_objects)
    root.after(5000, update_visible_objects)  # Refresh every 5 seconds

# Update the telescope position on the canvas
def update_telescope_position():
    if telescope.Connected:
        # Check if slewing or target position is not reached
        global target_ra 
        global target_dec 
        global hasClicked

        if (abs(telescope.RightAscension - target_ra) > 0.01 and abs(telescope.Declination - target_dec) > 0.01 and hasClicked == True):
            # Get the current RA/Dec
            current_ra = telescope.RightAscension
            current_dec = telescope.Declination
            current_alt, current_az = eq.convert_ra_dec_to_alt_az(current_ra, current_dec, UsS.LATITUDE, UsS.LONGITUDE, UsS.ELEVATION)

            # Map Alt-Az to canvas coordinates
            width = canvas.winfo_width()
            height = canvas.winfo_height()
            x = int((current_az - 130) / (200 - 130) * width)
            y = int(height - (current_alt - 10) / (80 - 10) * height)
            canvas.coords(telescope_circle, x - 5, y - 5, x + 5, y + 5)
            telescope_position_text.set(f"Telescope Position -> Alt: {current_alt:.2f}, Az: {current_az:.2f}")
        elif hasClicked == True:
            telescope.AbortSlew()
            print("Telescope aborted")
            hasClicked = False

        current_ra = telescope.RightAscension
        current_dec = telescope.Declination
        current_alt, current_az = eq.convert_ra_dec_to_alt_az(current_ra, current_dec, UsS.LATITUDE, UsS.LONGITUDE, UsS.ELEVATION)

        # Map Alt-Az to canvas coordinates
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        x = int((current_az - 130) / (200 - 130) * width)
        y = int(height - (current_alt - 10) / (80 - 10) * height)
        canvas.coords(telescope_circle, x - 5, y - 5, x + 5, y + 5)
        telescope_position_text.set(f"Telescope Position -> Alt: {current_alt:.2f}, Az: {current_az:.2f}")

    # Schedule the next update
    root.after(10, update_telescope_position)

# Function to handle mouse clicks in the window
def on_click(event):
    global target_ra, target_dec
    global hasClicked
    hasClicked = True
    # Calculate Alt-Az from window coordinates
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # Map x-coordinate to azimuth (130 to 200 degrees)
    azimuth = 130 + (event.x / width) * (200 - 130)

    # Map y-coordinate to altitude (10 to 60 degrees, inverted)
    altitude = 80 - (event.y / height) * (80 - 10)

    # Display clicked coordinates
    clicked_position_text.set(f"Clicked Position -> Alt: {altitude:.2f}, Az: {azimuth:.2f}")
    print(f"Clicked Alt: {altitude:.2f}, Az: {azimuth:.2f}")
    target_ra, target_dec = eq.convert_alt_az_to_ra_dec(altitude, azimuth, UsS.LATITUDE, UsS.LONGITUDE, UsS.ELEVATION)
    print(f"Converted RA: {target_ra} hours, Dec: {target_dec} degrees")

    # Slew the telescope
    telescope.SlewToCoordinates(target_ra, target_dec)
    print("Telescope slewing to target.")

if __name__ == "__main__":
    # Connect to the telescope
    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True

    # Create the GUI window
    root = tk.Tk()
    root.title("Telescope Control")
    root.geometry("600x400")  # Set window size

    # Create the canvas for visualization
    canvas = tk.Canvas(root, bg="black")
    canvas.pack(fill=tk.BOTH, expand=True)

    # Create the circle for the telescope's position
    telescope_circle = canvas.create_oval(0, 0, 10, 10, fill="red")

    # Create labels for clicked and telescope positions
    clicked_position_text = tk.StringVar()
    telescope_position_text = tk.StringVar()
    clicked_label = tk.Label(root, textvariable=clicked_position_text, fg="white", bg="black", anchor="w")
    clicked_label.pack(fill=tk.X)
    telescope_label = tk.Label(root, textvariable=telescope_position_text, fg="white", bg="black", anchor="w")
    telescope_label.pack(fill=tk.X)

    # Bind mouse clicks to the window
    canvas.bind("<Button-1>", on_click)

    # Start updating the visible objects
    update_visible_objects()

    # Start updating the telescope position
    root.after(100, update_telescope_position)

    # Run the GUI event loop
    root.mainloop()

    # Disconnect the telescope when the program ends
    telescope.Connected = False
