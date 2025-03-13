import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String

class BlobFollower(Node):
    def __init__(self):
        super().__init__('blob_follower')

        # Subscriber to the blob detection topic
        blob_topic = "rpi_05/blob_details"  
        self.subscription = self.create_subscription(
            String, 
            blob_topic, 
            self.blob_callback, 
            10
        )

        # Publisher to TurtleBot's velocity command topic
        cmd_vel_topic = "c3_05/cmd_vel"  
        self.publisher_ = self.create_publisher(Twist, cmd_vel_topic, 10)

    def blob_callback(self, msg):
        # Extract blob data (assuming red > green > blue priority)
        blobs = self.parse_blob_message(msg.data)

        if not blobs:
            self.get_logger().info("No blobs detected.")
            return

        # Take the largest red blob (or the largest available blob)
        target_blob = blobs[0]
        blob_x, blob_y, blob_size = target_blob['center'][0], target_blob['center'][1], target_blob['size']

        twist = Twist()

        # Normalize X position (-1 to 1 based on image width)
        img_width = 640  # Adjust this based on camera resolution
        normalized_x = (blob_x - img_width / 2) / (img_width / 2)

        # Movement logic based on blob position
        if normalized_x < -0.1:  # Blob is left
            twist.angular.z = 0.5  # Turn left
        elif normalized_x > 0.1:  # Blob is right
            twist.angular.z = -0.5  # Turn right
        else:
            twist.angular.z = 0.0  # Centered

        # Move forward or backward based on size (distance proxy)
        if blob_size < 1500:  # Blob is far
            twist.linear.x = 0.2
        elif blob_size > 5000:  # Blob is too close
            twist.linear.x = -0.2
        else:
            twist.linear.x = 0.0  # Stop

        # Publish velocity command to the correct topic
        self.publisher_.publish(twist)
        self.get_logger().info(f'Following blob at X: {blob_x}, Size: {blob_size} -> Vel: {twist.linear.x}, {twist.angular.z}')

    def parse_blob_message(self, data):
        """ Parses the blob details string and returns a list of blobs sorted by priority (red > green > blue). """
        blobs = []
        if not data:
            return blobs

        blob_entries = data.split(';')
        for entry in blob_entries:
            if not entry:
                continue
            try:
                color, size, x, y = entry.split(',')
                blobs.append({
                    'color': color,
                    'size': int(size),
                    'center': (int(x), int(y))
                })
            except ValueError:
                self.get_logger().warn(f"Invalid blob data format: {entry}")

        # Sort by color priority (red > green > blue) and size (largest first)
        blobs.sort(key=lambda obj: (['red', 'green', 'blue'].index(obj['color']), -obj['size']))
        return blobs

def main(args=None):
    rclpy.init(args=args)
    node = BlobFollower()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
