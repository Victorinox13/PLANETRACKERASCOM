import win32com.client
import time
from datetime import datetime, timezone
import SideFunctions.eqMath as eq
import SideFunctions.UserSettings as UsS

target_alt = 45.0 
target_az = 200.0

def CheckEQmaths(alt, az):
    ra, dec = eq.convert_alt_az_to_ra_dec(alt, az)
    print(f"Inp Alt: {alt}, Az: {az}")
    print(f"Conv RA: {ra} Dec: {dec}")

    print('sleeping for 5')
    time.sleep(5)

    alt, az = eq.convert_ra_dec_to_alt_az(ra, dec)
    print(f"Check Test Comppare Values:")
    print(f"Inp Alt: {alt}, Az: {az}")
    print(f"Conv RA: {ra} Dec: {dec}")
    
def SlewToAzAlt(alt, az, telescope, stop):

    ra, dec = eq.convert_alt_az_to_ra_dec(alt, az)
    telescope.SlewToCoordinates(ra, dec)
    if stop:
        while (abs(telescope.RightAscension - ra) > 0.01 and abs(telescope.Declination - dec) > 0.01):
            time.sleep(1)
        telescope.AbortSlew()

def SlewToAzAltOneSpeed(alt, az, telescope):
    #250 en
    telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)

    if telAz < az:  ra, dec = eq.convert_alt_az_to_ra_dec(alt, az + 10)
    else : ra, dec = eq.convert_alt_az_to_ra_dec(alt, az - 10)
    telescope.SlewToCoordinates(ra, dec)
    # 200 - 210 = -10 
    #240 -  2
    while (round(az - telAz) != 0 and round(az - telAz) != 1 and round(az - telAz) != -1):
            telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)
            print(f"Inp Alt: {telAlt}, Az: {telAz}")
            print(round(az - telAz))
            time.sleep(1)

    print('abort')
    telescope.AbortSlew()







if __name__ == "__main__":

    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True
    
    SlewToAzAltOneSpeed(45, 200, telescope)
    #SlewToAzAlt(45, 200, telescope, True)
    
        
