import win32com.client

def connect_telescope():
    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True
    return telescope

def read_telescope_data(telescope):
    attributes = [
        "RightAscension", "Declination", "Altitude", "Azimuth", "Tracking", "SiderealTime",
        "CanSlew", "CanSetTracking", "CanPark", "CanSync", "CanSetGuideRates", "SiteLongitude", "UTCDate"
    ]

    print("Telescope Data:")
    for attr in attributes:
        try:
            value = getattr(telescope, attr)
            print(f"{attr}: {value}")
        except Exception as e:
            print(f"{attr}: Not supported ({e})")

def disconnect_telescope(telescope):
    telescope.Connected = False

if __name__ == "__main__":
    telescope = connect_telescope()
    read_telescope_data(telescope)
    disconnect_telescope(telescope)