import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    config = os.path.join(
        get_package_share_directory('person_detection'), 'config', 'person_detection.yaml')
    image = LaunchConfiguration('image')

    return LaunchDescription([
        DeclareLaunchArgument('image', default_value='/odin1/image',
                              description='Raw sensor_msgs/Image topic to detect on'),
        DeclareLaunchArgument('detections', default_value='/person_detection/detections'),
        DeclareLaunchArgument('debug_image', default_value='/person_detection/debug_image'),
        DeclareLaunchArgument('model_path', default_value='yolox_tiny.onnx',
                              description='.onnx -> OpenCV (CPU), .engine -> TensorRT (GPU); '
                                          'bare file names are looked up in the models/ dir'),
        DeclareLaunchArgument('decompress', default_value='true',
                              description='Republish <image>/compressed as raw <image>'),

        # The bag only contains CompressedImage, so decode it to a raw Image first.
        Node(
            package='image_transport', executable='republish', name='image_decompressor',
            condition=IfCondition(LaunchConfiguration('decompress')),
            parameters=[{'in_transport': 'compressed', 'out_transport': 'raw'}],
            remappings=[('in/compressed', [image, '/compressed']), ('out', image)],
        ),
        Node(
            package='person_detection', executable='person_detector', name='person_detector',
            parameters=[config, {'model_path': LaunchConfiguration('model_path')}],
            remappings=[('image', image),
                        ('detections', LaunchConfiguration('detections')),
                        ('debug_image', LaunchConfiguration('debug_image'))],
            output='screen',
        ),
    ])
