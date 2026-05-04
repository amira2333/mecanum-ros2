from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
import os
from ament_index_python.packages import get_package_share_directory
from launch_ros.parameter_descriptions import ParameterValue
from launch.substitutions import Command, LaunchConfiguration
import xacro
def generate_launch_description():
    package_name = "mechanum_description"
    model_arg = DeclareLaunchArgument(name="model",
        default_value= os.path.join(get_package_share_directory("mechanum_description"), "urdf", "wpb_mani.urdf.xacro"),                          
        description="Model Path URDF FILE" 
        )
    
    use_sim_time_arg = DeclareLaunchArgument(
        name="use_sim_time",
        default_value="true",
        description="Use simulation time"
    )
    use_sim_time = LaunchConfiguration("use_sim_time")
    
    # robot_description = ParameterValue(Command(["xacro ", LaunchConfiguration("model")]), value_type= str)
    
    model_path = os.path.join(get_package_share_directory(package_name), "urdf", "robots/rosmaster_x3.urdf.xacro")
    # robot_description = ParameterValue(Command(["xacro ", model_path]), value_type=str)
    robot_description_content = xacro.process_file(model_path).toxml()
    
    robot_description = robot_description_content
    # Declare launch arguments
    # ic(robot_description)
    model_arg = DeclareLaunchArgument(name="model", default_value=model_path, description="Model Path URDF FILE")

    # Robot State Publisher
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[{"robot_description": robot_description}, {"use_sim_time": use_sim_time}]
    )
    joint_state_publisher_gui = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[
            {"use_sim_time": use_sim_time}
        ]
    )
    
    rviz_node = Node(
        package="rviz2",
        executable="rviz2",
        name="rviz2",
        output="screen",
        arguments=["-d", os.path.join(get_package_share_directory("mechanum_description"), "rviz", "mechanum_rviz.rviz")],
        parameters=[{"use_sim_time": use_sim_time}]
    )
    
    return LaunchDescription([
        model_arg,
        use_sim_time_arg,
        # robot_state_publisher, 
        joint_state_publisher_gui, 
        rviz_node
        ])

