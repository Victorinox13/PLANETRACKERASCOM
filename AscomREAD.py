import win32com.client

#This program is used to see what capabilities the telescope has.
TelescopeDriver = "ASCOM.SynScanMobile.Telescope"

def connect_telescope():
    telescope = win32com.client.Dispatch(TelescopeDriver)
    telescope.Connected = True
    return telescope

def read_telescope_data(telescope):
    attributes = [
        # Common properties
        
        "RightAscension","CanSlewAltAzAsync", "Declination", "Altitude", "Azimuth", "Tracking", "SiderealTime",
        "CanSlew", "CanSetTracking", "CanPark", "CanSync", "CanSetGuideRates", "SiteLongitude", "UTCDate",
        # Additional properties
        "SiteLatitude", "SiteElevation", "RightAscensionRate", "DeclinationRate", "TrackingRate", 
        "GuideRateRightAscension", "GuideRateDeclination", "CanSetRightAscensionRate", "CanSetDeclinationRate",
        "CanSetTrackingRates", "CanMoveAxis", "FocalLength", "ApertureDiameter", "ApertureArea",
        "DoesRefraction", "EquatorialSystem", "InterfaceVersion", "Name", "Description"
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