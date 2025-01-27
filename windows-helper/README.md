# PySide6 Helper Tool for Windows

## Overview

This project is a desktop application built using **PySide6**, designed to serve as a versatile helper tool for Windows. The tool provides an intuitive and user-friendly interface to perform a variety of tasks and enhance productivity.

## Features

- **Color Picker:** Select and copy HEX color values on your screen.
- **CMD Runner:** Save and execute custom command line instructions.
- **Chance:** flip a coin, roll a dice
- **Interface:** Runs at top layer and toggleable through hotkey. Adjustable layouts to fit your preferences.

  ![Color Picker Demo](demo/color.gif)
  ![CMD Runner Demo](demo/cmd.gif)

## Installation

### Option 1: Installing from ZIP and Running the Executable

To quickly set up and run the application:

1. **Download and Extract the ZIP file:**

   - Download the latest `windows-helper.zip` file from the releases page.
   - Extract the contents to your desired location on your computer.

2. **Run the Application:**
   - Navigate to the extracted folder.
   - Double-click on `windows-helper.exe` to launch the application.

### Option 2: Running Locally and Building the Executable

To run the application locally or build it as a standalone executable, follow these steps:

1. **Clone the repository:**

   ```bash
   git clone https://github.com/LeoCh01/windows-helper.git
   ```

2. **Set up the Python environment:**

   - Create a virtual environment in project directory:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     ```bash
     venv\Scripts\activate
     ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application locally:**

   - Once the environment is set up, you can run the app by executing:
     ```bash
     python windows-helper.py
     ```

5. **Convert to Executable (Optional):**
   - If you want to convert the application into a standalone `.exe` file, run the following command:
     ```bash
     pyinstaller --noconsole --onefile --icon=res/icon.ico windows-helper.py
     ```
   - The `.exe` file will be generated in the `dist` folder inside the project directory.

## Contact

For any inquiries or support, please reach out to leocheng333375749@gmail.com
