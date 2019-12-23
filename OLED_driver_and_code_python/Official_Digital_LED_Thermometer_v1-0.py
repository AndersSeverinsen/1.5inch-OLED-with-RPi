##### Code By Anders Severinsen
##### 2019-2020
##### License: Creative Commons - Attribution - Non-Commercial - Share Alike
print("Loading... The setup might take a few seconds")

import DEV_Config, OLED_Driver
import Image, ImageDraw, ImageFont, ImageColor

import json, requests, os, time
import RPi.GPIO as GPIO
from neopixel import *

#Font type:
temp_fontfamily = 'steelfish_bd.ttf'
city_fontfamily = 'Cocogoose-Pro-Semilight-trial.ttf'
weather_fontfamily = 'BebasNeue-Regular.ttf'

# Buttons
button_next = 23 # Pin 23
button_prev = 24 # Pin 24
button_shutdown = 25 # Pin 25
GPIO.setmode(GPIO.BCM)
GPIO.setup(button_next,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_prev,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setup(button_shutdown,GPIO.IN,pull_up_down=GPIO.PUD_UP)
GPIO.setwarnings(False)

# LDR
ldr_pin = 4              # GPIO pin connected to LDR

# LED Strip config
LED_COUNT      = 21      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 10      # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 155     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL    = 0       # Set to '1' for GPIOs 13, 19, 41, 45 or 53

strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip.begin()

# LED display config
spacing = 2              # Temperature spacing between leds 
cold_color_spacing = 2   # Amount of light blue leds
hot_color_spacing = 4    # Amount of orange leds
min_temp = -14           # The minimum temperature to be displayed. NOTE: Has to be an even number!
max_temp = min_temp + LED_COUNT * spacing   # Calculated value of the max temp that can be displayed, based on the minimum temp and $
#print("Max temp = " + str(max_temp))
led_before_show = False

##### Weather-api config
key = 'API_KEY'  # Change to your api key
units = 'metric'  #units = 'imperial'
city_ids = ['6455259', '2643743', '5128638', '6542285', '292223']
city_names = ['Paris', 'London', 'New York', 'Firenze', 'Dubai']
city_temp = []

# Other
update_displays = True
count_max = 30
count = count_max
weather_check = 180      # Amount of time before new weather reading
check = weather_check
c = 0
t = 0
ldr_list = [0,50,90,160,600]
LED_BRIGHTNESS_list = [150,130,120,90,60]

# Motion
ldr = 0
motion = False


# Getting the weather data from openweathermap.org
def get_temp():
    n = 0
    global city_temp
    city_temp = []
    for i in city_ids:
        url = requests.get('http://api.openweathermap.org/data/2.5/weather?id='+i+'&units='+units+'&APPID='+key)
        weather = json.loads(url.text)
        temp = weather['main']['temp']
        city_temp.append(temp)
        print("{0} = {1}".format(city_names[n], temp))
        n +=1
    print('---------')

degree_sign = u'\N{DEGREE SIGN}'

OLED = OLED_Driver.OLED()
OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
OLED.OLED_Init(OLED_ScanDir)
OLED.OLED_Clear()
DEV_Config.Driver_Delay_ms(2000)
image = Image.new("L", (OLED.OLED_Dis_Column, OLED.OLED_Dis_Page), 0) # grayscale (luminance)
draw = ImageDraw.Draw(image)

def display_update(c, city_temp, font_city, font_temp):
    OLED = OLED_Driver.OLED()
    OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
    OLED.OLED_Init(OLED_ScanDir)
    OLED.OLED_Clear()
    DEV_Config.Driver_Delay_ms(2000)
    image = Image.new("L", (OLED.OLED_Dis_Column, OLED.OLED_Dis_Page), 0) # grayscale (luminance)
    draw = ImageDraw.Draw(image)

    draw.text((16, 107), str(city_names[c]), fill = "White", font=font_city)

    if city_temp[c] >= 9.5:
        c_temp = '%.0f' % float(city_temp[c])
        draw.text((15, 13), str(c_temp) + degree_sign + 'C', fill = "White", font=font_temp)
        OLED.OLED_ShowImage(image,0,0)
    elif city_temp[c] <= -9.5:
        c_temp = '%.0f' % float(city_temp[c])
        draw.text((10, 13), str(c_temp) + degree_sign + 'C', fill = "White", font=font_temp)
        OLED.OLED_ShowImage(image,0,0)
    else:
        c_temp = '%.1f' % float(city_temp[c])
        draw.text((10, 13), str(c_temp) + degree_sign + 'C', fill = "White", font=font_temp)
        OLED.OLED_ShowImage(image,0,0)
    #DEV_Config.Driver_Delay_ms(500)

def leds_clear():
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()

def rc_time (ldr_pin):
    count_ldr = 0
  
    #Output on the ldr_pin for 
    GPIO.setup(ldr_pin, GPIO.OUT)
    GPIO.output(ldr_pin, GPIO.LOW)
    time.sleep(0.1)

    #Change the ldr_pin back to input
    GPIO.setup(ldr_pin, GPIO.IN)
  
    #Count until the ldr_pin goes high
    while (GPIO.input(ldr_pin) == GPIO.LOW):
        count_ldr += 1

    return count_ldr

def set_brightness():
    global ldr_pin
    global ldr_value
    global ldr
    global ldr_list
    global brightness_now
    global brightness_before
    global LED_BRIGHTNESS
    global motion
    global LED_BRIGHTNESS_list
    global t
    if ldr != 5:
        #print(ldr)
        ldr_value +=rc_time(ldr_pin)
        ldr +=1
    else:
        ldr_value = ldr_value/6
        b = -1
        for i in ldr_list:
            if ldr_value > i:
                brightness_now = i
                b +=1
        #print(b)
        if brightness_before != brightness_now:
            motion = True
            brightness_before = brightness_now
        LED_BRIGHTNESS = LED_BRIGHTNESS_list[b]
        # print(str(t) + " | " + str(rc_time(ldr_pin)) + " | " + str(brightness_now) + " | " + str(motion))
        ldr_value = 0
        ldr = 0

ldr_value = rc_time(ldr_pin)
brightness_now = ldr_value
brightness_before = brightness_now
get_temp()

if __name__ == '__main__':
    try:
        while True:
            set_brightness()

            if motion:
                t = 0
                motion = False

            if check == 0 and t != 5:
                get_temp()
                check = weather_check
            elif check != 0:
                check -=1

            while t != 4:
                font_temp = ImageFont.truetype(font='/home/pi/1.5inch-OLED-with-RPi/fonts/'+temp_fontfamily, size=75, index=0, encoding='unic')
                font_city = ImageFont.truetype(font='/home/pi/1.5inch-OLED-with-RPi/fonts/'+city_fontfamily, size=12, index=0, encoding='unic')
                font_weather = ImageFont.truetype(font='/home/pi/1.5inch-OLED-with-RPi/fonts/'+weather_fontfamily, size=12, index=0, encoding='unic')

                set_brightness()
                strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
                strip.begin()

                if update_displays:
                    leds_clear()
                    display_update(c, city_temp, font_city, font_temp)
                    update_displays = False

                if count == count_max:
                    temp_after = True
                    side = True
                    left = 0
                    right = LED_COUNT - 1

                    for i in range(strip.numPixels()):
                        temp_now = min_temp + i * spacing

                        if side:
                            strip_side = left
                        else:
                            strip_side = right

                        if city_temp[c] >= (temp_now):
                            if temp_now < 0:
                                strip.setPixelColor(strip_side, Color(0,0,255))
                            elif temp_now == 0:
                                strip.setPixelColor(strip_side, Color(255,255,255))
                            elif temp_now > 0 and temp_now <= 0 + hot_color_spacing:
                                strip.setPixelColor(strip_side, Color(30,255,0))
                            elif temp_now > 0 + hot_color_spacing:
                                strip.setPixelColor(strip_side, Color(0,255,0))
                        elif temp_after:
                            if not city_temp[c] >= max_temp:
                                if temp_now < 0:
                                    strip.setPixelColor(strip_side, Color(0,0,255))
                                elif temp_now == 0:
                                    strip.setPixelColor(strip_side, Color(255,255,255))
                                elif temp_now > 0 and temp_now <= 0 + hot_color_spacing:
                                    strip.setPixelColor(strip_side, Color(30,255,0))
                                elif temp_now > 0 + hot_color_spacing:
                                    strip.setPixelColor(strip_side, Color(0,255,0))
                                led_before = strip_side
                            else:
                                led_before = LED_COUNT - 1
                                strip.setPixelColor(led_before, Color(0,255,0))
                            temp_after = False

                        if side:
                            if left + 1 != right:
                                left +=1
                            side = False
                        else:
                            if right - 1 != left:
                                right -=1
                            side = True
                        strip.show()
                        time.sleep(0.1)

                    if led_before_show:
                        strip.show()
                        time.sleep(0.5)
                        strip.setPixelColor(led_before, Color(0,0,0))
                        strip.show()
                        time.sleep(0.5)
                        led_before_show = False
                    else:
                        led_before_show = True
                    count -=1

                elif count != 0:
                    temp_after = True
                    side = True
                    left = 0
                    right = LED_COUNT - 1

                    for i in range(strip.numPixels()):
                        temp_now = min_temp + i * spacing

                        if side:
                            strip_side = left
                        else:
                            strip_side = right

                        if city_temp[c] >= (temp_now):
                            if temp_now < 0:
                                strip.setPixelColor(strip_side, Color(0,0,255))
                            elif temp_now == 0:
                                strip.setPixelColor(strip_side, Color(255,255,255))
                            elif temp_now > 0 and temp_now <= 0 + hot_color_spacing:
                                strip.setPixelColor(strip_side, Color(30,255,0))
                            elif temp_now > 0 + hot_color_spacing:
                                strip.setPixelColor(strip_side, Color(0,255,0))
                        elif temp_after:
                            if not city_temp[c] >= max_temp:
                                if temp_now < 0:
                                    strip.setPixelColor(strip_side, Color(0,0,255))
                                elif temp_now == 0:
                                    strip.setPixelColor(strip_side, Color(255,255,255))
                                elif temp_now > 0 and temp_now <= 0 + hot_color_spacing:
                                    strip.setPixelColor(strip_side, Color(30,255,0))
                                elif temp_now > 0 + hot_color_spacing:
                                    strip.setPixelColor(strip_side, Color(0,255,0))
                                led_before = strip_side
                            else:
                                led_before = LED_COUNT - 1
                                strip.setPixelColor(led_before, Color(0,255,0))
                            temp_after = False

                        if side:
                            if left + 1 != right:
                                left +=1
                            side = False
                        else:
                            if right - 1 != left:
                                right -=1
                            side = True

                    if led_before_show:
                        strip.show()
                        time.sleep(0.5)
                        strip.setPixelColor(led_before, Color(0,0,0))
                        strip.show()
                        time.sleep(0.5)
                        led_before_show = False
                    else:
                        led_before_show = True
                    count -=1

                else:
                    if c == len(city_names)-1:
                        c = 0
                    else:
                        c +=1
                        t +=1
                    #print(c)
                    update_displays = True
                    count = count_max
                
                if GPIO.input(button_next)==0:
                    t = 1
                    leds_clear()
                    for i in range(len(city_temp)):
                        strip.setPixelColor(i, Color(50, 0, 0))
                    strip.setPixelColor(c, Color(255, 0, 0))
                    strip.show()
                    time.sleep(0.8)
                    strip.setPixelColor(c, Color(50, 0, 0))
                    ButtonPress = True
                    while (ButtonPress):
                        if GPIO.input(button_next)==0:
                            if c == (len(city_temp)-1):
                                c = 0
                            else:
                                c +=1
                            for i in range(len(city_temp)):
                                strip.setPixelColor(i, Color(50, 0, 0))
                            strip.setPixelColor(c, Color(255, 0, 0))
                            strip.show()
                            time.sleep(0.8)
                        else:
                            ButtonPress = False
                    update_displays = True
                    count = count_max

                if GPIO.input(button_prev)==0:
                    t = 1
                    leds_clear()
                    for i in range(len(city_temp)):
                        strip.setPixelColor(i, Color(50, 0, 0))
                    strip.setPixelColor(c, Color(255, 0, 0))
                    strip.show()
                    time.sleep(0.8)
                    strip.setPixelColor(c, Color(50, 0, 0))
                    ButtonPress = True
                    while (ButtonPress):
                        if GPIO.input(button_prev)==0:
                            if c == 0:
                                c = len(city_temp)-1
                            else:
                                c -=1
                            for i in range(len(city_temp)):
                                strip.setPixelColor(i, Color(50, 0, 0))
                            strip.setPixelColor(c, Color(255, 0, 0))
                            strip.show()
                            time.sleep(0.8)
                        else:
                            ButtonPress = False
                    update_displays = True
                    count = count_max

                if GPIO.input(button_shutdown)==0:
                    leds_clear()
                    OLED.OLED_Clear()
                    time.sleep(0.1)
                    GPIO.cleanup()
                    os.system("sudo shutdown now -h")

            leds_clear()
            OLED = OLED_Driver.OLED()
            OLED_ScanDir = OLED_Driver.SCAN_DIR_DFT  #SCAN_DIR_DFT = D2U_L2R
            OLED.OLED_Init(OLED_ScanDir)
            OLED.OLED_Clear()

            if GPIO.input(button_next)==0:
                t = 1
                leds_clear()
                for i in range(len(city_temp)):
                    strip.setPixelColor(i, Color(50, 0, 0))
                strip.setPixelColor(c, Color(255, 0, 0))
                strip.show()
                time.sleep(0.8)
                strip.setPixelColor(c, Color(50, 0, 0))
                ButtonPress = True
                while (ButtonPress):
                    if GPIO.input(button_next)==0:
                        if c == (len(city_temp)-1):
                            c = 0
                        else:
                            c +=1
                        for i in range(len(city_temp)):
                            strip.setPixelColor(i, Color(50, 0, 0))
                        strip.setPixelColor(c, Color(255, 0, 0))
                        strip.show()
                        time.sleep(0.8)
                    else:
                        ButtonPress = False
                update_displays = True
                count = count_max

            if GPIO.input(button_prev)==0:
                t = 1
                leds_clear()
                for i in range(len(city_temp)):
                    strip.setPixelColor(i, Color(50, 0, 0))
                strip.setPixelColor(c, Color(255, 0, 0))
                strip.show()
                time.sleep(0.8)
                strip.setPixelColor(c, Color(50, 0, 0))
                ButtonPress = True
                while (ButtonPress):
                    if GPIO.input(button_prev)==0:
                        if c == 0:
                            c = len(city_temp)-1
                        else:
                            c -=1
                        for i in range(len(city_temp)):
                            strip.setPixelColor(i, Color(50, 0, 0))
                        strip.setPixelColor(c, Color(255, 0, 0))
                        strip.show()
                        time.sleep(0.8)
                    else:
                        ButtonPress = False
                update_displays = True
                count = count_max

            if GPIO.input(button_shutdown)==0:
                leds_clear()
                OLED.OLED_Clear()
                time.sleep(0.1)
                GPIO.cleanup()
                os.system("sudo shutdown now -h")

    except KeyboardInterrupt:
        pass
    #except Exception:
    #    os.system("sudo python /home/pi/1.5inch-OLED-with-RPi/OLED_driver_and_code_python/Temp-display-cities-led-after-button-ldr-next-weather-motion-v2.py")
    finally:
        leds_clear()
        OLED.OLED_Clear()
        GPIO.cleanup()