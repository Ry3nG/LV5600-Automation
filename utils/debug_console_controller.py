import pygetwindow as gw
import pyautogui
import time

class DebugConsoleController:
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
        self.window = None

    def move_and_click(self, x, y):
        # Convert window-relative coordinates to screen-relative
        if(self.window is None):
            print("Window not found!")
            return False
        else:
            screen_x = self.window.left + x
            screen_y = self.window.top + y

        # Move the cursor
        pyautogui.moveTo(screen_x, screen_y, duration=0.25)
        time.sleep(0.5)

        # Perform a left mouse click
        pyautogui.click()
        time.sleep(0.5)

    def press_key(self, key):
        # Press the key
        pyautogui.press(key)
        time.sleep(0.5)

    # Util Functions
    def tune_up_light(self):
        self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
        self.press_key('down')
        self.press_key('enter')
        self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)

    def tune_down_light(self):
        self.move_and_click(self.LIGHT_SETTING_X, self.LIGHT_SETTING_Y)
        self.press_key('up')
        self.press_key('enter')
        self.move_and_click(self.DELIVERY_SETTING_X, self.DELIVERY_SETTING_Y)
    
    def tune_to_target_level(self,target_level, current_level):
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
        # Get a handle to the target application's window
        self.window = gw.getWindowsWithTitle(self.WINDOW_TITLE)[0]

        if self.window is None:
            print("Window not found!")
            return False

        # Bring the target application's window to the foreground
        self.window.activate()
        time.sleep(1)

        return True

def main():
    controller = DebugConsoleController()

    if not controller.activate():
        return

    # Operations
    controller.move_and_click(controller.SETTING_MENU_X, controller.SETTING_MENU_Y)
    controller.move_and_click(controller.ND_SETTING_X, controller.ND_SETTING_Y)
    controller.move_and_click(controller.LIGHT_SETTING_X, controller.LIGHT_SETTING_Y)
    controller.press_key('down')
    controller.press_key('enter')
    controller.move_and_click(controller.DELIVERY_SETTING_X, controller.DELIVERY_SETTING_Y)

if __name__ == "__main__":
    main()
