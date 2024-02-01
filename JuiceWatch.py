import os
import sys
import atexit
import subprocess
import psutil
import time
from win10toast import ToastNotifier
import tkinter as tk
from tkinter import Tk, Label, Button, Entry, ttk, messagebox, PhotoImage, END
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading
import logging

#  logging
logging.basicConfig(filename='JuiceWatch.log', level=logging.DEBUG)


LOCK_FILE_PATH = "JuiceWatch.lock"

app_name = "JuiceWatch.exe"

def acquire_lock():
    try:
        #  the lock file to avoid multiple runs of same program
        with open(LOCK_FILE_PATH, "x") as lock_file:
            #  timestamp to the lock file
            lock_file.write(f"{time.time()}\n")
        return True
    except FileExistsError:
        return False


def release_lock():
    # Remove the lock file
    try:
        os.remove(LOCK_FILE_PATH)
    except FileNotFoundError:
        pass  # It's okay if the file is not found when releasing the lock


def update_lock_timestamp():
    # write timestamp
    with open(LOCK_FILE_PATH, "a") as lock_file:
        lock_file.write(f"{time.time()}\n")


def check_lock_expiration():
    try:
        # Read the timestamp from the lock file
        with open(LOCK_FILE_PATH, "r") as lock_file:
            timestamp = float(lock_file.readline().strip())

        # threshhold check
        return time.time() - timestamp > 600  # 10 minutes in seconds
    except FileNotFoundError:
        return False


def check_if_already_running():
    if not acquire_lock():
        # logging.info("Another instance of the program is already running. Attempting to take control.")
        show_notification(
            "Another instance of the program is already running. Taking control.")

        # Try to find the process ID of the existing instance
        existing_instance_pid = find_existing_instance_pid()

        if existing_instance_pid is not None:
            try:
                # Terminate the existing instance
                existing_process = psutil.Process(existing_instance_pid)
                existing_process.terminate()
                logging.info("Terminated the existing instance.")
            except Exception as e:
                logging.info(f"Failed to terminate the existing instance: {e}")

        # Release the lock since the program is exiting
        release_lock()

        # Wait for a short time to allow the existing instance to terminate
        time.sleep(1)

        # Try to acquire the lock again
        if not acquire_lock():
            logging.info("Could not take control. Exiting.")
            sys.exit()
        else:
            logging.info("Successfully took control.")
            show_notification("Successfully took control.")

            os.remove(LOCK_FILE_PATH)

            restart_program()


def restart_program():
    python = sys.executable
    script = os.path.abspath(__file__)
    subprocess.Popen([python, script] + sys.argv[1:], creationflags=subprocess.CREATE_NEW_CONSOLE)



def find_existing_instance_pid():
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == f'{app_name}' and proc.info['pid'] != current_pid:
            return proc.info['pid']
    return None


def schedule_updates(func, interval):
    while True:
        time.sleep(interval)
        func()


# Global variable to track the state of the charger connection
charger_connected_prev = None


def show_notification(message):
     toaster = ToastNotifier()
     icon_path = 'icon.ico'  #  the path to your .ico file
     if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
            icon_path = os.path.join(sys._MEIPASS, "icon.ico")

    # Check if the icon file exists
     if not os.path.exists(icon_path):
        # If the file doesn't exist, provide a default icon or handle the error accordingly
        logging.info(f"Error: Icon file '{icon_path}' not found.")
        return

     toaster.show_toast("JuiceWatch 🩺🍂", message ,duration=3, icon_path=icon_path)


def check_battery_and_update_gui():
    global charger_connected_prev

    while True:
        percent, power_plugged = check_battery_status()

        if percent is not None and power_plugged is not None:
            if not power_plugged:
                handle_unplugged_scenario(percent, power_plugged)
            else:
                if charger_connected_prev is not None and not charger_connected_prev:
                    show_notification("Charger Connected!")

            charger_connected_prev = power_plugged

        time.sleep(2)


def handle_unplugged_scenario(percent, power_plugged):
    show_notification(f"Charger Unplugged! Battery: {percent}%")
    elapsed_time = 0

    while not power_plugged and elapsed_time < turn_off_delay:
        time.sleep(10)
        elapsed_time += 10

        percent, power_plugged = check_battery_status()
        if power_plugged:
            show_notification("Charger reconnected. Resetting shutdown timer.")
            elapsed_time = 0

    if not power_plugged and elapsed_time >= turn_off_delay:
        shutdown_with_confirmation()
        logging.info("Laptop would be turned off now.")
        show_notification("Shutdown canceled.")
        elapsed_time = 0


def check_battery_status():
    try:
        battery = psutil.sensors_battery()
        if battery is not None:
            percent = battery.percent
            power_plugged = battery.power_plugged
            return percent, power_plugged
        else:
            logging.info("No battery found.")
            return 0, None
    except AttributeError as e:
        logging.info(f"Error accessing battery attributes: {e}")
        return 0, None
    except Exception as e:
        logging.info(f"Error getting battery status: {e}")
        return 0, None


