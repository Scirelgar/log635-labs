import sys
from time import time

from Raspbot_Lib import Raspbot
#导入麦克纳姆小车驱动库 Import Mecanum Car Driver Library
# from McLumk_Wheel_Sports import *

# Constants related to the ultrasonic sensor
NEAR_DISTANCE = 200  # Define near distance threshold (millimeters)
FAR_DISTANCE = 425   # Define far distance threshold (millimeters)

OUT_OF_LAB = True

motion_speed =30

bot = Raspbot()

def _init_systems():
    # Ultrasonic sensor
    bot.Ctrl_Ulatist_Switch(1)
    time.sleep(0.1)

def _dist_compute():
    """

    """
    diss_H =bot.read_data_array(0x1b,1)[0]
    diss_L =bot.read_data_array(0x1a,1)[0]

    return diss_H << 8 | diss_L

    

def bot_follow_black_line(motion_speed:int = 15):
    """"Follow a black line using the IR sensors.

    This funciton reads the data from 4 IR sensors computes the movement the bot should do.
    The sensors data is read from data array at address 0x0a. The data is a single byte where each bit represents the state of a sensor.
    The sensors are arranged as follows:
    X2 X1 X3 X4
    |  |  |  |
    L1 L2 R1 R2
    L1: Left outermost sensor
    L2: Left inner sensor
    R1: Right inner sensor
    R2: Right outermost sensor
    
    
    """

    
    track_data = bot.read_data_array(0x0a, 1)
    track = int(track_data[0])


    x1 = (track >> 3) & 0x01  
    x2 = (track >> 2) & 0x01  
    x3 = (track >> 1) & 0x01  
    x4 = track & 0x01       

    lineL1=x2
    lineL2=x1
    lineR1=x3
    lineR2=x4

    if lineL1 == 0 and lineL2 == 0 and lineR1 == 0 and lineR2 == 0:  # 都是黑色, 加速前进 All black, speed up
        print("1")
        print(lineL1,lineL2,lineR1,lineR2)
        move_forward(int(motion_speed))

    

try:
    bot.Ctrl_Ulatist_Switch(1)
    time.sleep(0.1)

    while True:
        # 从I2C读取巡线传感器数据 Read line sensor data from I2C
        track_data = bot.read_data_array(0x0a, 1)
        track = int(track_data[0])

        # 解析巡线传感器的状态 Analyze the status of the line patrol sensor
        x1 = (track >> 3) & 0x01  
        x2 = (track >> 2) & 0x01  
        x3 = (track >> 1) & 0x01  
        x4 = track & 0x01       
        """
        X2 X1 X3 X4
        |  |  |  |
        L1 L2 R1 R2
        """
        lineL1=x2
        lineL2=x1
        lineR1=x3
        lineR2=x4


        dis = _dist_compute()



        if lineL1 == 0 and lineL2 == 0 and lineR1 == 0 and lineR2 == 0:  # 都是黑色, 加速前进 All black, speed up
            print("1")
            print(lineL1,lineL2,lineR1,lineR2)
            move_forward(int(motion_speed))
        elif NEAR_DISTANCE <= dis <= FAR_DISTANCE:
            print(f"Obstacle is at medium distance, distance: {dis} mm")
            stop_robot()
            time.sleep(2)
            bot.Ctrl_BEEP_Switch(1)  #蜂鸣器开  Buzzer on
            bot.Ctrl_BEEP_Switch(0)  #蜂鸣器关 Buzzer off


        elif( (lineL2 == 0 or lineL1 == 0) and lineR2 == 0):#右锐角：右大弯,0表示检测到黑线 Right acute angle: right big bend, 0 means black line is detected
            print("2")
            print(lineL1,lineL2,lineR1,lineR2)
            rotate_right(motion_speed)
            time.sleep(0.05)
        elif lineL1 == 0 and (lineR2 == 0 or lineR1 == 0):  # 左锐角或左大弯 Left sharp angle or left sharp bend
            print("3")
            print(lineL1,lineL2,lineR1,lineR2) 
            rotate_left(int(motion_speed*1.5))  # 左急转弯 Sharp left turn
            time.sleep(0.15)
        elif lineL1 == 0:  # 左最外侧检测 Left outermost detection
            print("4")
            print(lineL1,lineL2,lineR1,lineR2)
            rotate_left(motion_speed)  # 左急转弯 Sharp left turn
            time.sleep(0.02)
        elif lineR2 == 0:  # 右最外侧检测 Right outermost detection
            print("5")
            print(lineL1,lineL2,lineR1,lineR2)
            rotate_right(motion_speed)
            time.sleep(0.01)
        elif lineL2 == 0 and lineR1 == 1:  # 中间黑线上的传感器微调车左转 The sensor on the middle black line fine-tunes the car to turn left
            print("6")
            print(lineL1,lineL2,lineR1,lineR2)
            rotate_left(int(motion_speed))  # 左转 Turn left
        elif lineL2 == 1 and lineR1 == 0:  # 中间黑线上的传感器微调车右转 The sensor on the middle black line fine-tunes the car to turn right
            print("7")
            print(lineL1,lineL2,lineR1,lineR2) 
            rotate_right(int(motion_speed)) #右转 Turn right
        elif lineL2 == 0 and lineR1 == 0:  # 都是黑色, 加速前进 All black, speed up
            print("8")
            print(lineL1,lineL2,lineR1,lineR2)
            move_forward(motion_speed)

        

        # 等待一段时间再进行下一次检测 Wait for a while before the next test
        time.sleep(0.01)

except KeyboardInterrupt:
    # 当用户中断程序时，确保所有电机停止 Ensure that all motors stop when the user interrupts the program
    bot.Ctrl_Ulatist_Switch(0)
    time.sleep(0.1)
    stop_robot()
    print("Ending")
