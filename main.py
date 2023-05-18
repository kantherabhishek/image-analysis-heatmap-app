import cv2
import numpy as np
import os
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.graphics.texture import Texture


class HeatmapApp(App):
    def build(self):
        layout = GridLayout(cols=1)

        # File chooser to select the folder
        file_chooser = FileChooserListView()
        layout.add_widget(file_chooser)

        # Button to start the analysis
        button = Button(text="Start Analysis", on_press=lambda _: self.analyze_images(file_chooser.path))
        layout.add_widget(button)

        # Image widget for displaying the heatmap
        self.heatmap_image = Image()
        layout.add_widget(self.heatmap_image)

        # Image widget for displaying the image with bounding boxes
        self.bounding_boxes_image = Image()
        layout.add_widget(self.bounding_boxes_image)

        return layout

    def analyze_images(self, folder_path):
        # Get a list of all image files in the folder
        image_files = [f for f in os.listdir(folder_path) if
                       os.path.isfile(os.path.join(folder_path, f)) and f.lower().endswith(('.jpg', '.jpeg', '.png'))]

        heatmap_images = []  # To store the heatmap images

        # Analyze each image in the folder
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            print("Analyzing:", image_path)

            # Load the infrared image
            image = cv2.imread(image_path)

            # Convert the image to grayscale
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Apply a colormap to the grayscale image
            heatmap = cv2.applyColorMap(gray, cv2.COLORMAP_JET)

            # Add the heatmap image to the list
            heatmap_images.append(heatmap)

            # Detect people and draw bounding boxes
            self.detect_people(image)

        # Combine and save all heatmaps
        combined_heatmap = np.hstack(heatmap_images)
        cv2.imwrite("combined_heatmap.jpg", combined_heatmap)

        # Display the heatmap image in the GUI
        self.display_image(self.heatmap_image, np.flipud(combined_heatmap))

    def detect_people(self, image):
        # Convert the image to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Apply a threshold to create a binary image
        _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

        # Find contours of the binary image
        contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw bounding boxes around the detected contours
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Display the image with bounding boxes in the GUI
        self.display_image(self.bounding_boxes_image, np.flipud(image))

    def display_image(self, image_widget, image):
        # Convert the image to RGB format
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Get the image dimensions
        height, width, _ = image_rgb.shape

        # Create a texture with the image data
        texture = Texture.create(size=(width, height))
        texture.blit_buffer(image_rgb.flatten(), colorfmt='rgb', bufferfmt='ubyte')

        # Assign the texture to the image widget
        image_widget.texture = texture

    def run(self):
        super(HeatmapApp, self).run()


if __name__ == '__main__':
    HeatmapApp().run()
