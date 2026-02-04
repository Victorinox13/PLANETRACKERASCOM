LATITUDE =  51.28
LONGITUDE =  4.58
ELEVATION = 20

import win32com.client
import time
import ScndSpeedDemo as Ss



if __name__ == "__main__":

    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True
    Ss.SlewToAzAlt(40, 220, telescope, True)
    
