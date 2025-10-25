import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image, ImageDraw, ImageFont, ImageOps
from customtkinter import CTkImage
import os, io, json, sys
import qrcode
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import A4
import win32clipboard

# -------------------- Helper for PyInstaller paths --------------------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        base_path = sys._MEIPASS  # PyInstaller temp folder
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# -------------------- Constants --------------------
BASE_FOLDER = r"C:\AtharvaSolutions"
DATA_FILE = os.path.join(BASE_FOLDER, "user_data.json")
if not os.path.exists(BASE_FOLDER):
    os.makedirs(BASE_FOLDER)

# -------------------- User Data --------------------
def load_user_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_user_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

# -------------------- Font helper --------------------
def load_truetype(fontname="arial.ttf", size=14):
    font_path = resource_path(fontname)
    try:
        if os.path.exists(font_path):
            return ImageFont.truetype(font_path, size)
    except Exception:
        pass
    try:
        return ImageFont.truetype("arial.ttf", size)
    except Exception:
        return ImageFont.load_default()

# -------------------- Payment App --------------------
class PaymentApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Atharva Solutions - Payment QR")
        self.geometry("700x750")
        ctk.set_appearance_mode("dark")

        self.user_data = load_user_data()
        self.generated_qr = None  # PIL Image

        self.frames = {}
        for F in (WelcomePage, UPIPage, NamePage, HomePage, QRPage):
            frame = F(self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        if "upi_id" in self.user_data and "name" in self.user_data:
            self.show_frame(HomePage)
        else:
            self.show_frame(WelcomePage)

    def show_frame(self, page_class):
        frame = self.frames[page_class]
        frame.tkraise()

# -------------------- Pages --------------------
class WelcomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Welcome to Atharva Solutions", font=("Arial", 24)).pack(pady=30)
        ctk.CTkLabel(self, text="Generate professional UPI QR codes easily", font=("Arial", 16)).pack(pady=10)
        ctk.CTkButton(self, text="Next", command=lambda: master.show_frame(UPIPage)).pack(pady=20)

class UPIPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Enter your UPI ID", font=("Arial", 18)).pack(pady=30)
        self.entry = ctk.CTkEntry(self, placeholder_text="example@upi")
        self.entry.pack(pady=10)
        if master.user_data.get("upi_id"):
            self.entry.insert(0, master.user_data["upi_id"])
        ctk.CTkButton(self, text="Next", command=self.save_upi).pack(pady=20)
        self.master = master

    def save_upi(self):
        upi_id = self.entry.get().strip()
        if not upi_id:
            messagebox.showerror("Error", "UPI ID cannot be empty")
            return
        self.master.user_data["upi_id"] = upi_id
        save_user_data(self.master.user_data)
        self.master.show_frame(NamePage)

class NamePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Enter your Name", font=("Arial", 18)).pack(pady=30)
        self.entry = ctk.CTkEntry(self, placeholder_text="Your Name")
        self.entry.pack(pady=10)
        if master.user_data.get("name"):
            self.entry.insert(0, master.user_data["name"])
        ctk.CTkButton(self, text="Finish Setup", command=self.save_name).pack(pady=20)
        self.master = master

    def save_name(self):
        name = self.entry.get().strip()
        if not name:
            messagebox.showerror("Error", "Name cannot be empty")
            return
        self.master.user_data["name"] = name
        save_user_data(self.master.user_data)
        self.master.show_frame(HomePage)

class HomePage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        ctk.CTkLabel(self, text="Home - Generate QR", font=("Arial", 22)).pack(pady=20)

        self.amount_entry = ctk.CTkEntry(self, placeholder_text="Enter Amount (₹)")
        self.amount_entry.pack(pady=10)

        preset_frame = ctk.CTkFrame(self)
        preset_frame.pack(pady=5)
        for amt in [100, 500, 1000, 2000]:
            ctk.CTkButton(preset_frame, text=f"₹{amt}", width=60,
                          command=lambda a=amt: self.amount_entry.delete(0,"end") or self.amount_entry.insert(0,str(a))
                         ).pack(side="left", padx=5)

        ctk.CTkButton(self, text="Generate QR", command=self.generate_qr).pack(pady=20)
        ctk.CTkButton(self, text="Change UPI ID", command=self.change_upi).pack(pady=5)

    def generate_qr(self):
        amount = self.amount_entry.get().strip()
        if amount:
            if not (amount.replace('.', '', 1).isdigit()) or float(amount) <= 0:
                messagebox.showwarning("Invalid", "Enter an amount greater than ₹0")
                return

        upi_id = self.master.user_data.get("upi_id", "")
        name = self.master.user_data.get("name", "Merchant")

        params = f"pa={upi_id}&pn={name}"
        if amount:
            params += f"&am={amount}"
        params += "&cu=INR"
        upi_link = f"upi://pay?{params}"

        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=4)
        qr.add_data(upi_link)
        qr.make(fit=True)
        img_qr = qr.make_image(fill_color="black", back_color="white").convert("RGBA")

        canvas_w, canvas_h = 400, 500
        card = Image.new("RGBA", (canvas_w, canvas_h), (255,255,255,255))
        draw = ImageDraw.Draw(card)

        font_path = resource_path("arial.ttf")
        title_font = load_truetype(font_path, 22)
        upi_font = load_truetype(font_path, 16)
        tag_font = load_truetype(font_path, 13)

        top_y = 60
        draw.text((canvas_w//2, top_y), name.upper(), fill=(0,0,0), font=title_font, anchor="ms")

        qr_target = 260
        img_qr = img_qr.resize((qr_target, qr_target), Image.LANCZOS)
        qr_x = (canvas_w - qr_target)//2
        qr_y = 60
        card.paste(img_qr, (qr_x, qr_y), img_qr)

        upi_y = qr_y + qr_target + 10
        draw.text((canvas_w//2, upi_y), upi_id, fill=(60,60,60), font=upi_font, anchor="ms")

        logos = ["Asset/GPay.png", "Asset/Paytm.png", "Asset/PhonePe.png", "Asset/UPI-Logo.png"]
        logos_present = [resource_path(l) for l in logos if os.path.exists(resource_path(l))]

        logo_size = 36
        spacing = 10
        if logos_present:
            total_w = len(logos_present)*logo_size + (len(logos_present)-1)*spacing
            start_x = (canvas_w - total_w)//2
            logo_y = upi_y + 24
            for i, p in enumerate(logos_present):
                try:
                    li = Image.open(p).convert("RGBA")
                    li.thumbnail((logo_size, logo_size), Image.LANCZOS)
                    paste_x = start_x + i*(logo_size + spacing)
                    tile = Image.new("RGBA", (logo_size, logo_size), (255,255,255,0))
                    tile.paste(li, ((logo_size - li.size[0])//2, (logo_size - li.size[1])//2), li)
                    card.paste(tile, (paste_x, logo_y), tile)
                except Exception:
                    pass
            tag_y = logo_y + logo_size + 14
        else:
            tag_y = upi_y + 28

        draw.text((canvas_w//2, tag_y),
                  "Scan and pay with any BHIM UPI app",
                  fill=(90,90,90), font=tag_font, anchor="ms")

        self.master.generated_qr = card
        self.master.generated_qr_link = upi_link
        self.master.show_frame(QRPage)

    def change_upi(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to change UPI ID? This will reset saved data."):
            if os.path.exists(DATA_FILE):
                os.remove(DATA_FILE)
            self.master.user_data = {}
            self.master.show_frame(UPIPage)

class QRPage(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.main_container = ctk.CTkFrame(self, corner_radius=8)
        self.main_container.pack(pady=25, padx=25, fill="both", expand=True)

        self.qr_canvas = ctk.CTkLabel(self.main_container, text="")
        self.qr_canvas.pack(pady=(10, 5))

        btn_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        btn_frame.pack(pady=10)
        ctk.CTkButton(btn_frame, text="Back", width=110,
                      command=lambda: master.show_frame(HomePage)).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Copy QR", width=110,
                      command=self.copy_qr).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Save QR", width=110,
                      command=self.save_qr).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Export PDF", width=110,
                      command=self.export_pdf).pack(side="left", padx=5)

    def tkraise(self, *args, **kwargs):
        super().tkraise(*args, **kwargs)
        if self.master.generated_qr:
            display_img = self.master.generated_qr.copy()
            preview_w, preview_h = 360, 440
            display_img = ImageOps.contain(display_img, (preview_w, preview_h))
            self.tk_img = CTkImage(light_image=display_img, dark_image=display_img,
                                   size=(display_img.width, display_img.height))
            self.qr_canvas.configure(image=self.tk_img)

    def save_qr(self):
        if self.master.generated_qr:
            path = filedialog.asksaveasfilename(defaultextension=".png",
                                                filetypes=[("PNG Files","*.png")])
            if path:
                self.master.generated_qr.save(path)
                messagebox.showinfo("Saved", f"QR saved at {path}")

    def export_pdf(self):
        if self.master.generated_qr:
            path = filedialog.asksaveasfilename(defaultextension=".pdf",
                                                filetypes=[("PDF Files","*.pdf")])
            if path:
                temp_path = os.path.join(BASE_FOLDER, "temp_qr.png")
                self.master.generated_qr.save(temp_path)
                c = pdf_canvas.Canvas(path, pagesize=A4)
                w, h = A4
                draw_w, draw_h = 400, 500
                x = (w - draw_w) / 2
                y = (h - draw_h) / 2
                c.drawImage(temp_path, x, y, width=draw_w, height=draw_h)
                c.save()
                os.remove(temp_path)
                messagebox.showinfo("Exported", f"PDF saved at {path}")

    def copy_qr(self):
        if self.master.generated_qr:
            output = io.BytesIO()
            self.master.generated_qr.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:]
            output.close()
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
                win32clipboard.CloseClipboard()
                messagebox.showinfo("Copied", "QR copied to clipboard!")
            except Exception as e:
                messagebox.showerror("Clipboard Error", f"Failed to copy image to clipboard: {e}")

# -------------------- Run --------------------
if __name__ == "__main__":
    app = PaymentApp()
    app.mainloop()
