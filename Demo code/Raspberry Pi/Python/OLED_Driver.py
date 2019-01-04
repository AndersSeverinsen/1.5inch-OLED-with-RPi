 # -*- coding:UTF-8 -*-
 ##
 # | file       :   OLED_Driver.py
 # | version	:   V1.0
 # | date       :   2017-12-07
 # | function   :   On the ST7735S chip driver and clear screen, drawing lines, drawing, writing 
 #                  and other functions to achieve
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

import DEV_Config
import RPi.GPIO as GPIO

#Define the full screen height length of the display
OLED_X_MAXPIXEL = 128  #OLED width maximum memory 
OLED_Y_MAXPIXEL = 128  #OLED height maximum memory
OLED_X	= 0
OLED_Y	= 0

OLED_WIDTH  = (OLED_X_MAXPIXEL - 2 * OLED_X)  #OLED width
OLED_HEIGHT =  OLED_Y_MAXPIXEL                #OLED height

#buffer
BUFSIZ = OLED_WIDTH / 2 * OLED_HEIGHT
Buffer = [0 for i in range(BUFSIZ)]

#scanning method
L2R_U2D = 1
L2R_D2U = 2
R2L_U2D = 3
R2L_D2U = 4
U2D_L2R = 5
U2D_R2L = 6
D2U_L2R = 7
D2U_R2L = 8
SCAN_DIR_DFT = L2R_U2D

