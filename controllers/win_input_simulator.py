from ctypes import POINTER, c_void_p, cdll, c_wchar_p, c_int, c_ushort
import logging


class WinInputSimulator():
    # Error Codes
    SUCCESS = 0
    WINDOW_NOT_FOUND = 1
    FAILED_TO_ACTIVATE = 2
    FAILED_TO_PRESS_KEY = 3
    FAILED_TO_MOVE_CURSOR = 4
    FAILED_TO_LEFT_CLICK = 5
    FAILED_TO_RIGHT_CLICK = 6
    FAILED_TO_SCROLL = 7
    CURSOR_OUT_OF_BOUNDS = 8
    FAILED_TO_GET_WINDOW_RECT = 9
    FAILED_TO_SET_CURSOR_POS = 10
    UNKNOWN_ERROR = 99

    DLL_error_code = {
        SUCCESS: "Success",
        WINDOW_NOT_FOUND: "Window not found",
        FAILED_TO_ACTIVATE: "Failed to activate window",
        FAILED_TO_PRESS_KEY: "Failed to press key",
        FAILED_TO_MOVE_CURSOR: "Failed to move cursor",
        FAILED_TO_LEFT_CLICK: "Failed to left click",
        FAILED_TO_RIGHT_CLICK: "Failed to right click",
        FAILED_TO_SCROLL: "Failed to scroll",
        CURSOR_OUT_OF_BOUNDS: "Cursor out of bounds",
        FAILED_TO_GET_WINDOW_RECT: "Failed to get window rect",
        FAILED_TO_SET_CURSOR_POS: "Failed to set cursor position",
        UNKNOWN_ERROR: "Unknown error",
    }


    def __init__(self):
        self.myDLL = cdll.LoadLibrary('lib\\WinInputSimulator.dll')
        if not self.myDLL:
            raise Exception("Could not load DLL")
        else:
            logging.info("WinInputSimulator DLL loaded successfully")

        self.activate = self.myDLL.Activate
        self.activate.argtypes = [c_wchar_p, c_int]
        self.activate.restype = c_int

        self.press_key = self.myDLL.PressKey
        self.press_key.argtypes = [c_wchar_p, c_ushort, c_int]
        self.press_key.restype = c_int

        self.move_cursor = self.myDLL.MoveCursor
        self.move_cursor.argtypes = [c_wchar_p, c_int, c_int, c_int]
        self.move_cursor.restype = c_int

        self.left_click = self.myDLL.LeftClick
        self.left_click.argtypes = [c_wchar_p, c_int]
        self.left_click.restype = c_int

        self.get_windows_with_title = self.myDLL.GetWindowsWithTitle
        self.get_windows_with_title.argtypes = [c_wchar_p, POINTER(c_void_p), POINTER(c_int)]
        self.get_windows_with_title.restype = None
    
    def get_windows(self, title):
        # Allocate an array for the window handles
        max_windows = 10  # Maximum number of windows you expect to find
        array_type = c_void_p * max_windows  # Create a type for an array of c_void_p
        window_array = array_type()  # Create an instance of that array type

        # Create a variable to hold the number of windows found
        num_windows = c_int(max_windows)

        # Call the function
        self.get_windows_with_title(c_wchar_p(title), window_array, num_windows)

        # Convert the result to a Python list
        return [window_array[i] for i in range(num_windows.value)]