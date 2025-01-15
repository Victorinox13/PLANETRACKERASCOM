from astropy.coordinates import AltAz, EarthLocation, get_sun, get_body, SkyCoord
from astropy.time import Time
from astropy.coordinates.name_resolve import NameResolveError


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