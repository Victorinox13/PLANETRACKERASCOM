from astropy.coordinates import AltAz, EarthLocation, get_sun, get_body, SkyCoord
from astropy.time import Time
from astropy.coordinates.name_resolve import NameResolveError

from datetime import datetime, timezone


def get_visible_objects(location, time, alt_min, alt_max, az_min, az_max):
    objects = []
    try:
        # Sun
        sun = get_sun(time).transform_to(AltAz(obstime=time, location=location))
        if alt_min <= sun.alt.degree <= alt_max and az_min <= sun.az.degree <= az_max:
            objects.append(("Sun", sun.alt.degree, sun.az.degree))

        solarsys = ["mercury", "venus", "mars", "jupiter", "saturn", "uranus", "neptune", "moon"]
       
        for object_name in solarsys:
            try:
                body = get_body(object_name, time).transform_to(AltAz(obstime=time, location=location))
                if alt_min <= body.alt.degree <= alt_max and az_min <= body.az.degree <= az_max:
                    objects.append((object_name.capitalize(), body.alt.degree, body.az.degree))
            except Exception as e:
                print(f"Could not calculate {object_name}: {e}")
        
        stars = [
            "Sirius", "Canopus", "Arcturus", "Vega", "Capella", "Rigel", "Procyon", "Achernar",
            "Betelgeuse", "Hadar", "Altair", "Acrux", "Aldebaran", "Spica", "Antares", "Pollux",
            "Fomalhaut", "Deneb", "Mimosa", "Regulus"
        ]
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





def draw_objects_on_canvas(objects, canvas, MIN_AZ, MAX_AZ, MIN_ALT, MAX_ALT):
    canvas.delete("object")  # Clear previous objects
    width = canvas.winfo_width()
    height = canvas.winfo_height()

    for obj_name, alt, az in objects:
        x = int((az - MIN_AZ) / (MAX_AZ - MIN_AZ) * width)
        y = int(height - (alt - MIN_ALT) / (MAX_ALT - MIN_ALT) * height)
        canvas.create_oval(x - 2, y - 2, x + 2, y + 2, fill="white", tags="object")
        canvas.create_text(x + 10, y, text=obj_name, fill="white", font=("Arial", 8), tags="object")