##***********************************************************************************************************************
#------------------------------------------------------------------------
#|\\\																#/|
#|\\\						Drive layer								#/|
#|\\\																#/|
#------------------------------------------------------------------------
#************************************************************************************************************************
class OLED:
	def __init__(self):
		self.OLED_Dis_Column = OLED_WIDTH
		self.OLED_Dis_Page = OLED_HEIGHT
		self.OLED_Scan_Dir = SCAN_DIR_DFT
		self.OLED_X_Adjust = OLED_X
		self.OLED_Y_Adjust = OLED_Y

	"""    Hardware reset     """
	def  OLED_Reset(self):
		GPIO.output(DEV_Config.OLED_RST_PIN, GPIO.HIGH)
		DEV_Config.Driver_Delay_ms(100)
		GPIO.output(DEV_Config.OLED_RST_PIN, GPIO.LOW)
		DEV_Config.Driver_Delay_ms(100)
		GPIO.output(DEV_Config.OLED_RST_PIN, GPIO.HIGH)
		DEV_Config.Driver_Delay_ms(100)

	"""    Write register address and data     """
	def  OLED_WriteReg(self, Reg):
		if DEV_Config.USE_SPI_4W == 1:
			GPIO.output(DEV_Config.OLED_DC_PIN, GPIO.LOW)
			GPIO.output(DEV_Config.OLED_CS_PIN, GPIO.LOW)
			DEV_Config.SPI4W_Write_Byte([Reg])
			GPIO.output(DEV_Config.OLED_CS_PIN, GPIO.HIGH)
		else :
			DEV_Config.I2C_Write_Byte(Reg, DEV_Config.I2C_CMD)

	def OLED_WriteData(self, Data):
		if DEV_Config.USE_SPI_4W == 1:
			GPIO.output(DEV_Config.OLED_DC_PIN, GPIO.HIGH)
			GPIO.output(DEV_Config.OLED_CS_PIN, GPIO.LOW)
			DEV_Config.SPI4W_Write_Byte([Data])
			GPIO.output(DEV_Config.OLED_CS_PIN, GPIO.HIGH)
		else :
			DEV_Config.I2C_Write_Byte(Data,DEV_Config.I2C_RAM)
		
	"""    Common register initialization    """
	def OLED_InitReg(self):
		self.OLED_WriteReg(0xae)     #--turn off oled panel

		self.OLED_WriteReg(0x15)     #  set column address
		self.OLED_WriteReg(0x00)     #  start column   0
		self.OLED_WriteReg(0x7f)     #  end column   127

		self.OLED_WriteReg(0x75)     #   set row address
		self.OLED_WriteReg(0x00)     #  start row   0
		self.OLED_WriteReg(0x7f)     #  end row   127

		self.OLED_WriteReg(0x81)     # set contrast control
		self.OLED_WriteReg(0x80) 

		self.OLED_WriteReg(0xa0)     # gment remap
		self.OLED_WriteReg(0x51)     #51

		self.OLED_WriteReg(0xa1)     # start line
		self.OLED_WriteReg(0x00) 

		self.OLED_WriteReg(0xa2)     # display offset
		self.OLED_WriteReg(0x00) 

		self.OLED_WriteReg(0xa4)     # rmal display
		self.OLED_WriteReg(0xa8)     # set multiplex ratio
		self.OLED_WriteReg(0x7f) 

		self.OLED_WriteReg(0xb1)     # set phase leghth
		self.OLED_WriteReg(0xf1) 

		self.OLED_WriteReg(0xb3)     # set dclk
		self.OLED_WriteReg(0x00)     #80Hz:0xc1 90Hz:0xe1   100Hz:0x00   110Hz:0x30 120Hz:0x50   130Hz:0x70     01
 
		self.OLED_WriteReg(0xab)     #
		self.OLED_WriteReg(0x01)     #

		self.OLED_WriteReg(0xb6)     # set phase leghth
		self.OLED_WriteReg(0x0f) 

		self.OLED_WriteReg(0xbe) 
		self.OLED_WriteReg(0x0f) 

		self.OLED_WriteReg(0xbc) 
		self.OLED_WriteReg(0x08) 

		self.OLED_WriteReg(0xd5) 
		self.OLED_WriteReg(0x62) 

		self.OLED_WriteReg(0xfd) 
		self.OLED_WriteReg(0x12) 

	#********************************************************************************
	#function:	Set the display scan and color transfer modes
	#parameter: 
	#		Scan_dir   :   Scan direction
	#		Colorchose :   RGB or GBR color format
	#********************************************************************************
	def OLED_SetGramScanWay(self, Scan_dir):
		#Get the screen scan direction
		self.OLED_Scan_Dir = Scan_dir
		#Get GRAM and OLED width and height
		if(Scan_dir == L2R_U2D):
			self.OLED_WriteReg(0xa0)    #gment remap
			self.OLED_WriteReg(0x51)    #51	
		elif(Scan_dir == L2R_D2U):#Y
			self.OLED_WriteReg(0xa0)    #gment remap
			self.OLED_WriteReg(0x41)    #51
		elif(Scan_dir == R2L_U2D):
			self.OLED_WriteReg(0xa0)    #gment remap
			self.OLED_WriteReg(0x52)    #51
		elif(Scan_dir == R2L_D2U):
			self.OLED_WriteReg(0xa0)    #gment remap
			self.OLED_WriteReg(0x42)    #51
		else:
			print 'Scan_dir set error'
			return -1
		
		#Get GRAM and OLED width and height
		if(Scan_dir == L2R_U2D or Scan_dir == L2R_D2U or Scan_dir == R2L_U2D or Scan_dir == R2L_D2U):
			self.OLED_Dis_Column = OLED_WIDTH
			self.OLED_Dis_Page = OLED_HEIGHT
			self.OLED_X_Adjust = OLED_X
			self.OLED_Y_Adjust = OLED_Y
		else:
			self.OLED_Dis_Column = OLED_HEIGHT
			self.OLED_Dis_Page = OLED_WIDTH
			self.OLED_X_Adjust = OLED_Y
			self.OLED_Y_Adjust = OLED_X

	#/********************************************************************************
	#function:	
	#			initialization
	#********************************************************************************/
	def OLED_Init(self, OLED_ScanDir):		
		if (DEV_Config.GPIO_Init() != 0):
			return -1
			
		#Hardware reset
		self.OLED_Reset()
		
		#Set the initialization register
		self.OLED_InitReg()
		
		#Set the display scan and color transfer modes	
		self.OLED_SetGramScanWay(OLED_ScanDir )
		DEV_Config.Driver_Delay_ms(200)
		
		#Turn on the OLED display
		self.OLED_WriteReg(0xAF)
		DEV_Config.Driver_Delay_ms(120)

	#/********************************************************************************
	#function:	Sets the start position and size of the display area
	#parameter: 
	#	Xstart 	:   X direction Start coordinates
	#	Ystart  :   Y direction Start coordinates
	#	Xend    :   X direction end coordinates
	#	Yend    :   Y direction end coordinates
	#********************************************************************************/
	def OLED_SetWindows(self, Xstart, Ystart, Xend, Yend):
		if((Xstart > self.OLED_Dis_Column) or (Ystart > self.OLED_Dis_Page) or
		(Xend > self.OLED_Dis_Column) or (Yend > self.OLED_Dis_Page)):
			return
		self.OLED_WriteReg(0x15)
		self.OLED_WriteReg(Xstart)
		self.OLED_WriteReg(Xend - 1)

		self.OLED_WriteReg(0x75)
		self.OLED_WriteReg(Ystart)
		self.OLED_WriteReg(Yend - 1)
	
	#/********************************************************************************
	#function:	Set the display point (Xpoint, Ypoint)
	#parameter: 
	#		xStart :   X direction Start coordinates
	#		xEnd   :   X direction end coordinates
	#********************************************************************************/
	def OLED_SetCursor (self, Xpoint, Ypoint):
		if((Xpoint > self.OLED_Dis_Column) or (Ypoint > self.OLED_Dis_Page)):
			return
		self.OLED_WriteReg(0x15)
		self.OLED_WriteReg(Xpoint)
		self.OLED_WriteReg(Xpoint)

		self.OLED_WriteReg(0x75)
		self.OLED_WriteReg(Ypoint)
		self.OLED_WriteReg(Ypoint)
		
	'''
	#/********************************************************************************
	#function:	Set show color
	#parameter: 
	#		Color  :   Set show color
	#********************************************************************************/
	def OLED_SetColor(self, Color, Xpoint, Ypoint):
		if(Xpoint > self.OLED_Dis_Column or Ypoint > self.OLED_Dis_Page):
			return
			
		OLED_SetWindow(0, 0, self.OLED_Dis_Column, self.OLED_Dis_Page)
		#1 byte control two points
		if(Xpoint % 2 == 0):
			Buffer[Xpoint / 2 + Ypoint * 64] = (Color << 4) | Buffer[Xpoint / 2 + Ypoint * 64]
		else:
			Buffer[Xpoint / 2 + Ypoint * 64] = (Color & 0x0f) | Buffer[Xpoint / 2 + Ypoint * 64]
	
	def OLED_Display(self):
		
		#write data
		NUM = 0
		for page in range(0, self.OLED_Dis_Page):
			for Column in range(0, self.OLED_Dis_Column / 2):
				self.OLED_WriteData([Buffer[NUM]])
				NUM = NUM + 1
	'''
	

	#/********************************************************************************
	#function:	
	#			Clear screen 
	#********************************************************************************/
	def OLED_Clear(self):
		for i in range(0, self.OLED_Dis_Page):
			for m in range(0, self.OLED_Dis_Column / 2):				
				self.OLED_WriteData(0X00)				
	
	def OLED_ShowImage(self, Image, Xstart, Ystart):
		if (Image == None):
			return
		#self.OLED_Clear(0x00)
		self.OLED_SetWindows ( Xstart, Ystart, self.OLED_Dis_Column , self.OLED_Dis_Page)
		Pixels = Image.load()
		for j in range(0, self.OLED_Dis_Page ):
			for i in range(0, self.OLED_Dis_Column / 2 ):
				#print '0 = ',Pixels[2 * i, j] & 0x0f
				#print '1 = ',Pixels[2 * i + 1, j]
				Pixels_Color = ((Pixels[2 * i, j] & 0x0f) << 4) | ((Pixels[2 * i + 1, j] & 0x0f) )
				#print 'Pixels_Color',Pixels_Color
				self.OLED_WriteData(Pixels_Color)
				'''			
				Pixels_Color1 = (Pixels[2 * i, j][0]  + Pixels[2 * i, j][1]  + Pixels[2 * i, j][2])/3#RGB Data
				Pixels_Color2 = (Pixels[2 * i + 1, j][0]  + Pixels[2 * i + 1, j][1]  + Pixels[2 * i + 1, j][2] )/3#RGB Data
				Pixels_Color8b24b1 = Pixels_Color1 * 15 /255
				Pixels_Color8b24b2 = Pixels_Color2 * 15 /255 
				Pixels_Color = Pixels_Color8b24b1 | (Pixels_Color8b24b2 << 4)
				print 'Pixels_Color[1, j]',Pixels_Color
				self.OLED_WriteData(Pixels_Color)
				#self.OLED_SetColor(Pixels_Color , 1, 1)
				'''