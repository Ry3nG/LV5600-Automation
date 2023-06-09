import tkinter as tk
from tkinter import ttk
from scripts import capture_and_send_performa, change_preset
import asyncio
from ttkthemes import ThemedStyle
from Constants import Constants


class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("LV5600 Automation")
        self.master.geometry("350x320")  # Set a fixed window size
        self.master.resizable(False, False)  # Disable window resizing
        self.grid(padx=20, pady=20)  # Add some padding to the grid
        
        # Define the "AccentButton" style
        style = ThemedStyle(self.master)
        style.set_theme("plastik")
        style.configure("AccentButton.TButton", foreground="black", font=("Helvetica", 10))

        self.create_widgets()

    def create_widgets(self):
        # Title label
        self.title_label = ttk.Label(self, text="Control Center", font=("Helvetica", 24), background="#002147", foreground="white")
        self.title_label.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

        # Two columns of buttons
        for i in range(1, 6):
            if i == 1:
                btn_1 = ttk.Button(self, text=f"Capture and Send BMP", command=self.start_capture, width=20, style="AccentButton.TButton")
            elif i == 2:
                btn_1 = ttk.Button(self, text=f"Change Preset", command=self.change_preset, width=20, style="AccentButton.TButton")
            else:
                btn_1 = ttk.Button(self, text=f"Shortcut {i}", width=20, style="AccentButton.TButton")
            btn_1.grid(row=i, column=0, pady=5)
            btn_2 = ttk.Button(self, text=f"Shortcut {i+5}", width=20, style="AccentButton.TButton")
            btn_2.grid(row=i, column=1, pady=5)

        # Bottom label
        self.bottom_label = ttk.Label(self, text="MRDD M015 @ Olympus OSP", font=("Helvetica", 16), background="#002147", foreground="white")
        self.bottom_label.grid(row=6, column=0, columnspan=2, pady=10, sticky="ew")

    def start_capture(self):
        asyncio.run(capture_and_send_performa.run(Constants.IP_ADDRESS_TELNET, Constants.USERNAME_TELNET, Constants.PASSWORD_TELNET, Constants.IP_ADDRESS_FTP, Constants.USERNAME_FTP, Constants.PASSWORD_FTP))

    def change_preset(self):
        # Create a new window for user input
        self.preset_window = tk.Toplevel(self.master)
        self.preset_window.title("Change Preset")

        

        # Calculate the x and y coordinates of the top-left corner of the window
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 350
        window_height = 50
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.preset_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # Prompt label
        self.prompt_label = ttk.Label(self.preset_window, text="Enter preset number:")
        self.prompt_label.grid(row=0, column=0)

        # Input field
        self.input_area = ttk.Entry(self.preset_window)
        self.input_area.grid(row=0, column=1)

        # Submit button
        self.submit_button = ttk.Button(self.preset_window, text="Submit", command=self.submit_input, style="AccentButton.TButton")
        self.submit_button.grid(row=1, column=0, columnspan=2)

    def submit_input(self):
        user_input = self.input_area.get()  # Get the user input
        self.input_area.delete(0, tk.END)  # Clear the input field
        self.preset_window.destroy()  # Close the window
        asyncio.run(change_preset.run(Constants.IP_ADDRESS_TELNET, Constants.USERNAME_TELNET, Constants.PASSWORD_TELNET, user_input))

def main():
    root = tk.Tk()
    root.configure(background="white")
    app = Application(master=root)
    app.mainloop()

if __name__ == "__main__":
    main()
