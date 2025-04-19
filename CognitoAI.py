from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivymd.app import MDApp
from kivymd.toast import toast
from kivymd.uix.tab import MDTabsBase
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.datatables import MDDataTable
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.card import MDCard
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.clock import Clock
from plyer import filechooser
from kivy.graphics.texture import Texture
from datetime import date
import cv2
import face_recognition
import numpy as np
import mysql.connector
import os
from datetime import datetime, timedelta
import seaborn as sns
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for Matplotlib
import matplotlib.pyplot as plt
from io import BytesIO
from kivy.core.image import Image as CoreImage
import pandas as pd
from kivymd.uix.label import MDLabel
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.pickers import MDDatePicker
from kivymd.uix.button import MDRaisedButton, MDFlatButton, MDIconButton
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.screen import MDScreen

class MainScreen(MDScreen):
    pass


# Initialize Database Connection
def get_db_connection():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="0000",  # Replace with your MySQL password
            database="cognitoai"
        )
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

# Create necessary auxiliary functions to handle the existing database structure

def verify_database_consistency():
    """
    Verify that the database tables match expected structure and if not, 
    make necessary adjustments to work with existing structure.
    """
    db = get_db_connection()
    if not db:
        return False
    try:
        cursor = db.cursor()
        # Check tables exist
        cursor.execute("SHOW TABLES")
        tables = [table[0].lower() for table in cursor.fetchall()]
        
        print(f"Available tables: {tables}")
        
        # Check student table structure
        if 'student_info' in tables:
            cursor.execute("DESCRIBE student_info")
            columns = {column[0].lower(): column for column in cursor.fetchall()}
            print(f"student_info columns: {columns.keys()}")
            
            # Check if face_id column exists in student_info
            if 'face_id' not in columns:
                print("Adding face_id column to student_info table")
                cursor.execute("ALTER TABLE student_info ADD COLUMN face_id BLOB")
                db.commit()
                
        # Check attendance table structure
        if 'attendance' in tables:
            cursor.execute("DESCRIBE attendance")
            columns = {column[0].lower(): column for column in cursor.fetchall()}
            print(f"attendance columns: {columns.keys()}")
            
            # Check if status field is present (in our schema it's 'attendance')
            # We'll handle this in our SQL queries
            
        return True
    except mysql.connector.Error as err:
        print(f"Error verifying database: {err}")
        return False
    finally:
        cursor.close()
        db.close()

# Load Known Faces from the existing database structure
def load_known_faces():
    known_face_encodings = []
    known_names = []
    known_roll_nos = []
    db = get_db_connection()
    if not db:
        return [], [], []
    try:
        cursor = db.cursor()
        cursor.execute("SELECT roll_no, name, face_id FROM student_info WHERE face_id IS NOT NULL")
        for roll_no, name, face_encoding_blob in cursor.fetchall():
            if face_encoding_blob:
                try:
                    # Convert BLOB to numpy array
                    encoding = np.frombuffer(face_encoding_blob, dtype=np.float64)
                    if encoding.size > 0:
                        known_face_encodings.append(encoding)
                        known_names.append(name)
                        known_roll_nos.append(str(roll_no))  # Convert to string for consistency
                except Exception as e:
                    print(f"Error parsing face encoding for {name}: {e}")
    except mysql.connector.Error as err:
        print(f"Error loading faces: {err}")
    finally:
        cursor.close()
        db.close()
    return known_face_encodings, known_names, known_roll_nos

# KV Design String
KV = """
# ScrenManager:
MainScreen:
    # id: screen_manager

<MainScreen>:
    name: "main"
    
    MDBoxLayout:
        orientation: "horizontal"
        
        # Sidebar Navigation
        MDNavigationDrawer:
            id: nav_drawer
            type: "modal"
            radius: (0, 16, 16, 0)
            width: "280dp"
            
            MDBoxLayout:
                orientation: "vertical"
                padding: "8dp"
                spacing: "8dp"
                
                # App Logo and Title
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "120dp"
                    padding: "16dp"
                    
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "12dp"
                        adaptive_height: True
                        
                        MDIcon:
                            icon: "face-recognition"
                            font_size: "48sp"
                            theme_text_color: "Primary"
                            pos_hint: {"center_y": 0.5}
                        
                        MDLabel:
                            text: "CognitoAI"
                            font_style: "H5"
                            theme_text_color: "Primary"
                            size_hint_y: None
                            height: self.texture_size[1]
                            pos_hint: {"center_y": 0.5}
                    
                    MDLabel:
                        text: "Face Recognition ERP System"
                        theme_text_color: "Secondary"
                        font_style: "Caption"
                
                MDSeparator:
                    height: "1dp"
                
                # Navigation Items
                ScrollView:
                    MDList:
                        OneLineIconListItem:
                            text: "Face Recognition"
                            on_release: app.switch_screen("face_recognition")
                            IconLeftWidget:
                                icon: "face-recognition"
                                theme_text_color: "Primary"
                        
                        OneLineIconListItem:
                            text: "Dashboard"
                            on_release: app.switch_screen("dashboard")
                            IconLeftWidget:
                                icon: "chart-bar"
                                theme_text_color: "Primary"
                        
                        OneLineIconListItem:
                            text: "Student Records"
                            on_release: app.switch_screen("students")
                            IconLeftWidget:
                                icon: "account-group"
                                theme_text_color: "Primary"
                        
                        OneLineIconListItem:
                            text: "Reports"
                            on_release: app.switch_screen("reports")
                            IconLeftWidget:
                                icon: "file-chart"
                                theme_text_color: "Primary"
                        
                        OneLineIconListItem:
                            text: "Settings"
                            on_release: app.switch_screen("settings")
                            IconLeftWidget:
                                icon: "cog"
                                theme_text_color: "Primary"
                
                MDSeparator:
                    height: "1dp"
                
                # User Profile/Theme Toggle
                MDBoxLayout:
                    orientation: "vertical"
                    size_hint_y: None
                    height: "100dp"
                    padding: "16dp"
                    
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "12dp"
                        
                        MDIconButton:
                            icon: "theme-light-dark"
                            on_release: app.toggle_theme()
                        
                        MDLabel:
                            text: "Toggle Theme"
                            theme_text_color: "Secondary"
                    
                    MDBoxLayout:
                        orientation: "horizontal"
                        spacing: "12dp"
                        
                        MDIconButton:
                            icon: "information"
                            on_release: app.show_about()
                        
                        MDLabel:
                            text: "About CognitoAI"
                            theme_text_color: "Secondary"
        
        # Main Content Area
        MDBoxLayout:
            orientation: "vertical"
            
            # Top App Bar
            MDTopAppBar:
                title: "CognitoAI - Face Recognition"
                left_action_items: [["menu", lambda x: app.toggle_nav_drawer()]]
                right_action_items: [["account", lambda x: app.show_user_menu()]]
            
            # Content Screens - Using ScreenManager for different sections
            ScreenManager:
                id: screen_manager
                
                # Face Recognition Screen
                Screen:
                    name: "face_recognition"
                    
                    MDBoxLayout:
                        orientation: "vertical"
                        padding: "16dp"
                        spacing: "16dp"
                        
                        # Camera View Card
                        MDCard:
                            orientation: "vertical"
                            size_hint_y: 0.6
                            padding: "8dp"
                            elevation: 1
                            radius: [10, 10, 10, 10]
                            
                            MDLabel:
                                text: "Camera Feed"
                                size_hint_y: None
                                height: "30dp"
                                halign: "center"
                                theme_text_color: "Secondary"
                            
                            MDSeparator:
                                height: "1dp"
                            
                            MDBoxLayout:
                                id: camera_layout
                                padding: "8dp"
                                
                                Image:
                                    id: camera_feed
                                    allow_stretch: True
                                    keep_ratio: True
                        
                        # Controls Card
                        MDCard:
                            orientation: "vertical"
                            size_hint_y: 0.4
                            padding: "16dp"
                            elevation: 1
                            radius: [10, 10, 10, 10]
                            
                            MDLabel:
                                text: "Face Recognition Controls"
                                size_hint_y: None
                                height: "30dp"
                                halign: "center"
                                theme_text_color: "Secondary"
                            
                            MDSeparator:
                                height: "1dp"
                            
                            # Action Buttons Grid
                            MDGridLayout:
                                cols: 2
                                spacing: "16dp"
                                padding: "16dp"
                                
                                # Button 1 - Start Camera
                                MDRaisedButton:
                                    text: "Start Camera"
                                    icon: "camera"
                                    size_hint_x: 1
                                    on_release: app.start_camera()
                                
                                # Button 2 - Recognize Faces
                                MDRaisedButton:
                                    text: "Recognize Faces"
                                    icon: "face-recognition"
                                    size_hint_x: 1
                                    on_release: app.recognize_faces()
                                
                                # Button 3 - Mark Attendance
                                MDRaisedButton:
                                    text: "Mark Attendance"
                                    icon: "check-circle"
                                    size_hint_x: 1
                                    md_bg_color: app.theme_cls.accent_color
                                    on_release: app.recognize_faces()
                                
                                # Button 4 - Store New Face
                                MDRaisedButton:
                                    text: "Store New Face"
                                    icon: "account-plus"
                                    size_hint_x: 1
                                    md_bg_color: app.theme_cls.accent_color
                                    on_release: app.open_store_face_dialog()
                            
                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint_y: None
                                height: "50dp"
                                padding: "16dp"
                                
                                # Upload Group Photo Button
                                MDRaisedButton:
                                    text: "Upload Group Photo"
                                    icon: "image-multiple"
                                    size_hint_x: 1
                                    on_release: app.upload_group_photo()
                
                # Dashboard Screen
                Screen:
                    name: "dashboard"
                    on_enter: app.on_dashboard_enter()

                    MDBoxLayout:
                        orientation: "vertical"

                        MDBoxLayout:
                            id: debug_id_marker
                            orientation: "vertical"

                        MDBoxLayout:
                            orientation: "vertical"
                            padding: "16dp"
                            spacing: "16dp"

                            # Dashboard Header
                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint_y: None
                                height: "60dp"
                                spacing: "16dp"

                                MDTextField:
                                    id: roll_no_filter
                                    hint_text: "Filter by Roll No"
                                    helper_text: "Enter student roll number"
                                    helper_text_mode: "on_focus"
                                    icon_right: "magnify"
                                    on_text_validate: app.filter_dashboard()

                                MDTextField:
                                    id: date_range_label
                                    hint_text: "Date Range"
                                    readonly: True
                                    icon_right: "calendar"
                                    on_focus: app.show_date_picker() if self.focus else None

                            # Stats Cards
                            MDBoxLayout:
                                orientation: "horizontal"
                                size_hint_y: None
                                height: "100dp"
                                spacing: "16dp"

                                # Card 1
                                MDCard:
                                    orientation: "vertical"
                                    padding: "16dp"
                                    elevation: 1
                                    radius: [10, 10, 10, 10]

                                    MDIcon:
                                        icon: "account-group"
                                        halign: "center"
                                        font_size: "24sp"
                                        theme_text_color: "Primary"

                                    MDLabel:
                                        id: total_students
                                        text: "0"
                                        halign: "center"
                                        font_style: "H5"

                                    MDLabel:
                                        text: "Total Students"
                                        halign: "center"
                                        theme_text_color: "Secondary"
                                        font_style: "Caption"

                                # Card 2
                                MDCard:
                                    orientation: "vertical"
                                    padding: "16dp"
                                    elevation: 1
                                    radius: [10, 10, 10, 10]

                                    MDIcon:
                                        icon: "clipboard-text"
                                        halign: "center"
                                        font_size: "24sp"
                                        theme_text_color: "Primary"

                                    MDLabel:
                                        id: total_records
                                        text: "0"
                                        halign: "center"
                                        font_style: "H5"

                                    MDLabel:
                                        text: "Total Records"
                                        halign: "center"
                                        theme_text_color: "Secondary"
                                        font_style: "Caption"

                                # Card 3
                                MDCard:
                                    orientation: "vertical"
                                    padding: "16dp"
                                    elevation: 1
                                    radius: [10, 10, 10, 10]

                                    MDIcon:
                                        icon: "chart-arc"
                                        halign: "center"
                                        font_size: "24sp"
                                        theme_text_color: "Primary"

                                    MDLabel:
                                        id: attendance_rate
                                        text: "0%"
                                        halign: "center"
                                        font_style: "H5"

                                    MDLabel:
                                        text: "Attendance Rate"
                                        halign: "center"
                                        theme_text_color: "Secondary"
                                        font_style: "Caption"

                            # Graphs and Charts
                            ScrollView:
                                do_scroll_x: False
                                do_scroll_y: True

                                MDBoxLayout:
                                    id: graphs_layout
                                    orientation: "vertical"
                                    adaptive_height: True
                                    size_hint_x: 1
                                    spacing: "16dp"

                                    MDCard:
                                        orientation: "vertical"
                                        size_hint_y: None
                                        height: "300dp"
                                        padding: "16dp"
                                        elevation: 1
                                        radius: [10, 10, 10, 10]

                                        MDLabel:
                                            text: "Daily Attendance Chart"
                                            halign: "center"
                                            size_hint_y: None
                                            height: "30dp"

                                        MDBoxLayout:
                                            id: attendance_chart

                
                # Additional Screens (Student Records, Reports, Settings)
                # Add similar structure for the other screens
"""

