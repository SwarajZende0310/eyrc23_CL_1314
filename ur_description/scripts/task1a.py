#!/usr/bin/env python3


'''
*****************************************************************************************
*
*        		===============================================
*           		    Cosmo Logistic (CL) Theme (eYRC 2023-24)
*        		===============================================
*
*  This script should be used to implement Task 1A of Cosmo Logistic (CL) Theme (eYRC 2023-24).
*
*  This software is made available on an "AS IS WHERE IS BASIS".
*  Licensee/end user indemnifies and will keep e-Yantra indemnified from
*  any and all claim(s) that emanate from the use of the Software or
*  breach of the terms of this agreement.
*
*****************************************************************************************
'''

# Team ID:          [ 1314 ]
# Author List:		[ Swaraj Zende, Vishal Ghige, Vipul Pardeshi, Vishal Singh ]
# Filename:		    task1a.py
# Functions:
#			        [ Comma separated list of functions in this file ]
# Nodes:		    Add your publishing and subscribing node
#                   Example:
#			        Publishing Topics  - [ /tf ]
#                   Subscribing Topics - [ /camera/aligned_depth_to_color/image_raw, /etc... ]


################### IMPORT MODULES #######################

import rclpy
import sys
import cv2
import math
import tf2_ros
import tf_transformations
import numpy as np
from rclpy.node import Node
from cv_bridge import CvBridge, CvBridgeError
import geometry_msgs.msg
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformException
from scipy.spatial.transform import Rotation as R
from sensor_msgs.msg import CompressedImage, Image

'''Used for debugging angles issue

roll = 360
pitch = 360
yaw = 360

def on_roll(value):
    global roll
    roll = value - 360

def on_pitch(value):
    global pitch
    pitch = value - 360

def on_yaw(value):
    global yaw
    yaw = value - 360
'''


##################### FUNCTION DEFINITIONS #######################

def calculate_rectangle_area(coordinates):
    '''
    Description:    Function to calculate area or detected aruco

    Args:
        coordinates (list):     coordinates of detected aruco (4 set of (x,y) coordinates)

    Returns:
        area        (float):    area of detected aruco
        width       (float):    width of detected aruco
    '''

    ############ Function VARIABLES ############

    # You can remove these variables after reading the instructions. These are just for sample.

    area = None
    width = None

    ############ ADD YOUR CODE HERE ############

    # INSTRUCTIONS & HELP : 
    #	->  Recevice coordiantes from 'detectMarkers' using cv2.aruco library 
    #       and use these coordinates to calculate area and width of aruco detected.
    #	->  Extract values from input set of 4 (x,y) coordinates 
    #       and formulate width and height of aruco detected to return 'area' and 'width'.

    ############################################

    # We recieve coordinates in the following order
    # Left top corner, Right top corner, Right bottom corner, Left Bottom corner
    # Calculate the marker area
    width  =  math.sqrt((coordinates[0][0][0]-coordinates[0][1][0])**2+(coordinates[0][0][1]-coordinates[0][1][1])**2)
    height =  math.sqrt((coordinates[0][0][0]-coordinates[0][3][0])**2+(coordinates[0][0][1]-coordinates[0][3][1])**2)

    area = height * width

    return area, width


