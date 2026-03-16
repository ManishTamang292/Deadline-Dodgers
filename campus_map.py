import customtkinter as ctk
from tkinter import Canvas
from PIL import Image, ImageTk
import math


class CampusMap(ctk.CTkFrame):

    def __init__(self, parent, checkin_callback=None):
        super().__init__(parent)

        self.checkin_callback = checkin_callback

        # Title
        ctk.CTkLabel(
            self,
            text="Campus Map Navigation",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=10)

        # Canvas for map
        self.canvas = Canvas(self, width=700, height=450, bg="black", highlightthickness=0)
        self.canvas.pack()

        # Load map image
        image = Image.open("campus_map.png")
        image = image.resize((700, 450))

        self.map_photo = ImageTk.PhotoImage(image)

        self.canvas.create_image(0, 0, anchor="nw", image=self.map_photo)

        # Campus locations
        self.locations = {
            "Library": (200, 120),
            "Gym": (420, 200),
            "Student Union": (300, 350)
        }

        # Draw building markers
        for name, (x, y) in self.locations.items():

            self.canvas.create_oval(
                x - 10, y - 10,
                x + 10, y + 10,
                fill="#ff4b4b",
                outline="white",
                width=2
            )

            self.canvas.create_text(
                x,
                y - 15,
                text=name,
                fill="white"
            )

        # User marker
        self.user_marker = None

        # Map click event
        self.canvas.bind("<Button-1>", self.user_clicked)

    # --------------------------------
    # User clicked on map
    # --------------------------------
    def user_clicked(self, event):

        x = event.x
        y = event.y

        # Remove previous user marker
        if self.user_marker:
            self.canvas.delete(self.user_marker)

        # Draw user position
        self.user_marker = self.canvas.create_oval(
            x - 6,
            y - 6,
            x + 6,
            y + 6,
            fill="blue"
        )

        # Check nearest building
        nearest_location, distance = self.find_nearest_location(x, y)

        if nearest_location and distance < 60:

            if self.checkin_callback:
                self.checkin_callback(nearest_location)

    # --------------------------------
    # Find nearest campus location
    # --------------------------------
    def find_nearest_location(self, x, y):

        nearest_name = None
        nearest_distance = float("inf")

        for name, (lx, ly) in self.locations.items():

            dist = math.sqrt((x - lx) ** 2 + (y - ly) ** 2)

            if dist < nearest_distance:
                nearest_distance = dist
                nearest_name = name

        return nearest_name, nearest_distance