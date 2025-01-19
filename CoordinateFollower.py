LATITUDE =  51.28
LONGITUDE =  4.58
ELEVATION = 20

import win32com.client
import time
from datetime import datetime, timezone
import SideFunctions.eqMath as eq



target_alt = 45.0 
target_az = 200.0



if __name__ == "__main__":

    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True

    print(f"Input Alt: {target_alt}, Az: {target_az}")

    # Convert Alt-Az to RA/Dec
    target_ra, target_dec = eq.convert_alt_az_to_ra_dec(
        target_alt, target_az, LATITUDE, LONGITUDE, ELEVATION
    )
    print(f"Converted RA: {target_ra} hours, Dec: {target_dec} degrees")

    # Slew to the converted RA/Dec coordinates
    telescope.SlewToCoordinates(target_ra, target_dec) 
    print("slewing...")
   
    telescope.AbortSlew()
    print("Slewing aborted.")
    
