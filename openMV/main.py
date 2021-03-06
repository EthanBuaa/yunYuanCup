import time
from camera_control import CameraAsSensor
from PID_external import PID
from DAC_communicate import OutputToDue
from IO_communicate import InputFromDue
from my_servo import MyServo
from pyb import RTC, Timer

RED = 1
GREEN = 2
RED_HOME = 3
GREEN_HOME = 4

# settings before match or test: (double check before match!)
INVERSE = True      # is the camera inverse or not
TESTING = False      # if true then you can control which mode OpenMv is in (to set CAMERA_MODE and CONTROL_MODE)
COLOR = RED         # the color to recognize (RED or GREEN)
TITLE_ANGLE = 24     # the angle of the title servo (-90 to 90)

# setting modes during test: (if true the communication between OpenMv and Due will be invalid)
CAMERA_MODE = RED

# setting PID:
pid = PID()

# setting servos:
servos = MyServo(p=0.07, i=0, imax=90)
servos.init(tilt_angle=TITLE_ANGLE)

# setting timer:
rtc = RTC()
rtc.datetime((0, 0, 0, 0, 0, 0, 0, 0))

# setting input and output:
returning_pin = InputFromDue('P4')
output_pin = OutputToDue('P6')

# setting camera:
camera = CameraAsSensor(COLOR)
camera.init(INVERSE)

clock = time.clock()

while(True):
    clock.tick()
    img = camera.photo_taking()
    count = rtc.datetime()[6]       # number of second

    # read the value of returning pin:
    value_of_returning = returning_pin.value()
    if value_of_returning == 1 and camera.mode < 3:
        camera.mode += 2
        pid.clear()
    elif value_of_returning == 0 and camera.mode > 2:
        camera.mode -= 2
        pid.clear()

    center_of_target = camera.recognition(img)
    delta_pixel = 0


    if center_of_target >= 0:
        delta_pixel = (-center_of_target + 160) * INVERSE
        expected_pixel = pid.get_expected_pixel(delta_pixel)
        output_pin.write_message(expected_pixel / 2 + 75)
        print("Expected pixel: ", expected_pixel)
    else:
        pid.clear()
        output_pin.write_message(0)
        print(0)

    # with servo:
    '''
        if center_of_target >= 0:
            delta_pixel = (-center_of_target + 160) * INVERSE
            servos.rotate_steering_gear(delta_pixel)
            expected_angle = servos.pan.angle()
            output_pin.write_message(expected_angle / 3 + 75)
            print("Expected angle: ", expected_angle)
        else:
            servos.init(TITLE_ANGLE)
            servos.scan(count)
            output_pin.write_message(0)
            print(0)
    '''

    #print(clock.fps())
