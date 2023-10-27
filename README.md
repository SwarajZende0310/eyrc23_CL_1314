# Cosmo-Logistic-eYRC-2023-24

## Team ID :: 1314

## Theme Introduction
The “Cosmo Logistic” theme of eYRC 2023-24 is set in a warehouse used for inter-planet logistics from a space station. A robotic arm and mobile robot collaborate to sort and prepare packages to be transported to different planets. In this theme, teams will develop an algorithm for sorting packages autonomously with the help of a robotic arm and mobile robot shown in the figure. Teams will learn to navigate this mobile robot with the help of SLAM (simultaneous localization and mapping) method in a warehouse, detect and localise the packages placed on racks, and manipulate the robotic arm to pick them.

## Tasks
### __Task 1__
> [___Task 1A (Object Pose Estimation)___ __::__](/Task%201/Task1A/task1a.py)

__Locating Aruco in the world with respect to arm__

Subtasks::
1. Detecting and Locating Aruco markers using OpenCV. Calculating the Yaw angle to be published using Rotational Vector
2. Publishing Transform using TF2 library between 'camera_link' and 'cam_<marker_id>'
3. Looking for transform between 'base_link' and 'cam_<marker_id>' (as 'camera_link' and 'base_link' are connected in TF tree)
4. Publishing a tranform of 'obj_<marker_id>' with respect to 'base_link'

```sh
$ ros2 launch ur_description ur5_gazebo_launch.py
```
```sh
$ ros2 launch ur_description spawn_ur5_launch.py
```
```sh
$ ros2 run ur_description task1a.py
```

---

> [___Task 1B (Arm Manipulation using Moveit)___ __::__](/Task%201/Task1B/task1b.py)

__Manipulating Robotic Arm using Moveit framework__

Subtasks::
1. Using joint goals to achieve particular position
2. Using moveit_servo to achieve the box's position in a feedback loop
3. Using TF Listener to estimate the pose of end effector (i.e. gripper ) and calculating the unit vector to provide to moveit servo linear velocities
4. Repeat the task multiple hard coded positions 
```sh
$ ros2 launch ur_description ur5_gazebo_launch.py
```
```sh
$ ros2 launch ur5_moveit spawn_ur5_launch_moveit.launch.py
```
```sh
$ ros2 service call /servo_node/start_servo std_srvs/srv/Trigger {} # Enables Servoing
$ ros2 run pymoveit2 task1b.py
```
---

> [___Task 1C (Navigation)___ __::__](/Task%201/Task1C/nav2_cmd_task1c.py)

__Navigation with ROS2 Navigation Stack (Nav2)__

Subtasks::
1. Mapping the warehouse using teleop twist and saving the generated map using slam_toolbox
2. Using Simple Commander API to various positions 
3. Tuning the parameters in nav2_param.yaml to set the tolerance in position and orientation 
4. Marking a Avoiding Zone in a map

```sh
$ ros2 launch ebot_description ebot_gazebo_launch.py
```
```sh
$ ros2 launch ebot_nav2 ebot_bringup_launch.py
```
```sh
$ ros2 run ebot_nav2 task1c.py
```

---
---
---


### __Task 2__
> [___Task 2A (Manipulation with vision)___ __::__](/Task%202/Task2A/task2a.py)

__Motion planning of robotic arm with vision__

Subtasks::
1. Getting the transform generated in Task1A to get the Transform of randomly spawned Aruco boxes
2. Determining the pre pose of ur5 arm based on the position of box 
3. Using joint goals to achieve pre position for picking the box
4. Using moveit_servo to achieve the box's position in a feedback loop
5. Activating the magnetic gripper using ros2 service call
6. Going to drop position adding offset to drop position so that boxes dont collide
7. Deactivate the gripper and drop the box on the table

```sh
$ ros2 launch ur_description ur5_gazebo_launch.py
```
```sh
$ ros2 launch ur5_moveit spawn_ur5_launch_moveit.launch.py
```
```sh
$ ros2 run ur_description task1a.py
```
```sh
$ ros2 service call /servo_node/start_servo std_srvs/srv/Trigger {} # Enables Servoing
$ ros2 run pymoveit2 task2a.py
```

[Video Link](https://www.youtube.com/watch?v=V2NQAFl0xxk)
