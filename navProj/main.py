import argparse
import rospy,time,tf
import math

from turtleAPI import robot

from route import dijkstras
from adjMatrix import AdjMatrix
from pid import PID

def to_tuple(string):
    res = []
    for token in string.split(", "):
        num = float(token.replace("(", "").replace(")", "").replace('"', ""))
        res.append(num)
    return tuple(res)

def distError(current, target):
        currentX = current[0]
        currentY = current[1]
        targetX = target[0]
        targetY = target[1]
    
        #middle work to simplify the distance calculation line
        difX = targetX - currentX
        difY = targetY - currentY

        #calculate the raw distance between the 2 points which represents the coordinate error
        dist = math.sqrt((math.pow(difX, 2.0)) + (math.pow(difY, 2.0)))
        
        return dist

def angleError(current, target):
        target_x = target[0]
        target_y = target[1]

        (curr_x, curr_y, curr_yaw) = current
        angle = math.atan2(target_y - curr_y, target_x - curr_x)
        angleVel = angle - curr_yaw

        while angleVel < -math.pi/2 or angleVel > math.pi/2:
            if angleVel > math.pi/2:
                angleVel = -2*math.pi + angleVel
            elif angleVel < -math.pi/2:
                angleVel = 2*math.pi + angleVel 
        
        return angleVel

def GoTo(R, target, dist_pid, ang_pid):
    start = R.getMCLPose()
    RATE = rospy.Rate(10)

    start_x = start[0]
    start_y = start[1]

    target_x = target[0]
    target_y = target[1]

    goalDistance = math.sqrt(pow( start_x- target_x, 2) + pow(start_y - target_y, 2))
    distance = goalDistance

    while distance > 0.5 and not rospy.is_shutdown():
        RATE.sleep()
        print("entered loop")

        current = R.getMCLPose()
        # self.distError(current, target)

        lspeed = -1* dist_pid(distError(current, target))
        aspeed = -1* ang_pid(angleError(current, target))

        print("distance", distance)
        print("dist and angle pid", (lspeed, aspeed))

        if aspeed > .1 or aspeed < -.1:
            R.drive(angSpeed=aspeed, linSpeed=0)
        else:
            R.drive(angSpeed=aspeed, linSpeed=lspeed)

        print("current position", R.getPositionTup())
        print("goal", target)

        distance = math.sqrt(pow( current[0] - target_x, 2) + pow(current[1] - target_y, 2))


    print("Reached point")



if __name__ == "__main__":
    print("code running")
    parser = argparse.ArgumentParser()
    
    parser.add_argument("dotfile")
    parser.add_argument("goal", help='end point of robot: "(x, y)"')
    parser.add_argument("--start", help='starting point of robot: "(x, y)"')

    args = parser.parse_args()

    if args.start:
        start_loc = to_tuple(args.start)

        end_loc = to_tuple(args.goal)

        # adjacency matrix
        adj = AdjMatrix(args.dotfile, start_loc, end_loc)

        # run dikj
        route, points = dijkstras(adj, ("start", start_loc), ("finish", end_loc))

        print(route, points)
        
        exit()

    try:
        print("creating robot")
        r = robot()
        found = False

        tup = r.getMCLPose()
        # get location
        start_loc = (tup[0], tup[1])
        
        # end location
        end_loc = to_tuple(args.goal)

        # adjacency matrix
        adj = AdjMatrix(args.dotfile, start_loc, end_loc)

        # run dikj
        route, points = dijkstras(adj, ("start", start_loc), ("finish", end_loc))

        print(route, points)
        
        distPID = PID(kp = .15, output_limits=(-.4, .4))
        angPID = PID(kp = .25, output_limits=(-.5, .5))

        while not rospy.is_shutdown():
            for p in points:
                print(p)
                GoTo(r, p, distPID, angPID) 
        
        r.drive(angSpeed=0, linSpeed=0)
        print("Final location found")

    except Exception as e:
        print(e)
        rospy.loginto("node now terminated")