# Define Tabs
class Tab1(MDBoxLayout, MDTabsBase):
    pass

class Tab2(MDBoxLayout, MDTabsBase):
    pass

class MainScreen(Screen):
    pass

class FaceRecognitionApp(MDApp):
    
    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"
        self.screen_manager = Builder.load_string(KV)
        self.capture = None
        self.recognized_faces = []
        self.start_date = None
        self.end_date = None
        self.dialog = None
        self.camera_feed_widget = None  # Initialize to None
        
        sns.set_theme(style="whitegrid", palette="muted")
        
        # Wait longer before attempting to find the widget - 2 seconds
        Clock.schedule_once(self.store_camera_widget_reference, 2)
        
        self.db_config = {
            "host": "localhost",
            "user": "root",
            "password": "0000",
            "database": "cognitoai"
        }
        
        # Verify database structure
        verify_database_consistency()
        
        # Load known faces from the database
        self.known_face_encodings, self.known_names, self.known_roll_nos = load_known_faces()
        print(f"Loaded {len(self.known_face_encodings)} face encodings from database")
        
        return self.screen_manager
        return MainScreen()
    
    def on_dashboard_enter(self):
        try:
            # main_screen = self.screen_manager.get_screen("main")
            main_screen = self.screen_manager
            print("✅ Got main screen")
            
            inner_sm = main_screen.ids.screen_manager
            print("✅ Got inner screen manager:", inner_sm)

            dashboard_screen = inner_sm.get_screen("dashboard")
            print("✅ Got dashboard screen")

            print("✅ dashboard_screen.ids keys:", dashboard_screen.ids.keys())
            
        except Exception as e:
            print("❌ Error loading dashboard:", e)
            self.show_error_dialog(f"Error loading dashboard: {e}")



    def toggle_theme(self):
        current = self.theme_cls.theme_style
        self.theme_cls.theme_style = "Dark" if current == "Light" else "Light"

    def toggle_nav_drawer(self):
        try:
            nav_drawer = self.screen_manager.ids.nav_drawer
            nav_drawer.set_state("toggle")
        except Exception as e:
            print(f"❌ Error toggling nav drawer: {e}")


    # def switch_screen(self, screen_name):
    #     """Switch to the specified screen in the screen manager"""
    #     # Close the navigation drawer
    #     nav_drawer = self.screen_manager.get_screen('main').ids.nav_drawer
    #     nav_drawer.set_state("close")
        
    #     # Switch to the selected screen
    #     screen_manager = self.screen_manager.get_screen('main').ids.screen_manager
    #     screen_manager.current = screen_name
        
    #     # Update the app bar title - THIS IS LIKELY CAUSING THE ERROR
    #     # Fix by checking if top_app_bar exists in ids
    #     main_screen = self.screen_manager.get_screen('main')
    #     if hasattr(main_screen.ids, 'top_app_bar'):
    #         main_screen.ids.top_app_bar.title = f"CognitoAI - {screen_name.replace('_', ' ').title()}"
    def switch_screen(self, screen_name):
        try:
            main_screen = self.screen_manager
            nav_drawer = main_screen.ids.nav_drawer
            nav_drawer.set_state("close")

            screen_manager = main_screen.ids.screen_manager
            screen_manager.current = screen_name

            if screen_name == "dashboard":
                self.load_attendance_dashboard()

            # Update app bar
            top_bar = next((c for c in main_screen.walk() if isinstance(c, MDTopAppBar)), None)
            if top_bar:
                top_bar.title = f"CognitoAI - {screen_name.replace('_', ' ').title()}"

        except Exception as e:
            print(f"Error in switch_screen: {e}")




    def show_about(self):
        """Show about dialog"""
        about_dialog = MDDialog(
            title="About CognitoAI",
            text="CognitoAI is a Face Recognition ERP System designed for automated attendance tracking and student management.",
            buttons=[
                MDFlatButton(text="Close", on_press=lambda x: about_dialog.dismiss())
            ]
        )
        about_dialog.open()

    def on_tab_switch(self, instance_tabs, instance_tab, instance_tab_label, tab_text):
        if tab_text == "ERP Dashboard":
            self.load_attendance_dashboard()

    def on_stop(self):
        """Release resources when app stops"""
        if self.capture:
            self.capture.release()
            self.capture = None
        Clock.unschedule(self.update_camera)

    def start_camera(self):
        """Start Camera Feed"""
        print("Starting camera...")
        print(f"Camera feed widget exists: {hasattr(self, 'camera_feed_widget') and self.camera_feed_widget is not None}")
        
        if not hasattr(self, 'camera_feed_widget') or self.camera_feed_widget is None:
            # Try once more to find the widget
            print("Attempting emergency widget search...")
            found = False
            
            # Direct search for any Image widget that could work
            for widget in self.screen_manager.walk():
                if isinstance(widget, Image):
                    print(f"Found Image widget with id: {getattr(widget, 'id', 'No ID')}")
                    self.camera_feed_widget = widget
                    found = True
                    break
            
            if not found:
                self.show_error_dialog("Camera widget not initialized. Please try again in a moment.")
                return
        
        # Setup the camera
        if self.capture:
            self.capture.release()
        
        self.capture = cv2.VideoCapture(0)
        if not self.capture.isOpened():
            print("Error: Could not open camera")
            self.show_error_dialog("Could not open camera. Please check your camera connection.")
            self.capture = None
            return
        
        print("Camera opened successfully! Scheduling updates...")
        Clock.schedule_interval(self.update_camera, 1.0 / 30.0)

    def store_camera_widget_reference(self, *args): #debugging
        """Find and store reference to the camera feed widget using a deeper search"""
        # print("Attempting to find camera_feed widget...")
        
        # Print the entire widget tree for debugging
        # print("Widget tree:")
        for widget in self.screen_manager.walk():
            if hasattr(widget, 'id') and widget.id:
                print(f"Widget: {widget.__class__.__name__}, ID: {widget.id}")
        
        try:
            # Try to trace the exact path based on your KV structure
            # main_screen = self.screen_manager.get_screen('main')
            main_screen = self.screen_manager  # Already the MainScreen

            inner_screen_manager = None
            
            # Find the inner ScreenManager
            for child in main_screen.walk():
                if isinstance(child, ScreenManager) and hasattr(child, 'id') and child.id == 'screen_manager':
                    inner_screen_manager = child
                    break
            
            if inner_screen_manager:
                # Find the face_recognition screen
                face_recognition_screen = inner_screen_manager.get_screen('face_recognition')
                
                # Find the camera_feed Image widget
                for child in face_recognition_screen.walk():
                    if isinstance(child, Image) and hasattr(child, 'id') and child.id == 'camera_feed':
                        self.camera_feed_widget = child
                        # print("✅ Camera feed widget found and stored!")
                        return
            
            # print("❌ Camera feed widget NOT found. Scheduling another attempt...")
            # If not found, schedule another attempt
            Clock.schedule_once(self.store_camera_widget_reference, 1)
        except Exception as e:
            print(f"Error finding camera feed widget: {e}")
            # Schedule another attempt
            Clock.schedule_once(self.store_camera_widget_reference, 1)

    def update_camera(self, dt):
        """Update the Camera Frame"""
        if not hasattr(self, 'camera_feed_widget') or self.camera_feed_widget is None:
            # Try to find the camera feed widget
            try:
                main_screen = self.screen_manager.get_screen('main')
                if hasattr(main_screen.ids, 'screen_manager'):
                    inner_screen_manager = main_screen.ids.screen_manager
                    face_recognition_screen = inner_screen_manager.get_screen('face_recognition')
                    for child in face_recognition_screen.walk():
                        if isinstance(child, Image) and hasattr(child, 'id') and child.id == 'camera_feed':
                            self.camera_feed_widget = child
                            break
            except Exception as e:
                print(f"Error finding camera feed widget: {e}")
                return
                
        if self.capture and self.capture.isOpened():
            ret, frame = self.capture.read()
            if ret:
                frame = cv2.flip(frame, 0)  # Flip for Kivy's coordinate system
                frame = cv2.flip(frame, 1)  # Mirror image
                buffer = frame.tobytes()
                texture = Texture.create(size=(frame.shape[1], frame.shape[0]), colorfmt='bgr')
                texture.blit_buffer(buffer, colorfmt='bgr', bufferfmt='ubyte')
                
                # Apply texture to camera feed widget
                if self.camera_feed_widget:
                    self.camera_feed_widget.texture = texture

    def recognize_faces(self):
        """Recognize Faces in Camera"""
        # Try to find camera feed widget if not already set
        """Recognize Faces in Camera"""
        if not hasattr(self, 'capture') or self.capture is None or not self.capture.isOpened():
            self.show_error_dialog("Please start the camera first before recognizing faces")
            return
        
    # Rest of your method...
        if not self.capture or not self.capture.isOpened():
            self.show_error_dialog("Error: Camera not initialized")
            return
        ret, frame = self.capture.read()
        if not ret:
            self.show_error_dialog("Error: Unable to capture frame")
            return

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        self.recognized_faces = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name, roll_no = "Unknown", "N/A"
            if True in matches:
                # matched_idx = np.argmin(face_recognition.face_distance(self.known_face_encodings, face_encoding))
                # name, roll_no = self.known_names[matched_idx], self.known_roll_nos[matched_idx]
                distances = face_recognition.face_distance(self.known_face_encodings, face_encoding) #ye waala line add kiya hai
                matched_idx = np.argmin(distances) #ye waala line add kiya hai
                confidence = (1 - distances[matched_idx]) * 100 #ye waala line add kiya hai
                name = f"{self.known_names[matched_idx]} ({confidence:.1f}%)" #ye waala line add kiya hai
                roll_no = self.known_roll_nos[matched_idx] #ye waala line add kiya hai
            self.recognized_faces.append((roll_no, name))
        
        # Display results in app
        # self.show_recognition_results(self.recognized_faces)
        # DEBUG MODE: Ask for confirmation before marking attendance
        if self.recognized_faces:
            names_list = "\n".join([f"{name} (Roll No: {roll_no})" for roll_no, name in self.recognized_faces])
            dialog = MDDialog(
                title="Confirm Attendance Marking",
                text=f"The following students were recognized:\n\n{names_list}\n\nDo you want to mark them present?",
                buttons=[
                    MDFlatButton(text="Cancel", on_press=lambda x: dialog.dismiss()),
                    MDRaisedButton(
                        text="Mark Present",
                        on_press=lambda x: (self.mark_attendance(), dialog.dismiss())
                    )
                ]
            )
            dialog.open()
        else:
            toast("No recognizable faces found.")

    def show_user_menu(self):
        # Implement user account options
        pass

    def mark_attendance(self):
        db = None
        cursor = None
        try:
            db = mysql.connector.connect(**self.db_config)
            cursor = db.cursor()

            current_date = date.today().strftime('%Y-%m-%d')
            marked_students = []

            # recognized_rolls = [int(roll_no) for roll_no, _ in self.recognized_faces if roll_no != "N/A"]
            recognized_rolls = [str(roll_no) for roll_no, _ in self.recognized_faces if roll_no != "N/A"]

            # Get all registered students
            cursor.execute("SELECT roll_no, name FROM student_info")
            all_students = cursor.fetchall()

            for student_roll, student_name in all_students:
                # Check if attendance for today already exists
                cursor.execute(
                    "SELECT * FROM attendance WHERE roll_no = %s AND date = %s",
                    (student_roll, current_date)
                )
                existing = cursor.fetchone()

                # if student_roll in recognized_rolls:
                if str(student_roll) in recognized_rolls:
                    # Mark Present
                    if existing:
                        cursor.execute(
                            "UPDATE attendance SET attendance = 'P' WHERE roll_no = %s AND date = %s",
                            (student_roll, current_date)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO attendance (roll_no, date, attendance) VALUES (%s, %s, 'P')",
                            (student_roll, current_date)
                        )
                    marked_students.append(f"{student_name} (Roll No: {student_roll}) - Present")
                else:
                    # Mark Absent only if not already marked
                    if not existing:
                        cursor.execute(
                            "INSERT INTO attendance (roll_no, date, attendance) VALUES (%s, %s, 'A')",
                            (student_roll, current_date)
                        )
                        marked_students.append(f"{student_name} (Roll No: {student_roll}) - Absent")

            db.commit()

            if marked_students:
                message = "Attendance marked:\n\n" + "\n".join(marked_students)
                self.show_success_dialog(message)
            else:
                self.show_info_dialog("No valid students to mark attendance.")

            cursor.close()
            db.close()

        except mysql.connector.Error as err:
            if db is not None and db.is_connected():
                cursor.close()
                db.close()
            self.show_error_dialog(f"MySQL Error: {str(err)}")
        except Exception as e:
            if db is not None and db.is_connected():
                cursor.close()
                db.close()
            self.show_error_dialog(f"Error: {str(e)}")


    def mark_attendance_from_image(self, image_path):
        """Marks attendance from a group photo"""
        try:
            image = cv2.imread(image_path)
            if image is None:
                self.show_error_dialog("Unable to load image.")
                return

            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image)
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)

            recognized_rolls = set()

            for face_encoding in face_encodings:
                matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)

                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    recognized_rolls.add(self.known_roll_nos[best_match_index])

            if not recognized_rolls:
                self.show_info_dialog("No recognizable faces found in the uploaded image.")
                return

            # Mark attendance (same logic as existing `mark_attendance`)
            db = get_db_connection()
            cursor = db.cursor()
            current_date = date.today().strftime('%Y-%m-%d')
            marked_students = []

            cursor.execute("SELECT roll_no, name FROM student_info")
            all_students = cursor.fetchall()

            for student_roll, student_name in all_students:
                cursor.execute(
                    "SELECT * FROM attendance WHERE roll_no = %s AND date = %s",
                    (student_roll, current_date)
                )
                existing = cursor.fetchone()

                if str(student_roll) in recognized_rolls:
                    if existing:
                        cursor.execute(
                            "UPDATE attendance SET attendance = 'P' WHERE roll_no = %s AND date = %s",
                            (student_roll, current_date)
                        )
                    else:
                        cursor.execute(
                            "INSERT INTO attendance (roll_no, date, attendance) VALUES (%s, %s, 'P')",
                            (student_roll, current_date)
                        )
                    marked_students.append(f"{student_name} (Roll No: {student_roll}) - Present")
                else:
                    if not existing:
                        cursor.execute(
                            "INSERT INTO attendance (roll_no, date, attendance) VALUES (%s, %s, 'A')",
                            (student_roll, current_date)
                        )
                        marked_students.append(f"{student_name} (Roll No: {student_roll}) - Absent")

            db.commit()
            cursor.close()
            db.close()

            message = "Attendance marked from image:\n\n" + "\n".join(marked_students)
            self.show_success_dialog(message)

        except Exception as e:
            self.show_error_dialog(f"Error processing image: {str(e)}")

    def upload_group_photo(self):
        filechooser.open_file(on_selection=self._on_group_photo_selected,
                            filters=[("Image Files", "*.jpg", "*.jpeg", "*.png")])
        
    def _on_group_photo_selected(self, selection):
        if selection:
            self.mark_attendance_from_image(selection[0])

    def open_store_face_dialog(self):
        """Open Dialog to Store or Update Face Data"""
        content = MDBoxLayout(
            orientation="vertical",
            spacing="20dp",
            size_hint_y=None,
            height="300dp",  # Increased height
            padding="20dp"   # Added padding
        )
        
        # Add a spacer at the top
        content.add_widget(MDBoxLayout(size_hint_y=None, height="10dp"))
        
        roll_no_field = MDTextField(hint_text="Enter Roll No")
        roll_no_field.id = "roll_no"
        content.add_widget(roll_no_field)
        
        name_field = MDTextField(hint_text="Enter Name")
        name_field.id = "name"
        content.add_widget(name_field)
        
        course_field = MDTextField(hint_text="Enter Course")
        course_field.id = "course"
        content.add_widget(course_field)
        
        dob_field = MDTextField(hint_text="DOB (YYYY-MM-DD)")
        dob_field.id = "dob"
        content.add_widget(dob_field)
        
        self.dialog = MDDialog(
            title="Store Face Data",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Cancel", on_press=lambda x: self.dialog.dismiss()),
                MDFlatButton(text="Load from Image", on_press=self.open_file_chooser),
                MDRaisedButton(text="Capture from Camera", on_press=self.capture_face_data)
            ]
        )
        self.dialog.open()
        
        # Store references to fields for easier access
        self.dialog.roll_no_field = roll_no_field
        self.dialog.name_field = name_field
        self.dialog.course_field = course_field
        self.dialog.dob_field = dob_field
        
        # Bind to roll_no changes
        roll_no_field.bind(text=self.on_roll_no_change)
        # toast("Face stored successfully!") #toast



    def store_face_encoding(self, roll_no, name, course, dob, face_encoding):
        """Store face encoding in database"""
        # Convert numpy array to bytes for storage
        face_encoding_bytes = face_encoding.tobytes()
        
        db = get_db_connection()
        if not db:
            return
        try:
            cursor = db.cursor()
            
            # Check if student already exists
            cursor.execute("SELECT * FROM student_info WHERE roll_no = %s", (roll_no,))
            existing_student = cursor.fetchone()
            
            if existing_student:
                # Update existing student
                cursor.execute(
                    "UPDATE student_info SET name = %s, course = %s, dob = %s, face_id = %s WHERE roll_no = %s",
                    (name, course, dob, face_encoding_bytes, roll_no)
                )
                self.show_success_dialog(f"Student data updated successfully for {name} (Roll No: {roll_no})")
                toast(f"🔄 {name} updated successfully!")

            else:
                # Insert new student
                cursor.execute(
                    "INSERT INTO student_info (roll_no, name, course, dob, face_id) VALUES (%s, %s, %s, %s, %s)",
                    (roll_no, name, course, dob, face_encoding_bytes)
                )
                self.show_success_dialog(f"New student added: {name} (Roll No: {roll_no})")
                toast(f"{name} added successfully!")

            
            db.commit()
            
            # Update local face data cache
            self.known_face_encodings, self.known_names, self.known_roll_nos = load_known_faces()
        except mysql.connector.Error as err:
            self.show_error_dialog(f"Database error: {err}")
        finally:
            cursor.close()
            db.close()
            if self.dialog:
                self.dialog.dismiss()
                self.dialog = None

    def show_error_dialog(self, message):
        """Show error dialog with message"""
        dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDFlatButton(text="OK", on_press=lambda x: dialog.dismiss())]
        )
        dialog.open()

    def show_success_dialog(self, message):
        """Show success dialog with message"""
        dialog = MDDialog(
            title="Success",
            text=message,
            buttons=[
                MDFlatButton(text="OK", on_press=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()

    def on_roll_no_change(self, instance, value):
        """Load student data when roll number is entered"""
        if not value.strip():
            return
            
        try:
            roll_no = int(value)
            db = get_db_connection()
            if not db:
                return
                
            cursor = db.cursor()
            cursor.execute("SELECT name, course, dob FROM student_info WHERE roll_no = %s", (roll_no,))
            student = cursor.fetchone()
            cursor.close()
            db.close()
            
            if student:
                # Populate fields with existing data
                self.dialog.name_field.text = student[0]
                self.dialog.course_field.text = student[1]
                self.dialog.dob_field.text = student[2].strftime("%Y-%m-%d") if student[2] else ""
        except (ValueError, AttributeError, mysql.connector.Error) as e:
            print(f"Error loading student data: {e}")

    def show_info_dialog(self, message):
        """Show information dialog with message"""
        dialog = MDDialog(
            title="Information",
            text=message,
            buttons=[
                MDFlatButton(text="OK", on_press=lambda x: dialog.dismiss())
            ]
        )
        dialog.open()

    def show_recognition_results(self, faces):
        """Display recognition results in the app"""
        if not faces:
            self.show_info_dialog("No faces recognized")
            return
            
        # Create a results layout
        content = MDBoxLayout(
            orientation="vertical",
            spacing="10dp",
            size_hint_y=None,
            height=dp(50 + len(faces) * 50)  # Adjust height based on number of faces
        )
        
        content.add_widget(MDLabel(
            text="Recognized Faces:",
            font_style="H6",
            size_hint_y=None,
            height=dp(30)
        ))
        
        for roll_no, name in faces:
            content.add_widget(MDLabel(
                text=f"{name} (Roll No: {roll_no})",
                size_hint_y=None,
                height=dp(30)
            ))
        
        dialog = MDDialog(
            title="Face Recognition Results",
            type="custom",
            content_cls=content,
            buttons=[
                MDFlatButton(text="Close", on_press=lambda x: dialog.dismiss()),
                MDRaisedButton(text="Mark Attendance", on_press=lambda x: (self.mark_attendance(), dialog.dismiss()))
            ]
        )
        dialog.open()

    def open_file_chooser(self, instance):
        """Open file chooser to select a face image"""
        from plyer import filechooser
        filechooser.open_file(on_selection=self.process_selected_image, 
                            filters=[("Image Files", "*.jpg", "*.jpeg", "*.png")])
        
    def process_selected_image(self, selection):
        """Process selected image file"""
        if not selection:
            return  # No file selected
            
        image_path = selection[0]
        try:
            # Read image and process face
            image = cv2.imread(image_path)
            if image is None:
                self.show_error_dialog("Failed to load image")
                return
                
            self.process_face_image(image)
        except Exception as e:
            self.show_error_dialog(f"Error processing image: {e}")

    def capture_face_data(self, instance):
        """Capture face from camera"""
        if not self.capture or not self.capture.isOpened():
            self.show_error_dialog("Camera not initialized. Please start the camera first.")
            return
            
        ret, frame = self.capture.read()
        if not ret:
            self.show_error_dialog("Failed to capture image from camera")
            return
            
        self.process_face_image(frame)

    def process_face_image(self, image):
        """Process face in the provided image"""
        if self.dialog is None:
            return
            
        # Get form data
        roll_no = self.dialog.roll_no_field.text.strip()
        name = self.dialog.name_field.text.strip()
        course = self.dialog.course_field.text.strip()
        dob = self.dialog.dob_field.text.strip()
        
        # Validate form data
        if not roll_no or not name or not course:
            self.show_error_dialog("Please fill in all required fields")
            return
            
        try:
            roll_no = int(roll_no)
        except ValueError:
            self.show_error_dialog("Roll No must be a number")
            return
            
        try:
            datetime.strptime(dob, '%Y-%m-%d')
        except ValueError:
            self.show_error_dialog("Invalid date format. Use YYYY-MM-DD")
            return
        
        # Detect and encode face
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            self.show_error_dialog("No face detected in the image")
            return
            
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        if not face_encodings:
            self.show_error_dialog("Failed to encode the detected face")
            return
        
        # Store in database
        self.store_face_encoding(roll_no, name, course, dob, face_encodings[0])

    # def show_date_picker(self, *args):
    #     """Show Date Range Picker"""
    #     date_dialog = MDDatePicker(
    #         mode="range",
    #         min_date=date.today() - timedelta(days=60),
    #         max_date=date.today()
    #     )
    #     date_dialog.bind(on_save=self.on_date_range_selected, on_cancel=lambda *args: None)
    #     date_dialog.open()
    def show_date_picker(self, *args):
        """Show Date Range Picker"""
        from datetime import date, timedelta
        from kivymd.uix.pickers import MDDatePicker
        
        date_dialog = MDDatePicker(
            mode="range",
            min_date=date.today() - timedelta(days=60),
            max_date=date.today()
        )
        date_dialog.bind(on_save=self.on_date_range_selected)
        date_dialog.open()

    def on_date_range_selected(self, instance, value, date_range):
        """Handle Date Range Selection"""
        if date_range:
            self.start_date = date_range[0]
            self.end_date = date_range[-1]
            date_label = f"{self.start_date} to {self.end_date}"
            self.root.ids.screen_manager.get_screen('dashboard').ids.date_range_label.text = date_label
            self.load_attendance_dashboard()

    def filter_dashboard(self):
        """Filter Dashboard by Roll No and Date Range"""
        try:
            main_screen = self.screen_manager.get_screen('main')
            # Check if we're using the new UI structure with screen_manager or the old one with tabs
            if hasattr(main_screen.ids, 'screen_manager'):
                # New structure
                dashboard_screen = main_screen.ids.screen_manager.get_screen('dashboard')
                # Update your field references accordingly
            elif hasattr(main_screen.ids, 'tab2'):
                # Old structure with tabs
                # Use the old references
                pass
            
            self.load_attendance_dashboard()
        except Exception as e:
            print(f"Error in filter_dashboard: {e}")
            self.show_error_dialog(f"Error filtering dashboard: {e}")

    # def refresh_dashboard(self, *args):
    #     """Refresh Dashboard"""
    #     self.start_date = None
    #     self.end_date = None
    #     self.screen_manager.get_screen('main').ids.tab2.ids.roll_no_filter.text = ""
    #     self.screen_manager.get_screen('main').ids.tab2.ids.date_range_label.text = ""
    #     self.load_attendance_dashboard()
    def refresh_dashboard(self, *args):
        """Refresh Dashboard"""
        self.start_date = None
        self.end_date = None

        main_screen = self.screen_manager  # This is already MainScreen
        try:
            # Get the inner ScreenManager inside MainScreen
            screen_manager = main_screen.ids.screen_manager

            # Optional: switch to dashboard if needed
            screen_manager.current = "dashboard"

            # Get the dashboard screen
            dashboard_screen = screen_manager.get_screen("dashboard")

            # Clear filter fields
            dashboard_screen.ids.roll_no_filter.text = ""
            dashboard_screen.ids.date_range_label.text = ""

            self.load_attendance_dashboard()

        except Exception as e:
            print(f"❌ Error refreshing dashboard: {e}")
            self.show_error_dialog(f"Error refreshing dashboard: {e}")


    def export_to_csv(self, *args):
        """Export Attendance Data to CSV"""
        db = get_db_connection()
        if not db:
            return
        try:
            cursor = db.cursor()
            
            # Build the query with joins to get student names
            query = """
                SELECT a.roll_no, s.name, a.date, a.attendance 
                FROM attendance a
                JOIN student_info s ON a.roll_no = s.roll_no
            """
            
            params = []
            where_clauses = []
            
            if self.start_date and self.end_date:
                where_clauses.append("a.date BETWEEN %s AND %s")
                params.extend([self.start_date, self.end_date])
                
            # roll_no_filter = self.screen_manager.get_screen('main').ids.tab2.ids.roll_no_filter.text.strip()
            roll_no_filter = self.screen_manager.ids.roll_no_filter.text.strip()

            if roll_no_filter:
                try:
                    roll_no_int = int(roll_no_filter)
                    where_clauses.append("a.roll_no = %s")
                    params.append(roll_no_int)
                except ValueError:
                    print("Invalid roll number format")
            
            # Add WHERE clause if any conditions exist
            if where_clauses:
                query += " WHERE " + " AND ".join(where_clauses)

            cursor.execute(query, params)
            data = cursor.fetchall()
            
            # Convert 'P'/'A' to 'Present'/'Absent' for better readability
            formatted_data = []
            for row in data:
                roll_no, name, date, status = row
                status_text = "Present" if status == 'P' else "Absent" if status == 'A' else status
                formatted_data.append((roll_no, name, date, status_text))
            
            df = pd.DataFrame(formatted_data, columns=["Roll No", "Name", "Date", "Status"])
            
            # Create output directory if it doesn't exist
            output_dir = os.path.expanduser("~/Desktop")
            os.makedirs(output_dir, exist_ok=True)
            
            output_path = os.path.join(output_dir, f"attendance_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
            df.to_csv(output_path, index=False)
            print(f"Data exported to {output_path} successfully!")
            toast("📁 Data exported to Desktop!")
        except mysql.connector.Error as err:
            print(f"Error exporting CSV: {err}")
        finally:
            cursor.close()
            db.close()

    # def load_attendance_dashboard(self):
    #     """Load ERP Dashboard with Visualizations and Data Table"""
        
    #     # Find the graphs_layout safely
    #     try:
    #         screen_manager = self.root.ids.screen_manager
    #         dashboard_screen = screen_manager.get_screen('dashboard')
    #         graphs_layout = dashboard_screen.ids.graphs_layout
    #         graphs_layout.clear_widgets()
    #     except AttributeError as e:
    #         print(f"Error accessing UI elements: {e}")
    #         self.show_error_dialog("Error loading dashboard: UI elements not found")
    #         return
        
    #     db = get_db_connection()
    #     if not db:
    #         return
    #     try:
    #         cursor = db.cursor()
            
    #         # Get filter values - safely access these widgets
    #         roll_no_filter = ""
    #         try:
    #             # Try to get the filter field from the new UI structure
    #             roll_no_field = dashboard_screen.ids.roll_no_filter
    #             roll_no_filter = roll_no_field.text.strip()
    #         except AttributeError:
    #             print("Warning: Could not find roll_no_filter in dashboard screen")
            
    #         roll_no_int = None
    #         if roll_no_filter:
    #             try:
    #                 roll_no_int = int(roll_no_filter)
    #             except ValueError:
    #                 print("Invalid roll number format")
            
    #         # Update Summary Cards with animations
    #         try:
    #             cursor.execute("SELECT COUNT(*) FROM student_info")
    #             total_students = cursor.fetchone()[0]
    #             total_students_widget = dashboard_screen.ids.total_students
    #             self._animate_counter(total_students_widget, 0, total_students)
    #         except AttributeError:
    #             print("Warning: Could not find total_students widget")
            
    #         # Count total attendance records based on filters
    #         attendance_query = "SELECT COUNT(*) FROM attendance a"
    #         attendance_params = []
    #         where_clauses = []
            
    #         if self.start_date and self.end_date:
    #             where_clauses.append("a.date BETWEEN %s AND %s")
    #             attendance_params.extend([self.start_date, self.end_date])
                    
    #         if roll_no_int is not None:
    #             where_clauses.append("a.roll_no = %s")
    #             attendance_params.append(roll_no_int)
            
    #         if where_clauses:
    #             attendance_query += " WHERE " + " AND ".join(where_clauses)
                    
    #         cursor.execute(attendance_query, attendance_params)
    #         total_records = cursor.fetchone()[0]
            
    #         try:
    #             total_records_widget = dashboard_screen.ids.total_records
    #             self._animate_counter(total_records_widget, 0, total_records)
    #         except AttributeError:
    #             print("Warning: Could not find total_records widget")

    #         # Count 'Present' attendance records based on filters
    #         present_query = "SELECT COUNT(*) FROM attendance a WHERE attendance = 'P'"
    #         present_params = []
            
    #         if where_clauses:
    #             present_query += " AND " + " AND ".join(where_clauses)
    #             present_params = attendance_params.copy()
            
    #         cursor.execute(present_query, present_params)
    #         present_count = cursor.fetchone()[0]
            
    #         # Calculate attendance rate with animation
    #         attendance_rate = (present_count / total_records * 100) if total_records > 0 else 0
    #         try:
    #             attendance_rate_widget = dashboard_screen.ids.attendance_rate
    #             self._animate_counter(attendance_rate_widget, 0, attendance_rate, suffix="%", decimal_places=1)
    #         except AttributeError:
    #             print("Warning: Could not find attendance_rate widget")

    #         # Add top students card (new feature)
    #         self._add_top_students_card(cursor, graphs_layout)
            
    #         # Check if we're viewing by specific roll number or full dashboard
    #         if roll_no_int is not None:
    #             # Individual student view - show detailed student graphs
    #             self._show_individual_student_dashboard(cursor, roll_no_int, graphs_layout)
    #         else:
    #             # Overview dashboard - show aggregate data
    #             self._show_aggregate_dashboard(cursor, where_clauses, attendance_params, graphs_layout)

    #         # Add Data Table at the bottom with search functionality
    #         self._add_attendance_data_table(cursor, where_clauses, attendance_params, graphs_layout)
                
    #     except mysql.connector.Error as err:
    #         print(f"Error loading dashboard: {err}")
    #         self.show_error_dialog(f"Error loading dashboard: {err}")
    #     finally:
    #         cursor.close()
    #         db.close()

    def load_attendance_dashboard(self):
        try:
            # Access the nested screen manager inside the root MainScreen
            # Assuming self.root is your MainScreen
            screen_manager = self.root.ids.screen_manager
            screen_manager.current = "dashboard"
            
            # Schedule loading after screen transition
            Clock.schedule_once(self._safe_load_dashboard, 0.5)
            
            # Get dashboard screen
            dashboard_screen = screen_manager.get_screen('dashboard')
            print("Available screens:", screen_manager.screen_names)

            # Get UI elements
            total_students = dashboard_screen.ids.get("total_students")
            total_records = dashboard_screen.ids.get("total_records")
            attendance_rate = dashboard_screen.ids.get("attendance_rate")
            chart_box = dashboard_screen.ids.get("graphs_layout")

            print("✅ dashboard_screen.ids keys:", list(dashboard_screen.ids.keys()))

            if not all([total_students, total_records, attendance_rate, chart_box]):
                raise Exception("UI elements not found")

            # Example mock data
            students_count = len(self.fetch_students())
            records_count = len(self.fetch_attendance_data())
            rate = (records_count / students_count) * 100 if students_count > 0 else 0

            total_students.text = str(students_count)
            total_records.text = str(records_count)
            attendance_rate.text = f"{rate:.2f}%"

            # Clear and add new chart placeholder
            chart_box.clear_widgets()
            chart_box.add_widget(MDLabel(text="(chart placeholder)", halign="center"))

        except Exception as e:
            print(f"Error switching to dashboard: {e}")
            self.show_error_dialog(f"Error switching to dashboard: {e}")

    def _safe_load_dashboard(self, dt):
        try:
            # Get dashboard screen
            dashboard_screen = self.root.ids.screen_manager.get_screen('dashboard')
            
            # Debug: print all available IDs
            print("Dashboard screen IDs:", dashboard_screen.ids.keys())
            
            # Access UI elements
            total_students = dashboard_screen.ids.total_students
            total_records = dashboard_screen.ids.total_records
            attendance_rate = dashboard_screen.ids.attendance_rate
            charts_layout = dashboard_screen.ids.graphs_layout
            
            # Example mock data
            students_count = len(self.fetch_students())
            records_count = len(self.fetch_attendance_data())
            rate = (records_count / students_count) * 100 if students_count > 0 else 0
            
            # Update UI elements
            total_students.text = str(students_count)
            total_records.text = str(records_count)
            attendance_rate.text = f"{rate:.2f}%"
            
            # Clear and add new chart placeholder
            charts_layout.clear_widgets()
            charts_layout.add_widget(MDLabel(text="(chart placeholder)", halign="center"))
            
        except AttributeError as e:
            print(f"ID not found error: {e}")
            # More specific error message that tells you exactly which ID is missing
            self.show_error_dialog(f"Dashboard UI element not found: {e}")
        except Exception as e:
            print(f"Error loading dashboard data: {e}")
            self.show_error_dialog(f"Error loading dashboard data: {e}")

    def _animate_counter(self, widget, start_val, end_val, duration=1.0, suffix="", decimal_places=0):
        """Animate counter from start_val to end_val"""
        if widget is None:
            print("Warning: Widget is None in _animate_counter")
            return
            
        try:
            start_val = float(start_val) if isinstance(start_val, str) and start_val.replace('.', '', 1).isdigit() else float(start_val)
            
            # Define the animation step function
            def update_value(dt):
                nonlocal step_count
                step_count += 1
                progress = min(step_count / total_steps, 1.0)
                eased_progress = 1 - (1 - progress) * (1 - progress)
                current = start_val + (end_val - start_val) * eased_progress
                
                if decimal_places > 0:
                    formatted = f"{current:.{decimal_places}f}{suffix}"
                else:
                    formatted = f"{int(current)}{suffix}"
                    
                widget.text = formatted
                widget.text_color = (0.2, 0.7, 0.3, 1) if suffix == "%" else (0, 0, 0, 1)
                if step_count >= total_steps:
                    return False
                    
            # Animation parameters    
            fps = 30
            total_steps = int(fps * duration)
            step_count = 0
            
            # Schedule the animation
            Clock.schedule_interval(update_value, 1.0/fps)
        except Exception as e:
            print(f"Error in _animate_counter: {e}")

    def _add_top_students_card(self, cursor, layout):
        """Add top students with highest attendance card"""
        try:
            # Create card for top students
            top_card = MDCard(
                orientation="vertical",
                padding="10dp",
                size_hint_y=None,
                height=dp(200),
                elevation=4,
                radius=[10, 10, 10, 10]
            )
            
            # Add title to card
            top_card.add_widget(MDLabel(
                text="Top Students by Attendance",
                font_style="H6",
                halign="center",
                size_hint_y=None,
                height=dp(30)
            ))
            
            # Query to get top 5 students with highest attendance percentage
            query = """
            SELECT s.roll_no, s.name, 
                SUM(CASE WHEN a.attendance = 'P' THEN 1 ELSE 0 END) as present_count,
                COUNT(*) as total_count,
                (SUM(CASE WHEN a.attendance = 'P' THEN 1 ELSE 0 END) / COUNT(*)) * 100 as attendance_rate
            FROM student_info s
            JOIN attendance a ON s.roll_no = a.roll_no
            GROUP BY s.roll_no, s.name
            ORDER BY attendance_rate DESC
            LIMIT 5
            """
            
            cursor.execute(query)
            top_students = cursor.fetchall()
            
            if not top_students:
                top_card.add_widget(MDLabel(
                    text="No attendance data available",
                    halign="center"
                ))
                layout.add_widget(top_card)
                return
                
            # Create horizontal layout for leaderboard
            leaderboard = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(150),
                padding="10dp",
                spacing="10dp"
            )
            
            # Add students to leaderboard
            for i, (roll_no, name, present, total, rate) in enumerate(top_students):
                position = i + 1
                student_card = MDCard(
                    orientation="vertical",
                    size_hint_x=0.2,
                    padding="8dp",
                    elevation=2,
                    radius=[8, 8, 8, 8],
                    md_bg_color=(1, 0.97, 0.8, 1)  if i == 0 else (1, 1, 1, 1)
                )
                
                # Position badge
                # badge_color = [(0.9, 0.7, 0.1, 1), (0.8, 0.8, 0.8, 1), (0.8, 0.5, 0.2, 1), 
                #             (0.7, 0.7, 0.7, 1), (0.7, 0.7, 0.7, 1)][min(i, 4)]
                badge_colors = [
                    (0.9, 0.7, 0.1, 1),  # Gold - 1st
                    (0.8, 0.8, 0.8, 1),  # Silver - 2nd
                    (0.8, 0.5, 0.2, 1),  # Bronze - 3rd
                    (0.45, 0.62, 0.8, 1),  # Blue - 4th
                    (0.6, 0.4, 0.7, 1),  # Purple - 5th
                ]

                badge_color = badge_colors[i] if i < len(badge_colors) else (0.7, 0.7, 0.7, 1)

                
                badge = MDBoxLayout(
                    size_hint=(None, None),
                    size=(dp(30), dp(30)),
                    md_bg_color=badge_color,
                    radius=[15, 15, 15, 15],
                    pos_hint={"center_x": 0.5}
                )
                
                badge.add_widget(MDLabel(
                    text=str(position),
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(1, 1, 1, 1),
                    font_style="H6"
                ))
                
                student_card.add_widget(badge)
                
                # Add student name (shortened if too long)
                short_name = name if len(name) < 12 else name[:10] + "..."
                student_card.add_widget(MDLabel(
                    text=short_name,
                    halign="center",
                    size_hint_y=None,
                    height=dp(30),
                    font_style="Subtitle1"
                ))
                
                # Add attendance percentage
                student_card.add_widget(MDLabel(
                    text=f"{rate:.1f}%",
                    halign="center",
                    theme_text_color="Custom",
                    text_color=(0.2, 0.6, 0.2, 1),
                    font_style="H6"
                ))
                
                # Add roll number
                student_card.add_widget(MDLabel(
                    text=f"Roll: {roll_no}",
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Caption"
                ))
                
                leaderboard.add_widget(student_card)
                
            top_card.add_widget(leaderboard)
            layout.add_widget(top_card)
            
        except mysql.connector.Error as err:
            print(f"Error creating top students card: {err}")

    def _show_individual_student_dashboard(self, cursor, roll_no, graphs_layout):
        """Show detailed dashboard for a single student with enhanced visualizations"""
        # Get student info
        cursor.execute("SELECT name FROM student_info WHERE roll_no = %s", (roll_no,))
        result = cursor.fetchone()
        if not result:
            graphs_layout.add_widget(MDLabel(
                text=f"No student found with roll number {roll_no}",
                halign="center",
                size_hint_y=None,
                height=dp(50)
            ))
            return
        
        student_name = result[0]
        
        student_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(80),
            padding="10dp",
            elevation=3,
            radius=[10, 10, 10, 10]
        )

        student_card.add_widget(MDLabel(
            text=f"{student_name}",
            font_style="H5",
            halign="center",
            size_hint_y=None,
            height=dp(40),
            theme_text_color="Custom",
            text_color=self.theme_cls.primary_color
        ))

        student_card.add_widget(MDLabel(
            text=f"Roll No: {roll_no}",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            theme_text_color="Secondary",
            font_style="Subtitle1"
        ))

        graphs_layout.add_widget(student_card)

        
        # Get attendance data for this student
        attendance_query = "SELECT date, attendance FROM attendance WHERE roll_no = %s"
        params = [roll_no]
        
        if self.start_date and self.end_date:
            attendance_query += " AND date BETWEEN %s AND %s"
            params.extend([self.start_date, self.end_date])
            
        cursor.execute(attendance_query, params)
        attendance_data = cursor.fetchall()
        
        if not attendance_data:
            graphs_layout.add_widget(MDLabel(
                text=f"No attendance data for {student_name} (Roll No: {roll_no})",
                halign="center",
                size_hint_y=None,
                height=dp(50)
            ))
            return
        
        dates = [row[0].strftime("%Y-%m-%d") for row in attendance_data]
        statuses = [row[1] for row in attendance_data]
        
        # Create a dashboard stats card
        stats_card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(120),
            padding="15dp",
            spacing="15dp",
            elevation=3,
            radius=[10, 10, 10, 10]
        )
        
        # Calculate statistics
        present_count = statuses.count("P")
        absent_count = statuses.count("A")
        total_days = len(statuses)
        attendance_percentage = (present_count / total_days) * 100 if total_days > 0 else 0
        
        # Create three stat boxes
        stat_colors = [(0.2, 0.7, 0.3, 1), (0.9, 0.3, 0.3, 1), (0.2, 0.6, 0.9, 1)]
        stat_icons = ["check-circle", "close-circle", "percent"]
        stat_values = [present_count, absent_count, f"{attendance_percentage:.1f}%"]
        stat_labels = ["Present", "Absent", "Attendance"]
        
        for icon, value, label, color in zip(stat_icons, stat_values, stat_labels, stat_colors):
            stat_box = MDBoxLayout(
                orientation="vertical",
                size_hint_x=0.33,
                padding="5dp"
            )
            
            # Icon
            icon_box = MDBoxLayout(
                size_hint=(None, None),
                size=(dp(30), dp(30)),
                pos_hint={"center_x": 0.5}
            )
            icon_box.add_widget(MDIconButton(
                icon=icon,
                theme_text_color="Custom",
                text_color=color,
                icon_size=dp(30),
                pos_hint={"center_x": 0.5, "center_y": 0.5}
            ))
            stat_box.add_widget(icon_box)
            
            # Value
            stat_box.add_widget(MDLabel(
                text=str(value),
                halign="center",
                theme_text_color="Custom",
                text_color=color,
                font_style="H5"
            ))
            
            # Label
            stat_box.add_widget(MDLabel(
                text=label,
                halign="center",
                theme_text_color="Secondary",
                font_style="Caption"
            ))
            
            stats_card.add_widget(stat_box)
        
        graphs_layout.add_widget(stats_card)
        
        # Create a horizontal layout for placing graphs side by side
        graphs_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(300),
            padding="10dp",
            spacing="10dp"
        )
        
        # Bar Chart: Present vs Absent (left side) with improved styling
        status_display = ["Present" if s == "P" else "Absent" if s == "A" else s for s in statuses]
        df_bar = pd.DataFrame({"Status": status_display})
        
        plt.figure(figsize=(5, 4), facecolor='#f0f0f0')
        ax = sns.countplot(data=df_bar, x="Status", palette={"Present": "#4CAF50", "Absent": "#F44336"})
        plt.title("Attendance Summary", fontsize=14, pad=20)
        plt.ylabel("Count", fontsize=12)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add count labels on top of bars
        for p in ax.patches:
            ax.annotate(f'{int(p.get_height())}', 
                    (p.get_x() + p.get_width()/2., p.get_height() + 0.3), 
                    ha='center', va='bottom', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        bar_texture = CoreImage(buffer, ext='png').texture
        plt.close()
        
        bar_chart = Image(
            texture=bar_texture,
            size_hint=(0.5, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Add chart to a card
        bar_card = MDCard(
            size_hint=(0.5, 1),
            elevation=2,
            radius=[10, 10, 10, 10],
            padding="5dp"
        )
        bar_card.add_widget(bar_chart)
        graphs_row.add_widget(bar_card)
        
        # Pie Chart: Proportion of Attendance (right side)
        plt.figure(figsize=(5, 4), facecolor='#f0f0f0')
        plt.pie([present_count, absent_count], 
            labels=["Present", "Absent"], 
            colors=['#4CAF50', '#F44336'], 
            autopct='%1.1f%%',
            textprops={'fontsize': 12, 'fontweight': 'bold'},
            explode=[0.05, 0],
            shadow=True)
        plt.title("Attendance Proportion", fontsize=14, pad=20)
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        pie_texture = CoreImage(buffer, ext='png').texture
        plt.close()
        
        pie_chart = Image(
            texture=pie_texture,
            size_hint=(0.5, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        
        # Add chart to a card
        pie_card = MDCard(
            size_hint=(0.5, 1),
            elevation=2,
            radius=[10, 10, 10, 10],
            padding="5dp"
        )
        pie_card.add_widget(pie_chart)
        graphs_row.add_widget(pie_card)
        
        # Add the row to the main layout
        graphs_layout.add_widget(graphs_row)
        
        # Create another row for the weekday analysis chart and trends
        graphs_row2 = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(300),
            padding="10dp",
            spacing="10dp"
        )
        
        # Add a weekday analysis chart with improved styling
        date_objects = [datetime.strptime(d, "%Y-%m-%d") for d in dates]
        weekdays = [d.strftime("%A") for d in date_objects]  # Get day names
        
        # Create a DataFrame with day and status
        df_weekday = pd.DataFrame({
            "Weekday": weekdays,
            "Status": statuses
        })
        
        # Count present/absent by weekday
        weekday_counts = df_weekday.groupby(['Weekday', 'Status']).size().unstack(fill_value=0)
        
        # Ensure all weekdays are in order
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekday_counts = weekday_counts.reindex(weekday_order, fill_value=0)
        
        # Plot weekday analysis with improved styling
        plt.figure(figsize=(8, 4), facecolor='#f0f0f0')
        ax = weekday_counts.plot(kind='bar', color=['#F44336', '#4CAF50'], edgecolor='black', linewidth=0.5)
        plt.title("Attendance by Day of Week", fontsize=14, pad=15)
        plt.ylabel("Count", fontsize=12)
        plt.xlabel("Weekday", fontsize=12)
        plt.legend(["Absent", "Present"], frameon=True, fancybox=True, shadow=True)
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.tight_layout()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        weekday_texture = CoreImage(buffer, ext='png').texture
        plt.close()
        
        # Add chart to a card
        weekday_card = MDCard(
            size_hint=(1, 1),
            elevation=2,
            radius=[10, 10, 10, 10],
            padding="5dp"
        )
        
        weekday_chart = Image(
            texture=weekday_texture,
            size_hint=(1, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        weekday_card.add_widget(weekday_chart)
        graphs_row2.add_widget(weekday_card)
        
        # Add the second row to the main layout
        graphs_layout.add_widget(graphs_row2)
        
        # Add attendance timeline (streak analysis) - New feature
        self._add_attendance_timeline(roll_no, dates, statuses, graphs_layout)

    def _add_attendance_timeline(self, roll_no, dates, statuses, layout):
        """Add attendance timeline visualization to show streaks and patterns"""
        if not dates or not statuses:
            return
            
        # Create a DataFrame with dates and statuses
        df = pd.DataFrame({
            'date': [datetime.strptime(d, "%Y-%m-%d") for d in dates],
            'status': statuses
        })
        
        # Sort by date
        df = df.sort_values('date')
        
        # Fill in missing dates with 'Missing'
        date_range = pd.date_range(start=df['date'].min(), end=df['date'].max())
        all_dates = pd.DataFrame({'date': date_range})
        df = pd.merge(all_dates, df, on='date', how='left')
        df['status'].fillna('Missing', inplace=True)
        
        # Create status map
        status_map = {'P': 1, 'A': -1, 'Missing': 0}
        df['value'] = df['status'].map(status_map)
        
        # Create figure
        plt.figure(figsize=(10, 2.5), facecolor='#f0f0f0')
        
        # Create a colormap
        cmap = plt.cm.RdYlGn  # Red for absent, yellow for missing, green for present
        norm = plt.Normalize(-1, 1)
        
        # Plot each day as a colored cell
        for i, (_, row) in enumerate(df.iterrows()):
            color = cmap(norm(row['value']))
            plt.fill_between([i, i+0.9], 0, 1, color=color, edgecolor='white', linewidth=0.5)
        
        # Add month dividers and labels
        month_starts = {}
        for i, date in enumerate(df['date']):
            month_start = date.replace(day=1)
            if month_start not in month_starts:
                month_starts[month_start] = i
                plt.axvline(x=i, color='black', linestyle='-', linewidth=0.8, alpha=0.5)
                plt.text(i+2, -0.15, date.strftime('%b %Y'), 
                        fontsize=9, ha='left', va='center', rotation=0)
        
        # Create custom legend
        import matplotlib.patches as mpatches
        present_patch = mpatches.Patch(color=cmap(norm(1)), label='Present')
        absent_patch = mpatches.Patch(color=cmap(norm(-1)), label='Absent')
        missing_patch = mpatches.Patch(color=cmap(norm(0)), label='No Record')
        plt.legend(handles=[present_patch, absent_patch, missing_patch], 
                loc='upper center', bbox_to_anchor=(0.5, -0.15),
                ncol=3, frameon=True, fancybox=True)
        
        # Set plot appearance
        plt.title('Attendance Timeline', fontsize=14, pad=10)
        plt.ylim(-0.1, 1.1)
        plt.xlim(-0.5, len(df) + 0.5)
        plt.axis('off')
        plt.tight_layout()
        
        # Save the figure
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        timeline_texture = CoreImage(buffer, ext='png').texture
        plt.close()
        
        # Create a card for the timeline
        timeline_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(200),
            elevation=3,
            radius=[10, 10, 10, 10],
            padding="10dp"
        )
        
        timeline_card.add_widget(MDLabel(
            text="Attendance Timeline",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            font_style="H6"
        ))
        
        timeline_chart = Image(
            texture=timeline_texture,
            size_hint_y=None,
            height=dp(150),
            allow_stretch=True,
            keep_ratio=True
        )
        
        timeline_card.add_widget(timeline_chart)
        layout.add_widget(timeline_card)
        
        # Calculate and display streaks
        self._calculate_streaks(df, layout)

    def _calculate_streaks(self, df, layout):
        """Calculate and display attendance streaks"""
        # Find current and longest present streaks
        current_streak = 0
        longest_streak = 0
        current_streak_type = None
        longest_absent = 0
        current_absent = 0
        
        for status in df['status']:
            if status == 'P':
                if current_streak_type == 'P' or current_streak_type is None:
                    current_streak += 1
                    current_streak_type = 'P'
                else:
                    current_streak = 1
                    current_streak_type = 'P'
                longest_streak = max(longest_streak, current_streak)
                current_absent = 0
            elif status == 'A':
                if current_streak_type == 'A' or current_streak_type is None:
                    current_absent += 1
                    current_streak_type = 'A'
                else:
                    current_absent = 1
                    current_streak_type = 'A'
                longest_absent = max(longest_absent, current_absent)
                current_streak = 0
            else:  # Missing
                current_streak = 0
                current_absent = 0
                current_streak_type = None
        
        # Display streak information
        streak_card = MDCard(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(100),
            elevation=2,
            radius=[10, 10, 10, 10],
            padding="10dp",
            spacing="10dp"
        )
        
        # Longest present streak
        present_streak = MDBoxLayout(
            orientation="vertical",
            size_hint_x=0.5,
            padding="5dp"
        )
        
        present_streak.add_widget(MDLabel(
            text="Longest Present Streak",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1"
        ))
        
        present_streak.add_widget(MDLabel(
            text=f"{longest_streak} days",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.2, 0.7, 0.3, 1),
            font_style="H5"
        ))
        
        streak_card.add_widget(present_streak)
        
        # Longest absent streak
        absent_streak = MDBoxLayout(
            orientation="vertical",
            size_hint_x=0.5,
            padding="5dp"
        )
        
        absent_streak.add_widget(MDLabel(
            text="Longest Absent Streak",
            halign="center",
            theme_text_color="Secondary",
            font_style="Body1"
        ))
        
        absent_streak.add_widget(MDLabel(
            text=f"{longest_absent} days",
            halign="center",
            theme_text_color="Custom",
            text_color=(0.9, 0.3, 0.3, 1),
            font_style="H5"
        ))
        
        streak_card.add_widget(absent_streak)
        layout.add_widget(streak_card)

    def _show_aggregate_dashboard(self, cursor, where_clauses, params, graphs_layout):
        """Show aggregate dashboard for all students"""
        self._add_class_summary_card(cursor, where_clauses, params, graphs_layout)
        # Create a horizontal layout for placing graphs side by side
        graphs_row = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(300),
            padding="10dp",
            spacing="10dp"
        )
        
        # Add overview title
        # graphs_layout.add_widget(MDLabel(
        #     text="Attendance Overview",
        #     font_style="H5",
        #     halign="center",
        #     size_hint_y=None,
        #     height=dp(40)
        # ))
        
        # Get aggregate data from attendance table
        aggregate_query = "SELECT attendance, COUNT(*) FROM attendance a"
        aggregate_params = []
        
        if where_clauses:
            aggregate_query += " WHERE " + " AND ".join(where_clauses)
            aggregate_params = params.copy()
        
        aggregate_query += " GROUP BY attendance"
        cursor.execute(aggregate_query, aggregate_params)
        attendance_counts = cursor.fetchall()
        
        # Process the results
        status_dict = {status: count for status, count in attendance_counts}
        present_count = status_dict.get('P', 0)
        absent_count = status_dict.get('A', 0)
        
        # Pie Chart: Overall Attendance Distribution
        plt.figure(figsize=(5, 4))
        plt.pie([present_count, absent_count], 
            labels=["Present", "Absent"], 
            colors=['green', 'red'], 
            autopct='%1.1f%%')
        plt.title("Overall Attendance Distribution")
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        pie_texture = CoreImage(buffer, ext='png').texture
        plt.close()
        
        pie_chart = Image(
            texture=pie_texture,
            size_hint=(0.5, 1),
            allow_stretch=True,
            keep_ratio=True
        )
        overview_card = MDCard(
            orientation="vertical",
            size_hint=(0.5, 1),
            padding="10dp",
            elevation=3,
            radius=[10, 10, 10, 10]
        )
        overview_card.add_widget(MDLabel(
            text="Attendance Overview",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            font_style="H6"
        ))
        overview_card.add_widget(pie_chart)
        graphs_row.add_widget(overview_card)
        
        # Daily Attendance Trend (Bar chart for each date)
        # daily_query = """
        #     SELECT date, 
        #         SUM(CASE WHEN attendance = 'P' THEN 1 ELSE 0 END) as present_count,
        #         COUNT(*) as total_count
        #     FROM attendance a
        # """
        # daily_params = []
        
        # if where_clauses:
        #     daily_query += " WHERE " + " AND ".join(where_clauses)
        #     daily_params = params.copy()
        
        # daily_query += " GROUP BY date ORDER BY date"
        # cursor.execute(daily_query, daily_params)
        # daily_data = cursor.fetchall()
        
        # if daily_data:
        #     dates = [row[0].strftime("%Y-%m-%d") for row in daily_data]
        #     present_counts = [row[1] for row in daily_data]
        #     total_counts = [row[2] for row in daily_data]
        #     attendance_rates = [present/total*100 if total > 0 else 0 for present, total in zip(present_counts, total_counts)]
            
        #     plt.figure(figsize=(6, 4))
        #     plt.bar(dates, attendance_rates, color='blue')
        #     plt.title("Daily Attendance Rate")
        #     plt.ylabel("Attendance Rate (%)")
        #     plt.xticks(rotation=45)
        #     plt.ylim(0, 105)  # Set y-axis limit to 0-100% with a little margin
        #     plt.tight_layout()
            
        #     buffer = BytesIO()
        #     plt.savefig(buffer, format='png', bbox_inches='tight')
        #     buffer.seek(0)
        #     daily_texture = CoreImage(buffer, ext='png').texture
        #     plt.close()
            
        #     daily_chart = Image(
        #         texture=daily_texture,
        #         size_hint=(0.5, 1),
        #         allow_stretch=True,
        #         keep_ratio=True
        #     )
        #     graphs_row.add_widget(daily_chart)
        # Attendance Heatmap
        heatmap_query = """
            SELECT date, 
                SUM(CASE WHEN attendance = 'P' THEN 1 ELSE 0 END) as present_count,
                COUNT(*) as total_count
            FROM attendance a
        """
        heatmap_params = []
        if where_clauses:
            heatmap_query += " WHERE " + " AND ".join(where_clauses)
            heatmap_params = params.copy()
        heatmap_query += " GROUP BY date ORDER BY date"

        cursor.execute(heatmap_query, heatmap_params)
        heatmap_data = cursor.fetchall()

        if heatmap_data:
            df = pd.DataFrame(heatmap_data, columns=["date", "present", "total"])
            df['date'] = pd.to_datetime(df['date'])
            df['rate'] = df['present'] / df['total'] * 100
            df['day'] = df['date'].dt.day
            df['month'] = df['date'].dt.month_name()

            pivot_table = df.pivot_table(index='month', columns='day', values='rate')
            pivot_table = pivot_table.fillna(0)  # Replace NaN with zeros
            pivot_table = pivot_table.astype(float)

            # Plot heatmap
            plt.figure(figsize=(6, 4))
            sns.heatmap(pivot_table, annot=False, cmap="YlGnBu", linewidths=0.5, cbar_kws={'label': 'Attendance Rate (%)'})
            plt.title("Attendance Heatmap")
            plt.xlabel("Day of Month")
            plt.ylabel("Month")
            plt.tight_layout()

            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight')
            buffer.seek(0)
            heatmap_texture = CoreImage(buffer, ext='png').texture
            plt.close()

            heatmap_chart = Image(
                texture=heatmap_texture,
                size_hint=(0.5, 1),
                allow_stretch=True,
                keep_ratio=True
            )
            # Wrap heatmap in a card
            heatmap_card = MDCard(
                orientation="vertical",
                size_hint=(0.5, 1),
                padding="10dp",
                elevation=3,
                radius=[10, 10, 10, 10]
            )

            heatmap_card.add_widget(MDLabel(
                text="Attendance Heatmap",
                halign="center",
                size_hint_y=None,
                height=dp(30),
                font_style="H6"
            ))

            heatmap_card.add_widget(heatmap_chart)
            graphs_row.add_widget(heatmap_card)

            # graphs_row.add_widget(heatmap_chart)

        
        graphs_layout.add_widget(graphs_row)
        
        # Create another row for additional charts
        graphs_row2 = MDBoxLayout(
            orientation="horizontal",
            size_hint_y=None,
            height=dp(300),
            padding="10dp",
            spacing="10dp"
        )
        
        trend_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(350),
            elevation=3,
            radius=[10, 10, 10, 10],
            padding="10dp"
        )
        
        trend_card.add_widget(MDLabel(
            text="Attendance Trend Over Time",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            font_style="H6"
        ))
        
        # Get attendance trend data
        trend_query = """
            SELECT date, 
                SUM(CASE WHEN attendance = 'P' THEN 1 ELSE 0 END) as present_count,
                COUNT(*) as total_count
            FROM attendance a
        """
        trend_params = []
        
        if where_clauses:
            trend_query += " WHERE " + " AND ".join(where_clauses)
            trend_params = params.copy()
        
        trend_query += " GROUP BY date ORDER BY date"
        cursor.execute(trend_query, trend_params)
        trend_data = cursor.fetchall()
        
        if trend_data:
            dates = [row[0].strftime("%Y-%m-%d") for row in trend_data]
            present_counts = [row[1] for row in trend_data]
            total_counts = [row[2] for row in trend_data]
            attendance_rates = [present/total*100 if total > 0 else 0 for present, total in zip(present_counts, total_counts)]
            
            # Plotting with rolling average for trend visibility
            plt.figure(figsize=(10, 4), facecolor='#f0f0f0')
            plt.plot(dates, attendance_rates, 'o-', color='#3366cc', linewidth=1, markersize=4, alpha=0.7, label='Daily Rate')
            
            # Add 7-day moving average if we have enough data
            if len(dates) > 7:
                moving_avg = pd.Series(attendance_rates).rolling(window=7).mean().tolist()
                plt.plot(dates, moving_avg, '-', color='#cc3366', linewidth=2.5, label='7-Day Average')
            
            plt.title("Attendance Rate Trend", fontsize=14, pad=15)
            plt.ylabel("Attendance Rate (%)", fontsize=12)
            plt.grid(True, linestyle='--', alpha=0.7)
            # plt.xticks(rotation=45)
            plt.xticks(rotation=45, ha='right')
            plt.gca().xaxis.set_major_locator(plt.MaxNLocator(nbins=10))
            plt.ylim(0, 105)
            plt.legend(frameon=True, fancybox=True, shadow=True)
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            trend_texture = CoreImage(buffer, ext='png').texture
            plt.close()
            
            trend_chart = Image(
                texture=trend_texture,
                size_hint=(1, 1),
                allow_stretch=True,
                keep_ratio=True
            )
            trend_card.add_widget(trend_chart)
            graphs_layout.add_widget(trend_card)

        # Weekday analysis for all students
        weekday_query = """
            SELECT DAYNAME(date) as weekday, 
                SUM(CASE WHEN attendance = 'P' THEN 1 ELSE 0 END) as present_count,
                COUNT(*) as total_count
            FROM attendance a
        """
        weekday_params = []
        
        if where_clauses:
            weekday_query += " WHERE " + " AND ".join(where_clauses)
            weekday_params = params.copy()
        
        weekday_query += " GROUP BY weekday ORDER BY FIELD(weekday, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday')"
        
        try:
            cursor.execute(weekday_query, weekday_params)
            weekday_data = cursor.fetchall()
            
            if weekday_data:
                weekdays = [row[0] for row in weekday_data]
                present_counts = [row[1] for row in weekday_data]
                total_counts = [row[2] for row in weekday_data]
                
                plt.figure(figsize=(6, 4))
                
                # Create positions for grouped bars
                x = np.arange(len(weekdays))
                width = 0.35
                
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.bar(x - width/2, present_counts, width, label='Present')
                ax.bar(x + width/2, [total-present for total, present in zip(total_counts, present_counts)], width, label='Absent')
                
                ax.set_title('Attendance by Day of Week')
                ax.set_xlabel('Weekday')
                ax.set_ylabel('Count')
                ax.set_xticks(x)
                ax.set_xticklabels(weekdays, rotation=45, ha='right')
                ax.legend()
                
                plt.tight_layout()
                
                buffer = BytesIO()
                plt.savefig(buffer, format='png', bbox_inches='tight')
                buffer.seek(0)
                weekday_texture = CoreImage(buffer, ext='png').texture
                plt.close()
                
                weekday_chart = Image(
                    texture=weekday_texture,
                    size_hint=(1, 1),
                    allow_stretch=True,
                    keep_ratio=True
                )
                weekday_card = MDCard(
                    orientation="vertical",
                    size_hint=(1, 1),
                    # size_hint_y=None,
                    height=dp(350),
                    padding="10dp",
                    spacing="10dp",
                    elevation=3,
                    radius=[10, 10, 10, 10]
                )
                weekday_card.add_widget(MDLabel(
                    text="Attendance by Day of Week",
                    halign="center",
                    size_hint_y=None,
                    height=dp(30),
                    font_style="H6"
                ))
                weekday_card.add_widget(weekday_chart)
                graphs_row2.add_widget(weekday_card)
        except mysql.connector.Error as err:
            print(f"Error generating weekday analysis: {err}")
        
        graphs_layout.add_widget(graphs_row2)
        self._add_daily_comparison(cursor, where_clauses, params, graphs_layout)
        self._add_roll_number_distribution(cursor, where_clauses, params, graphs_layout)

    def _add_daily_comparison(self, cursor, where_clauses, params, graphs_layout):
        """Add chart showing daily attendance comparison"""
        
        # Create card for daily comparison
        daily_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(350),
            elevation=3,
            radius=[10, 10, 10, 10],
            padding="10dp"
        )
        
        daily_card.add_widget(MDLabel(
            text="Last 10 Days Attendance",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            font_style="H6"
        ))
        
        # Get daily attendance for last 10 days
        daily_query = """
            SELECT date, 
                SUM(CASE WHEN attendance = 'P' THEN 1 ELSE 0 END) as present_count,
                COUNT(*) as total_count
            FROM attendance a
        """
        daily_params = []
        
        if where_clauses:
            daily_query += " WHERE " + " AND ".join(where_clauses)
            daily_params = params.copy()
        
        daily_query += " GROUP BY date ORDER BY date DESC LIMIT 10"
        
        cursor.execute(daily_query, daily_params)
        daily_data = cursor.fetchall()
        
        if daily_data and len(daily_data) > 0:
            # Reverse to show in chronological order
            daily_data.reverse()
            
            dates = [row[0].strftime("%m/%d") for row in daily_data]
            present_counts = [row[1] for row in daily_data]
            total_counts = [row[2] for row in daily_data]
            attendance_rates = [present/total*100 if total > 0 else 0 for present, total in zip(present_counts, total_counts)]
            
            plt.figure(figsize=(10, 4), facecolor='#f0f0f0')
            
            # Bar chart with two bars per day - present and absent
            x = np.arange(len(dates))
            width = 0.35
            
            ax = plt.subplot(111)
            present_bars = ax.bar(x - width/2, present_counts, width, label='Present', color='#4CAF50')
            absent_bars = ax.bar(x + width/2, [t-p for t,p in zip(total_counts, present_counts)], width, label='Absent', color='#F44336')
            
            # Add total count as text above bars
            for i, (p, t) in enumerate(zip(present_counts, total_counts)):
                plt.text(i, t + 1, f'Total: {t}', ha='center', fontsize=9)
                
            # Add present percentage inside present bars if there's room
            for i, (p, t) in enumerate(zip(present_counts, total_counts)):
                if p > 3:  # Only if there's room
                    plt.text(i - width/2, p/2, f'{p/t*100:.0f}%', ha='center', va='center', color='white', fontsize=9, fontweight='bold')
            
            plt.title('Daily Attendance Comparison', fontsize=14, pad=15)
            plt.xlabel('Date', fontsize=12)
            plt.ylabel('Student Count', fontsize=12)
            plt.xticks(x, dates)
            plt.legend(frameon=True)
            plt.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add a second y-axis for percentage
            ax2 = ax.twinx()
            ax2.plot(x, attendance_rates, 'o-', color='#FF9800', linewidth=2, label='Rate %')
            ax2.set_ylabel('Attendance Rate (%)', color='#FF9800', fontsize=12)
            ax2.tick_params(axis='y', labelcolor='#FF9800')
            ax2.set_ylim(0, 110)
            
            # Add the percentage line to the legend
            lines, labels = ax.get_legend_handles_labels()
            lines2, labels2 = ax2.get_legend_handles_labels()
            ax.legend(lines + lines2, labels + labels2, loc='upper right', frameon=True)
            
            plt.tight_layout()
            
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            daily_texture = CoreImage(buffer, ext='png').texture
            plt.close()
            
            daily_chart = Image(
                texture=daily_texture,
                size_hint=(1, 1),
                allow_stretch=True,
                keep_ratio=True
            )
            daily_card.add_widget(daily_chart)
        else:
            daily_card.add_widget(MDLabel(
                text="Not enough data available for daily comparison",
                halign="center"
            ))
        
        graphs_layout.add_widget(daily_card)

    def _add_class_summary_card(self, cursor, where_clauses, params, graphs_layout):
        """Add a card showing class attendance summary"""
        
        # Create card for class summary
        class_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(180),
            elevation=3,
            radius=[10, 10, 10, 10],
            padding="15dp"
        )
        
        # Query to get summary statistics
        query = """
            SELECT 
                COUNT(DISTINCT a.roll_no) as students_present,
                (SELECT COUNT(*) FROM student_info) as total_students,
                COUNT(DISTINCT a.date) as days_tracked,
                SUM(CASE WHEN a.attendance = 'P' THEN 1 ELSE 0 END) as total_present,
                COUNT(*) as total_records
            FROM attendance a
        """
        
        params_copy = []
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
            params_copy = params.copy()
        
        cursor.execute(query, params_copy)
        result = cursor.fetchone()
        
        if result:
            students_present, total_students, days_tracked, total_present, total_records = result
            attendance_rate = (total_present / total_records * 100) if total_records > 0 else 0
            student_coverage = (students_present / total_students * 100) if total_students > 0 else 0
            
            # Create title
            class_card.add_widget(MDLabel(
                text="Class Summary",
                halign="center",
                size_hint_y=None,
                height=dp(30),
                font_style="H6"
            ))
            
            # Create horizontal layout for stats
            stats_layout = MDBoxLayout(
                orientation="horizontal",
                size_hint_y=None,
                height=dp(120),
                spacing="15dp"
            )
            
            # Create four stat boxes
            stat_data = [
                {"icon": "calendar-range", "value": f"{days_tracked}", "label": "Days Tracked", "color": (0.3, 0.6, 0.9, 1)},
                {"icon": "account-group", "value": f"{students_present}/{total_students}", "label": "Students Covered", "color": (0.2, 0.7, 0.3, 1)},
                {"icon": "percent", "value": f"{attendance_rate:.1f}%", "label": "Attendance Rate", "color": (0.9, 0.6, 0.2, 1)},
                {"icon": "account-check", "value": f"{student_coverage:.1f}%", "label": "Student Coverage", "color": (0.6, 0.4, 0.8, 1)}
            ]
            
            for stat in stat_data:
                stat_box = MDBoxLayout(
                    orientation="vertical",
                    size_hint_x=0.25,
                    padding="5dp"
                )
                
                # Icon
                icon_box = MDBoxLayout(
                    size_hint=(None, None),
                    size=(dp(30), dp(30)),
                    pos_hint={"center_x": 0.5}
                )
                icon_box.add_widget(MDIconButton(
                    icon=stat["icon"],
                    theme_text_color="Custom",
                    text_color=stat["color"],
                    icon_size=dp(30),
                    pos_hint={"center_x": 0.5, "center_y": 0.5}
                ))
                stat_box.add_widget(icon_box)
                
                # Value
                stat_box.add_widget(MDLabel(
                    text=stat["value"],
                    halign="center",
                    theme_text_color="Custom",
                    text_color=stat["color"],
                    font_style="H6"
                ))
                
                # Label
                stat_box.add_widget(MDLabel(
                    text=stat["label"],
                    halign="center",
                    theme_text_color="Secondary",
                    font_style="Caption"
                ))
                
                stats_layout.add_widget(stat_box)
            
            class_card.add_widget(stats_layout)
            graphs_layout.add_widget(class_card)

    def _add_roll_number_distribution(self, cursor, where_clauses, params, graphs_layout):
        """Add chart showing attendance distribution by roll number ranges"""
        
        # Create card for roll range distribution
        roll_card = MDCard(
            orientation="vertical",
            size_hint_y=None,
            height=dp(350),
            elevation=3,
            radius=[10, 10, 10, 10],
            padding="10dp"
        )
        
        roll_card.add_widget(MDLabel(
            text="Attendance by Roll Number Groups",
            halign="center",
            size_hint_y=None,
            height=dp(30),
            font_style="H6"
        ))
        
        # Get min and max roll numbers
        range_query = "SELECT MIN(roll_no), MAX(roll_no) FROM student_info"
        cursor.execute(range_query)
        min_roll, max_roll = cursor.fetchone()
        
        if min_roll is None or max_roll is None:
            roll_card.add_widget(MDLabel(
                text="No student data available",
                halign="center"
            ))
            graphs_layout.add_widget(roll_card)
            return
        
        # Create roll number ranges (e.g., groups of 10)
        group_size = 10
        ranges = [(i, min(i+group_size-1, max_roll)) for i in range(min_roll, max_roll+1, group_size)]
        
        # Get attendance data by roll number ranges
        results = []
        
        for start, end in ranges:
            query = """
                SELECT 
                    COUNT(DISTINCT a.roll_no) as student_count,
                    SUM(CASE WHEN a.attendance = 'P' THEN 1 ELSE 0 END) as present_count,
                    COUNT(*) as total_count
                FROM attendance a
                WHERE a.roll_no BETWEEN %s AND %s
            """
            params = [start, end]
            
            if where_clauses:
                query += " AND " + " AND ".join(where_clauses)
                params.extend(params)
            
            cursor.execute(query, params)
            row = cursor.fetchone()
            
            if row and row[0] > 0:  # If there are students in this range
                results.append((f"{start}-{end}", row[0], row[1], row[2]))
        
        if results:
            # Prepare data for plotting
            ranges = [r[0] for r in results]
            student_counts = [r[1] for r in results]
            attendance_rates = [r[2]/r[3]*100 if r[3] > 0 else 0 for r in results]
            
            # Create figure with two subplots
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4), facecolor='#f0f0f0')
            
            # Student count by range
            bars1 = ax1.bar(ranges, student_counts, color='#5588bb')
            ax1.set_title('Student Count by Roll Number Range')
            ax1.set_xlabel('Roll Number Range')
            ax1.set_ylabel('Number of Students')
            ax1.tick_params(axis='x', rotation=45)
            ax1.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add count labels
            for bar in bars1:
                height = bar.get_height()
                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1, 
                        f'{int(height)}', ha='center', va='bottom', fontsize=9)
            
            # Attendance rate by range
            bars2 = ax2.bar(ranges, attendance_rates, color='#66aa66')
            ax2.set_title('Attendance Rate by Roll Number Range')
            ax2.set_xlabel('Roll Number Range')
            ax2.set_ylabel('Attendance Rate (%)')
            ax2.tick_params(axis='x', rotation=45)
            ax2.set_ylim(0, 105)
            ax2.grid(axis='y', linestyle='--', alpha=0.7)
            
            # Add percentage labels
            for bar in bars2:
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + 1, 
                        f'{height:.1f}%', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            
            # Save plot to buffer
            buffer = BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
            buffer.seek(0)
            roll_texture = CoreImage(buffer, ext='png').texture
            plt.close()
            
            # Add plot to card
            roll_chart = Image(
                texture=roll_texture,
                size_hint=(1, 1),
                allow_stretch=True,
                keep_ratio=True
            )
            roll_card.add_widget(roll_chart)
        
        graphs_layout.add_widget(roll_card)

    def _add_attendance_data_table(self, cursor, where_clauses, params, graphs_layout):
        """Add data table to dashboard"""
        data_query = """
            SELECT a.roll_no, s.name, a.date, a.attendance as status 
            FROM attendance a
            JOIN student_info s ON a.roll_no = s.roll_no
        """
        data_params = []
        
        if where_clauses:
            data_query += " WHERE " + " AND ".join(where_clauses)
            data_params = params.copy()
            
        data_query += " ORDER BY a.date DESC, a.roll_no ASC"
        
        cursor.execute(data_query, data_params)
        data = cursor.fetchall()

        if data:
            table_card = MDCard(
                orientation="vertical",
                padding="10dp",
                size_hint=(1, None),
                height=dp(400),
                elevation=2,
                radius=[12, 12, 12, 12],
            )

            # Properly centered label
            title_label = MDLabel(
                text="Recent Attendance Records",
                font_style="H5",
                halign="center",
                valign="middle",
                size_hint_y=None,
                height=dp(40)
            )
            title_label.bind(size=title_label.setter("text_size"))  # Ensures vertical alignment too
            table_card.add_widget(title_label)

            # Data Table
            data_table = MDDataTable(
                size_hint=(1, None),
                height=dp(300),
                use_pagination=True,
                rows_num=10,
                column_data=[
                    ("Roll No", dp(30)),
                    ("Name", dp(40)),
                    ("Date", dp(30)),
                    ("Status", dp(20))
                ],
                row_data=data,
                sorted_on="Date",
                sorted_order="DSC",
                elevation=0
            )
            table_card.add_widget(data_table)

            graphs_layout.add_widget(table_card)


if __name__ == '__main__':
    # Window.size = (1200, 800)
    FaceRecognitionApp().run()