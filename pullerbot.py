#!/usr/bin/env python3
# so that script can be run from Brickman
import subprocess
import termios, tty, sys
from ev3dev.ev3 import *
from time import sleep

motor_left = LargeMotor('outA')
motor_right = LargeMotor('outB')
motor_grabber = MediumMotor('outC')
sensor_color = ColorSensor()
sensor_color.mode = 'COL-REFLECT'

# LINKKI DOKKAREIHIN https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/index.html

print("READY")

def getch():
  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  tty.setcbreak(fd)
  ch = sys.stdin.read(1)
  termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
  return ch

def up():
  motor_grabber.run_timed(time_sp=50, speed_sp=200)

def down():
  motor_grabber.run_forever(speed_sp=-1000)

def forward():
  motor_left.run_timed(time_sp=100, speed_sp=1000)
  motor_right.run_timed(time_sp=100, speed_sp=1000)

def back():
  motor_left.run_timed(time_sp=100, speed_sp=-1000)
  motor_right.run_timed(time_sp=100, speed_sp=-1000)

def left():
  motor_left.run_timed(time_sp=100, speed_sp=-250)
  motor_right.run_timed(time_sp=100, speed_sp=250)

def right():
  motor_left.run_timed(time_sp=100, speed_sp=250)
  motor_right.run_timed(time_sp=100, speed_sp=-250)

def line_follow_left():
  motor_left.run_timed(time_sp=25, speed_sp=250)
  motor_right.run_timed(time_sp=25, speed_sp=750)

def line_follow_right():
  motor_left.run_timed(time_sp=25, speed_sp=750)
  motor_right.run_timed(time_sp=25, speed_sp=250)

def line_follow_back():
  motor_left.run_timed(time_sp=60, speed_sp=-900)
  motor_right.run_timed(time_sp=60, speed_sp=-900)
  sleep(0.06)

def line_follow_check(direction):
  if direction == 'left':
    motor_left.run_timed(time_sp=10, speed_sp=-300)
    motor_right.run_timed(time_sp=10, speed_sp=300)
    sleep(0.01)
  if direction == 'right':
    motor_left.run_timed(time_sp=10, speed_sp=300)
    motor_right.run_timed(time_sp=10, speed_sp=-300)
    sleep(0.01)
  return measure_color()

black_count = 0
max_black_count = 2

left_check_area = 80
right_check_area = 220

def line_follow_step():
  global black_count
  if not measure_color():
    black_count += 1
    line_follow_left()
  else:
    black_count = 0
    line_follow_right()
  if black_count > max_black_count:
    for _ in range(left_check_area):
      if line_follow_check("left"):
        for j in range(4):
          line_follow_check("left")
        return
    for _ in range(left_check_area + right_check_area):
      if line_follow_check("right"):
        for j in range(4):
          line_follow_check("right")
        return
    for _ in range(right_check_area):
      if line_follow_check("left"):
        black_count = max(black_count - 1, 0)
        for j in range(4):
          line_follow_check("left")
    line_follow_back()

color_dark = 45
color_light = 74
color_threshold = (color_dark + color_light) // 2

def calibrate_color():
  global color_dark
  global color_light
  global color_threshold
  print("DARK VALUE")
  getch()
  color_dark = sensor_color.value()
  print("VALUE = {}".format(color_dark))
  print("LIGHT VALUE")
  getch()
  color_light = sensor_color.value()
  print("VALUE = {}".format(color_light))
  color_threshold = (color_dark + color_light) / 2

def measure_color():
  return sensor_color.value() > color_threshold

def manual_control():
  while True:
    k = getch()
    print(k)
    if k == '0':
      calibrate_color()
    if k == '5':
      line_follow_step()
    if k == '8':
      forward()
    if k == '4':
      left()
    if k == '6':
      right()
    if k == '2':
      back()
    if k == '1':
      up()
    if k == '3':
      down()

manual_control()