def detect_aruco(image):
    '''
    Description:    Function to perform aruco detection and return each detail of aruco detected 
                    such as marker ID, distance, angle, width, center point location, etc.

    Args:
        image                   (Image):    Input image frame received from respective camera topic

    Returns:
        center_aruco_list       (list):     Center points of all aruco markers detected
        distance_from_rgb_list  (list):     Distance value of each aruco markers detected from RGB camera
        angle_aruco_list        (list):     Angle of all pose estimated for aruco marker
        width_aruco_list        (list):     Width of all detected aruco markers
        ids                     (list):     List of all aruco marker IDs detected in a single frame 
    '''

    ############ Function VARIABLES ############

    # ->  You can remove these variables if needed. These are just for suggestions to let you get started

    # Use this variable as a threshold value to detect aruco markers of certain size.
    # Ex: avoid markers/boxes placed far away from arm's reach position  
    aruco_area_threshold = 1500

    # The camera matrix is defined as per camera info loaded from the plugin used. 
    # You may get this from /camer_info topic when camera is spawned in gazebo.
    # Make sure you verify this matrix once if there are calibration issues.
    cam_mat = np.array([[931.1829833984375, 0.0, 640.0], [0.0, 931.1829833984375, 360.0], [0.0, 0.0, 1.0]])

    # The distortion matrix is currently set to 0. 
    # We will be using it during Stage 2 hardware as Intel Realsense Camera provides these camera info.
    dist_mat = np.array([0.0,0.0,0.0,0.0,0.0])

    # We are using 150x150 aruco marker size
    size_of_aruco_m = 0.15

    # You can remove these variables after reading the instructions. These are just for sample.
    center_aruco_list = []
    distance_from_rgb_list = []
    angle_aruco_list = []
    width_aruco_list = []
    ids = []

    height_aruco_list = []
    ############ ADD YOUR CODE HERE ############

    # INSTRUCTIONS & HELP : 

    #	->  Convert input BGR image to GRAYSCALE for aruco detection

    #   ->  Use these aruco parameters-
    #       ->  Dictionary: 4x4_50 (4x4 only until 50 aruco IDs)

    #   ->  Detect aruco marker in the image and store 'corners' and 'ids'
    #       ->  HINT: Handle cases for empty markers detection. 

    #   ->  Draw detected marker on the image frame which will be shown later

    #   ->  Loop over each marker ID detected in frame and calculate area using function defined above (calculate_rectangle_area(coordinates))

    #   ->  Remove tags which are far away from arm's reach positon based on some threshold defined

    #   ->  Calculate center points aruco list using math and distance from RGB camera using pose estimation of aruco marker
    #       ->  HINT: You may use numpy for center points and 'estimatePoseSingleMarkers' from cv2 aruco library for pose estimation

    #   ->  Draw frame axes from coordinates received using pose estimation
    #       ->  HINT: You may use 'cv2.drawFrameAxes'

    ############################################
    #covert input BGR to Grayscale
    grayscale_img=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)

    #Load the aruco dictionary
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()  # Marker detection parameters

    #Detecting aruco id and retrieving ids and corners
    corners,ids,rejectedImagePoints = cv2.aruco.detectMarkers(grayscale_img,aruco_dict,parameters=parameters)

    # Handle cases for empty markers detection
    # we can calculate the area of the marker and if area is less than the threshold area we pop the element from the dictionary
    corners,ids,width_aruco_list = nonEmptyMarkers(corners,ids,aruco_area_threshold)
    
    for i in range(len(ids)):
        # Draw a bounding box around each detected marker
        cv2.aruco.drawDetectedMarkers(image, corners)
    
    # Calculate Center points of aruco markers
    center_aruco_list = calculateCenter(corners)

    if ids is not None:
        for i in range(len(ids)):
            marker_id=ids[i][0]

            # Estimate the pose of the marker (distance, angle, and width)
            rvec, tvec, _ = cv2.aruco.estimatePoseSingleMarkers(corners[i], size_of_aruco_m, cam_mat, dist_mat)

            angle_aruco=rvec[0][0][2]
            distance_from_rgb = np.linalg.norm(tvec)

            angle_aruco_list.append(angle_aruco)
            distance_from_rgb_list.append(distance_from_rgb)

            # draw coordinate axes on detected marker 
            cv2.drawFrameAxes(image, cam_mat, dist_mat, rvec, tvec, size_of_aruco_m)

    return center_aruco_list, distance_from_rgb_list, angle_aruco_list, width_aruco_list, ids

def nonEmptyMarkers(allCorners,allIDs,threshold):
    """
    Description:    Function that returns non empty aruco markers which have area greater than threshold

    Args:
        allCorners                   (allCorners):    list of all detected corners
        allIDs                       (allIDs)    :    list of all corresponding IDs to corners
        threshold                    (threshold) :    minimum area to be considered as Non Empty Marker
        
    Returns:
        newCorners                   (newCorners):    list of corners of all non Empty aruco markers
        newIDs                       (newIDs)    :    list of IDs of all non Empty aruco markers
        width                        (width)     :    list of width of all non Empty aruco markers

    """
    #Stores non empty aruco markers
    newCorners = []
    newIDs = []
    width = []
    i=0

    for corner in allCorners:
        # Calculate the area of current marker
        area,widthi = calculate_rectangle_area(corner)
        i+=1
        #Check is area is greater than threshold 
        # if yes add to list
        if area >= threshold:
            newCorners.append(corner)
            newIDs.append(allIDs[i-1])
            width.append(widthi)

    return newCorners, newIDs, width  

