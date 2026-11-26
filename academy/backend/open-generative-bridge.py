"""Academy bridge for the separately installed Open Generative AI sd.cpp engine.
No downloads, API keys, remote requests or shell. User selects trusted binaries.
Uses the documented sd-cli SD 1.5 text-to-image invocation.
"""
import json, os, sys, subprocess, threading, queue
from pathlib import Path
from datetime import datetime, timezone

def command(engine,model,output,prompt,seed):
    engine,model,output=map(Path,(engine,model,output))
    if engine.name.lower() not in ("sd-cli","sd-cli.exe") or not engine.is_file():
        raise ValueError("Select the installed, trusted sd-cli executable")
    if model.suffix.lower() not in (".safetensors",".gguf",".ckpt") or not model.is_file():
        raise ValueError("Select a downloaded SD 1.5 model")
    if output.suffix.lower()!=".png" or not output.parent.is_dir() or output.exists():
        raise ValueError("Choose a new PNG output in an existing folder")
    if not isinstance(prompt,str) or not 1<=len(prompt.strip())<=2000 or "\x00" in prompt:
        raise ValueError("Prompt must contain 1–2000 characters")
    if type(seed) is not int or not 0<=seed<=2147483647:raise ValueError("Invalid seed")
    return [str(engine.resolve()),"-m",str(model.resolve()),"-p",prompt.strip(),"-o",str(output.resolve()),"--steps","12","-H","512","-W","512","--cfg-scale","7.5","--seed",str(seed),"--sampling-method","euler_a"]

def execute(engine,model,output,prompt,seed):
    args=command(engine,model,output,prompt,seed)
    env=os.environ.copy()
    folder=str(Path(args[0]).parent)
    key="DYLD_LIBRARY_PATH" if sys.platform=="darwin" else "PATH" if os.name=="nt" else "LD_LIBRARY_PATH"
    env[key]=folder+os.pathsep+env.get(key,"")
    result=subprocess.run(args,cwd=folder,env=env,shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=900)
    if result.returncode!=0:raise RuntimeError("sd-cli failed; test the model in the official desktop application first")
    with Path(output).open("rb") as f:
        if f.read(8)!=b"\x89PNG\r\n\x1a\n":raise RuntimeError("No valid PNG output")
    return {"tool":"Open Generative AI / sd.cpp","model":Path(model).name,"prompt":prompt.strip(),"seed":seed,"width":512,"height":512,"steps":12,"output":Path(output).name,"created_at":datetime.now(timezone.utc).isoformat(),"note":"Local output; self-reported production evidence, not official assessment"}

def main():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title("ZER0LIFE · Open Generative AI Bridge");root.geometry("780x660")
    ttk.Label(root,text="Local Image Studio · SD 1.5",font=("Arial",19,"bold")).pack(pady=12)
    ttk.Label(root,text="Install Open Generative AI separately. In Settings → Local Models install sd.cpp and an SD 1.5 model. Select the trusted files below. No API key.",wraplength=730).pack(padx=16)
    values={}
    for key,label in (("engine","Trusted sd-cli executable"),("model","Downloaded SD 1.5 model"),("output","New PNG output")):
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=6);ttk.Label(row,text=label,width=29).pack(side="left")
        var=tk.StringVar();values[key]=var;ttk.Entry(row,textvariable=var).pack(side="left",fill="x",expand=True)
        def pick(k=key,v=var):
            path=filedialog.asksaveasfilename(defaultextension=".png",filetypes=[("PNG","*.png")]) if k=="output" else filedialog.askopenfilename()
            if path:v.set(path)
        ttk.Button(row,text="Browse",command=pick).pack(side="left")
    ttk.Label(root,text="Prompt (original or authorized subjects only)").pack(anchor="w",padx=16)
    prompt=tk.Text(root,height=7,wrap="word");prompt.pack(fill="x",padx=16)
    seed=tk.StringVar(value="42");ttk.Label(root,text="Seed").pack(anchor="w",padx=16);ttk.Entry(root,textvariable=seed).pack(anchor="w",padx=16)
    status=tk.StringVar(value="Ready");ttk.Label(root,textvariable=status,wraplength=730).pack(pady=10)
    events=queue.Queue();report=None
    def run():
        nonlocal report
        try:
            args=[values[k].get() for k in ("engine","model","output")]+[prompt.get("1.0","end").strip(),int(seed.get())]
            command(*args)
        except Exception as e:messagebox.showerror("Input",str(e));return
        if not messagebox.askyesno("Run locally","Run only the trusted installed sd-cli and an authorized SD 1.5 model? This uses your local CPU/GPU and may take time."):return
        report=None;start.configure(state="disabled");save.configure(state="disabled");status.set("Generating locally…")
        def worker():
            try:events.put(("ok",execute(*args)))
            except Exception as e:events.put(("error",str(e)))
        threading.Thread(target=worker,daemon=True).start()
    def export():
        if report is None:return
        dest=filedialog.asksaveasfilename(defaultextension=".json",filetypes=[("JSON report","*.json")])
        if dest:Path(dest).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf-8")
    start=ttk.Button(root,text="Generate 512 × 512",command=run);start.pack(pady=5)
    save=ttk.Button(root,text="Export Academy report",command=export,state="disabled");save.pack(pady=5)
    def poll():
        nonlocal report
        try:
            kind,value=events.get_nowait();start.configure(state="normal")
            if kind=="ok":report=value;save.configure(state="normal");status.set("PNG generated: "+value["output"])
            else:status.set(value)
        except queue.Empty:pass
        root.after(200,poll)
    root.after(200,poll);root.mainloop()
if __name__=="__main__":main()
