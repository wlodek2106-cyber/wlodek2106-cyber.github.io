"""Local four-shot MP4 assembler for Academy's Commercial Video Production.
Requires a trusted local FFmpeg binary and Python/Tkinter. No shell, API, or uploads.
"""
import json, os, shutil, subprocess, threading, queue, tempfile
from pathlib import Path
FORMATS={"9:16":(1080,1920),"16:9":(1920,1080),"1:1":(1080,1080)}
TIMES={15:[3,5,4,3],30:[5,10,9,6],60:[8,22,20,10]}
VIDEO={".mp4",".mov",".mkv",".webm",".m4v"}
AUDIO={".wav",".mp3",".m4a",".aac",".flac",".ogg"}
def read_plan(path):
    p=Path(path)
    if p.stat().st_size>100000:raise ValueError("Plan exceeds 100 KB")
    d=json.loads(p.read_text(encoding="utf-8"))
    return validate_plan(d)
def validate_plan(d):
    if not isinstance(d,dict):raise ValueError("Invalid production plan")
    duration,fmt=d.get("duration"),d.get("format")
    if type(duration) is not int or duration not in TIMES or not isinstance(fmt,str) or fmt not in FORMATS:raise ValueError("Invalid format or duration")
    w,h=FORMATS[fmt]
    if (d.get("width"),d.get("height"))!=(w,h):raise ValueError("Invalid dimensions")
    scenes=d.get("scenes")
    if not isinstance(scenes,list) or len(scenes)!=4:raise ValueError("Four scenes required")
    start=0
    for scene,seconds in zip(scenes,TIMES[duration]):
        if not isinstance(scene,dict) or any(type(scene.get(k)) is not int for k in ("start","end","seconds")) or (scene["start"],scene["end"],scene["seconds"])!=(start,start+seconds,seconds):raise ValueError("Invalid scene timeline")
        start+=seconds
    return {"duration":duration,"format":fmt,"width":w,"height":h,"seconds":list(TIMES[duration])}
def local_file(path,extensions):
    p=Path(path).resolve()
    if not p.is_file() or p.suffix.lower() not in extensions:raise ValueError("Select an existing supported local media file")
    return str(p)
def build_command(ffmpeg,plan,clips,audio,output,narration=None,subtitles=None):
    exe=Path(ffmpeg).resolve()
    if exe.name.lower() not in ("ffmpeg","ffmpeg.exe") or not exe.is_file():raise ValueError("Select trusted FFmpeg executable")
    if len(clips)!=4:raise ValueError("Select four clips in scene order")
    sources=[local_file(x,VIDEO) for x in clips]
    out=Path(output).resolve()
    if out.suffix.lower()!=".mp4" or not out.parent.is_dir() or out.exists():raise ValueError("Choose a new MP4 output")
    w,h=FORMATS[plan["format"]];times=TIMES[plan["duration"]]
    if plan!={"duration":sum(times),"format":plan["format"],"width":w,"height":h,"seconds":times}:raise ValueError("Invalid normalized plan")
    cmd=[str(exe),"-hide_banner","-nostdin","-loglevel","error","-n","-filter_complex_threads","2"]
    for path in sources:cmd+=["-protocol_whitelist","file","-i",path]
    music_index=voice_index=subtitle_index=None
    index=4
    if audio:
        music_index=index;index+=1
        cmd+=["-protocol_whitelist","file","-i",local_file(audio,AUDIO)]
    if narration:
        voice_index=index;index+=1
        cmd+=["-protocol_whitelist","file","-i",local_file(narration,AUDIO)]
    if subtitles:
        subtitle_index=index
        cmd+=["-protocol_whitelist","file","-f","srt","-i",local_file(subtitles,{".srt"})]
    filters=[]
    for i,seconds in enumerate(times):
        filters.append(f"[{i}:v:0]setpts=PTS-STARTPTS,scale={w}:{h}:force_original_aspect_ratio=decrease:force_divisible_by=2,pad={w}:{h}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration={seconds},trim=duration={seconds},setpts=PTS-STARTPTS[v{i}]")
    filters.append("[v0][v1][v2][v3]concat=n=4:v=1:a=0[v]")
    duration=plan["duration"]
    if music_index is not None and voice_index is not None:
        filters.extend([f"[{music_index}:a:0]asetpts=PTS-STARTPTS,aresample=48000,volume=0.2,apad,atrim=duration={duration}[music]",
                        f"[{voice_index}:a:0]asetpts=PTS-STARTPTS,aresample=48000,apad,atrim=duration={duration}[voice]",
                        "[voice][music]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]"])
    elif music_index is not None or voice_index is not None:
        track=music_index if music_index is not None else voice_index
        filters.append(f"[{track}:a:0]asetpts=PTS-STARTPTS,apad,atrim=duration={duration}[a]")
    cmd+=["-filter_complex",";".join(filters),"-map","[v]"]
    if audio or narration:cmd+=["-map","[a]","-c:a","aac","-b:a","192k","-ar","48000"]
    else:cmd+=["-an"]
    if subtitle_index is not None:cmd+=["-map",f"{subtitle_index}:s:0","-c:s","mov_text","-disposition:s:0","default"]
    cmd+=["-map_metadata","-1","-map_chapters","-1","-c:v","libx264","-preset","fast","-crf","20","-threads","2","-pix_fmt","yuv420p","-t",str(plan["duration"]),"-movflags","+faststart",str(out)]
    return cmd
