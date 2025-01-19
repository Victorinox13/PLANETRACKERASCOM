import win32com.client
import time
import tkinter as tk
from datetime import datetime, timezone

from astropy.coordinates import AltAz, EarthLocation
from astropy.time import Time
 
import SideFunctions.eqMath as eq
import SideFunctions.UserSettings as UsS
import SideFunctions.drawNightSky as ns

# BASIS INSTELLINGEN
target_ra = 0.00
target_dec = 0.00
hasClicked = False

# Configurable Alt-Az ranges
MIN_ALT = 10  # Minimum altitude
MAX_ALT = 60  # Maximum altitude
MIN_AZ = 150  # Minimum azimuth
MAX_AZ = 225  # Maximum azimuth

# Function to generate visible objects


def update_visible_objects():
    location = EarthLocation(UsS.LONGITUDE, UsS.LATITUDE, UsS.ELEVATION)
    time = Time(datetime.now(timezone.utc))

    visible_objects = ns.get_visible_objects(location, time, MIN_ALT, MAX_ALT, MIN_AZ, MAX_AZ)
    ns.draw_objects_on_canvas(visible_objects, canvas, MIN_AZ, MAX_AZ, MIN_ALT, MAX_ALT)
    root.after(1000, update_visible_objects)  # Refresh every 5 seconds

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
            x = int((current_az - MIN_AZ) / (MAX_AZ - MIN_AZ) * width)
            y = int(height - (current_alt - MIN_ALT) / (MAX_ALT - MIN_ALT) * height)
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
        x = int((current_az - MIN_AZ) / (MAX_AZ - MIN_AZ) * width)
        y = int(height - (current_alt - MIN_ALT) / (MAX_ALT - MIN_ALT) * height)
        canvas.coords(telescope_circle, x - 5, y - 5, x + 5, y + 5)
        telescope_position_text.set(f"Telescope Position -> Alt: {current_alt:.2f}, Az: {current_az:.2f}")

    # Schedule the next update
    root.after(100, update_telescope_position)

# Function to handle mouse clicks in the window
def on_click(event):
    global target_ra, target_dec
    global hasClicked
    hasClicked = True
    # Calculate Alt-Az from window coordinates
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    # Map x-coordinate to azimuth
    azimuth = MIN_AZ + (event.x / width) * (MAX_AZ - MIN_AZ)

    # Map y-coordinate to altitude
    altitude = MAX_ALT - (event.y / height) * (MAX_ALT - MIN_ALT)

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

    root = tk.Tk()
    root.title("Telescope Control")
    #root.attributes('-fullscreen', True)  # Enable full-screen mode
    root.geometry("1000x500")
    



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
    print("start map")
    # Start updating the visible objects
    update_visible_objects()
    print("map started")
    # Start updating the telescope position
    root.after(100, update_telescope_position)
    telescope.TrackingRate = 3  # Set to "Custom"
    telescope.SetCustomRate(0,5, 0)

    # Run the GUI event loop
    root.mainloop()

    # Disconnect the telescope when the program ends
    telescope.Connected = False