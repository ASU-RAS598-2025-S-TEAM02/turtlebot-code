from setuptools import find_packages, setup

package_name = 'predprey'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='ubuntu',
    maintainer_email='ubuntu@todo.todo',
    description='TODO: Package description',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'esp_rel_pos = predprey.esp32_location:main',
            'tag_move = predprey.move_to_tag:main'
            'aruco_location = predprey.aruco_pose_estimator:main',
        ],
    },
)
