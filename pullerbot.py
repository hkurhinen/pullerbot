#!/usr/bin/env python3
# so that script can be run from Brickman
import subprocess
import termios, tty, sys, select
from ev3dev.ev3 import *
from time import sleep
from string import digits

"""
Challenge 1: First the robot navigates to button using gyro
and then follows line after that

Challenge 2: Line follower using color sensor

Challenges 3-6: Manual control
"""

motor_left = LargeMotor('outA')
motor_right = LargeMotor('outB')
motor_grabber = MediumMotor('outC')
sensor_color = ColorSensor()
sensor_gyro = GyroSensor()
sensor_color.mode = ColorSensor.MODE_COL_COLOR
sensor_gyro.mode = GyroSensor.MODE_GYRO_ANG

# LINKKI DOKKAREIHIN https://ev3dev-lang.readthedocs.io/projects/python-ev3dev/en/stable/index.html

print("READY")

def getch(*, blocking=True):
  fd = sys.stdin.fileno()
  old_settings = termios.tcgetattr(fd)
  tty.setcbreak(fd)
  i,_,_ = select.select([sys.stdin],[],[],0.0001)
  ch = None
  if not blocking:
    for s in i:
      if s == sys.stdin:
          ch = sys.stdin.read(1)
  else:
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
  motor_left.run_timed(time_sp=25, speed_sp=200)
  motor_right.run_timed(time_sp=25, speed_sp=600)

def line_follow_right():
  motor_left.run_timed(time_sp=25, speed_sp=600)
  motor_right.run_timed(time_sp=25, speed_sp=200)

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

left_check_area = 120
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

def find_line():
  while not measure_color():
    motor_left.run_timed(time_sp=25, speed_sp=300)
    motor_right.run_timed(time_sp=25, speed_sp=300)
    sleep(0.025)

color_dark = 45
color_light = 74
color_threshold = (color_dark + color_light) // 2

colors = {
  0: "none",
  1: "black",
  2: "blue",
  3: "green",
  4: "yellow",
  5: "red",
  6: "white",
  7: "brown"
}

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

def is_button():
  sensor_color.value()
  return sensor_color.color == ColorSensor.COLOR_YELLOW

def measure_color():
  return sensor_color.value() > color_threshold

def normalize(angle):
  while angle < -180:
    angle += 360
  while angle > 179:
    angle -= 360
  return angle

def gyro_left():
  motor_left.run_timed(time_sp=25, speed_sp=-100)
  motor_right.run_timed(time_sp=25, speed_sp=100)
  sleep(0.025)

def gyro_right():
  motor_left.run_timed(time_sp=25, speed_sp=100)
  motor_right.run_timed(time_sp=25, speed_sp=-100)
  sleep(0.025)

def gyro_turn(target_angle):
  start_angle = sensor_gyro.value()
  angle = sensor_gyro.value() - start_angle
  diff = target_angle - angle
  while abs(diff) > 5:
    if diff > 0:
      gyro_left()
    else:
      gyro_right()
    angle = sensor_gyro.value() - start_angle
    diff = target_angle - angle
    print(diff)
    
def gyro_forward(distance):
  rotations = distance/17.6
  ticks = rotations*360
  motor_left.run_to_rel_pos(speed_sp=300, position_sp=ticks)
  motor_right.run_to_rel_pos(speed_sp=300, position_sp=ticks)
  while motor_left.is_running:
    sleep(0.001)

def gyro_path_run(path):
  for move, value in path:
    if move == 'forward':
      gyro_forward(value)
    if move == 'turn':
      gyro_turn(value)
    sleep(0.2)

maze_prelude = [
  ('forward',50),
  ('turn',-100),
  ('forward',35),
  ('turn',80),
  ('forward',20),
  ('turn',-50),
  ('forward',10),
  ('turn',-35),
  ('forward',20),
  ('turn',45),
  ('forward',20)
]
iron_forest = [
  ('forward',10),
  ('turn',30),
  ('forward',20),
  ('turn',60),
  ('forward',30),
  ('turn',-30),
  ('forward',10),
  ('turn',-50),
  ('forward',10),
  ('turn',-40),
  ('forward',30),
  ('turn',80),
  ('forward',10),
  ('turn',20),
  ('forward',20),
  ('turn',20),
  ('turn',40),
  ('forward',15),
  ('turn',-20),
  ('forward',10),
  ('turn',-35),
  ('forward',10),
  ('turn',-55),
  ('forward',30),
  ('turn',-20),
  ('forward',20),
  ('turn',30),
  ('forward',15),
  ('forward',20),
]

def manual_control():
  while True:
    k = getch()
    if k == '0':
      calibrate_color()
    if k == '5':
      gyro_path_run(maze_prelude)
      find_line()
      while getch(blocking=False) != '5':
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
    if k == '7':
      gyro_path_run(iron_forest)
    if k == '+':
      while getch(blocking=False) != '5':
        line_follow_step()
    if k == '9':
      sensor_color.value()
      Sound.speak(colors[sensor_color.color])

def getdigit():
  val = 'x'
  while val not in digits:
    val = getch()
  return val

def gyro_control():
  item = getdigit()
  if item == '0': # forward
    arg = int(getdigit() + getdigit() + getdigit())
    gyro_forward(arg)
  elif item == '1': # turn
    arg = int(getdigit() + getdigit() + getdigit()) - 180
    gyro_turn(arg)

manual_control()