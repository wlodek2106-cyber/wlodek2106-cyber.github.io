"""Zer0Life Academy independent local launcher. Install official OpenMVS separately.
Uses native CreateStructure in recent releases; no network, paid API or uploads.
"""
from pathlib import Path
import subprocess, threading, queue, shutil, os, sys, tempfile
import tkinter as tk
from tkinter import filedialog, messagebox

def commands(bins, source, output):
    b=Path(bins).resolve()
    src=Path(source).resolve()
    out=Path(output).resolve()
    def exe(name):
        p=b/(name+(".exe" if os.name=="nt" else ""))
        if not p.is_file(): raise ValueError("Missing executable: "+str(p))
        return str(p)
    if src.is_dir():
        if len([p for p in src.iterdir() if p.is_file() and p.suffix.lower() in (".jpg",".jpeg",".png")])<5:
            raise ValueError("Select a folder with at least 5 JPG/PNG photos; 30–60 recommended.")
        sfm_source=str(src)
        first=[]
    elif src.is_file() and src.suffix.lower() in (".mp4",".mov",".mkv",".avi",".webm"):
        first=[[exe("ExtractKeyframes"),"-i",str(src),"-o","scene_keyframes.sfm","-d","frames"]]
        sfm_source="scene_keyframes.sfm"
    else: raise ValueError("Choose a photo folder or supported video.")
    return first+[
        [exe("CreateStructure"),"-s",sfm_source,"-o","scene.sfm","--export-mvs","scene.mvs","--extract-colors","1"],
        [exe("DensifyPointCloud"),"scene.mvs"],
        [exe("ReconstructMesh"),"scene_dense.mvs","-p","scene_dense.ply"],
        [exe("TextureMesh"),"scene_dense.mvs","-m","scene_dense_mesh.ply","-o","model.mvs","--export-type","glb"]
    ]

def main():
    root=tk.Tk();root.title("Zer0Life 3D Studio — local OpenMVS")
    root.geometry("720x440")
    values=[tk.StringVar() for _ in range(3)]
    events=queue.Queue(); active=False; stopping=threading.Event(); proc=None; lock=threading.Lock()
    def choose(i, video=False):
        v=filedialog.askopenfilename(filetypes=[("Video","*.mp4 *.mov *.mkv *.avi *.webm")]) if video else filedialog.askdirectory()
        if v: values[i].set(v)
    for i,label in enumerate(("OpenMVS binaries folder","Input photos or video","Output parent folder")):
        tk.Label(root,text=label).grid(row=i,column=0,sticky="w",padx=6,pady=5)
        tk.Entry(root,textvariable=values[i],width=45).grid(row=i,column=1,sticky="ew")
        tk.Button(root,text="Folder",command=lambda i=i:choose(i)).grid(row=i,column=2)
    tk.Button(root,text="Video",command=lambda:choose(1,True)).grid(row=1,column=3)
    status=tk.StringVar(value="Ready · all processing stays on your computer")
    tk.Label(root,textvariable=status,wraplength=680).grid(row=4,column=0,columnspan=4,sticky="w")
    def work(plan,out):
        nonlocal proc
        try:
            with (out/"academy-run.log").open("w",encoding="utf-8") as log:
                for i,cmd in enumerate(plan,1):
                    if stopping.is_set(): raise RuntimeError("Cancelled")
                    events.put(("status",f"Stage {i}/{len(plan)} · {Path(cmd[0]).stem}"))
                    with lock:
                        if stopping.is_set(): raise RuntimeError("Cancelled")
                        proc=subprocess.Popen(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT,shell=False)
                    code=proc.wait()
                    with lock: proc=None
                    if stopping.is_set(): raise RuntimeError("Cancelled")
                    if code: raise RuntimeError(f"{Path(cmd[0]).stem} failed ({code}); see academy-run.log")
            result=out/"model.glb"
            if not result.is_file() or not result.stat().st_size:
                raise RuntimeError("No model.glb produced. Check OpenMVS version and log.")
            events.put(("done","GLB ready: "+str(result)))
        except Exception as e: events.put(("done",str(e)+" | "+str(out)))
    def start():
        nonlocal active
        if active:return
        try:
            if not all(v.get().strip() for v in values):raise ValueError("Select all three paths.")
            parent=Path(values[2].get()).resolve()
            if not parent.is_dir(): raise ValueError("Output parent must exist.")
            plan=commands(values[0].get(),values[1].get(),parent)
            out=Path(tempfile.mkdtemp(prefix="zer0life-3d-",dir=parent))
            stopping.clear();active=True;startbtn.config(state="disabled");stopbtn.config(state="normal")
            threading.Thread(target=work,args=(plan,out),daemon=True).start()
        except Exception as e: messagebox.showerror("Cannot start",str(e))
    def stop():
        stopping.set()
        with lock:
            if proc and proc.poll() is None:proc.terminate()
        status.set("Stopping…")
    def pump():
        nonlocal active
        try:
            while True:
                kind,msg=events.get_nowait();status.set(msg)
                if kind=="done":
                    active=False;startbtn.config(state="normal");stopbtn.config(state="disabled")
        except queue.Empty: pass
        root.after(200,pump)
    def close():
        if active:
            stop()
            messagebox.showinfo("Stopping","Close after the current process stops.")
        else:root.destroy()
    startbtn=tk.Button(root,text="Start reconstruction",command=start);startbtn.grid(row=3,column=1,sticky="w",pady=12)
    stopbtn=tk.Button(root,text="Cancel",command=stop,state="disabled");stopbtn.grid(row=3,column=2)
    root.columnconfigure(1,weight=1);root.protocol("WM_DELETE_WINDOW",close);root.after(200,pump);root.mainloop()

if __name__=="__main__":main()
