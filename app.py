import os
import sys
import subprocess
import time

def main():
    


    
    os.chdir("./frontend")
    subprocess.Popen(["python", "front.py"])
    
    
    os.chdir("../backend/databaseedge")
    subprocess.Popen(["python", "data.py"])
    
    os.chdir("../forecastdeeplearningLSTM")
    subprocess.Popen(["python", "forecast.py"])
  
    os.chdir("../databasecloud")
    subprocess.Popen(["python", "datacloud.py"])
    

if __name__ == "__main__":
   main()
   time.sleep(10)
   
   
   