import os
from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, SetEnvironmentVariable, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from nav2_common.launch import RewrittenYaml


def generate_launch_description():

    pkg_nav  = get_package_share_directory('mecanum_navigation')
    pkg_desc = get_package_share_directory('mechanum_description')
    pkg_loc  = get_package_share_directory('mecanum_localization')

    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart    = LaunchConfiguration('autostart')
    params_file  = LaunchConfiguration('params_file')
    map_file     = LaunchConfiguration('map')

    # ── lifecycle nodes Nav2 ──────────────────────────────────
    lifecycle_nodes = [
        'map_server',
        'amcl',
        'controller_server',
        'planner_server',
        'behavior_server',
        'bt_navigator',
        'waypoint_follower',
        'smoother_server',
        'velocity_smoother',
    ]

    # nav2_param.yaml avec use_sim_time/autostart/yaml_filename injectés
    configured_params = RewrittenYaml(
        source_file=params_file,
        root_key=None,
        param_rewrites={
            'use_sim_time': use_sim_time,
            'autostart':    autostart,
            'yaml_filename': map_file,
        },
        convert_types=True
    )

    # amcl.yaml avec use_sim_time injecté — AMCL a ses propres paramètres
    amcl_params = RewrittenYaml(
        source_file=os.path.join(pkg_loc, 'config', 'amcl.yaml'),
        root_key=None,
        param_rewrites={
            'use_sim_time': use_sim_time,
            'yaml_filename': map_file,
        },
        convert_types=True
    )

    return LaunchDescription([

        SetEnvironmentVariable('RCUTILS_LOGGING_BUFFERED_STREAM', '1'),

        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('autostart',    default_value='true'),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(pkg_nav, 'config', 'nav2_param.yaml'),
        ),
        DeclareLaunchArgument(
            'map',
            default_value=os.path.join(pkg_loc, 'map', 'map_3x3_mecanum.yaml'),
        ),

        # ── Gazebo + Robot ───────────────────────────────────
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_desc, 'launch', 'gazebo.launch.py')
            )
        ),

        # ── EKF — publie /odometry/filtered ──────────────────
        Node(
            package='robot_localization',
            executable='ekf_node',
            name='ekf_filter_node',
            output='screen',
            parameters=[
                os.path.join(pkg_loc, 'config', 'mecanum_localization.yaml'),
                {'use_sim_time': use_sim_time}
            ]
        ),

        # ── RViz2 ────────────────────────────────────────────
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=['-d', os.path.join(pkg_nav, 'config', 'nav2.rviz')],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'
        ),

        # ── Map Server ───────────────────────────────────────
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            output='screen',
            parameters=[configured_params]
        ),

        # ── AMCL — reçoit amcl.yaml (scan_topic, frames, OmniMotionModel...)
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            output='screen',
            parameters=[amcl_params, {'use_sim_time': use_sim_time}]
        ),

        # ── Nav2 Nodes ───────────────────────────────────────
        Node(
            package='nav2_controller',
            executable='controller_server',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_behaviors',
            executable='behavior_server',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_bt_navigator',
            executable='bt_navigator',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_waypoint_follower',
            executable='waypoint_follower',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_smoother',
            executable='smoother_server',
            output='screen',
            parameters=[configured_params],
        ),
        Node(
            package='nav2_velocity_smoother',
            executable='velocity_smoother',
            output='screen',
            parameters=[configured_params],
        ),

        # ── Lifecycle Manager ────────────────────────────────
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            output='screen',
            parameters=[
                {'use_sim_time': use_sim_time},
                {'autostart':    autostart},
                {'node_names':   lifecycle_nodes}
            ]
        ),
    ])