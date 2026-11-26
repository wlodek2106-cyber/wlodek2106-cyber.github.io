"""Local narration renderer using an installed eSpeak or eSpeak NG executable.
No cloud service. Every scene retains its exact duration; overlong speech is rejected.
"""
import json, shutil, subprocess, tempfile, threading, queue, wave
from pathlib import Path
TIMES={15:[3,5,4,3],30:[5,10,9,6],60:[8,22,20,10]}
LANGUAGES=("en","ru","uk","pl")
def validate(data):
    if not isinstance(data,dict) or set(data)!={"duration","captions"}:raise ValueError("Invalid narration JSON")
    duration=data["duration"];captions=data["captions"]
    if type(duration) is not int or duration not in TIMES or not isinstance(captions,list) or len(captions)!=4:raise ValueError("Invalid scene timeline")
    if any(not isinstance(s,str) or len(s)>160 or any(ord(c)<32 and c not in "\n\t" for c in s) or "<" in s or ">" in s for s in captions):raise ValueError("Invalid caption text")
    clean=[" ".join(s.split()) for s in captions]
    if not any(clean):raise ValueError("Enter at least one caption")
    return duration,clean
def render(engine,data,lang,speed,output):
    duration,captions=validate(data)
    if lang not in LANGUAGES or type(speed) is not int or not 120<=speed<=220:raise ValueError("Choose language and 120–220 words/minute")
    exe=Path(engine).resolve()
    if not exe.is_file() or exe.name.lower() not in ("espeak","espeak-ng","espeak.exe","espeak-ng.exe"):raise ValueError("Select trusted eSpeak executable")
    out=Path(output).resolve()
    if out.suffix.lower()!=".wav" or not out.parent.is_dir() or out.exists():raise ValueError("Choose a new WAV file")
    reports=[];parts=[];rate=None
    with tempfile.TemporaryDirectory() as tmp:
        for i,(caption,seconds) in enumerate(zip(captions,TIMES[duration])):
            if not caption:parts.append((None,seconds));reports.append({"scene":i+1,"seconds":0,"slot":seconds});continue
            f=Path(tmp)/f"scene-{i}.wav"
            result=subprocess.run([str(exe),"-v",lang,"-s",str(speed),"-w",str(f),"--stdin"],input=caption.encode("utf-8"),stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=60,shell=False)
            if result.returncode or not f.exists():raise RuntimeError("Local voice failed: verify the installed language")
            with wave.open(str(f),"rb") as w:
                if w.getnchannels()!=1 or w.getsampwidth()!=2 or w.getcomptype()!="NONE":raise ValueError("Expected mono PCM16 WAV")
                r=w.getframerate()
                if not 8000<=r<=48000 or (rate is not None and r!=rate):raise ValueError("Inconsistent sample rate")
                rate=r;n=w.getnframes()
                if n>seconds*rate:raise ValueError(f"Scene {i+1}: speech {n/r:.2f}s exceeds {seconds}s. Shorten text or increase speed.")
                pcm=w.readframes(n)
                if len(pcm)!=n*2:raise ValueError("Incomplete audio")
            parts.append((pcm,seconds));reports.append({"scene":i+1,"seconds":round(n/r,3),"slot":seconds})
        if rate is None:raise ValueError("No audio produced")
        # No overwrite; remove incomplete output only if this invocation created it.
        with out.open("xb") as dest:
            try:
                with wave.open(dest,"wb") as w:
                    w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate)
                    for pcm,seconds in parts:
                        pcm=pcm or b""
                        w.writeframes(pcm+b"\0"*(seconds*rate*2-len(pcm)))
            except BaseException:
                dest.close();out.unlink(missing_ok=True);raise
    return {"tool":"Zer0Life local eSpeak narration","output":out.name,"language":lang,"speed":speed,"sample_rate":rate,"duration":duration,"scenes":reports}
def main():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title("ZER0LIFE · Local Narration Studio");root.geometry("780x470")
    ttk.Label(root,text="Local narration · WAV",font=("Arial",19,"bold")).pack(pady=12)
    ttk.Label(root,text="Install eSpeak NG separately. Load the Academy narration JSON. Speech that exceeds a scene is rejected; silence fills unused time. Synthetic system voice, no cloning.",wraplength=730).pack(padx=16)
    values={}
    for key,label in (("engine","Trusted eSpeak executable"),("plan","Academy narration JSON"),("output","New WAV output")):
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=6);ttk.Label(row,text=label,width=29).pack(side="left")
        var=tk.StringVar(value=(shutil.which("espeak-ng") or shutil.which("espeak") or "") if key=="engine" else "");values[key]=var
        ttk.Entry(row,textvariable=var).pack(side="left",fill="x",expand=True)
        def pick(k=key,v=var):
            path=filedialog.asksaveasfilename(defaultextension=".wav") if k=="output" else filedialog.askopenfilename()
            if path:v.set(path)
        ttk.Button(row,text="Browse",command=pick).pack(side="left")
    lang=tk.StringVar(value="en");speed=tk.StringVar(value="170")
    ttk.Combobox(root,textvariable=lang,values=LANGUAGES,state="readonly").pack(pady=4)
    ttk.Label(root,text="Words per minute (120–220)").pack();ttk.Entry(root,textvariable=speed).pack()
    status=tk.StringVar(value="Ready");ttk.Label(root,textvariable=status,wraplength=720).pack(pady=8)
    events=queue.Queue();report=None
    def run():
        nonlocal report
        try:
            path=Path(values["plan"].get())
            if path.stat().st_size>10000:raise ValueError("Narration JSON too large")
            data=json.loads(path.read_text(encoding="utf-8"));validate(data)
            args=(values["engine"].get(),data,lang.get(),int(speed.get()),values["output"].get())
        except Exception as e:messagebox.showerror("Input",str(e));return
        if not messagebox.askyesno("Confirm","Use the trusted local speech engine and authorized script?"):return
        report=None;start.configure(state="disabled");save.configure(state="disabled");status.set("Rendering locally…")
        def worker():
            try:events.put(("ok",render(*args)))
            except Exception as e:events.put(("error",str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def export():
        if report is None:return
        f=filedialog.asksaveasfilename(defaultextension=".json")
        if f:Path(f).write_text(json.dumps(report,indent=2),encoding="utf-8")
    start=ttk.Button(root,text="Generate WAV",command=run);start.pack(pady=5)
    save=ttk.Button(root,text="Save timing report",command=export,state="disabled");save.pack(pady=5)
    def poll():
        nonlocal report
        try:
            kind,v=events.get_nowait();start.configure(state="normal")
            if kind=="ok":report=v;save.configure(state="normal");status.set("WAV ready: "+v["output"])
            else:status.set(v)
        except queue.Empty:pass
        root.after(200,poll)
    root.after(200,poll);root.mainloop()
if __name__=="__main__":main()
