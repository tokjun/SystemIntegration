import os
from posixpath import join
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription, actions, conditions
from launch.substitutions.launch_configuration import LaunchConfiguration
from launch.actions import IncludeLaunchDescription
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.actions import DeclareLaunchArgument
from launch.substitutions import PythonExpression

pkg_stage_control = get_package_share_directory('stage_control')
pkg_needle_pose_sensors = get_package_share_directory('needle_pose_sensors')
pkg_needle_path_control = get_package_share_directory('needle_path_control')
pkg_trajcontrol = get_package_share_directory('trajcontrol')
pkg_hyperion_interrogator = get_package_share_directory('hyperion_interrogator')
pkg_needle_shape_publisher = get_package_share_directory('needle_shape_publisher')

def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument(
            "sim_level",
            default_value="1",
            description="Simulation level: 0 - Emulation only, " +
                "1 - virtual only, 2 - hardware only, 3 - virtual and hardware"
                
        ),
        DeclareLaunchArgument(
            "sim_level_trajcontrol",
            default_value="1",
            description="Simulation level: 1 - demo.launch, " +
                "2 - virtual"
                ),
        DeclareLaunchArgument(
            "sim_level_needle_sensing",
            default_value="1",
            description="Simulation level: 1 - hyperrion demo, " +
                "2 - real sensors"
                
        ),
        DeclareLaunchArgument( 'needleParamFile',
                                             description="The shape-sensing needle parameter json file." ),

        actions.LogInfo(msg=["Launching with sim level: ", LaunchConfiguration('sim_level')]),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_stage_control, 'launch', 'stage_control_launch.py')
                )
            , launch_arguments={'sim_level': LaunchConfiguration('sim_level')}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_needle_pose_sensors, 'launch', 'needle_pose_sensors_launch.py')
                )
            ),
	IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_trajcontrol, 'launch', 'virtual_nodes.launch.py')
                ),
                condition=conditions.IfCondition(
               PythonExpression([LaunchConfiguration('sim_level_trajcontrol'), " == 2"]))
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_trajcontrol, 'launch', 'demo.launch.py')
                ),
                condition=conditions.IfCondition(
               PythonExpression([LaunchConfiguration('sim_level_trajcontrol'), " == 1"]))
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_hyperion_interrogator, 'hyperion_demo.launch.py')
                ),
                condition=conditions.IfCondition(
               PythonExpression([LaunchConfiguration('sim_level_needle_sensing'), " == 1"]))
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_hyperion_interrogator, 'hyperion_streamer.launch.py')
                ),
                condition=conditions.IfCondition(
               PythonExpression([LaunchConfiguration('sim_level_needle_sensing'), " == 2"]))
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_needle_shape_publisher, 'sensorized_shapesensing_needle_decomposed.launch.py')
               ),
                launch_arguments = {'needleParamFile': LaunchConfiguration( 'needleParamFile')}.items()
            ),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(pkg_needle_path_control, 'launch', 'needle_position_launch.py')
                ),
            condition=conditions.IfCondition(
               PythonExpression([LaunchConfiguration('sim_level'), " == 1 or ", 
               LaunchConfiguration('sim_level'), " == 3"]))
            ),
        Node(
            package="adaptive_guide",
            executable="stage_state_builder",
            name="stage_state_builder_node",
            output="screen"
        )
        

    ])