def calculateCenter(corners):
    """
    Description:    Function that returns list of center points of aruco markers 

    Args:
        corners                  (corners):    list of corners of all non Empty aruco markers
        
    Returns:
        center                   (center):    list of centers of all non Empty aruco markers

    """
    center = []

    for corner in corners:
        centerX = (corner[0][0][0] + corner[0][1][0] + corner[0][2][0] + corner[0][3][0]) / 4
        centerY = (corner[0][0][1] + corner[0][1][1] + corner[0][2][1] + corner[0][3][1]) / 4
        center.append([int(centerX),int(centerY)])
    
    return center

##################### CLASS DEFINITION #######################

class aruco_tf(Node):
    '''
    ___CLASS___

    Description:    Class which servers purpose to define process for detecting aruco marker and publishing tf on pose estimated.
    '''

    def __init__(self):
        '''
        Description:    Initialization of class aruco_tf
                        All classes have a function called __init__(), which is always executed when the class is being initiated.
                        The __init__() function is called automatically every time the class is being used to create a new object.
                        You can find more on this topic here -> https://www.w3schools.com/python/python_classes.asp
        '''

        super().__init__('aruco_tf_publisher')                                          # registering node

        ############ Topic SUBSCRIPTIONS ############

        self.color_cam_sub = self.create_subscription(Image, '/camera/color/image_raw', self.colorimagecb, 10)
        self.depth_cam_sub = self.create_subscription(Image, '/camera/aligned_depth_to_color/image_raw', self.depthimagecb, 10)

        ############ Constructor VARIABLES/OBJECTS ############

        image_processing_rate = 0.2                                                     # rate of time to process image (seconds)
        self.bridge = CvBridge()                                                        # initialise CvBridge object for image conversion
        self.tf_buffer = tf2_ros.buffer.Buffer()                                        # buffer time used for listening transforms
        self.listener = tf2_ros.TransformListener(self.tf_buffer, self)
        self.br = tf2_ros.TransformBroadcaster(self)                                    # object as transform broadcaster to send transform wrt some frame_id
        self.timer = self.create_timer(image_processing_rate, self.process_image)       # creating a timer based function which gets called on every 0.2 seconds (as defined by 'image_processing_rate' variable)
        
        self.cv_image = None                                                            # colour raw image variable (from colorimagecb())
        self.depth_image = None                                                         # depth image variable (from depthimagecb())
        
        '''
        Code for Sliders
        cv2.namedWindow("Slider Example")
        global roll,pitch,yaw
        cv2.createTrackbar("roll", "Slider Example", roll, 720, on_roll)
        cv2.createTrackbar("pitch", "Slider Example", pitch, 720, on_pitch)
        cv2.createTrackbar("yaw", "Slider Example", yaw, 720, on_yaw)
        '''



    def depthimagecb(self, data):
        '''
        Description:    Callback function for aligned depth camera topic. 
                        Use this function to receive image depth data and convert to CV2 image

        Args:
            data (Image):    Input depth image frame received from aligned depth camera topic

        Returns:
        '''

        ############ ADD YOUR CODE HERE ############

        # INSTRUCTIONS & HELP : 

        #	->  Use data variable to convert ROS Image message to CV2 Image type

        #   ->  HINT: You may use CvBridge to do the same

        ############################################
        self.depth_image = self.bridge.imgmsg_to_cv2(data, "passthrough")


    def colorimagecb(self, data):
        '''
        Description:    Callback function for colour camera raw topic.
                        Use this function to receive raw image data and convert to CV2 image

        Args:
            data (Image):    Input coloured raw image frame received from image_raw camera topic

        Returns:
        '''

        ############ ADD YOUR CODE HERE ############

        # INSTRUCTIONS & HELP : 

        #	->  Use data variable to convert ROS Image message to CV2 Image type

        #   ->  HINT:   You may use CvBridge to do the same
        #               Check if you need any rotation or flipping image as input data maybe different than what you expect to be.
        #               You may use cv2 functions such as 'flip' and 'rotate' to do the same

        ############################################
        # Convert ROS Image message to CV2 Image type
        self.cv_image = self.bridge.imgmsg_to_cv2(data,"bgr8")


    def process_image(self):
        '''
        Description:    Timer function used to detect aruco markers and publish tf on estimated poses.

        Args:
        Returns:
        '''

        ############ Function VARIABLES ############

        # These are the variables defined from camera info topic such as image pixel size, focalX, focalY, etc.
        # Make sure you verify these variable values once. As it may affect your result.
        # You can find more on these variables here -> http://docs.ros.org/en/melodic/api/sensor_msgs/html/msg/CameraInfo.html
        
        sizeCamX = 1280
        sizeCamY = 720
        centerCamX = 640 
        centerCamY = 360
        focalX = 931.1829833984375
        focalY = 931.1829833984375
            

        ############ ADD YOUR CODE HERE ############

        # INSTRUCTIONS & HELP : 

        #	->  Get aruco center, distance from rgb, angle, width and ids list from 'detect_aruco_center' defined above

        #   ->  Loop over detected box ids received to calculate position and orientation transform to publish TF 

        #   ->  Use this equation to correct the input aruco angle received from cv2 aruco function 'estimatePoseSingleMarkers' here
        #       It's a correction formula- 
        #       angle_aruco = (0.788*angle_aruco) - ((angle_aruco**2)/3160)

        #   ->  Then calculate quaternions from roll pitch yaw (where, roll and pitch are 0 while yaw is corrected aruco_angle)

        #   ->  Use center_aruco_list to get realsense depth and log them down. (divide by 1000 to convert mm to m)

        #   ->  Use this formula to rectify x, y, z based on focal length, center value and size of image
        #       x = distance_from_rgb * (sizeCamX - cX - centerCamX) / focalX
        #       y = distance_from_rgb * (sizeCamY - cY - centerCamY) / focalY
        #       z = distance_from_rgb
        #       where, 
        #               cX, and cY from 'center_aruco_list'
        #               distance_from_rgb is depth of object calculated in previous step
        #               sizeCamX, sizeCamY, centerCamX, centerCamY, focalX and focalY are defined above

        #   ->  Now, mark the center points on image frame using cX and cY variables with help of 'cv2.cirle' function 

        #   ->  Here, till now you receive coordinates from camera_link to aruco marker center position. 
        #       So, publish this transform w.r.t. camera_link using Geometry Message - TransformStamped 
        #       so that we will collect it's position w.r.t base_link in next step.
        #       Use the following frame_id-
        #           frame_id = 'camera_link'
        #           child_frame_id = 'cam_<marker_id>'          Ex: cam_20, where 20 is aruco marker ID

        #   ->  Then finally lookup transform between base_link and obj frame to publish the TF
        #       You may use 'lookup_transform' function to pose of obj frame w.r.t base_link 

        #   ->  And now publish TF between object frame and base_link
        #       Use the following frame_id-
        #           frame_id = 'base_link'
        #           child_frame_id = 'obj_<marker_id>'          Ex: obj_20, where 20 is aruco marker ID

        #   ->  At last show cv2 image window having detected markers drawn and center points located using 'cv2.imshow' function.
        #       Refer MD book on portal for sample image -> https://portal.e-yantra.org/


        #   ->  NOTE:   The Z axis of TF should be pointing inside the box (Purpose of this will be known in task 1B)
        #               Also, auto eval script will be judging angular difference aswell. So, make sure that Z axis is inside the box (Refer sample images on Portal - MD book)

        ############################################
        if(self.cv_image is None or self.depth_image is None):
            print('Cannot read image')
            return
        
        # Get aruco center, distance from rgb, angle, width and ids list from 'detect_aruco_center' defined above
        aruco_centers, distances_from_rgb, angles, widths, ids = detect_aruco(self.cv_image)

        # Loop over detected box ids received to calculate position and orientation transform to publish TF
        for i, id in enumerate(ids):
            id=id[0]

            # Correct the input aruco angle received from cv2 aruco function 'estimatePoseSingleMarkers' here
            angle_aruco = (0.788*angles[i]) - ((angles[i]**2)/3160)

            # Matching the axis of boxes with camera as it is different in RVix
            roll = 77.0
            pitch = 0.0 
            yaw = 90.0 
            print("CORRECTED ANGLE IS "+str(math.degrees(angle_aruco))+" for id = "+str(id))

            rotation = R.from_euler('xyz', [roll,pitch,yaw], degrees=True).as_quat()

            # Giving yaw required to every box 
            quaternion = R.from_quat(rotation)
            quaternion = quaternion * R.from_euler('y',-angle_aruco,degrees=False) #Giving rotation in y axis as we have rotated all the axis around z
            quaternion = quaternion.as_quat()

            # Use center_aruco_list to get realsense depth and log them down. (divide by 1000 to convert mm to m)
            distance_from_rgb = self.depth_image[aruco_centers[i][1]][aruco_centers[i][0]] / 1000

            # Use this formula to rectify x, y, z based on focal length, center value and size of image
            y = distance_from_rgb * (sizeCamX - aruco_centers[i][0] - centerCamX) / focalX
            z = distance_from_rgb * (sizeCamY - aruco_centers[i][1] - centerCamY) / focalY
            x = distance_from_rgb

            # Now, mark the center points on image frame using cX and cY variables with help of 'cv2.cirle' function
            cv2.circle(self.cv_image, (aruco_centers[i][0], aruco_centers[i][1]), 3, (0, 0, 255), -1)

            # Publish the transform from the camera link to the ArUco marker center position using the 'GeometryMessage.TransformStamped' message.
            # Set the 'frame_id' to 'camera_link' and the 'child_frame_id' to 'cam_<marker_id>`, where '<marker_id>' is the ArUco marker ID.
            t = TransformStamped()

            t.header.stamp = self.get_clock().now().to_msg()
            t.header.frame_id = 'camera_link'
            t.child_frame_id = 'cam_'+str(id)
            t.transform.translation.x = x
            t.transform.translation.y = y
            t.transform.translation.z = z
            t.transform.rotation.x = quaternion[0]
            t.transform.rotation.y = quaternion[1]
            t.transform.rotation.z = quaternion[2]
            t.transform.rotation.w = quaternion[3]
     
            self.br.sendTransform(t)

            # Lookup the transform between the base link and the object frame using the 'lookup_transform()` function.
            to_frame_rel = 'base_link'
            from_frame_rel = 'cam_'+str(id)
            try:
                t = self.tf_buffer.lookup_transform( to_frame_rel, from_frame_rel, rclpy.time.Time())       
                # self.get_logger().info(f'Successfully received data!')
            except TransformException as e:
                self.get_logger().info(f'Could not transform {to_frame_rel} to {from_frame_rel}: {e}')
                return
            
            # Publish the TF between the object frame and the base link using the `GeometryMessage.TransformStamped` message.
            # Set the 'frame_id' to 'base_link' and the 'child_frame_id' to 'obj_<marker_id>`, where '<marker_id>' is the ArUco marker ID.
            
            transform_stamped = TransformStamped()
            transform_stamped.header.stamp = self.get_clock().now().to_msg()
            transform_stamped.header.frame_id = 'base_link'
            transform_stamped.child_frame_id = 'obj_' + str(id)
            transform_stamped.transform = t.transform
            self.br.sendTransform(transform_stamped)

        # print()
        # cv2.imshow("Image", self.cv_image)
        # cv2.waitKey(1)



##################### FUNCTION DEFINITION #######################
def main():
    '''
    Description:    Main function which creates a ROS node and spin around for the aruco_tf class to perform it's task
    '''

    rclpy.init(args=sys.argv)                                       # initialisation

    node = rclpy.create_node('aruco_tf_process')                    # creating ROS node

    node.get_logger().info('Node created: Aruco tf process')        # logging information

    aruco_tf_class = aruco_tf()                                     # creating a new object for class 'aruco_tf'

    rclpy.spin(aruco_tf_class)                                      # spining on the object to make it alive in ROS 2 DDS

    aruco_tf_class.destroy_node()                                   # destroy node after spin ends

    rclpy.shutdown()                                                # shutdown process


if __name__ == '__main__':
    '''
    Description:    If the python interpreter is running that module (the source file) as the main program, 
                    it sets the special __name__ variable to have a value “__main__”. 
                    If this file is being imported from another module, __name__ will be set to the module’s name.
                    You can find more on this here -> https://www.geeksforgeeks.org/what-does-the-if-__name__-__main__-do/
    '''

    main()
