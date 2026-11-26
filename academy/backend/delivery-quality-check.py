"""Local delivery metadata check using trusted FFprobe. No media upload or API."""
import json, math, shutil, subprocess, threading, queue, hashlib
from fractions import Fraction
from pathlib import Path
FORMATS={"9:16":(1080,1920),"16:9":(1920,1080),"1:1":(1080,1080)}
def evaluate(data,duration,fmt,require_audio=True,require_subtitles=False):
    if type(duration) is not int or duration not in (15,30,60) or fmt not in FORMATS:raise ValueError("Invalid target")
    if type(require_audio) is not bool or type(require_subtitles) is not bool:raise ValueError("Invalid requirements")
    streams=data.get("streams",[])
    video=next((s for s in streams if s.get("codec_type")=="video" and not s.get("disposition",{}).get("attached_pic")),None)
    if not video:raise ValueError("No video stream")
    audio=[s for s in streams if s.get("codec_type")=="audio"]
    subs=[s for s in streams if s.get("codec_type")=="subtitle"]
    try:
        seconds=float(data["format"]["duration"])
        fps=float(Fraction(video.get("avg_frame_rate","0/1")))
        width,height=int(video["width"]),int(video["height"])
        if not math.isfinite(seconds) or not math.isfinite(fps) or seconds<=0 or fps<=0 or width<=0 or height<=0:raise ValueError()
    except (KeyError,ValueError,TypeError,ZeroDivisionError,OverflowError):raise ValueError("Invalid media metadata")
    rotation=video.get("tags",{}).get("rotate",0)
    for side in video.get("side_data_list",[]):
        if "rotation" in side:rotation=side["rotation"]
    try:rotation=float(rotation)
    except (TypeError,ValueError):raise ValueError("Invalid rotation metadata")
    checks={"duration":abs(seconds-duration)<=0.5,"resolution":(width,height)==FORMATS[fmt] and rotation%360==0,
            "frame_rate":abs(fps-30)<=0.05,"video_codec":video.get("codec_name")=="h264",
            "pixel_format":video.get("pix_fmt")=="yuv420p",
            "audio":not require_audio or any(s.get("codec_name")=="aac" for s in audio),
            "subtitles":not require_subtitles or any(s.get("codec_name")=="mov_text" for s in subs)}
    return {"tool":"Zer0Life FFprobe delivery check","target":{"duration":duration,"format":fmt,"audio_required":require_audio,"subtitles_required":require_subtitles},
            "actual":{"duration":round(seconds,3),"width":width,"height":height,"fps":round(fps,3),"video_codec":video.get("codec_name"),
            "pixel_format":video.get("pix_fmt"),"audio_codecs":[s.get("codec_name") for s in audio],"subtitle_codecs":[s.get("codec_name") for s in subs]},
            "checks":checks,"metadata_pass":all(checks.values()),"note":"Metadata only; does not establish playback integrity, subtitle sync, loudness, rights or client acceptance."}
def inspect(engine,media,duration,fmt,require_audio=True,require_subtitles=False):
    exe=Path(engine).resolve();file=Path(media).resolve()
    if not exe.is_file() or exe.name.lower() not in ("ffprobe","ffprobe.exe"):raise ValueError("Select trusted FFprobe executable")
    if not file.is_file() or file.suffix.lower()!=".mp4":raise ValueError("Select local MP4")
    result=subprocess.run([str(exe),"-v","error","-protocol_whitelist","file","-show_streams","-show_format","-of","json",str(file)],shell=False,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=60)
    if result.returncode or len(result.stdout)>1000000:raise ValueError("FFprobe could not inspect the file")
    report=evaluate(json.loads(result.stdout),duration,fmt,require_audio,require_subtitles)
    digest=hashlib.sha256()
    with file.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""):digest.update(chunk)
    report["video_sha256"]=digest.hexdigest()
    return report
def main():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title("ZER0LIFE · Delivery Quality Check");root.geometry("780x660")
    ttk.Label(root,text="Delivery Quality Check · FFprobe",font=("Arial",19,"bold")).pack(pady=12)
    ttk.Label(root,text="Metadata check only. Review the entire video, audio, captions and rights yourself. No uploads.",wraplength=730).pack(padx=16)
    values={}
    for key,label in (("engine","Trusted FFprobe"),("media","Final local MP4")):
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=6);ttk.Label(row,text=label,width=25).pack(side="left")
        var=tk.StringVar(value=(shutil.which("ffprobe") or "") if key=="engine" else "");values[key]=var
        ttk.Entry(row,textvariable=var).pack(side="left",fill="x",expand=True)
        def pick(v=var):
            path=filedialog.askopenfilename()
            if path:v.set(path)
        ttk.Button(row,text="Browse",command=pick).pack(side="left")
    duration=tk.StringVar(value="30");fmt=tk.StringVar(value="9:16")
    ttk.Label(root,text="Target duration (seconds)").pack();ttk.Combobox(root,textvariable=duration,values=("15","30","60"),state="readonly").pack()
    ttk.Label(root,text="Target format").pack();ttk.Combobox(root,textvariable=fmt,values=tuple(FORMATS),state="readonly").pack()
    audio=tk.BooleanVar(value=True);subs=tk.BooleanVar(value=False)
    ttk.Checkbutton(root,text="Require AAC audio",variable=audio).pack();ttk.Checkbutton(root,text="Require selectable MP4 subtitles",variable=subs).pack()
    status=tk.StringVar(value="Ready");ttk.Label(root,textvariable=status).pack(pady=6)
    result=tk.Text(root,height=12,wrap="word");result.pack(fill="both",expand=True,padx=16)
    events=queue.Queue();report=None
    def run():
        nonlocal report
        args=(values["engine"].get(),values["media"].get(),int(duration.get()),fmt.get(),audio.get(),subs.get())
        report=None;start.configure(state="disabled");save.configure(state="disabled");status.set("Inspecting…")
        def worker():
            try:events.put(("ok",inspect(*args)))
            except Exception as e:events.put(("error",str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def export():
        if report is None:return
        f=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if f:
            try:Path(f).write_text(json.dumps(report,indent=2),encoding="utf-8")
            except OSError as e:messagebox.showerror("Save",str(e))
    start=ttk.Button(root,text="Inspect MP4",command=run);start.pack(pady=4)
    save=ttk.Button(root,text="Export QC report",command=export,state="disabled");save.pack(pady=4)
    def poll():
        nonlocal report
        try:
            kind,v=events.get_nowait();start.configure(state="normal");result.delete("1.0","end")
            if kind=="ok":report=v;result.insert("1.0",json.dumps(v,indent=2));save.configure(state="normal");status.set("Metadata passed" if v["metadata_pass"] else "Fix metadata mismatches")
            else:status.set("Inspection failed");result.insert("1.0",v)
        except queue.Empty:pass
        root.after(200,poll)
    root.after(200,poll);root.mainloop()
if __name__=="__main__":main()
