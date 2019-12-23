##
 #  @filename   :   DEV_Config.py
 #  @brief      :   OLED hardware interface implements (GPIO, SPI)
 #  @author     :   Yehui from Waveshare
 #
 #  Copyright (C) Waveshare     July 10 2017
 #
 # Permission is hereby granted, free of charge, to any person obtaining a copy
 # of this software and associated documnetation files (the "Software"), to deal
 # in the Software without restriction, including without limitation the rights
 # to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 # copies of the Software, and to permit persons to  whom the Software is
 # furished to do so, subject to the following conditions:
 #
 # The above copyright notice and this permission notice shall be included in
 # all copies or substantial portions of the Software.
 #
 # THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 # IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 # FITNESS OR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 # AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 # LIABILITY WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 # OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
 # THE SOFTWARE.
 #
 
import spidev #SPI
import smbus  #I2C	

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)	
OLED_RST_PIN = 25
OLED_DC_PIN  = 24
OLED_CS_PIN  = 8
GPIO.setup(OLED_RST_PIN, GPIO.OUT)
GPIO.setup(OLED_DC_PIN, GPIO.OUT)
GPIO.setup(OLED_CS_PIN, GPIO.OUT)

USE_SPI_4W = 0
USE_I2C = 1
if USE_SPI_4W == 1:#Initialize SPI	
	SPI = spidev.SpiDev(0, 0)
	SPI.max_speed_hz = 9000000
	SPI.mode = 0b00
elif USE_I2C == 1:#Initialize I2C
	GPIO.output(OLED_DC_PIN, GPIO.HIGH)
	I2C = smbus.SMBus(1)
	I2C_CMD = 0X00
	I2C_RAM = 0X40
	address = 0x3d

def GPIO_Init():
	GPIO.setwarnings(False)
	GPIO.setup(OLED_RST_PIN, GPIO.OUT)
	GPIO.setup(OLED_DC_PIN, GPIO.OUT)
	GPIO.setup(OLED_CS_PIN, GPIO.OUT)
	return 0

def SPI4W_Write_Byte(data):
	SPI.writebytes(data)

def I2C_Write_Byte(data, Cmd):
	I2C.write_byte_data(address, Cmd, data)
	#I2C.write_byte(address,data)

def Driver_Delay_ms(xms):
	time.sleep(xms / 1000.0)

### END OF FILE ###
