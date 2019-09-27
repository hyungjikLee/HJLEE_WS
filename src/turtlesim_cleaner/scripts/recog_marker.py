#!/usr/bin/env python

import rospy
from geometry_msgs.msg import PoseStamped, Twist
from ar_track_alvar_msgs.msg import AlvarMarkers


class RecogMarker():

  def __init__(self):
    rospy.init_node("recog_maker")
    rospy.Subscriber("ar_pose_marker", AlvarMarkers, self.get_marker)
    
    self.p  = PoseStamped()
    self.id = -1
			
  def get_marker(self, msg):
  
    n = len(msg.markers)

    if n == 0:
	    return

    else:
      rospy.loginfo("  id = %d" %msg.markers[0].id)
      
      self.id = msg.markers[0].id
      self.p  = msg.markers[0].pose

  def print_info(self):
      while not rospy.is_shutdown():
          print("-------------------------------------")
          print("id = %d" %self.id)
          print("-------------------------------------")
          print("position.x   = %f" %(self.p.pose.position.x))
          print("position.y   = %f" %(self.p.pose.position.y))
          print("position.z   = %f" %(self.p.pose.position.z))
          print("-------------------------------------")
          print("orientaion.x = %f" %(self.p.pose.orientation.x))
          print("orientaion.y = %f" %(self.p.pose.orientation.y))
          print("orientaion.z = %f" %(self.p.pose.orientation.z))
          print("orientaion.w = %f" %(self.p.pose.orientation.w))
	  
  
if __name__ == '__main__':
	try:
		marker = RecogMarker()
		marker.print_info()
		rospy.spin()
	except rospy.ROSInterruptException: pass