def assemble(ffmpeg,plan,clips,audio,output,narration=None,subtitles=None):
    out=Path(output).resolve()
    if out.suffix.lower()!=".mp4" or not out.parent.is_dir() or out.exists():raise ValueError("Choose a new MP4 output")
    # Render in a private temporary directory, then publish without overwriting.
    with tempfile.TemporaryDirectory(prefix="zer0life-",dir=out.parent) as tmp:
        temp=Path(tmp)/"assembled.mp4"
        cmd=build_command(ffmpeg,plan,clips,audio,temp,narration,subtitles)
        result=subprocess.run(cmd,shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,timeout=1800)
        if result.returncode or not temp.is_file() or temp.stat().st_size<100:
            raise RuntimeError("FFmpeg export failed; verify input clips and H.264 encoder. "+result.stderr.decode("utf-8","replace")[-600:])
        try:
            with out.open("xb") as dest,temp.open("rb") as src:
                try:shutil.copyfileobj(src,dest)
                except BaseException:
                    dest.close();out.unlink(missing_ok=True);raise
        except FileExistsError:raise ValueError("Output already exists")
    return {"tool":"Zer0Life local FFmpeg assembler","output":out.name,"planned_duration":plan["duration"],"format":plan["format"],"width":plan["width"],"height":plan["height"],"fps":30,"audio":"mixed voice and music" if audio and narration else "narration" if narration else "external track" if audio else "silent","subtitles":"selectable MP4 subtitle track" if subtitles else "none","note":"Export completed; confirm actual metadata and visual/audio quality in Academy."}
def main():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title("ZER0LIFE · Commercial Video Assembler");root.geometry("850x760")
    ttk.Label(root,text="Commercial Video Assembler",font=("Arial",19,"bold")).pack(pady=12)
    ttk.Label(root,text="Load the Academy JSON plan and four local clips. Short clips freeze on the final frame; long clips are trimmed. Original clip audio is muted. Optional narration, licensed music and selectable SRT subtitles.",wraplength=790).pack(padx=16)
    entries={}
    for key,label in [("ffmpeg","Trusted FFmpeg executable"),("plan","Academy production JSON"),("clip1","1 · Hook"),("clip2","2 · Demonstration"),("clip3","3 · Evidence"),("clip4","4 · Call to action"),("audio","Optional background music"),("narration","Optional narration audio"),("subtitles","Optional SRT subtitles"),("output","New MP4 output")]:
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=4)
        ttk.Label(row,text=label,width=30).pack(side="left")
        var=tk.StringVar(value=(shutil.which("ffmpeg") or "") if key=="ffmpeg" else "");entries[key]=var
        ttk.Entry(row,textvariable=var).pack(side="left",fill="x",expand=True)
        def pick(k=key,v=var):
            f=filedialog.asksaveasfilename(defaultextension=".mp4",filetypes=[("MP4","*.mp4")]) if k=="output" else filedialog.askopenfilename()
            if f:v.set(f)
        ttk.Button(row,text="Browse",command=pick).pack(side="left")
    status=tk.StringVar(value="Ready");ttk.Label(root,textvariable=status,wraplength=790).pack(pady=10)
    events=queue.Queue();report=None
    def run():
        nonlocal report
        try:
            values={k:v.get().strip() for k,v in entries.items()}
            plan=read_plan(values["plan"]);clips=[values["clip"+str(i)] for i in range(1,5)]
            args=(values["ffmpeg"],plan,clips,values["audio"],values["output"],values["narration"],values["subtitles"])
            build_command(*args)
        except Exception as e:messagebox.showerror("Input",str(e));return
        if not messagebox.askyesno("Confirm export",f"Export {plan['duration']} seconds at {plan['width']}×{plan['height']}? Clip audio is muted; short scenes freeze and long scenes trim. Use authorized media only."):return
        start.configure(state="disabled");save.configure(state="disabled");report=None;status.set("Rendering locally…")
        def worker():
            try:events.put(("ok",assemble(*args)))
            except Exception as e:events.put(("error",str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def export():
        if report is None:return
        f=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON","*.json")])
        if f:
            try:Path(f).write_text(json.dumps(report,indent=2),encoding="utf-8")
            except OSError as e:messagebox.showerror("Save",str(e))
    start=ttk.Button(root,text="Export MP4",command=run);start.pack(pady=5)
    save=ttk.Button(root,text="Save export report",command=export,state="disabled");save.pack(pady=5)
    def poll():
        nonlocal report
        try:
            kind,value=events.get_nowait();start.configure(state="normal")
            if kind=="ok":report=value;save.configure(state="normal");status.set("Export complete: "+value["output"])
            else:status.set(value)
        except queue.Empty:pass
        root.after(200,poll)
    root.after(200,poll);root.mainloop()
if __name__=="__main__":main()
