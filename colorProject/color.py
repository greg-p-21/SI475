import cv2
import numpy as np
import rospy,time,tf
from turtleAPI import robot

class Filter:
    HSV_COLOR_RANGES = {
        'red1': [[180, 255, 255], [159, 50, 70]],
        'red2': [[9, 255, 255], [0, 50, 70]],
        'green': [[89, 255, 255], [36, 50, 70]],
        'blue': [[128, 255, 255], [90, 50, 70]],
        'yellow': [[35, 255, 255], [25, 50, 70]],
        'purple': [[158, 255, 255], [129, 50, 70]]
    }

    RGB_COLORS = {
        'red': [0,0,255],
        'green': [0,255,0],
        'blue': [255,0,0],
        'purple': [255,0,255],
        'yellow': [0,255,255]
    }

    @staticmethod
    def get_filtered(img, color):

        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        mask = None
        if color == 'red':
            lower_red1 = np.array(Filter.HSV_COLOR_RANGES['red1'][1])
            upper_red1 = np.array(Filter.HSV_COLOR_RANGES['red1'][0])

            lower_red2 = np.array(Filter.HSV_COLOR_RANGES['red2'][1])
            upper_red2 = np.array(Filter.HSV_COLOR_RANGES['red2'][0])

            mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
            mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
            mask = mask1 + mask2
        else:
            lower = np.array(Filter.HSV_COLOR_RANGES[color][1])
            upper = np.array(Filter.HSV_COLOR_RANGES[color][0])
            mask = cv2.inRange(hsv, lower, upper)

        img[mask != 0] = Filter.RGB_COLORS[color]

        return img

    @staticmethod
    def get_PID_value(filtered_img, color):
        num_ys = len(filtered_img[0])
        num_xs = len(filtered_img)
        rgb_color = np.asarray(Filter.RGB_COLORS[color])

        color_columns = []
        max_column = 0
        max_amount = 0
        # print(f_img)
        for y in range(num_ys):
            amount = 0
            for x in range(num_xs):
                if (filtered_img[x,y] == rgb_color).all():
                    amount = amount + 1

            color_columns.append(amount)
            if (amount > color_columns[max_column]):
                max_column = y
                max_amount = amount

        return (num_ys/2 - max_column), max_amount

def PID_img(curr_img, end_img, prev_img):
    Kp = 0.0003
    Ekp = Kp*curr_img

    Ki = 0.0
    Eki = 0
    for i in range(0,len(prev_img)):
        Eki += prev_img[i]
    Eki = Ki*Eki

    Kd = 0
    Ekd = curr_img - prev_img[len(prev_img)-2]
    Ekd = Kd*Ekd

    return Ekp + Eki + Ekd

try:
    colors = ['red', 'blue', 'green', 'purple', 'yellow']
    print("creating robot")
    r = robot()
    color = raw_input("Choose your color: ")
    found = False
    popped = False

    if color not in colors:
        print("Please choose from one of the following colors (case sensitive):\n")
        print(colors)
        color = raw_input("Choose your color: ")
    if color not in colors:
        exit(1)

    prev_img = []
    while not popped and not rospy.is_shutdown():
        img = r.getImage()
        f_img = Filter.get_filtered(img, color)
        curr_tup = Filter.get_PID_value(f_img, color)
        
        cv2.imshow("Filtered Image", f_img)
        cv2.waitKey(1)

        curr = curr_tup[0]
        detected = curr_tup[1]

        if detected > 30:
            prev_img.append(curr)
            pid_speed = PID_img(curr, 0, prev_img)
            print(pid_speed)
            found = True
        else:
            found = False

        if not found:
            r.drive(angSpeed=0.2, linSpeed=0)
        else:
            r.drive(angSpeed=pid_speed, linSpeed=0.3)
        time.sleep(0.1)
        #cv2.waitKey(1)

except Exception as e:
  print(e)
  rospy.loginto("node now terminated")
