# QR Code Generator App 🚀

## Overview
This is a standalone desktop application built with Python and CustomTkinter that generates stylish, customizable UPI QR codes with additional features like PDF export, clipboard copy, and image saving. All assets are self-contained inside the app.

## 🧩 Features
- Custom name and UPI ID input fields  
- Real-time QR preview  
- Export to PDF option  
- Save QR and copy to clipboard  
- Pre-styled modern CustomTkinter UI  
- Fully offline and standalone execution  

## 🗂️ Folder Structure
```
QR-App/
├── Assets/
│   ├── Icon.ico
│   ├── logo.png
│   ├── background.png
├── main.py
├── requirements.txt
├── README.md
```

## 🧱 Tech Stack
- Python 3.x  
- CustomTkinter  
- Pillow (PIL)  
- qrcode  
- reportlab  
- pyinstaller (for EXE creation)  

## ⚙️ Run Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/YourUsername/QR-App.git
   ```

2. Navigate into the project folder:
   ```bash
   cd QR-App
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the app:
   ```bash
   python main.py
   ```

## 💡 Build EXE
To create a standalone executable (with your app icon included):
```bash
pyinstaller --onefile --noconsole --icon=Assets\Icon.ico main.py
```
The generated EXE will appear inside the **dist** folder.

## 📸 Preview
![App Screenshot](Assets/screenshot.png)

## 🏆 Credits
Developed by **Atharva Nitin Bhoir** 💻  
Portfolio: [https://your-portfolio-link.com](https://your-portfolio-link.com)
