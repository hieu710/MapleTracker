"""MapleTracker Desktop - capture/diagnostics prototype (Windows 11).
Install: py -m pip install mss pillow pygetwindow
Run: py desktop_tracker.py
No memory access, no keyboard hooks, no network transmission.
"""
import time, json, pathlib, datetime, tkinter as tk
from tkinter import ttk
import mss
import pygetwindow as gw
from PIL import Image, ImageTk

ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/"desktop_diagnostics"
OUT.mkdir(exist_ok=True)

def game_window():
    matches=[w for w in gw.getAllWindows() if "maplestory" in w.title.lower() and w.width>400 and w.height>300]
    return matches[0] if matches else None

def capture():
    win=game_window()
    if not win: raise RuntimeError("Không tìm thấy cửa sổ MapleStory đang mở.")
    if win.isMinimized: raise RuntimeError("Cửa sổ game đang thu nhỏ; hãy mở lại.")
    rect={"left":max(0,win.left),"top":max(0,win.top),"width":win.width,"height":win.height}
    with mss.mss() as s:
        shot=s.grab(rect)
    return Image.frombytes("RGB",shot.size,shot.rgb),win

class App:
    def __init__(self,root):
        self.root=root
        root.title("MapleTracker Desktop - EXP capture diagnostic")
        root.geometry("700x530")
        self.status=tk.StringVar(value="Chưa chụp. Mở MapleStory rồi bấm Chụp thử.")
        ttk.Label(root,text="MapleTracker Desktop — bản kiểm tra vùng EXP",font=("Segoe UI",14,"bold")).pack(pady=12)
        ttk.Label(root,textvariable=self.status,wraplength=660).pack(pady=6)
        ttk.Button(root,text="Chụp thử cửa sổ game",command=self.snap).pack(pady=8)
        self.panel=ttk.Label(root);self.panel.pack(expand=True)
        ttk.Label(root,text="Chưa nhận diện số EXP. Ảnh chỉ lưu trên máy để kiểm tra; không tự gửi đi.",wraplength=660).pack(pady=10)
    def snap(self):
        try:
            img,win=capture()
            stamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            # Initial HUD proposal: lower-right of game window; diagnostic only.
            w,h=img.size
            roi=img.crop((int(w*.50),int(h*.88),int(w*.80),h))
            filename=OUT/f"maple_{stamp}.png"
            roi_file=OUT/f"exp_roi_{stamp}.png"
            img.save(filename);roi.save(roi_file)
            (OUT/f"capture_{stamp}.json").write_text(json.dumps({"title":win.title,"size":[w,h],"window":[win.left,win.top,win.width,win.height],"exp_roi":[int(w*.50),int(h*.88),int(w*.80),h],"recognition":"NOT_IMPLEMENTED"},ensure_ascii=False,indent=2),encoding="utf8")
            view=roi.copy();view.thumbnail((650,340));self.photo=ImageTk.PhotoImage(view)
            self.panel.configure(image=self.photo)
            self.status.set(f"Đã chụp {w}×{h}. Lưu ảnh và vùng EXP tại {OUT}. Đây mới là bước kiểm tra vị trí.")
        except Exception as exc:
            self.status.set(str(exc))
if __name__=="__main__":
    root=tk.Tk();App(root);root.mainloop()
