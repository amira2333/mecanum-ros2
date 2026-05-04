import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml

def generate_launch_description():
    our_package = "mecanum_localization"
    param_path = os.path.join(get_package_share_directory(our_package), "config", "amcl.yaml")
    map_path = os.path.join(get_package_share_directory(our_package),'map', 'map_3x3_mecanum.yaml')
  
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value= "true")
    autostart_arg = DeclareLaunchArgument("autostart", default_value="true")
    params_file_arg = DeclareLaunchArgument('params_file', default_value=param_path)
    map_file_arg = DeclareLaunchArgument('map', default_value=map_path)
    
    map_file = LaunchConfiguration('map')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration("autostart")
    nav2_param = LaunchConfiguration("params_file")
    
    lifecylce_nodes = ['map_server', "amcl"]

    param_substitutions = {
        'use_sim_time': use_sim_time,
        'yaml_filename': map_file}
    
    configured_params = RewrittenYaml(
        source_file=nav2_param,
        # root_key=namespace,
        param_rewrites=param_substitutions,
        convert_types=True)
    
    map_server_node = Node(
        package="nav2_map_server",
        executable="map_server",
        output="screen",
        parameters=[{"yaml_filename": map_file}, {"use_sim_time": use_sim_time}]
    )
    
    nav2_lifecyle_node = Node(
        package="nav2_lifecycle_manager",
        executable="lifecycle_manager",
        output="screen",
        parameters=[{"use_sim_time": use_sim_time}, {"autostart": autostart}, {"node_names": lifecylce_nodes}]
    )    

    nav2_amcl = Node(
        package="nav2_amcl",
        executable="amcl",
        output ="screen",
        parameters=[configured_params]
    )
    
    ekf_localization = Node(
        package="robot_localization",
        executable="ekf_node",
        name="ekf_filter_node",
        output="screen",
        parameters=[os.path.join(get_package_share_directory(our_package), "config", "mecanum_localization.yaml")],
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        autostart_arg,
        params_file_arg,
        map_file_arg,
        ekf_localization,
        nav2_lifecyle_node,
        nav2_amcl,
        map_server_node
    ])