def shutdown_with_confirmation():
    show_notification(
        "Laptop will shut down in 1 minute. Click here to Cancel.")
    cancel_shutdown = messagebox.askyesno(
        "Cancel Shutdown", "Do you want to cancel the shutdown?")

    if not cancel_shutdown:
        os.system("shutdown /s /t 60")


def update_settings():
    global notification_entry, turnoff_entry, notification_label, turnoff_label
    global notification_interval, turn_off_delay, current_notification_label, current_turnoff_label

    try:
        notification_interval = int(notification_entry.get()) * 60
        turn_off_delay = int(turnoff_entry.get()) * 60

        notification_label.config(text=f"Notification Interval: {notification_interval} seconds")
        turnoff_label.config(text=f"Turn-off Delay: {turn_off_delay} seconds")

        # Update the current labels
        current_notification_label.config(text=f"Current Notification Interval: {notification_interval // 60} minutes")
        current_turnoff_label.config(text=f"Current Turn-off Delay: {turn_off_delay // 60} minutes")
    except Exception as e:
        logging.info(f"Error updating settings: {e}")



def create_info_notification():
    message = "This Program helps check when laptop charger disconnected🙄,if the user doesn't connect, it shuts down the laptop to save the user's battery."
    show_notification(message)


def opening_settings():
    message = "Settings..."
    show_notification(message)

def opening_about():
    message = "About.."
    show_notification(message)


notification_entry = None
turnoff_entry = None
about_tab = None
current_notification_label = None
current_turnoff_label = None
menu_icon = None

def open_settings_window():
    global notification_entry, turnoff_entry, notification_label, turnoff_label, current_notification_label, current_turnoff_label

    settings_window = tk.Tk()
    settings_window.title("Juice Watch Settings")

    if os.path.exists(icon_path):
        settings_window.iconbitmap(icon_path)

    # Create a notebook to hold the tabs
    notebook = ttk.Notebook(settings_window)
    notebook.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    # Create the first tab for settings
    settings_tab = ttk.Frame(notebook)
    notebook.add(settings_tab, text="Settings")

    # Additional label for the message
    message_label = ttk.Label(settings_tab, text="Enter The time in minutes")
    message_label.grid(row=0, column=0, pady=(10, 5), sticky="w")

    notification_frame = ttk.Frame(settings_tab, padding="10 5 10 5")
    notification_frame.grid(row=1, column=0, sticky="ew")

    notification_label = ttk.Label(notification_frame, text="Notification Interval:")
    notification_label.grid(row=0, column=0, pady=10, sticky="e")

    notification_entry = ttk.Entry(notification_frame)
    notification_entry.insert(tk.END, "1")
    notification_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    # Label to display the current notification interval
    current_notification_label = ttk.Label(notification_frame, text="")
    current_notification_label.grid(row=1, column=1, padx=(0, 10), sticky="ew")

    turnoff_frame = ttk.Frame(settings_tab, padding="10 5 10 5")
    turnoff_frame.grid(row=2, column=0, sticky="ew")

    turnoff_label = ttk.Label(turnoff_frame, text="Turn-off Delay(mins):")
    turnoff_label.grid(row=0, column=0, sticky="w")

    turnoff_entry = ttk.Entry(turnoff_frame)
    turnoff_entry.insert(tk.END, "2")
    turnoff_entry.grid(row=0, column=1, padx=(0, 10), sticky="ew")

    # Label to display the current turn-off delay
    current_turnoff_label = ttk.Label(turnoff_frame, text="")
    current_turnoff_label.grid(row=1, column=1, padx=(0, 10), sticky="ew")

    button_frame = ttk.Frame(settings_tab, padding="10 5 10 5")
    button_frame.grid(row=3, column=0, sticky="ew")

    update_button = ttk.Button(button_frame, text="Update Settings", command=update_settings)
    update_button.grid(row=0, column=0, padx=5)

    shutdown_button = ttk.Button(button_frame, text="Shutdown", command=shutdown_with_confirmation)
    shutdown_button.grid(row=0, column=1, padx=5)

    # Display current settings values
    display_current_settings_values()

    # Create the second tab for program information
    about_tab = ttk.Frame(notebook)
    notebook.add(about_tab, text="About Program")


    about_label = ttk.Label(
     about_tab, text="JuiceWatch\nVersion 1.0\n© 2024 Trakexcel Agency-@Uzitrake")
    about_label.pack(padx=20, pady=14)

    explanation_text = (
    "JuiceWatch is a battery monitoring program designed to provide real-time insights\n"
    "into your laptop's battery status. Here's how you can use JuiceWatch:\n\n"
    "Usage:\n"
    "1. Launch JuiceWatch and configure your notification settings.\n"
    "2. The program will continuously monitor your laptop's battery status.\n"
    "3. Receive notifications for charger connection and disconnection events.\n"
    "4. Customize notification intervals and turn-off delays to suit your preferences.\n"
    "5. Optionally, manually initiate a shutdown using the 'Shutdown' button.\n\n"
    "JuiceWatch helps you conserve battery life by taking proactive actions when your\n"
    "laptop is not connected to the charger. Stay informed and in control of your power usage!"
    )

    explanation_label = ttk.Label(
      about_tab, text=explanation_text, anchor="w", justify="left")
    explanation_label.pack(padx=20, pady=20, fill="both")



    # Handle window closure event
    settings_window.protocol("WM_DELETE_WINDOW", lambda: on_settings_window_close(settings_window))


