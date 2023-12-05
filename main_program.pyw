import os
import psutil
import time
from win10toast import ToastNotifier
from tkinter import Tk, Label, Button, Entry, messagebox, END
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
import threading

def show_notification(message):
    toaster = ToastNotifier()
    icon_path = 'icons8-connect-48.ico'
    toaster.show_toast("Uzi Battery Monitor 🩺🍂", message, duration=10, icon_path=icon_path)

def check_battery_and_update_gui():
    global charger_connected_prev

    while True:
        percent, power_plugged = check_battery_status()

        if percent is not None and power_plugged is not None:
            if not power_plugged:
                handle_unplugged_scenario(percent, power_plugged)
            else:
                if not charger_connected_prev:  # Only show if charger was disconnected in the previous iteration
                    show_notification("Charger Connected!")

            # Update the previous state after checking charger status
            charger_connected_prev = power_plugged

        # Sleep for 2 seconds before the next check
        time.sleep(2)

def handle_unplugged_scenario(percent, power_plugged):
    show_notification(f"Charger Unplugged! Battery: {percent}%")
    elapsed_time = 0  # Reset the elapsed time on unplug

    while not power_plugged and elapsed_time < turn_off_delay:
        time.sleep(10)  # Check every 10 seconds
        elapsed_time += 10

        # Check if charger is reconnected during the waiting period
        percent, power_plugged = check_battery_status()
        if power_plugged:
            show_notification("Charger reconnected. Resetting shutdown timer.")
            elapsed_time = 0  # Reset the elapsed time

    if not power_plugged and elapsed_time >= turn_off_delay:
        shutdown_with_confirmation()
        print("Laptop would be turned off now.")
        # Charger is reconnected or shutdown is canceled
        show_notification("Shutdown canceled.")
        elapsed_time = 0  # Reset the elapsed time

def check_battery_status():
    try:
        battery = psutil.sensors_battery()
        percent = battery.percent
        power_plugged = battery.power_plugged
        return percent, power_plugged
    except Exception as e:
        print(f"Error getting battery status: {e}")
        return None, None

def shutdown_with_confirmation():
    # Notify the user about the impending shutdown
    show_notification("Laptop will shut down in 1 minute. Click here to Cancel.")

    # Ask the user if they want to cancel the shutdown
    cancel_shutdown = messagebox.askyesno("Cancel Shutdown", "Do you want to cancel the shutdown?")

    if not cancel_shutdown:
        # User did not cancel, proceed with shutdown
        os.system("shutdown /s /t 60")

def update_settings():
    global notification_interval, turn_off_delay

    notification_interval = int(notification_entry.get()) * 60
    turn_off_delay = int(turnoff_entry.get()) * 60

    notification_label.config(text=f"Notification Interval: {notification_interval} seconds")
    turnoff_label.config(text=f"Turn-off Delay: {turn_off_delay} seconds")

# ... (other imports)

def minimize_to_tray(root, menu_icon):
    root.iconify()
    menu_icon.visible = True

def maximize_from_tray(root, menu_icon):
    root.deiconify()
    menu_icon.visible = False

def on_exit(icon, item):
    root.iconify()  # Minimize to the system tray
    icon.stop()

def create_window():
    root = Tk()
    root.title("Uzi Battery Monitor Settings")

    global notification_entry, turnoff_entry, notification_label, turnoff_label

    # Set column weights to make the columns center-aligned
    root.columnconfigure(0, weight=1)
    root.columnconfigure(1, weight=1)

    # Create and arrange widgets with a grid layout
    notification_label = Label(root, text=f"Notification Interval:")
    notification_label.grid(row=0, column=0, pady=10, sticky="e")

    notification_entry = Entry(root)
    notification_entry.insert(END, "1")  # Default value
    notification_entry.grid(row=0, column=1, pady=10, sticky="w")

    turnoff_label = Label(root, text=f"Turn-off Delay:")
    turnoff_label.grid(row=1, column=0, pady=10, sticky="e")

    turnoff_entry = Entry(root)
    turnoff_entry.insert(END, "2")  # Default value
    turnoff_entry.grid(row=1, column=1, pady=10, sticky="w")

    update_button = Button(root, text="Update Settings", command=update_settings)
    update_button.grid(row=2, column=0, columnspan=1, pady=10)

    shutdown_button = Button(root, text="Shutdown", command=shutdown_with_confirmation)
    shutdown_button.grid(row=2, column=0, columnspan=3, pady=10)

    # Set the size of the window
    root.geometry("400x200")

    # Add system tray functionality
    menu = [
        item('Open', lambda icon, item: maximize_from_tray(root, menu_icon)),
        item('Exit', lambda icon, item: on_exit(icon, item))
    ]
    image = Image.open('icons8-connect-48.ico')
    menu_icon = pystray.Icon("Uzi Battery Monitor", image, "Uzi Battery Monitor", menu)
    menu_icon.visible = False

    # Bind minimize_to_tray to the window minimize event
    root.protocol("WM_DELETE_WINDOW", lambda: minimize_to_tray(root, menu_icon))

    # Run the menu_icon
    menu_icon.run()

    return root

if __name__ == "__main__":
    notification_interval = 0.5 * 60  # 1 minute
    turn_off_delay = 1 * 60  # 2 minutes
    charger_connected_prev = psutil.sensors_battery().power_plugged  # Initial value

    # Create a thread for the battery checking loop
    battery_thread = threading.Thread(target=check_battery_and_update_gui, daemon=True)
    battery_thread.start()

    root = create_window()

    # Start the Tkinter main loop
    root.mainloop()

