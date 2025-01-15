import time
from datetime import datetime, timezone
from astropy.coordinates import AltAz, EarthLocation, SkyCoord
from astropy.time import Time





# WISKUNDIGE FORMULE DIE AZ -> RA doet
def convert_alt_az_to_ra_dec(alt, az, latitude, longitude, elevation):
    location = EarthLocation(lat=latitude, lon=longitude, height=elevation)
    now = Time(datetime.now(timezone.utc))
    altaz_frame = AltAz(obstime=now, location=location)
    altaz = SkyCoord(alt=alt, az=az, frame=altaz_frame, unit="deg")
    radec = altaz.transform_to("icrs")
    return radec.ra.hour, radec.dec.degree

# EN OMGEKEERD
def convert_ra_dec_to_alt_az(ra, dec, latitude, longitude, elevation):
    location = EarthLocation(lat=latitude, lon=longitude, height=elevation)
    now = Time(datetime.now(timezone.utc))
    radec = SkyCoord(ra=ra, dec=dec, unit=("hourangle", "deg"), frame="icrs")
    altaz = radec.transform_to(AltAz(obstime=now, location=location))
    return altaz.alt.degree, altaz.az.degree