# def show_about_tab():
#     notebook.select(about_tab)

def display_current_settings_values():
    # Get the current values from the entry fields
    current_notification_value = notification_entry.get()
    current_turnoff_value = turnoff_entry.get()

    # Update the labels to display the current values
    current_notification_label.config(text=f"Current Notification Interval: {current_notification_value} minutes")
    current_turnoff_label.config(text=f"Current Turn-off Delay: {current_turnoff_value} minutes")


    # settings_window.geometry("400x200")


def on_settings_window_close(settings_window):
    settings_window.iconify()  # Minimize to the taskbar
    settings_window.withdraw()  # Hide the window from the taskbar

    release_lock()

    if os.path.exists(LOCK_FILE_PATH):
        try:

            os.remove(LOCK_FILE_PATH)
        except Exception as e:
            logging.info(f"Error while removing lock file: {e}")

    restart_program()


def minimize_to_tray(settings_window, menu_icon):
    settings_window.iconify()  # Minimize to the system tray
    settings_window.withdraw()

    menu_icon.visible = True


def maximize_from_tray(root, menu_icon):
    # root.deiconify()
    menu_icon.visible = False


def on_exit(icon, item):
    root.iconify()
    icon.stop()


def exit_program(icon, item):
    response = messagebox.askyesno(
        "Exit Program", "Are you sure you want to exit?")
    if response:
        icon.stop()
        release_lock()
        root.destroy()
        os._exit(0)


def show_notification_thread(message):
    notification_thread = threading.Thread(
        target=show_notification, args=(message,))
    notification_thread.start()

def show_initial_notification():
    show_notification_thread("JuiceWatch is running. Click the icon in the system tray to access the program.")

def release_lock_at_exit():
    # Attempt to acquire the lock
    acquired = acquire_lock()

    if acquired:
        # Release the lock only if it was successfully acquired
        release_lock()
    else:
        logging.info("Lock was not acquired. Another instance is already running.")


def initialize_icons():
    global notification_icon, turnoff_icon, icon_path

    turnoff_icon = 'turnoff.png'  #  the path to your .ico file
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        turnoff_icon = os.path.join(sys._MEIPASS, "turnoff.png")

    notification_icon = 'notify.png'  #  the path to your .ico file
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        notification_icon = os.path.join(sys._MEIPASS, "notify.png")

    icon_path = 'icon.ico'  #  the path to your .ico file
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")

if __name__ == "__main__":
    check_if_already_running()

    # Check if the lock has expired
    if check_lock_expiration():
        logging.info("Lock has expired. Exiting.")
        # show_notification("Lock has expired. Exiting.")
        sys.exit()

    notification_interval = 0.5 * 60
    turn_off_delay = 1 * 60

    # Initialize charger_connected_prev based on the initial battery status
    _, charger_connected_prev = check_battery_status()

    battery_thread = threading.Thread(
        target=check_battery_and_update_gui, daemon=True)
    battery_thread.start()

    root = Tk()
    root.withdraw()

    initialize_icons()

    menu = [
        item('Settings', lambda icon, item: (
            opening_settings(), open_settings_window())),
        item('Mini info', lambda icon, item: show_notification_thread(
            "This Program helps check when laptop charger disconnected🙄, if the user doesn't connect, it shuts down the laptop to save the user's battery.")),
        item('Program Info', lambda icon, item: (opening_about(), open_settings_window())),
        item('Exit Program', lambda icon, item: exit_program(menu_icon, item)),
    ]


    icon_path = 'icon.ico'  #  the path to your .ico file
    if getattr(sys, 'frozen', False):  # Check if running as a PyInstaller executable
        icon_path = os.path.join(sys._MEIPASS, "icon.ico")

    image = Image.open(icon_path)
    menu_icon = pystray.Icon("Juice Watch",
                             image, "Juice Watch", menu)
    menu_icon.visible = False
    
    #show notification its in the notification panel
    show_initial_notification()

    root.protocol("WM_DELETE_WINDOW",
                  lambda: minimize_to_tray(root, menu_icon))

    atexit.register(release_lock_at_exit)

    # thread to update the lock timestamp every 10 minutes
    lock_update_thread = threading.Thread(
        target=lambda: schedule_updates(update_lock_timestamp, 600), daemon=True)
    lock_update_thread.start()

    menu_icon.run()

    root.mainloop()

    release_lock()

