"""Local ELITE Production Suite launcher. No installation, model downloads, APIs or uploads."""
import sys, shutil, subprocess, hashlib, json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
TOOLS=(
 ("01 · Image generation / SD 1.5","open-generative-bridge.py","Open Generative AI sd-cli + downloaded SD 1.5 model"),
 ("02 · Narration / WAV","local-narration-studio.py","eSpeak or eSpeak NG"),
 ("03 · Video assembly / MP4","commercial-video-assembler.py","FFmpeg with libx264 and AAC"),
 ("04 · Delivery QC","delivery-quality-check.py","FFprobe"),
 ("05 · Client delivery / ZIP","client-delivery-kit.py","No extra engine"))
def verify_bundle(root=ROOT):
    """Check extracted files against the bundled manifest (not a signature)."""
    root=Path(root)
    expected={t[1] for t in TOOLS}|{"elite-production-launcher.py","README.txt"}
    try:
        manifest=root/"manifest.json"
        if manifest.is_symlink() or not manifest.is_file() or manifest.stat().st_size>32768:
            raise ValueError("Missing or invalid manifest.json")
        data=json.loads(manifest.read_text(encoding="utf-8"))
        entries=data["files"]
        if not isinstance(entries,list) or len(entries)!=len(expected):
            raise ValueError("Unexpected manifest file count")
        seen=set()
        for entry in entries:
            name=entry["name"]
            if not isinstance(name,str) or name not in expected or name in seen:
                raise ValueError("Unexpected or duplicate manifest entry")
            seen.add(name)
            path=root/name
            size=entry["bytes"]
            if type(size) is not int or not 0<=size<=200000 or path.is_symlink() or not path.is_file() or path.stat().st_size!=size:
                raise ValueError("Missing or changed file: "+name)
            with path.open("rb") as stream:
                raw=stream.read(200001)
            if len(raw)!=size or hashlib.sha256(raw).hexdigest()!=entry["sha256"]:
                raise ValueError("Checksum mismatch: "+name)
        if seen!=expected:raise ValueError("Incomplete manifest")
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as exc:
        return False,str(exc)
    return True,"All bundled files match the manifest. This is not a digital signature."

def command(filename):
    if filename not in {t[1] for t in TOOLS}:raise ValueError("Unknown tool")
    valid,detail=verify_bundle()
    if not valid:raise ValueError("Bundle check failed: "+detail+"; download and extract a fresh copy from Academy.")
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
    buttons=[]
    def refresh():
        valid,detail=verify_bundle()
        for button in buttons:button.configure(state="normal" if valid else "disabled")
        status.set(("Bundle integrity: "+detail+"\n\n")+"\n".join(k+": "+(v or "Not detected on PATH; select installed executable manually in tool") for k,v in diagnostics().items()))
    def launch(filename):
        try:subprocess.Popen(command(filename),cwd=str(ROOT),shell=False)
        except Exception as e:messagebox.showerror("Launch failed",str(e))
    for title,filename,need in TOOLS:
        row=ttk.Frame(root);row.pack(fill="x",padx=20,pady=8)
        button=ttk.Button(row,text=title,command=lambda f=filename:launch(f),width=36)
        button.pack(side="left");buttons.append(button)
        ttk.Label(row,text=need,wraplength=440).pack(side="left",padx=10)
    ttk.Separator(root).pack(fill="x",padx=20,pady=12)
    ttk.Label(root,textvariable=status,wraplength=790,justify="left").pack(anchor="w",padx=20)
    ttk.Button(root,text="Refresh integrity and dependency check",command=refresh).pack(pady=8)
    refresh();root.mainloop()
if __name__=="__main__":main()
