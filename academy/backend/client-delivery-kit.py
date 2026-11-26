"""Client delivery manifest. Files and rights evidence remain local; no transfer or payment."""
import hashlib, json, os, re, threading, queue
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile, ZIP_STORED, ZIP_DEFLATED
from tempfile import TemporaryDirectory
KINDS={"video":{".mp4"},"captions":{".srt"},"voice":{".wav"},"plan":{".json"},"qc":{".json"},"rights":{".txt",".pdf"}}
NAMES={"video":"final.mp4","captions":"captions.srt","voice":"narration.wav","plan":"production-plan.json","qc":"quality-report.json"}
CHECKS=("playback","audio_sync","captions","claims","rights","client_brief")
def clean(value,limit):
    if not isinstance(value,str) or not 1<=len(value.strip())<=limit or any(ord(c)<32 for c in value):raise ValueError("Invalid text field")
    return value.strip()
def package(files,details,checks,output):
    if not isinstance(files,dict) or not {"video","plan","qc","rights"}<=set(files)<=set(KINDS):raise ValueError("Final video, plan, QC and rights notes required")
    if not isinstance(details,dict) or set(details)!={"project","revision","limitations"}:raise ValueError("Invalid delivery details")
    details={k:clean(v,500 if k=="limitations" else 120) for k,v in details.items()}
    if not isinstance(checks,dict) or set(checks)!=set(CHECKS) or any(v is not True for v in checks.values()):raise ValueError("Complete all manual acceptance checks before packaging")
    paths={}
    for key,value in files.items():
        src=Path(value).resolve()
        if not src.is_file() or src.suffix.lower() not in KINDS[key] or src.stat().st_size==0:raise ValueError("Invalid local "+key+" file")
        paths[key]=src
    if sum(f.stat().st_size for f in paths.values())>2*1024**3:raise ValueError("Maximum package size 2 GiB")
    for key in ("plan","qc"):
        if paths[key].stat().st_size>100000:raise ValueError("JSON too large")
    plan=json.loads(paths["plan"].read_text(encoding="utf-8"));qc=json.loads(paths["qc"].read_text(encoding="utf-8"))
    duration=plan.get("duration");fmt=plan.get("format")
    if type(duration) is not int or duration not in (15,30,60) or fmt not in ("9:16","16:9","1:1"):raise ValueError("Invalid plan")
    target=qc.get("target",{})
    required={"duration","resolution","frame_rate","video_codec","pixel_format","audio","subtitles"}
    qc_checks=qc.get("checks",{})
    if qc.get("tool")!="Zer0Life FFprobe delivery check" or target.get("duration")!=duration or target.get("format")!=fmt or set(qc_checks)!=required or not all(v is True for v in qc_checks.values()) or qc.get("metadata_pass") is not True:raise ValueError("Supply passing QC report matching the plan")
    video_hash=qc.get("video_sha256")
    if not isinstance(video_hash,str) or not re.fullmatch(r"[a-f0-9]{64}",video_hash):raise ValueError("Regenerate QC with the latest checker to bind it to this video")
    out=Path(output).resolve()
    if out.suffix.lower()!=".zip" or not out.parent.is_dir() or out.exists():raise ValueError("Choose new ZIP output")
    manifest={"project":details["project"],"revision":details["revision"],"limitations":details["limitations"],"duration":duration,"format":fmt,"created_at":datetime.now(timezone.utc).isoformat(),"manual_checks":checks,"files":[],"notice":"Creator-supplied checks and report; no independent Academy or client approval. Verify licenses, terms, and final file before delivery."}
    with TemporaryDirectory(prefix="zer0life-delivery-",dir=out.parent) as tmp:
        temp=Path(tmp)/"delivery.zip"
        with ZipFile(temp,"w",compression=ZIP_STORED,allowZip64=True) as z:
            for key,src in paths.items():
                name=NAMES[key] if key in NAMES else "rights"+src.suffix.lower()
                digest=hashlib.sha256();size=0
                with src.open("rb") as f,z.open(name,"w",force_zip64=True) as dest:
                    for chunk in iter(lambda:f.read(1024*1024),b""):
                        size+=len(chunk)
                        if size>2*1024**3:raise ValueError("File too large")
                        digest.update(chunk);dest.write(chunk)
                if key=="video" and digest.hexdigest()!=video_hash:raise ValueError("Final video differs from inspected file; rerun QC")
                manifest["files"].append({"role":key,"name":name,"bytes":size,"sha256":digest.hexdigest()})
            z.writestr("delivery-manifest.json",json.dumps(manifest,ensure_ascii=False,indent=2),compress_type=ZIP_DEFLATED)
        # Exclusive destination; never overwrite existing work.
        import shutil
        with out.open("xb") as dest:
            try:
                with temp.open("rb") as src:shutil.copyfileobj(src,dest)
            except BaseException:
                dest.close();out.unlink(missing_ok=True);raise
    return manifest
