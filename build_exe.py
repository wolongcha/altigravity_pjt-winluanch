import os
import sys
import subprocess
import shutil

def build():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app_py = os.path.join(base_dir, "app.py")
    icon_ico = os.path.join(base_dir, "icon.ico")
    icon_png = os.path.join(base_dir, "icon.png")

    print("Building AntigravityLauncher.exe with PyInstaller...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm",
        "--onedir",             # Onedir mode is much faster and cleaner for customtkinter
        "--windowed",           # Hide console window for launcher itself
        "--name", "AntigravityLauncher",
        "--icon", icon_ico,
        "--add-data", f"{icon_ico};.",
        "--add-data", f"{icon_png};.",
        "--collect-all", "customtkinter",
        app_py
    ]

    res = subprocess.run(cmd, cwd=base_dir)
    if res.returncode == 0:
        print("\nBuild Successful!")
        dist_exe = os.path.join(base_dir, "dist", "AntigravityLauncher", "AntigravityLauncher.exe")
        print(f"Executable path: {dist_exe}")

        # Automatically sign executable
        sign_script = os.path.join(base_dir, "sign_exe.ps1")
        if os.path.exists(sign_script):
            print("\nApplying code signing signature...")
            subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", sign_script], cwd=base_dir)
    else:
        print("\nBuild failed!")

if __name__ == "__main__":
    build()
