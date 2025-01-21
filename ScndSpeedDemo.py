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

    telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)
    
    if telAz > az:
        
        print('slewing LEFT.')
        ra, dec = eq.convert_alt_az_to_ra_dec(alt, az - 10)
        time.sleep(1)    
        telescope.SlewToCoordinates(ra, dec)
        while (az - (telAz-1)) < -1:
            
            telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)
            #print(f"Still have to do: {round(az - telAz)}, Current Az: {telAz}, Target Az: {telAz}, {(az - (telAz-1.5))}")    
        print('Abort slewing.')
        telescope.AbortSlew()
    else:
        print('slewing RIGHT.')
        ra, dec = eq.convert_alt_az_to_ra_dec(alt, az + 10)
        time.sleep(1)    
        telescope.SlewToCoordinates(ra, dec)
        while (az - (telAz+1)) > 1:
            telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)
            #print(f"still have to do: {round(az - telAz)}, Az: {telAz}, Az: {telAz + 2}, {(az - (telAz+2))}")

        print('abort')
        telescope.AbortSlew()  

      
          

   







if __name__ == "__main__":

    telescope = win32com.client.Dispatch("ASCOM.BRESSER.Telescope")
    telescope.Connected = True

    telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)
    time.sleep(2)
    telAlt, telAz = eq.convert_ra_dec_to_alt_az(telescope.RightAscension, telescope.Declination)
    
    if telAz >= 210: #THIS IS FOR TESTING
     SlewToAzAltOneSpeed(45, 200, telescope)
    if telAz < 210: #THIS IS FOR TESTING
     SlewToAzAltOneSpeed(45, 220, telescope)
   
    
        
