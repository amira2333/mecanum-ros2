import os
import xacro
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (DeclareLaunchArgument, IncludeLaunchDescription,
                             TimerAction, ExecuteProcess)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition
from launch_ros.actions import Node


def generate_launch_description():

    package_name = "mechanum_description"
    pkg_share    = get_package_share_directory(package_name)

    world_model = os.path.join(pkg_share, "worlds", "map_3x3.world")
    # CORRECTION : chemin vers le bon fichier URDF de votre robot
    model_path  = os.path.join(pkg_share, "urdf", "robots", "rosmaster_x3.urdf.xacro")

    # Traitement xacro au lancement (plus fiable que Command(['xacro', ...]))
    robot_description_content = xacro.process_file(model_path).toxml()

    use_sim_time = LaunchConfiguration("use_sim_time")

    # ── Arguments ────────────────────────────────────────────
    world_arg        = DeclareLaunchArgument("world",        default_value=world_model)
    use_sim_time_arg = DeclareLaunchArgument("use_sim_time", default_value="true")
    x_arg            = DeclareLaunchArgument("x_pose",       default_value="0.0")
    y_arg            = DeclareLaunchArgument("y_pose",       default_value="0.0")
    z_arg            = DeclareLaunchArgument("z_pose",       default_value="0.10")

    # ── Gazebo (server + client) ──────────────────────────────
    gazebo_server = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'),
                         'launch', 'gzserver.launch.py')
        ),
        launch_arguments={
            'world':        LaunchConfiguration("world"),
            'use_sim_time': use_sim_time
        }.items()
    )

    gazebo_client = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory('gazebo_ros'),
                         'launch', 'gzclient.launch.py')
        )
    )

    # ── Robot State Publisher ─────────────────────────────────
    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        output="screen",
        parameters=[
            {"robot_description": robot_description_content},
            {"use_sim_time": use_sim_time}
        ]
    )

    # ── Joint State Publisher ─────────────────────────────────
    # Ecoute /joint_states publié par le plugin Gazebo (roues)
    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        name="joint_state_publisher",
        output="screen",
        parameters=[{
            "use_sim_time": use_sim_time,
            "source_list": ["/joint_states"],
            "rate": 30.0
        }]
    )

    # ── Spawn robot ───────────────────────────────────────────
    # TimerAction 3s : laisse Gazebo démarrer avant de spawner le robot
    spawn_entity = TimerAction(
        period=3.0,
        actions=[
            ExecuteProcess(
                cmd=[
                    'ros2', 'run', 'gazebo_ros', 'spawn_entity.py',
                    '-topic', 'robot_description',
                    '-entity', 'mecanum_robot',
                    '-x', LaunchConfiguration('x_pose'),
                    '-y', LaunchConfiguration('y_pose'),
                    '-z', LaunchConfiguration('z_pose'),
                ],
                output='screen'
            )
        ]
    )

    return LaunchDescription([
        world_arg,
        use_sim_time_arg,
        x_arg, y_arg, z_arg,
        gazebo_server,
        gazebo_client,
        robot_state_publisher,
        joint_state_publisher,
        spawn_entity,
    ])