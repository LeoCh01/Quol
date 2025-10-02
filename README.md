# PySide6 Quick Tools for Windows

## Overview

Quol (Quick-Tool) is an overlay desktop application built using **PySide6**, designed to serve as a versatile toolbox for Windows. The toolbox provides an intuitive and user-friendly interface to perform a variety of tasks and enhance productivity.

## Features

- **Chat:** Run AI prompts on your screen.
- **Draw:** Draw and annotate on your screen.
- **Key mapper:** Create key bindings to custom actions.
- **Color Picker:** Select and copy HEX color values on your screen.

This application Runs at the top layer and is toggleable through a hotkey. Layouts are adjustable to fit your preferences. More features can be found in the built-in store or at the [Quol-Tools](https://github.com/LeoCh01/Quol-Tools) repository.

[//]: # '<img src="demo/snip.png" width="500">'

<table>
  <tr>
    <td><img src="demo/quol-chat.gif" width="250"></td>
    <td><img src="demo/wh-draw.gif" width="250"></td>
  </tr>
  <tr>
    <td><img src="demo/wh-color.gif" width="250"></td>
    <td><img src="demo/wh-cmd.gif" width="250"></td>
  </tr>
</table>

## Installation

### Option 1: Installing from ZIP and Running the Executable

Click [here](https://github.com/LeoCh01/Quol/releases) for the latest release of Quol.

1. **Download and Extract the ZIP file:**

   - Download the latest `Quol.zip` file from the releases page.
   - Extract the contents to your desired location on your computer.

2. **Run the Application:**
   - Navigate to the extracted folder.
   - Double-click on `Quol.exe` to launch the application.

### Option 2: Running Locally

To run the application locally or build it as a standalone executable, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/LeoCh01/quol.git
   ```

2. **Set up the Python environment (Python 3.12 or greater recommended):**

   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application locally:**

   - Once the environment is set up, you can run the app by executing:

   ```bash
   python app/main.py
   ```

5. **Building the Executable (Optional):**

   - you can also build the exe yourself by installing `pyinstaller` and using the `quol.spec` file

   ```bash
     pyinstaller quol.spec
   ```

## Adding Custom Tools

To create a new tool, you can add a folder to the `tools` directory and add the folder name in the `settings.json` file. You can use the template provided in `tools/example` folder as a starting point.

```
example/
├── windows.py
├── res/config.json
└── lib/ (optional)
```

- `windows.py`: main window script.
- `res/`: images and other miscellaneous items.
- `res/config.json`: configurations linked to window script.
- `lib/`: additional libraries/scripts to be dynamically loaded.

By following these steps, you can easily add custom tools without rebuilding the application.

## Contact

For any support, please reach out to ch3.leoo@gmail.com
