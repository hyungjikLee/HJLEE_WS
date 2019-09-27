#!/usr/bin/env python
#################################################################################
# Copyright 2018 ROBOTIS CO., LTD.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#################################################################################

# Authors: Gilbert #

import rospy
from geometry_msgs.msg import Twist, Point, Quaternion, PoseStamped
import tf
from math import radians, copysign, sqrt, pow, pi, atan2
from tf.transformations import euler_from_quaternion
from ar_track_alvar_msgs.msg import AlvarMarkers
from sensor_msgs.msg import LaserScan
import numpy as np
#Lee write
import random
import sys


msg = """
control your Turtlebot3!
-----------------------
function
	s = stop
	1 = patrol
	2 = position order
	3 = search_marker
	x = exit

-----------------------
"""


class GotoPoint():
	def __init__(self):
		rospy.init_node('turtlebot3_pointop_key', anonymous=False)
		rospy.on_shutdown(self.shutdown)
		self.cmd_vel = rospy.Publisher('cmd_vel', Twist, queue_size=5)
		position = Point()
		self.tf_listener = tf.TransformListener()
		self.odom_frame = 'odom'
		self.p  = PoseStamped()
		self.id = -1

		self.marker_detect = rospy.Subscriber("ar_pose_marker", AlvarMarkers, self.get_marker)
		self.marker_detect_flag = False


		self.laser_scan_detect = rospy.Subscriber("/scan", LaserScan, self.get_scan)
		self.laserScan_data = []


		try:
			self.tf_listener.waitForTransform(self.odom_frame, 'base_footprint', rospy.Time(), rospy.Duration(1.0))
			self.base_frame = 'base_footprint'
		except (tf.Exception, tf.ConnectivityException, tf.LookupException):
			try:
				self.tf_listener.waitForTransform(self.odom_frame, 'base_link', rospy.Time(), rospy.Duration(1.0))
				self.base_frame = 'base_link'
			except (tf.Exception, tf.ConnectivityException, tf.LookupException):
				rospy.loginfo("Cannot find transform between odom and base_link or base_footprint")
				rospy.signal_shutdown("tf Exception")





		(position, rotation) = self.get_odom()

		(goal_x, goal_y, goal_z) = self.getkey()

		if goal_z > 180 or goal_z < -180:
			print("you input wrong z range.")
			self.shutdown()
		goal_z = np.deg2rad(goal_z)
		goal_distance = sqrt(pow(goal_x - position.x, 2) + pow(goal_y - position.y, 2))
		distance = goal_distance

		self.action_turtlebot(distance, goal_x, goal_y, goal_z)







	def action_turtlebot(self, distance, goal_x, goal_y, goal_z):

		last_rotation = 0
		linear_speed = 1
		angular_speed = 1
		move_cmd = Twist()
		r = rospy.Rate(10)

		while distance > 0.05:
			(position, rotation) = self.get_odom()
			x_start = position.x
			y_start = position.y
			path_angle = atan2(goal_y - y_start, goal_x- x_start)

			if path_angle < -pi/4 or path_angle > pi/4:
				if goal_y < 0 and y_start < goal_y:
					path_angle = -2*pi + path_angle
				elif goal_y >= 0 and y_start > goal_y:
					path_angle = 2*pi + path_angle
			if last_rotation > pi-0.1 and rotation <= 0:
				rotation = 2*pi + rotation
			elif last_rotation < -pi+0.1 and rotation > 0:
				rotation = -2*pi + rotation
			
			move_cmd.angular.z = angular_speed * path_angle-rotation

			distance = sqrt(pow((goal_x - x_start), 2) + pow((goal_y - y_start), 2))
			move_cmd.linear.x = min(linear_speed * distance, 0.1)

			if move_cmd.angular.z > 0:
				move_cmd.angular.z = min(move_cmd.angular.z, 1.5)
			else:
				move_cmd.angular.z = max(move_cmd.angular.z, -1.5)

			last_rotation = rotation
			self.cmd_vel.publish(move_cmd)
			r.sleep()
		(position, rotation) = self.get_odom()


		while abs(rotation - goal_z) > 0.05:
			(position, rotation) = self.get_odom()
			if goal_z >= 0:
				if rotation <= goal_z and rotation >= goal_z - pi:
					move_cmd.linear.x = 0.00
					move_cmd.angular.z = 0.5
				else:
					move_cmd.linear.x = 0.00
					move_cmd.angular.z = -0.5
			else:
				if rotation <= goal_z + pi and rotation > goal_z:
					move_cmd.linear.x = 0.00
					move_cmd.angular.z = -0.5
				else:
					move_cmd.linear.x = 0.00
					move_cmd.angular.z = 0.5
			self.cmd_vel.publish(move_cmd)
			r.sleep()

		
		rospy.loginfo("Stopping the robot...")
		self.cmd_vel.publish(Twist())






	def getkey(self):
		rospy.loginfo("let's choice function!!\n")	
		command_by_human = raw_input("command = ") 
		x = y = z = 0
		try:
			if command_by_human == 's':
				self.shutdown()
		
			elif command_by_human == '1':
				x, y, z = self.patrol_turtlebot()
				rospy.loginfo("x, y, z = {0}, {1}, {2}".format(x, y, z))
		
			elif command_by_human == '2':
				x, y, z = self.command_move()
				rospy.loginfo("x, y, z = {0}, {1}, {2}".format(x, y, z))

			elif command_by_human == '3':
				if self.marker_detect_flag == True:
					print("execute")
					x, y, z = self.marker_get_odom()
					print("x, y, z = {0}, {1}, {2}".format(x, y, z))

			elif command_by_human == 'x':
				sys.exit(1)

			else:
				rospy.loginfo("are you pressed another key??")
				pass				

			return x, y, z


		except KeyboardInterrupt:
			rospy.loginfo("shutdown program.")
			self.shutdown()

	#-------------------------------------------------------------------------
	



	def patrol_turtlebot(self):
		angle = 180
		x_dir = 1
		y_dir = 1		

		# random.random() value is 0.0 ~ 0.9999
		if random.random() < 0.5:
			angle = -180
			x_dir = -1
			y_dir = -1
		
		x, y, z = [float(random.random() * x_dir), float(random.random() * y_dir), float(random.random() * angle)]

		return x, y, z






	def command_move(self):
		x_, y_, z_ = raw_input("x | y | z( -180 <= z.angle <= 180 |\n").split()

		x, y, z = [float(x_), float(y_), float(z_)]
		
		return x, y, z 






	def get_marker(self, msg):
		n = len(msg.markers)

		if n == 0:
			self.marker_detect_flag = False

		else:
			self.id = msg.markers[0].id
			self.p  = msg.markers[0].pose
			#print("x = {0}, y = {1}".format(self.p.pose.position.x, self.p.pose.position.y))

			if self.p.pose.position.x != 0 or self.p.pose.position.y != 0: 			
				self.marker_detect_flag = True
			else:
				self.marker_detect_flag = False







	def marker_get_odom(self):
		marker_vector_x = []
		marker_vector_y = []
		sum_x = 0.0
		sum_y = 0.0
		
		for i in range(0, 10):
			marker_vector_x.append(float(self.p.pose.position.x))
			marker_vector_y.append(float(self.p.pose.position.y)) 			
			sum_x += float(self.p.pose.position.x)
			sum_y += float(self.p.pose.position.y)

		marker_vector = [float(sum_x / len(marker_vector_x)), float(sum_y / len(marker_vector_y)) ]			


		#tf.transformations.euler_from_quaternion(quaternion, axes='sxyz')
		marker_quaternion = [self.p.pose.orientation.w,
							self.p.pose.orientation.x,
							self.p.pose.orientation.y,
							self.p.pose.orientation.z]


		rotation = euler_from_quaternion(marker_quaternion)

		angular_z_deg = 180 + np.rad2deg(rotation[2])
		print("compare_anlge = {0}".format(angular_z_deg))


		adjust_x = 0.0
		adjust_y = 0.0
		adjust_angular = 0.0
		constant_x = 10.0
		constant_y = 1.0


		x = float((marker_vector[0] * constant_x - adjust_x))
		y = float((marker_vector[1] * constant_y - adjust_y))
		z_angular = (angular_z_deg - adjust_angular)


		try:
			check_flag = False
			if self.laserScan_data:
				self.laserScan_data.sort()
				temp_x = self.laserScan_data[0] - x 			

				if temp_x <= 0.02:  
					check_flag = True			
				else:
					check_flag = False


			if check_flag == False:
				x, y = 0.0

		except Exception as e:
				print("error description : {0}".format(e))

		return [x, y, z_angular]






	def get_scan(self, msg):
		try:
			for i in range(0, 5):
				if msg.ranges[i] != 0.0 and msg.ranges[i] < 3.5 and msg.ranges[i] > 0.12 and msg.intensities[i] > 500.0 :
					self.laserScan_data.append(msg.ranges[i])


				if msg.ranges[-i] != 0.0 and msg.ranges[-i] < 3.5 and msg.ranges[-i] > 0.12 and msg.intensities[-i] > 500.0:
					self.laserScan_data.append(msg.ranges[-i])

		except Exception as e:
			print("error description : {0}".format(e))


	#-------------------------------------------------------------------------



	def get_odom(self):
		try:
			(trans, rot) = self.tf_listener.lookupTransform(self.odom_frame, self.base_frame, rospy.Time(0))
			rotation = euler_from_quaternion(rot)

		except (tf.Exception, tf.ConnectivityException, tf.LookupException):
			rospy.loginfo("TF Exception")
			return

		return (Point(*trans), rotation[2])


	def shutdown(self):
		self.cmd_vel.publish(Twist())
		rospy.sleep(1)




if __name__ == '__main__':
    try:
        while not rospy.is_shutdown():
			print(msg)
			GotoPoint()

	rospy.spin()

    except Exception as e:
        rospy.loginfo("{0}.".format(e))

