import subprocess
import pkg_resources

def check_and_install(package_name):
    try:
        # Check if the package is installed
        pkg_resources.get_distribution(package_name)
    except pkg_resources.DistributionNotFound:
        # Install the package if not installed
        subprocess.check_call(["sudo", "pip3", "install", package_name])

# Check and install required packages
required_packages = ["requests", "Adafruit_GPIO", "Adafruit_SSD1306", "Pillow", "schedule"]
for package in required_packages:
    check_and_install(package)

import time
import socket
import requests
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import schedule

class Monitor:
    def __init__(self):
        # Raspberry Pi pin configuration:
        RST = None
        DC = 23
        SPI_PORT = 0
        SPI_DEVICE = 0

        # Initialize the display based on your configuration.
        self.disp = Adafruit_SSD1306.SSD1306_128_32(rst=RST)

        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        # Create blank image for drawing.
        width = self.disp.width
        height = self.disp.height
        self.image = Image.new('1', (width, height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Define some constants for text positioning.
        self.padding = -2
        self.top = self.padding
        self.bottom = height - self.padding
        self.x = 0

        # Load default font.
        self.font = ImageFont.load_default()

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Doesn't matter if the following IP is unreachable. We just use it to establish a socket.
            s.connect(("10.254.254.254", 1))
            IP = s.getsockname()[0]
            s.close()
        except:
            IP = "Error"
        return IP

    def get_public_ip(self):
        try:
            response = requests.get("https://httpbin.org/ip")
            return response.json()["origin"]
        except:
            return "Error"

    def update_display(self):
        # Draw a black filled box to clear the image.
        self.draw.rectangle((0, 0, self.disp.width, self.disp.height), outline=0, fill=0)

        local_ip = self.get_local_ip()
        public_ip = self.get_public_ip()

        self.draw.text((self.x, self.top), "Local IP: " + local_ip, font=self.font, fill=255)
        # draw space
        self.draw.text((self.x, self.top+8), "                ", font=self.font, fill=255)
        self.draw.text((self.x, self.top+16), "Public IP: " + public_ip, font=self.font, fill=255)

        # Display image.
        self.disp.image(self.image)
        self.disp.display()

    def run(self):
        while True:
            self.update_display()
            time.sleep(10)  # Update every 10 seconds.

class Perma:
    def __init__(self):
        self.url = 'http://personal-projects.a2hosted.com/static-ip'

    def send(self):
        requests.get(self.url)
        print("Request sent to static-ip")

    def runner(self):
        schedule.every().hour.do(self.send)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == "__main__":
    monitor = Monitor()
    perma = Perma()
    monitor.run()
    perma.runner()
    