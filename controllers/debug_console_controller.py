"""
This module provides a class DebugConsoleController that can be used to control the debug console . The class provides methods to move the cursor to specific coordinates, press keys, and adjust the light setting of the console. The module requires the pygetwindow and pyautogui libraries to be installed.
"""
import pygetwindow as gw
import pyautogui
import time

class DebugConsoleController:
    """
    A class that controls the debug console of a specific application.

    Attributes:
    WINDOW_TITLE (str): The title of the debug console window.
    SETTING_MENU_X (int): The x-coordinate of the setting menu button.
    SETTING_MENU_Y (int): The y-coordinate of the setting menu button.
    ND_SETTING_X (int): The x-coordinate of the ND setting button.
    ND_SETTING_Y (int): The y-coordinate of the ND setting button.
    LIGHT_SETTING_X (int): The x-coordinate of the light setting button.
    LIGHT_SETTING_Y (int): The y-coordinate of the light setting button.
    DELIVERY_SETTING_X (int): The x-coordinate of the delivery setting button.
    DELIVERY_SETTING_Y (int): The y-coordinate of the delivery setting button.
    window (pygetwindow.Window): The window object of the debug console.
    """

    # Constants:
    WINDOW_TITLE = "デバッグコンソール"
    SETTING_MENU_X = 240
    SETTING_MENU_Y = 80
    ND_SETTING_X = 88
    ND_SETTING_Y = 205
    LIGHT_SETTING_X = 635
    LIGHT_SETTING_Y = 194
    DELIVERY_SETTING_X = 670
    DELIVERY_SETTING_Y = 194

    def __init__(self):
        """
        Initializes a new instance of the DebugConsoleController class.
        """
        self.window = None

    def move_and_click(self, x, y):
        """
        Moves the cursor to the specified coordinates and performs a left mouse click.

        Args:
        x (int): The x-coordinate of the target location.
        y (int): The y-coordinate of the target location.

        Returns:
        bool: True if the operation was successful, False otherwise.
        """
        # Convert window-relative coordinates to screen-relative
        if(self.window is None):
            print("Window not found!")
            return False
        else:
            screen_x = self.window.left + x
            screen_y = self.window.top + y

        # Move the cursor
        pyautogui.moveTo(screen_x, screen_y, duration=0.25)

        # Perform a left mouse click
        pyautogui.click()

        return True

    def press_key(self, key):
        """
        Presses the specified key.

        Args:
        key (str): The key to be pressed.

        Returns:
        None
        """
        # Press the key
        pyautogui.press(key)

    # Util Functions
    def tune_up_light(self):
        """
        Increases the light setting by one step.

        Returns:
        None
        """
        self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
        self.press_key('down')
        self.press_key('enter')
        self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)

    def tune_down_light(self):
        """
        Decreases the light setting by one step.

        Returns:
        None
        """
        self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
        self.press_key('up')
        self.press_key('enter')
        self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)
    
    def tune_to_target_level(self,target_level, current_level):
        """
        Adjusts the light setting to the specified target level.

        Args:
        target_level (int): The target light level (0-255).
        current_level (int): The current light level.

        Returns:
        None
        """
        # target level can only be 0 to 255
        if(target_level > 255):
            target_level = 255
        elif(target_level < 0):
            target_level = 0
        
        if target_level > current_level:
            num_of_press = target_level - current_level
            self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
            for i in range(num_of_press):
                self.press_key('down')
            self.press_key('enter')
            self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)
        elif target_level < current_level:
            num_of_press = current_level - target_level
            self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
            for i in range(num_of_press):
                self.press_key('up')
            self.press_key('enter')
            self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)
        else:
            pass
            
        

    def activate(self):
        """
        Activates the debug console window.

        Returns:
        bool: True if the operation was successful, False otherwise.
        """
        # Get a handle to the target application's window
        self.window = gw.getWindowsWithTitle(self.WINDOW_TITLE)[0]

        if self.window is None:
            print("Window not found!")
            return False

        # Bring the target application's window to the foreground
        self.window.activate()
        time.sleep(1)

        return True

    def reset_light_level(self):
        """
        Resets the light setting to the default value.
        a dumb method of resetting the light level
        scrolling all the way to the top and then scrolling all the way to light level 00

        Returns:
        None
        """
        self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
        # press home button
        self.press_key('home')
        for i in range(5):
            self.press_key('down')
        self.press_key('enter')
        self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)