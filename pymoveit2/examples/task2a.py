#!/usr/bin/python3

'''
Code to get all the frame names of the TF tree 
'''

import time
import yaml

import rclpy
import tf2_ros

frame_names = []

class TfFramesFinder(rclpy.node.Node):
    def __init__(self):
        super().__init__("tf2_frames_finder")
        self.get_logger().info("In class")

        self._tf_buffer = tf2_ros.buffer.Buffer()
        self._tf_listener = tf2_ros.transform_listener.TransformListener(self._tf_buffer, self)
        time.sleep(5.0)

    def get_all_frames(self):
        _frames_dict = yaml.safe_load(self._tf_buffer.all_frames_as_yaml())
        if _frames_dict:
            #self.get_logger().info(yaml.dump(_frames_dict))
            global frame_names
            for frame_name in _frames_dict.keys():
                frame_names.append(frame_name)
                #self.get_logger().info(frame_name)

        else:
            self.get_logger().warn("No frames collected")


def main():
    rclpy.init()
    node = TfFramesFinder()
    try:
        # Spin the node for 3 seconds.
        for _ in range(20):
            rclpy.spin_once(node)
            time.sleep(0.01)
        node.get_all_frames()
    except KeyboardInterrupt as e:
        print("k/b interrupted")
    global frame_names
    print(frame_names)
    rclpy.shutdown()
if __name__ == "__main__":
    main()
