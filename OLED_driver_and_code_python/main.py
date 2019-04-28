 # -*- coding:UTF-8 -*-
 ##
 # | file       :   main.py
 # | version    :   V1.0
 # | date       :   2017-12-08
 # | function   :   1.5inch OLED 
 #					
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
import OLED_Driver

import Image
import ImageDraw
import ImageFont
import ImageColor

#try:
def main():
	OLED = OLED_Driver.OLED()
	
	print "**********Init OLED**********"
	OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
	OLED.OLED_Init(OLED_ScanDir)
	
	#OLED.OLED_Clear()
	DEV_Config.Driver_Delay_ms(2000)
	image = Image.new("L", (OLED.OLED_Dis_Column, OLED.OLED_Dis_Page), 0)# grayscale (luminance)
	draw = ImageDraw.Draw(image)
	#font = ImageFont.truetype('/usr/share/fonts/truetype/freefont/FreeMonoBold.ttf', "White")
	
	print "***draw line"
	draw.line([(0,0),(127,0)], fill = "White",width = 1)
	draw.line([(127,0),(127,60)], fill = "White",width = 1)
	draw.line([(127,60),(0,60)], fill = "White",width = 1)
	draw.line([(0,60),(0,0)], fill = "White",width = 1)
	print "***draw rectangle"
	draw.rectangle([(18,10),(110,20)],fill = "White")
	
	print "***draw text"
	draw.text((33, 22), 'WaveShare ', fill = "White")
	draw.text((32, 36), 'Electronic ', fill = "White")
	draw.text((28, 48), '1.44inch OLED ', fill = "White")
		
	OLED.OLED_ShowImage(image,0,0)
	DEV_Config.Driver_Delay_ms(500)

	image = Image.open('flower.bmp')#this pis is small ,Will trigger an exception,but you can show
	OLED.OLED_ShowImage(image,0,70)
	#while (True):
	
if __name__ == '__main__':
    main()

#except:
#	print("except")
#	GPIO.cleanup()