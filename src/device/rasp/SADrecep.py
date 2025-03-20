import serial
import time
import os
import subprocess

def simpleCheckSumRecep(array_cmd):
    
    cs = sum(int(byte) for byte in array_cmd[:-3])
        
    cs = cs & 0xFF
    
    return cs
    
def simpleCheckSum(array_cmd):
    
    cs = sum(int(byte) for byte in array_cmd)
        
    cs = cs & 0xFF
    
    return cs
    

ser = serial.Serial(port='/dev/serial0', baudrate=9600, timeout=1)
ser.reset_input_buffer()
os.system("pkill -f rasp-adxl")

ser.flushInput()

process_id = 0

time.sleep(2)
mensagem = [0x00,0x01,0x28,0x02,0x53,0x41,0x44,0x20,0x4F,0x4E]
mensagem.append(simpleCheckSum(mensagem))
ser.write(mensagem)
time.sleep(2)

#thread_adxl = threading.Thread(target=adxl_exe, daemon=True)

ser.flushOutput()

while True:
    
    if ser.in_waiting > 6:
        
        hex_cmd = []
        recive_cmd = ser.read(7)
        cs_calculate = simpleCheckSumRecep(recive_cmd)
        
        hex_cmd.extend(recive_cmd)
        print(hex_cmd)
        
        if recive_cmd[4] == cs_calculate:
             
        
            if hex_cmd[3] == 0x01:
                mensagem = [0x00,0x01,0x28,0x02]
                mensagem.append(simpleCheckSum(mensagem))
                ser.write(mensagem)
                ser.flushInput()
                time.sleep(2)
                ser.flushOutput()
                process_id = subprocess.Popen("sudo python3 /home/pi/Desktop/sac-dm/src/device/rasp/rasp-adxl.py", shell=True)
                
                
            
            elif hex_cmd[3] == 0x00:
                mensagem = [0x00,0x01,0x28,0x02]
                mensagem.append(simpleCheckSum(mensagem))
                ser.write(mensagem)
                ser.flushInput()
                time.sleep(2)
                ser.flushOutput()
                os.system(f"sudo kill -9 {process_id.pid+1}")
            
                
                
            elif hex_cmd[3] == 0x04:
                mensagem = [0x00,0x01,0x28,0x02,0x65,0x78,0x69,0x74]
                mensagem.append(simpleCheckSum(mensagem))
                ser.write(mensagem)
                ser.flushInput()
                time.sleep(2)
                ser.flushOutput()
                os.system("pkill -f python")
                break
            
            else:
                mensagem = [0x00,0x01,0x28,0x03]
                mensagem.append(simpleCheckSum(mensagem))
                ser.write(mensagem)
                ser.flushInput()
                time.sleep(2)
                ser.flushOutput()
                
                
        else:
            mensagem = [0x00,0x01,0x28,0x05]
            mensagem.append(simpleCheckSum(mensagem))
            ser.write(mensagem)
            ser.flushInput()
            time.sleep(1)
            ser.flushOutput()

