from Raspbot_Lib import Raspbot
import time, math


bot = Raspbot()

duration = 1
speed = 100


def move_forward(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 90)
    print(f'L1:{l1:>4}| ↑ |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_backward(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 270)
    print(f'L1:{l1:>4}| ↓ |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_left(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 180)
    print(f'L1:{l1:>4}| ← |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_right(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 0)
    print(f'L1:{l1:>4}| → |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def rotate_left(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 180)
    print(f'L1:{l1:>4}| ↖ |R1:{r1:<4}')
    print(f'L2:{-l2:>4}|   |R2:{abs(r2):<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, -l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, abs(r2) + 0)
    time.sleep(duration)
    stop_robot(bot)

def rotate_right(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 0)
    print(f'L1:{l1:>4}| ↗ |R1:{r1:<4}')
    print(f'L2:{abs(l2):>4}|   |R2:{-r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, abs(l2) + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, -r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_diagonal_left_front(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 135)
    print(f'L1:{l1:>4}| ↖ |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_diagonal_left_back(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 225)
    print(f'L1:{l1:>4}| ↙ |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_diagonal_right_front(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 45)
    print(f'L1:{l1:>4}| ↗ |R1:{r1:<4}')
    print(f'L2:{l2:>4}|   |R2:{r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def move_diagonal_right_back(speed, duration):
    l1, l2, r1, r2 = set_deflection(speed, 315)
    print(f'L1:={l1:>4}| ↘ |R1:={r1:<4}')
    print(f'L2:={l2:>4}|   |R2:={r2:<4}\n')
    bot.Ctrl_Muto(0, l1 + 0)
    bot.Ctrl_Muto(1, l2 + 0)
    bot.Ctrl_Muto(2, r1 + 0)
    bot.Ctrl_Muto(3, r2 + 0)
    time.sleep(duration)
    stop_robot(bot)

def stop_robot(bot):

    bot.Ctrl_Car(0, 0, 0)
    bot.Ctrl_Car(1, 0, 0)
    bot.Ctrl_Car(2, 0, 0)
    bot.Ctrl_Car(3, 0, 0)

def set_deflection(speed, deflection):
    """
        90
    180--丨--0
        270
    """
    rad2deg = math.pi / 180
    vx = speed * math.cos(deflection * rad2deg)
    vy = speed * math.sin(deflection * rad2deg)
    l1 = int(vy + vx)
    l2 = int(vy - vx)
    r1 = int(vy - vx)
    r2 = int(vy + vx)
    return l1, l2, r1, r2
