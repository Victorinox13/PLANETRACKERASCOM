import time

def move_telescope_constant_speed_azimuth(telescope, start_az, end_az, altitude, speed, step_size, convert_altaz_to_radec):
    """
    Move the telescope in azimuth at a constant speed.

    Args:
        telescope: The ASCOM telescope object.
        start_az (float): Starting azimuth in degrees.
        end_az (float): Ending azimuth in degrees.
        altitude (float): Fixed altitude in degrees.
        speed (float): Desired azimuth speed in degrees per second.
        step_size (float): Step size for azimuth increments in degrees.
        convert_altaz_to_radec (function): Function that converts Alt/Az to RA/Dec.
    """
    try:
        if not telescope.Tracking:
            telescope.Tracking = True  # Enable tracking if it's off

        current_az = start_az
        while current_az <= end_az:
            # Convert the current Alt/Az to RA/Dec
            ra, dec = convert_altaz_to_radec(altitude, current_az)
            telescope.SlewToCoordinates(ra, dec)
            print(f"Slewing to RA: {ra:.6f}, Dec: {dec:.6f} (Alt: {altitude}, Az: {current_az})")

            # Wait to achieve the desired speed
            time.sleep(step_size / speed )

            # Increment azimuth
            current_az += step_size

        print(f"Final Position -> Azimuth: {end_az}, Altitude: {altitude}")
    
    except Exception as e:
        print(f"Error during telescope movement: {e}")


# Example conversion function (replace with your implementation)
def convert_altaz_to_radec(altitude, azimuth):
    """
    Dummy function for converting Alt/Az to RA/Dec.
    Replace this with your actual implementation.
    """
    from datetime import datetime
    from astropy.coordinates import AltAz, EarthLocation, SkyCoord
    from astropy.time import Time
    import astropy.units as u

    # Replace these with your telescope's actual location
    observer_location = EarthLocation(lat=51.46666717529297 * u.deg, lon=4.6196491 * u.deg, height=1800 * u.m)
    observing_time = Time(datetime.utcnow())

    altaz = AltAz(alt=altitude * u.deg, az=azimuth * u.deg, location=observer_location, obstime=observing_time)
    radec = SkyCoord(altaz).transform_to("icrs")
    return radec.ra.hour, radec.dec.degree


# Example usage
if __name__ == "__main__":
    import win32com.client

    # Connect to the telescope
    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True

    starting_ra, starting_dec = convert_altaz_to_radec(45, 200)
    telescope.SlewToCoordinates(starting_ra, starting_dec)
    if (abs(telescope.RightAscension - starting_ra) > 0.01 and abs(telescope.Declination - starting_dec) > 0.01):
        time.sleep(1)
    
    # Move from Azimuth 200 to 300 degrees at a constant speed of 2 degrees/second
    move_telescope_constant_speed_azimuth(
        telescope,
        start_az=200,
        end_az=240,
        altitude=45,
        speed=0.5,  # 2 degrees/second
        step_size=1,  # 0.5-degree increments
        convert_altaz_to_radec=convert_altaz_to_radec
    )

    # Disconnect the telescope
    telescope.Connected = False
