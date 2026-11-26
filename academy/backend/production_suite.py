"""Build the small source-only desktop production suite on demand."""
from pathlib import Path
from io import BytesIO
from zipfile import ZipFile,ZIP_DEFLATED
import hashlib,json
VERSION="1.0.0"
FILES=("elite-production-launcher.py","open-generative-bridge.py","local-narration-studio.py","commercial-video-assembler.py","delivery-quality-check.py","client-delivery-kit.py")
GUIDES={
"en":"Extract the entire ZIP into one folder. Open elite-production-launcher.py using Python 3.11+ with Tkinter. If your system does not associate .py files with Python, open the launcher from Python IDLE. Install the external engines separately. The suite does not include models, Python, FFmpeg or eSpeak. Use only trusted executables and licensed media. The image engine requires a compatible sd-cli build and SD 1.5 model; video generation itself is external (e.g. Open Generative AI/Wan2GP with compatible hardware).",
"ru":"Распакуй весь ZIP в одну папку. Открой elite-production-launcher.py в Python 3.11+ с Tkinter. Если .py не открывается двойным нажатием, открой файл в Python IDLE и запусти через Run Module. Движки устанавливаются отдельно. Python, FFmpeg, eSpeak и модели в комплект не входят. Используй доверенные программы и разрешённые материалы. Для изображений нужен совместимый sd-cli и SD 1.5; генерация видео выполняется отдельно, например в Open Generative AI/Wan2GP на совместимом оборудовании.",
"uk":"Розпакуй весь ZIP в одну папку. Відкрий elite-production-launcher.py у Python 3.11+ з Tkinter або Python IDLE (Run Module). Рушії встановлюються окремо. Python, FFmpeg, eSpeak та моделі не включені. Використовуй довірені програми та дозволені матеріали. Для зображень потрібен сумісний sd-cli та SD 1.5; відео генерується окремо.",
"pl":"Rozpakuj cały ZIP do jednego folderu. Otwórz elite-production-launcher.py w Python 3.11+ z Tkinter lub Python IDLE (Run Module). Silniki zainstaluj osobno. Python, FFmpeg, eSpeak i modele nie są zawarte. Korzystaj z zaufanych programów i licencjonowanych materiałów. Obrazy wymagają sd-cli i SD 1.5; generacja wideo odbywa się osobno."
}
def build(lang="en",root=None):
    root=Path(root) if root is not None else Path(__file__).resolve().parent
    if not isinstance(lang,str) or lang not in GUIDES:lang="en"
    guide=("ZER0LIFE ELITE Production Suite "+VERSION+"\n\n"+GUIDES[lang]+"\n\n"
        "Python: https://www.python.org/downloads/\nFFmpeg / FFprobe: https://ffmpeg.org/download.html\n"
        "eSpeak NG: https://github.com/espeak-ng/espeak-ng\n"
        "Open Generative AI: https://github.com/Anil-matcha/Open-Generative-AI/releases\n\n"
        "Workflow: Academy storyboard JSON -> generate authorized scenes externally -> narration JSON to WAV -> assemble MP4 -> inspect using FFprobe -> ZIP delivery kit.\n"
        "The desktop suite is a source-only GUI collection, not a signed native installer. No cloud API keys or services are required by the bundled scripts. External model/engine licenses and hardware requirements vary.\n"
        "QC is a metadata check; verify playback, synchronization, factual claims and rights manually. Do not send customer assets without permission.\n")
    files={name:(root/name).read_bytes() for name in FILES}
    for name,data in files.items():
        if len(data)>200000:raise ValueError("Unexpected tool size")
        compile(data,name,"exec")
    files["README.txt"]=guide.encode("utf-8")
    manifest={"version":VERSION,"files":[{"name":name,"sha256":hashlib.sha256(data).hexdigest(),"bytes":len(data)} for name,data in files.items()]}
    files["manifest.json"]=json.dumps(manifest,indent=2).encode("utf-8")
    buf=BytesIO()
    with ZipFile(buf,"w",compression=ZIP_DEFLATED) as z:
        for name,data in files.items():z.writestr(name,data)
    return buf.getvalue()
def student_bundle(token,lang):
    from elite_program import access,unlocked
    if not unlocked(access(token)):raise PermissionError("Complete core lessons first")
    return build(lang)
