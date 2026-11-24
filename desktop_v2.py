"""MapleTracker Desktop V2 - experimental OCR, Windows 11.
Dependencies: py -m pip install mss pillow pygetwindow pytesseract
Also install Tesseract OCR for Windows and add executable to PATH.
No memory reading, no game interaction, no network.
"""
import re,time,threading,queue,statistics,datetime,pathlib,tkinter as tk
from tkinter import ttk
from PIL import Image,ImageOps,ImageEnhance,ImageFilter
import mss,pygetwindow as gw,pytesseract

OUT=pathlib.Path(__file__).resolve().parent/"desktop_diagnostics"
OUT.mkdir(exist_ok=True)
def capture():
    wins=[w for w in gw.getAllWindows() if "maplestory" in w.title.lower() and w.width>500 and w.height>400 and not w.isMinimized]
    if not wins: raise RuntimeError("Không tìm thấy cửa sổ MapleStory đang mở")
    w=wins[0]
    with mss.mss() as s:
        shot=s.grab({"left":max(0,w.left),"top":max(0,w.top),"width":w.width,"height":w.height})
        return Image.frombytes("RGB",shot.size,shot.rgb)
def rois(img):
    w,h=img.size
    # Window-relative HUD and inventory regions; can be refined with additional screenshots.
    return {"exp":img.crop((int(w*.50),int(h*.935),int(w*.75),h)),
            "mesos":img.crop((int(w*.80),int(h*.32),w,int(h*.39)))}
def recognize(img,kind):
    results=[]
    for factor in [3,4]:
        scaled=img.resize((img.width*factor,img.height*factor),Image.Resampling.NEAREST)
        gray=ImageOps.grayscale(scaled)
        for threshold in [None,145,190]:
            frame=gray if threshold is None else gray.point(lambda p:255 if p>threshold else 0)
            text=pytesseract.image_to_string(frame,config="--psm 6 -c tessedit_char_whitelist=0123456789EXPexpMESOSmesos,.()%: ")
            pattern=r"EXP\s*[:.]?\s*([\d,\.]+)\s*\(\s*([\d.]+)\s*%\s*\)" if kind=="exp" else r"([\d,]{4,12})\s*(?:MESOS?)?"
            match=re.search(pattern,text,re.I)
            if match:
                try:
                    value=int(re.sub(r"\D","",match.group(1)))
                    if value>0:
                        pct=float(match.group(2)) if kind=="exp" else None
                        if pct is None or 0<=pct<100:results.append((value,pct,text.strip()))
                except ValueError:pass
    # Never accept a single OCR result: require 2 independent preprocessing votes.
    votes={}
    for v,p,t in results:votes.setdefault((v,p),[]).append(t)
    stable=[(k,len(ts)) for k,ts in votes.items() if len(ts)>=2]
    if not stable:return None,len(results)
    return max(stable,key=lambda x:x[1])[0],len(results)

class App:
    def __init__(self,root):
        self.root=root;root.title("MapleTracker Desktop V2 - EXP thử nghiệm");root.geometry("640x310")
        self.status=tk.StringVar(value="Chưa chạy")
        self.exp=tk.StringVar(value="EXP: chưa xác định")
        self.mesos=tk.StringVar(value="Mesos: chưa xác định")
        self.running=False;self.q=queue.Queue();self.history=[]
        ttk.Label(root,text="MapleTracker Desktop V2",font=("Segoe UI",16,"bold")).pack(pady=10)
        ttk.Label(root,textvariable=self.exp,font=("Segoe UI",13)).pack()
        ttk.Label(root,textvariable=self.mesos,font=("Segoe UI",13)).pack()
        ttk.Label(root,textvariable=self.status,wraplength=590).pack(pady=10)
        ttk.Button(root,text="Bắt đầu / Dừng",command=self.toggle).pack()
        ttk.Label(root,text="Chỉ đọc hình ảnh. Không dùng số OCR chưa ổn định để tính EXP/h.",wraplength=590).pack(pady=12)
        root.after(150,self.poll)
    def toggle(self):
        self.running=not self.running
        if self.running:threading.Thread(target=self.loop,daemon=True).start()
        else:self.status.set("Đã dừng")
    def loop(self):
        while self.running:
            try:
                image=capture()
                parts=rois(image)
                exp,n=recognize(parts["exp"],"exp")
                mes,m=recognize(parts["mesos"],"mesos")
                self.q.put((exp,mes,n,m,image,parts,None))
            except Exception as e:self.q.put((None,None,0,0,None,None,str(e)))
            time.sleep(3)
    def poll(self):
        while not self.q.empty():
            exp,mes,n,m,img,parts,error=self.q.get()
            if error:self.status.set(error);continue
            if exp:
                self.history.append(exp);self.history=self.history[-3:]
                if len(self.history)>=2 and self.history[-1]==self.history[-2]:
                    self.exp.set(f"EXP: {exp[0]:,} ({exp[1]:.2f}%)")
                else:self.status.set("EXP OCR chưa ổn định giữa các lần chụp")
            if mes:self.mesos.set(f"Mesos (khi Inventory mở): {mes[0]:,}")
            if not exp:self.exp.set("EXP: chưa xác định")
            self.status.set(f"Đã quét ảnh; EXP {n} mẫu, mesos {m} mẫu. Chưa xác nhận độ chính xác.")
            if img and not exp:
                stamp=datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                parts["exp"].save(OUT/f"exp_failed_{stamp}.png")
        self.root.after(150,self.poll)
if __name__=="__main__":
    root=tk.Tk();App(root);root.mainloop()
