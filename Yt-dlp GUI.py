import PySimpleGUI as sg
import subprocess
import sys

# Define the mapping from dropdown option to yt-dlp arguments
# Assuming 'yt-dlp' is in your system's PATH.
# If not, replace 'yt-dlp' with the full path to the executable.
COMMAND_MAP = {
    "audio playlist": [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--embed-thumbnail",
        "--parse-metadata", "description:(?s)(?P<meta_comment>.+)", # Argument string
        "--add-metadata",
        "-o", "%(playlist)s/%(playlist_index)s - %(title)s.%(ext)s" # Output template string
    ],
    "audio vg playlist": [ # Assuming 'vg' means video game, arguments adjusted based on input
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--embed-thumbnail",
        "--parse-metadata", "title:%(title)s - %(album)s",      # Metadata parsing
        "--parse-metadata", "playlist_index:%(track_number)s", # Metadata parsing
        "--parse-metadata", "description:(?s)(?P<meta_comment>.+)", # Metadata parsing
        "--add-metadata",
        "-o", "%(playlist)s\\%(playlist_index)s - %(title)s.%(ext)s" # Output template string (use \\ for literal backslash)
    ],
    "single song": [
        "yt-dlp",
        "-x",
        "--audio-format", "mp3",
        "--embed-thumbnail",
        "--parse-metadata", "description:(?s)(?P<meta_comment>.+)", # Argument string
        "--add-metadata",
        "-o", "%(title)s.%(ext)s" # Output template string
    ],
    "single video": [
        "yt-dlp",
        "-f", "mp4", # Specify format as mp4
        "-o", "%(title)s.%(ext)s" # Output template string
    ],
    "video playlist": [
        "yt-dlp",
        "-o", "%(playlist)s\\%(playlist_index)s - %(title)s.%(ext)s" # Output template string (use \\ for literal backslash)
    ],
}

options = list(COMMAND_MAP.keys()) # Use keys from the map for dropdown options

layout = [
    [sg.Text("Select download type:")],
    [sg.Combo(options, default_value="single video", key='-COMBO-', enable_events=True, readonly=True)], # readonly=True prevents typing
    [sg.Text("Enter URL(s):")],
    [sg.InputText(key='-URL_INPUT-', expand_x=True)], # Renamed key for clarity
    [sg.Button('Download', bind_return_key=True)]  # Renamed button for clarity
]

# Create the Window
window = sg.Window('Youtube Downloader', layout, resizable=True)

# Event Loop
while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == 'Download': # Check for the button click event
        selected_option = values['-COMBO-']
        user_input_url = values['-URL_INPUT-'].strip() # Get text and remove leading/trailing whitespace

        if not user_input_url:
            print("Please enter a URL.")
            continue # Skip execution if textbox is empty

        if selected_option not in COMMAND_MAP:
            print(f"Error: Unknown option selected: {selected_option}")
            continue # Skip execution if option is invalid

        # Get the base command and arguments from the map
        command_base = COMMAND_MAP[selected_option]

        # Construct the full command list
        # yt-dlp [options] URL(s)
        full_command = command_base + [user_input_url] # Append the user's URL to the argument list

        print(f"Attempting to run command: {full_command}")

        try:
            # Execute the command directly (no cmd.exe /C needed for yt-dlp)
            # Use CREATE_NO_WINDOW to hide the console window on Windows
            result = subprocess.run(
                full_command,          # Pass the command as a list of strings
                creationflags=subprocess.CREATE_NO_WINDOW, # Hide window on Windows
                check=False,           # Don't raise exception for non-zero exit codes
                capture_output=True,   # Capture stdout and stderr
                text=True,             # Decode stdout/stderr as text
                encoding='utf-8'       # Specify encoding
            )

            print(f"Command finished with return code: {result.returncode}")
            if result.stdout:
                print("--- STDOUT ---")
                print(result.stdout)
            if result.stderr:
                 print("--- STDERR ---")
                 print(result.stderr)

        except FileNotFoundError:
            print(f"Error: Executable '{full_command[0]}' not found.")
            print("Please ensure yt-dlp is installed and in your system's PATH.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

# Close the window
window.close()