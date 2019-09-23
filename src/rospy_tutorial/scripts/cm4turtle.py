#!/usr/bin/env python
# 위 첫 행은 이 스크립트 파일의 해석기의 위치를 지정하는 셔뱅(Shebang)이다. 파이썬으로 ROS 노드를 작성하는 
# 경우, 반드시 첫 행에 이 셔뱅(Shebang)을 적어 주어야만 한다.

import rospy                # roscpp 코드의 "#include <ros.h>"에 해당하는 구문
import geometry_msgs.msg    # ROS 메세지 중 geometry_msg 모듈 import
                            # roscpp 코드라면 "#include <geometry_msgs/Twist.h>"에 해당
def move_turtle():          # move_turtle() 함수 사용자 정의 시작
    
    # 노드명 "move_turtlesim" 노드 초기화. roscpp의 'ros::init(argc, argv, "move_turtlesim");'
    rospy.init_node("move_turtlesim")
    
    # 토픽명이 "turtle1/cmd_vel"이고, 토픽형식이 geometry_msgs.msg.Twist인 퍼블리셔 'pub' 선언
    pub = rospy.Publisher("turtle1/cmd_vel", geometry_msgs.msg.Twist, queue_size=10)
    
    # geometry_msgs 메세지 중 Twist 메세지 객체 "tw" 선언
    tw  = geometry_msgs.msg.Twist()
    
    # tw 메세지 객체의 맴버 중 "linear.x"를 0.25(m/sec)로, "angular.z"를 0.25(rad/sec)로 설정
    tw.linear.x = tw.angular.z = 0.25
    
    # tw 메세지 퍼블리쉬
    pub.publish(tw)

# 실행 중인 이 모듈의 __name__ 변수 값이 '__main__'이면 다음 내용 실행
if __name__ == '__main__': 
    try:
        # rospy가 종료되지 않았으면 반복할 루프. roscpp의 "while(ros::ok())"에 해당.
        while not rospy.is_shutdown():
            move_turtle()		# 앞 서 정의한 move_turtle()함수 호출
    
    except rospy.ROSInterruptException:
        print "Program terminated!"
