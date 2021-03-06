#!/usr/bin/env python
import rospy 
import numpy as np
import cv2
from sensor_msgs.msg import Image as img
from std_msgs.msg import String
from cv_bridge import CvBridge
import PIL
from PIL import ImageFont
from PIL import Image
from PIL import ImageDraw
import random
import time
hrange = [0,180]
srange = [0,256]
ranges = hrange+srange  
class saveColor:
	def __init__(self):
		print("initiated")
		self.bridge = CvBridge()
		self.img_sub = rospy.Subscriber("/camera/rgb/image_rect_color", img, self.camCallback)
		self.pub = rospy.Publisher("/images", img, queue_size=1)
		self.img_pub = rospy.Publisher("/exploring_challenge", String, queue_size=1)
		self.index = 1
		
	def camCallback(self,msg):
		print("Image recieved! Processing...")	
		img_data = self.bridge.imgmsg_to_cv2(msg)
		self.processImg(img_data)
		time.sleep(1)
        
	def processImg(self,img):
		print("processing")
		hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
		contourList = []
		maskG = cv2.inRange(hsv, np.array([35,100,100]), np.array([70, 255, 255])) 
		maskG = self.blur(maskG)      
		maskR = cv2.inRange(hsv, np.array([0,100,100]), np.array([15, 255, 255]))   
		maskR = self.blur(maskR)
		maskB = cv2.inRange(hsv, np.array([90,150,150]), np.array([130, 255, 255])) 
		maskB = self.blur(maskB)  
		maskY = cv2.inRange(hsv, np.array([23,100,160]), np.array([30, 255, 255]))  
		maskY = self.blur(maskY) 
		maskP1 = cv2.inRange(hsv, np.array([0,50,230]), np.array([10, 150, 255]))  
		maskP2 = cv2.inRange(hsv, np.array([150,50,230]), np.array([180,150,255]))  
		maskP = maskP1+maskP2 
		maskP = self.blur(maskP)
		contoursG = cv2.findContours(maskG, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contoursR = cv2.findContours(maskR, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contoursB = cv2.findContours(maskB, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contoursY = cv2.findContours(maskY, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		contoursP = cv2.findContours(maskP, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
		self.contourAppend(contourList,contoursG,"green")
		self.contourAppend(contourList,contoursR,"red")
		self.contourAppend(contourList,contoursB,"blue")
		self.contourAppend(contourList,contoursY,"yellow")
		self.contourAppend(contourList,contoursP,"pink")
		if len(contourList)>0:
			biggest = self.findBiggest(contourList)
		else:
			biggest = None
		if biggest != None:
			print(biggest.text)
			#print(biggest.contour)
			cv2.drawContours(img, biggest.contour, -1, (0, 255, 0), 3)
			#cv2.imshow("oooo",img)
			#cv2.waitKey(0)
			if biggest.text != "pink":
				self.saveImg(img,biggest.text)
			elif biggest.text == "lol":
				x,y,w,h = cv2.boundingRect(biggest.contour)
				sliced = hsv[x:x+w,y:y+h,:]
				hsvTest = cv2.calcHist(sliced,[0,1],None,[180,256],ranges)
				racecarVal = cv2.compareHist(hsvTest,self.racecar,cv2.cv.CV_COMP_CORREL)
				ariVal = cv2.compareHist(hsvTest,self.ari,cv2.cv.CV_COMP_CORREL)
				sertacVal = cv2.compareHist(hsvTest,self.sertac,cv2.cv.CV_COMP_CORREL)
				catVal = cv2.compareHist(hsvTest,self.cat,cv2.cv.CV_COMP_CORREL)
				maxVal = max(racecarVal,ariVal,sertacVal,catVal)
				if maxVal == racecarVal:
					self.saveImg(img,"racecar")
				elif maxVal == ariVal:
					self.saveImg(img,"ari")
				elif maxVal == sertacVal:
					self.saveImg(img,"sertac")
				else:
					self.saveImg(img,"cat")
	def saveImg(self,img,text):
		cv2.imwrite("troll.jpeg",img)
		processed_img = self.bridge.cv2_to_imgmsg(img, "bgr8")
		self.pub.publish(processed_img)
		pic = Image.open("troll.jpeg")
		font = ImageFont.truetype("/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf",25)
		draw = ImageDraw.Draw(pic)
		draw.text((0, 0),text,(255,255,0),font=font)
		rand = self.index
		self.index = self.index + 1
		fileName = "/home/racecar/challenge_photos/"+str(rand)+".jpeg"
		pic.save(fileName,"jpeg")
		self.img_pub.publish(text)
	def findBiggest(self,contourList):
		result = contourList[0]
		for x in contourList:
			if cv2.contourArea(x.contour)>cv2.contourArea(result.contour):
				result = x
		if cv2.contourArea(result.contour)>2000:
			return result
		else:
			return None
	def contourAppend(self,contourList,contour,color):
		for x in contour[0]:
			appendedStuff = contours(x,color)
			contourList.append(appendedStuff)
	def blur(self,mask):
		mask = cv2.GaussianBlur(mask,(21,21),0)
		return cv2.erode(mask,(3,3),iterations=5)
class contours:
	def __init__(self,contour,text):
		self.contour = contour
		self.text = text
if __name__ == "__main__":
	rospy.init_node("save_color")
	node = saveColor()
	rospy.spin()