def main():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title("ZER0LIFE · Client Delivery Kit");root.geometry("850x820")
    ttk.Label(root,text="Client Delivery Kit · Local ZIP",font=("Arial",19,"bold")).pack(pady=8)
    ttk.Label(root,text="Choose final local files and rights notes. Check every item manually. Only package files you have permission to share. Nothing is sent to a client automatically.",wraplength=790).pack()
    values={}
    for key,label in (("video","Final MP4 (required)"),("plan","Production JSON (required)"),("qc","Passing QC JSON (required)"),("rights","Rights notes TXT/PDF (required)"),("captions","Optional SRT"),("voice","Optional WAV"),("output","New ZIP output")):
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=3);ttk.Label(row,text=label,width=30).pack(side="left")
        var=tk.StringVar();values[key]=var;ttk.Entry(row,textvariable=var).pack(side="left",fill="x",expand=True)
        def pick(k=key,v=var):
            f=filedialog.asksaveasfilename(defaultextension=".zip") if k=="output" else filedialog.askopenfilename()
            if f:v.set(f)
        ttk.Button(row,text="Browse",command=pick).pack(side="left")
    details={}
    for key,label,default in (("project","Project title",""),("revision","Revision","v1"),("limitations","Limitations / usage notes","None declared")):
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=3);ttk.Label(row,text=label,width=30).pack(side="left")
        var=tk.StringVar(value=default);details[key]=var;ttk.Entry(row,textvariable=var).pack(side="left",fill="x",expand=True)
    flags={}
    for key,label in zip(CHECKS,("Watched entire video","Reviewed audio and sync","Reviewed captions or agreed no captions","Checked factual claims","Confirmed rights and model licenses","Compared against client brief")):
        v=tk.BooleanVar(value=False);flags[key]=v;ttk.Checkbutton(root,text=label,variable=v).pack(anchor="w",padx=18)
    status=tk.StringVar(value="Ready");ttk.Label(root,textvariable=status,wraplength=790).pack(pady=8)
    events=queue.Queue()
    def run():
        files={k:v.get().strip() for k,v in values.items() if k!="output" and v.get().strip()}
        args=(files,{k:v.get() for k,v in details.items()},{k:v.get() for k,v in flags.items()},values["output"].get())
        if not messagebox.askyesno("Confirm","Create a local ZIP containing the selected files? Inspect it before sharing."):return
        start.configure(state="disabled");status.set("Packaging locally…")
        def worker():
            try:events.put(("ok",package(*args)))
            except Exception as e:events.put(("error",str(e)))
        threading.Thread(target=worker,daemon=True).start()
    start=ttk.Button(root,text="Create delivery ZIP",command=run);start.pack(pady=5)
    def poll():
        try:
            kind,value=events.get_nowait();start.configure(state="normal");status.set("ZIP created · "+str(len(value["files"]))+" files + manifest" if kind=="ok" else value)
        except queue.Empty:pass
        root.after(200,poll)
    root.after(200,poll);root.mainloop()
if __name__=="__main__":main()
