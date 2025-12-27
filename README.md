# Ball-x-pit multi python mod

A custom mod for **Ball-x-Pit** created using Python.
This mod adds new behavior, features, or enhancements to the game by interacting with the game at runtime.



## Features

- Speeding up the game via a configurable keybind
- Enabling a hidden game mode
- Mutiple automation methods/quality-of-life features
- Various methods of cheating



## Requirements

- **Windows** (required for memory / hook libraries)
- Python 3.8+ (this was only tested on python 3.14 so it may not work on older versions)


### Python Dependencies

dearpygui
cyminhook
pylocalmem
pymousekey
colorama


## Installation
1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ball-x-pit-python-mod.git
   cd ball-x-pit-python-mod
   ```


2. **Install dependencies**

    pip install -r requirements.txt

3. **Move files to the game directory**

    Locate your game’s installation folder, then move all project files into that directory or make sure the files are installed globally so they can be imported from anywhere


4. **Load the mod**

    In order to actually be able to use the mod you need any python mod loader. If your on python 3.11 or earlier you can use the library called "pymem": https://github.com/srounet/Pymem and then using the "inject_python_interpreter" and "inject_python_shellcode" methods.
    Python 3.12+ injection is currently broken due to interpreter changes.