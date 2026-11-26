"""Local Academy media/document bridge. External engines are installed by the user."""
from pathlib import Path
import os, subprocess, tempfile, shutil, wave, threading, queue

TOOLS={
    "Whisper.cpp":("https://github.com/ggml-org/whisper.cpp",(".wav",),".bin",".txt"),
    "Piper":("https://github.com/OHF-Voice/piper1-gpl",(".txt",),".onnx",".wav"),
    "MarkItDown":("https://github.com/microsoft/markitdown",(".pdf",".docx",".pptx",".xlsx",".txt",".csv"),None,".md"),
}
def regular(path,extensions=None,limit=None):
    if not path:raise ValueError("Select an existing file")
    p=Path(path).expanduser().resolve(strict=True)
    if not p.is_file() or (extensions and p.suffix.lower() not in extensions):
        raise ValueError("Unsupported file: "+p.name)
    if limit and p.stat().st_size>limit:raise ValueError("File exceeds size limit")
    return p

def prepare(tool,executable,source,model,directory):
    if tool not in TOOLS:raise ValueError("Unknown tool")
    _,extensions,model_ext,out_ext=TOOLS[tool]
    exe=regular(executable)
    if exe.suffix.lower() in (".bat",".cmd",".ps1") or not os.access(exe,os.X_OK):
        raise ValueError("Select the installed executable, not a shell script")
    src=regular(source,extensions,100*1024*1024)
    output=Path(directory)/("result"+out_ext)
    stdin=None
    if tool=="Whisper.cpp":
        m=regular(model,(model_ext,))
        with wave.open(str(src),"rb") as wav:
            if wav.getnchannels()!=1 or wav.getsampwidth()!=2 or wav.getframerate()!=16000:
                raise ValueError("Whisper input must be mono 16 kHz 16-bit PCM WAV")
            if wav.getnframes()>16000*1800:raise ValueError("Maximum audio duration: 30 minutes")
        command=[str(exe),"-m",str(m),"-f",str(src),"-l","auto","-otxt","-of",str(output.with_suffix(""))]
    elif tool=="Piper":
        m=regular(model,(model_ext,))
        regular(str(m)+".json",(".json",),1024*1024)
        if src.stat().st_size>20000:raise ValueError("Narration must be under 20 KB")
        text=src.read_text(encoding="utf-8-sig").strip()
        if not text or len(text)>4000:raise ValueError("Enter 1–4000 characters in the text file")
        stdin=(text+"\n").encode("utf-8")
        command=[str(exe),"-m",str(m),"-f",str(output)]
    else:
        command=[str(exe),str(src),"-o",str(output)]
    return command,stdin,output

def run(tool,executable,source,model,destination,runner=subprocess.run):
    if tool not in TOOLS:raise ValueError("Unknown tool")
    dest=Path(destination).expanduser()
    if dest.suffix.lower()!=TOOLS[tool][3]:raise ValueError("Use the required output extension")
    if dest.exists() or dest.is_symlink():raise FileExistsError("Output already exists; choose a new name")
    with tempfile.TemporaryDirectory(prefix="zer0life-local-") as directory:
        command,stdin,output=prepare(tool,executable,source,model,directory)
        options={"cwd":directory,"shell":False,"timeout":300,"stdout":subprocess.DEVNULL,"stderr":subprocess.DEVNULL,"check":True}
        if stdin is None:options["stdin"]=subprocess.DEVNULL
        else:options["input"]=stdin
        runner(command,**options)
        if output.is_symlink() or not output.is_file() or not 0<output.stat().st_size<=100*1024*1024:
            raise ValueError("Engine produced no valid output")
        if tool=="Piper":
            with wave.open(str(output),"rb") as w:
                if not w.getnframes():raise ValueError("Empty audio")
        else:output.read_text(encoding="utf-8")
        created=False
        try:
            with dest.open("xb") as target:
                created=True
                with output.open("rb") as source_file:shutil.copyfileobj(source_file,target)
        except BaseException:
            if created:dest.unlink(missing_ok=True)
            raise
    return str(dest)

def main():
    import tkinter as tk
    from tkinter import ttk,filedialog,messagebox
    root=tk.Tk();root.title("ZER0LIFE · Local Tool Bridge");root.geometry("760x480")
    tool=tk.StringVar(value="Whisper.cpp")
    fields={key:tk.StringVar() for key in ("Executable","Input","Model")}
    status=tk.StringVar(value="Install the selected engine and model separately from its official GitHub.")
    ttk.Label(root,text="ZER0LIFE · Local Tool Bridge",font=("Arial",19,"bold")).pack(pady=12)
    picker=ttk.Combobox(root,textvariable=tool,values=list(TOOLS),state="readonly");picker.pack(fill="x",padx=16)
    info=ttk.Label(root,wraplength=700);info.pack(pady=8,padx=16)
    def refresh(*args):
        model=TOOLS[tool.get()][2]
        info.configure(text=TOOLS[tool.get()][0]+"\nInput: "+", ".join(TOOLS[tool.get()][1])+" · Model: "+(model or "not needed")+" · Output: "+TOOLS[tool.get()][3])
        fields["Input"].set("");fields["Model"].set("");fields["Executable"].set("")
    picker.bind("<<ComboboxSelected>>",refresh)
    for name,value in fields.items():
        row=ttk.Frame(root);row.pack(fill="x",padx=16,pady=5)
        ttk.Label(row,text=name,width=13).pack(side="left")
        ttk.Entry(row,textvariable=value).pack(side="left",fill="x",expand=True)
        def select(v=value):
            path=filedialog.askopenfilename()
            if path:v.set(path)
        ttk.Button(row,text="Browse",command=select).pack(side="right")
    events=queue.Queue();busy=False
    def start():
        nonlocal busy
        if busy:return
        mode=tool.get();suffix=TOOLS[mode][3]
        dest=filedialog.asksaveasfilename(defaultextension=suffix,filetypes=[("Output","*"+suffix)])
        if not dest:return
        if not messagebox.askyesno("Local execution","Use only a trusted installed executable and licensed models. The Academy does not download tools, upload files or provide paid APIs. External programs can have their own network behavior. Continue?"):return
        args=(mode,fields["Executable"].get(),fields["Input"].get(),fields["Model"].get(),dest)
        busy=True;button.configure(state="disabled");picker.configure(state="disabled");status.set("Running locally…")
        def job():
            try:events.put(("ok",run(*args)))
            except Exception as e:events.put(("error",str(e)))
        threading.Thread(target=job,daemon=True).start()
    button=ttk.Button(root,text="Run and export",command=start);button.pack(pady=12)
    ttk.Label(root,textvariable=status,wraplength=700).pack(padx=16)
    def poll():
        nonlocal busy
        try:
            kind,value=events.get_nowait();busy=False;button.configure(state="normal");picker.configure(state="readonly")
            status.set(("Saved: " if kind=="ok" else "Error: ")+value)
        except queue.Empty:pass
        root.after(150,poll)
    refresh();root.after(150,poll);root.mainloop()
if __name__=="__main__":main()
