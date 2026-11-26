"""Local ELITE Production Suite launcher. No installation, model downloads, APIs or uploads."""
import sys, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TOOLS=(
 ("01 · Image generation / SD 1.5","open-generative-bridge.py","Open Generative AI sd-cli + downloaded SD 1.5 model"),
 ("02 · Narration / WAV","local-narration-studio.py","eSpeak or eSpeak NG"),
 ("03 · Video assembly / MP4","commercial-video-assembler.py","FFmpeg with libx264 and AAC"),
 ("04 · Delivery QC","delivery-quality-check.py","FFprobe"),
 ("05 · Client delivery / ZIP","client-delivery-kit.py","No extra engine"))
def command(filename):
    if filename not in {t[1] for t in TOOLS}:raise ValueError("Unknown tool")
    path=ROOT/filename
    if not path.is_file():raise ValueError("Missing tool; extract the entire suite again")
    return [sys.executable,str(path)]
def diagnostics():
    return {"Python":sys.version.split()[0],"FFmpeg":shutil.which("ffmpeg"),"FFprobe":shutil.which("ffprobe"),"eSpeak":shutil.which("espeak-ng") or shutil.which("espeak"),"sd-cli":shutil.which("sd-cli")}
def main():
    import tkinter as tk
    from tkinter import ttk,messagebox
    root=tk.Tk();root.title("ZER0LIFE · ELITE Production Suite");root.geometry("850x640")
    ttk.Label(root,text="ZER0LIFE · ELITE Production Suite",font=("Arial",20,"bold")).pack(pady=12)
    ttk.Label(root,text="Run each production step on this computer. Install the trusted engines separately. No automatic downloads or cloud services.",wraplength=790).pack(padx=16)
    status=tk.StringVar()
    def refresh():
        status.set("\n".join(k+": "+(v or "Not detected on PATH; select installed executable manually in tool") for k,v in diagnostics().items()))
    def launch(filename):
        try:subprocess.Popen(command(filename),cwd=str(ROOT),shell=False)
        except Exception as e:messagebox.showerror("Launch failed",str(e))
    for title,filename,need in TOOLS:
        row=ttk.Frame(root);row.pack(fill="x",padx=20,pady=8)
        ttk.Button(row,text=title,command=lambda f=filename:launch(f),width=36).pack(side="left")
        ttk.Label(row,text=need,wraplength=440).pack(side="left",padx=10)
    ttk.Separator(root).pack(fill="x",padx=20,pady=12)
    ttk.Label(root,textvariable=status,wraplength=790,justify="left").pack(anchor="w",padx=20)
    ttk.Button(root,text="Refresh dependency check",command=refresh).pack(pady=8)
    refresh();root.mainloop()
if __name__=="__main__":main()
