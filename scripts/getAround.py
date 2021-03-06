#!/usr/bin/env python
import rospy
import math
from sensor_msgs.msg import LaserScan
from ackermann_msgs.msg import AckermannDriveStamped
from racecar import racecar
import time

class getAround:
	def __init__(self):

		# create Subscriber and initialize racecar class
		self.scanResult = rospy.Subscriber("/scan",LaserScan,self.callBack)
		self.car = racecar()

	def calcLargestDistance(self, ranges, side):
        
		if side == "L":                 # Wall on left side
		    leftSide = ranges[700: 900]
		    return max(leftSide)


	def callBack(self,msg):
		# perform lidar data smoothing (by averaging)
		resultList = []
		for i in range(60,1020):				# creates array with 960 elements
			average = 0
			for j in range(-2,3):
				average = average+msg.ranges[i+j]	# averages 5 values together
			resultList.append(average/5)

		print(resultList[480])					# print value of center front

		if min(resultList)<0.4:					# if too close avoid
			self.avoid(resultList)
		else:
			self.follow(resultList)				# else wall follow
			
	def avoid(self,msg):
		result = msg.index(min(msg))				# takes index of closes point

		difference = 480-result if (480-result) != 0 else 1	# calculates angle from front

		steering = 200.0/difference if abs(200.0/difference)<1 else difference/abs(difference)	# calculate steering 

		if min(msg[420:540])<0.2: 					# if front is too close, go back
			self.car.drive(-.5,0.0)
			print("going back")
			time.sleep(0.1)
		elif(self.calcLargestDistance(msg, "L") > .7):	# if left is empty, turn left
			self.car.turn(msg, "CCW")
			print("turning")	
		else:
			self.car.drive(0.25,steering)			# else avoid the obstacle
			print("avoiding")
	def follow(self,msg):		
    		self.car.drive(1.0,0.0)					# drive straight
		print("wallfollowing")

if __name__ == "__main__":
	rospy.init_node("getAround")
	getAround = getAround()
	rospy.spin()
