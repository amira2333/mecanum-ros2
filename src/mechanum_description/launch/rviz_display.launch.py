from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
import os
from ament_index_python.packages import get_package_share_directory
from launch.substitutions import LaunchConfiguration
import xacro

def generate_launch_description():
    package_name = "mechanum_description"

    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description="Use simulation time"
    )
    use_sim_time = LaunchConfiguration("use_sim_time")

    model_path = os.path.join(
        get_package_share_directory(package_name),
        "urdf", "robots", "rosmaster_x3.urdf.xacro"
    )
    robot_description_content = xacro.process_file(model_path).toxml()

    model_arg = DeclareLaunchArgument(
        name="model",
        default_value=model_path,
        description="Model Path URDF FILE"
    )

    # OBLIGATOIRE — publie /robot_description et les TF
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {"robot_description": robot_description_content},
            {"use_sim_time": use_sim_time}
        ]
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[{"use_sim_time": use_sim_time}]
    )

    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(
            get_package_share_directory(package_name),
            "rviz", "mechanum_rviz.rviz"
        )],
        parameters=[{"use_sim_time": use_sim_time}]
    )

    return LaunchDescription([
        model_arg,
        use_sim_time_arg,
        robot_state_publisher,   # ← décommenté
        joint_state_publisher,
        rviz_node,
    ])