"""Tiered curriculum of external public repositories. No third-party execution or hosted APIs."""
PLANS=("starter","pro","vip","elite")
LANGS=("en","ru","uk","pl")
ROWS=[
  [
    "starter",
    "Ollama",
    "ollama/ollama",
    "cpu",
    "llm",
    "/free-ai",
    "Run a small local model and compare two prompts.",
    "Запусти небольшую модель и сравни два промпта.",
    "Запусти малу модель і порівняй два промпти.",
    "Uruchom mały model i porównaj dwa prompty."
  ],
  [
    "starter",
    "llama.cpp",
    "ggml-org/llama.cpp",
    "cpu",
    "llm",
    "/free-ai",
    "Run a compatible GGUF model and measure latency.",
    "Запусти совместимую GGUF-модель и измерь задержку.",
    "Запусти сумісну GGUF-модель і виміряй затримку.",
    "Uruchom zgodny model GGUF i zmierz opóźnienie."
  ],
  [
    "starter",
    "Qwen3",
    "QwenLM/Qwen3",
    "cpu",
    "llm",
    "/free-ai",
    "Create a study dialogue and verify three factual answers.",
    "Создай учебный диалог и проверь три фактических ответа.",
    "Створи навчальний діалог і перевір три відповіді.",
    "Stwórz dialog edukacyjny i sprawdź trzy odpowiedzi."
  ],
  [
    "starter",
    "Whisper.cpp",
    "ggml-org/whisper.cpp",
    "cpu",
    "voice",
    "/voice-studio",
    "Transcribe your own 30-second recording and correct errors.",
    "Расшифруй собственную запись на 30 секунд и исправь ошибки.",
    "Розшифруй власний запис на 30 секунд і виправ помилки.",
    "Przepisz własne nagranie 30 s i popraw błędy."
  ],
  [
    "starter",
    "Kokoro",
    "hexgrad/kokoro",
    "cpu",
    "voice",
    "/voice-studio",
    "Generate a short narration in a supported language.",
    "Создай короткую озвучку на поддерживаемом языке.",
    "Створи коротку озвучку підтримуваною мовою.",
    "Wygeneruj krótką narrację w obsługiwanym języku."
  ],
  [
    "starter",
    "Piper",
    "OHF-Voice/piper1-gpl",
    "cpu",
    "voice",
    "/voice-studio",
    "Synthesize a sentence with a permitted voice model.",
    "Озвучь фразу разрешённой голосовой моделью.",
    "Озвуч фразу дозволеною голосовою моделлю.",
    "Wygeneruj zdanie dozwolonym modelem głosu."
  ],
  [
    "starter",
    "MarkItDown",
    "microsoft/markitdown",
    "cpu",
    "knowledge",
    "/dashboard?module=knowledge",
    "Convert a sample document to Markdown; inspect missing text.",
    "Преобразуй учебный документ в Markdown и проверь пропуски.",
    "Перетвори документ у Markdown і перевір пропуски.",
    "Zamień dokument na Markdown i sprawdź braki."
  ],
  [
    "starter",
    "Penpot",
    "penpot/penpot",
    "server",
    "design",
    "/design-studio",
    "Design a mobile screen using an existing local installation.",
    "Создай мобильный экран в установленном локальном Penpot.",
    "Створи мобільний екран у локальному Penpot.",
    "Zaprojektuj ekran mobilny w lokalnym Penpot."
  ],
  [
    "pro",
    "ComfyUI",
    "Comfy-Org/ComfyUI",
    "gpu",
    "image",
    "/design-studio",
    "Build an image workflow and record the seed and settings.",
    "Собери workflow изображения, запиши seed и настройки.",
    "Збери workflow зображення, запиши seed і налаштування.",
    "Zbuduj workflow obrazu, zapisz seed i ustawienia."
  ],
  [
    "pro",
    "WanGP",
    "deepbeepmeep/WanGP",
    "gpu",
    "video",
    "/animation-studio",
    "Produce a short clip with a compatible low-memory configuration.",
    "Создай короткий клип в совместимой конфигурации с малой памятью.",
    "Створи короткий кліп у сумісній конфігурації з малою пам’яттю.",
    "Stwórz krótki klip w zgodnej konfiguracji o małej pamięci."
  ],
  [
    "pro",
    "LivePortrait",
    "KlingAIResearch/LivePortrait",
    "gpu",
    "human",
    "/animation-studio",
    "Animate an original fictional portrait and check artifacts.",
    "Оживи вымышленный портрет и проверь артефакты.",
    "Оживи вигаданий портрет і перевір артефакти.",
    "Ożyw fikcyjny portret i sprawdź artefakty."
  ],
  [
    "pro",
    "MuseTalk",
    "TMElyralab/MuseTalk",
    "gpu",
    "human",
    "/animation-studio",
    "Synchronize a permitted avatar with your own narration.",
    "Синхронизируй разрешённый аватар с собственной озвучкой.",
    "Синхронізуй дозволений аватар із власною озвучкою.",
    "Zsynchronizuj dozwolony awatar z własną narracją."
  ],
  [
    "pro",
    "ACE-Step",
    "ace-step/ACE-Step",
    "gpu",
    "music",
    "/music-studio",
    "Create an original short music cue and log model rights.",
    "Создай оригинальную музыкальную заставку и запиши права модели.",
    "Створи оригінальну музичну заставку й запиши права моделі.",
    "Stwórz oryginalny motyw i zanotuj prawa modelu."
  ],
  [
    "pro",
    "LangGraph",
    "langchain-ai/langgraph",
    "cpu",
    "agent",
    "/automation-studio",
    "Create a three-node draft-only agent with a local model.",
    "Создай агента из трёх узлов без внешних действий.",
    "Створи агента з трьох вузлів без зовнішніх дій.",
    "Stwórz agenta z trzema węzłami bez działań zewnętrznych."
  ],
  [
    "pro",
    "Qdrant",
    "qdrant/qdrant",
    "server",
    "knowledge",
    "/dashboard?module=knowledge",
    "Index synthetic notes locally and compare retrieval results.",
    "Индексируй вымышленные заметки локально и сравни поиск.",
    "Індексуй вигадані нотатки локально й порівняй пошук.",
    "Indeksuj fikcyjne notatki lokalnie i porównaj wyniki."
  ],
  [
    "pro",
    "Docling",
    "docling-project/docling",
    "cpu",
    "knowledge",
    "/dashboard?module=knowledge",
    "Extract a table from a sample PDF and validate it.",
    "Извлеки таблицу из учебного PDF и сверь её.",
    "Витягни таблицю з навчального PDF і перевір її.",
    "Wyodrębnij tabelę z przykładowego PDF i sprawdź ją."
  ],
  [
    "pro",
    "Nemotron",
    "NVIDIA-NeMo/Nemotron",
    "gpu",
    "llm",
    "/free-ai",
    "Choose compatible local weights from the hub; compare a tutor answer with Qwen.",
    "Выбери совместимые локальные веса из хаба; сравни ответ с Qwen.",
    "Вибери сумісні локальні ваги; порівняй відповідь із Qwen.",
    "Wybierz zgodne lokalne wagi; porównaj odpowiedź z Qwen."
  ],
  [
    "pro",
    "NeMo Speech C++",
    "NVIDIA/NeMo-Speech.cpp",
    "cpu",
    "voice",
    "/voice-studio",
    "Transcribe a permitted sample with a supported local model.",
    "Расшифруй разрешённый пример совместимой локальной моделью.",
    "Розшифруй дозволений приклад сумісною локальною моделлю.",
    "Przepisz dozwoloną próbkę zgodnym lokalnym modelem."
  ],
  [
    "vip",
    "Wan 2.2",
    "Wan-Video/Wan2.2",
    "gpu",
    "video",
    "/animation-studio",
    "Generate a short scene and check temporal continuity.",
    "Создай короткую сцену и проверь временную согласованность.",
    "Створи коротку сцену й перевір часову узгодженість.",
    "Wygeneruj krótką scenę i sprawdź spójność czasową."
  ],
  [
    "vip",
    "LTX Video",
    "Lightricks/LTX-Video",
    "gpu",
    "video",
    "/animation-studio",
    "Generate two connected shots and compare motion.",
    "Создай два связанных кадра и сравни движение.",
    "Створи два пов’язані кадри й порівняй рух.",
    "Wygeneruj dwa powiązane ujęcia i porównaj ruch."
  ],
  [
    "vip",
    "FastVideo",
    "hao-ai-lab/FastVideo",
    "cuda",
    "video",
    "/animation-studio",
    "Benchmark a supported video workflow with fixed settings.",
    "Измерь скорость совместимого видео-workflow при фиксированных настройках.",
    "Виміряй швидкість сумісного відеопроцесу зі сталими налаштуваннями.",
    "Zmierz szybkość zgodnego workflow ze stałymi ustawieniami."
  ],
  [
    "vip",
    "TRELLIS",
    "microsoft/TRELLIS",
    "cuda",
    "3d",
    "/openmvs-lab",
    "Generate an original 3D asset and inspect its mesh.",
    "Создай оригинальный 3D-объект и проверь сетку.",
    "Створи оригінальний 3D-об’єкт і перевір сітку.",
    "Stwórz oryginalny obiekt 3D i sprawdź siatkę."
  ],
  [
    "vip",
    "Audio2Face 3D",
    "NVIDIA/Audio2Face-3D",
    "cuda",
    "human",
    "/animation-studio",
    "Choose a permitted model and create a fictional avatar animation.",
    "Выбери разрешённую модель и анимируй вымышленного аватара.",
    "Вибери дозволену модель і анімуй вигаданого аватара.",
    "Wybierz dozwolony model i animuj fikcyjny awatar."
  ],
  [
    "vip",
    "NeMo Speech",
    "NVIDIA-NeMo/Speech",
    "cuda",
    "voice",
    "/voice-studio",
    "Evaluate speech recognition on three own recordings.",
    "Оцени распознавание речи на трёх собственных записях.",
    "Оціни розпізнавання мовлення на трьох власних записах.",
    "Oceń rozpoznawanie mowy na trzech własnych nagraniach."
  ],
  [
    "vip",
    "NeMo Agent Toolkit",
    "NVIDIA/NeMo-Agent-Toolkit",
    "cpu",
    "agent",
    "/automation-studio",
    "Build a local-model workflow with explicit human approval.",
    "Собери workflow с локальной моделью и подтверждением человека.",
    "Збери workflow з локальною моделлю та підтвердженням людини.",
    "Zbuduj workflow z modelem lokalnym i zgodą człowieka."
  ],
  [
    "vip",
    "NeMo Agent Examples",
    "NVIDIA/NeMo-Agent-Toolkit-Examples",
    "reference",
    "agent",
    "/automation-studio",
    "Adapt a reference example to synthetic data; remove paid endpoints.",
    "Адаптируй пример на вымышленных данных; убери платные endpoints.",
    "Адаптуй приклад до вигаданих даних; прибери платні endpoints.",
    "Dostosuj przykład do fikcyjnych danych; usuń płatne endpointy."
  ],
  [
    "vip",
    "Generative AI Examples",
    "NVIDIA/GenerativeAIExamples",
    "reference",
    "agent",
    "/automation-studio",
    "Map one example to a local architecture without paid calls.",
    "Перенеси один пример в локальную архитектуру без платных вызовов.",
    "Перенеси приклад у локальну архітектуру без платних викликів.",
    "Przenieś przykład do lokalnej architektury bez płatnych wywołań."
  ],
  [
    "vip",
    "SANA",
    "NVlabs/Sana",
    "cuda",
    "image",
    "/design-studio",
    "Generate a visual from a brief and document settings.",
    "Создай визуал по брифу и задокументируй настройки.",
    "Створи візуал за брифом і задокументуй налаштування.",
    "Stwórz wizualizację według briefu i zapisz ustawienia."
  ],
  [
    "vip",
    "NVIDIA RAG",
    "NVIDIA-AI-Blueprints/rag",
    "server",
    "knowledge",
    "/dashboard?module=knowledge",
    "Design a local retrieval prototype and verify citations; no hosted NIM.",
    "Спроектируй локальный поиск и проверь цитаты; без облачного NIM.",
    "Спроєктуй локальний пошук і перевір цитати; без хмарного NIM.",
    "Zaprojektuj lokalne wyszukiwanie i sprawdź cytaty; bez chmury NIM."
  ],
  [
    "vip",
    "NVIDIA Skills",
    "NVIDIA/skills",
    "reference",
    "agent",
    "/automation-studio",
    "Review one skill and adapt only its permitted local steps.",
    "Изучи один skill и адаптируй только разрешённые локальные шаги.",
    "Вивчи один skill і адаптуй лише дозволені локальні кроки.",
    "Przejrzyj skill i dostosuj tylko dozwolone lokalne kroki."
  ],
  [
    "elite",
    "Model Optimizer",
    "NVIDIA/Model-Optimizer",
    "cuda",
    "infra",
    "/ai-workspace",
    "Compare memory and quality before and after supported quantization.",
    "Сравни память и качество до и после совместимой квантизации.",
    "Порівняй пам’ять і якість до та після сумісної квантизації.",
    "Porównaj pamięć i jakość przed i po zgodnej kwantyzacji."
  ],
  [
    "elite",
    "Audio2Face Training",
    "NVIDIA/Audio2Face-3D-Training-Framework",
    "cuda",
    "human",
    "/animation-studio",
    "Study a training recipe with licensed sample data; document constraints.",
    "Изучи рецепт обучения на лицензированных данных; опиши ограничения.",
    "Вивчи рецепт навчання на ліцензованих даних; опиши обмеження.",
    "Przeanalizuj trening na licencjonowanych danych; opisz ograniczenia."
  ],
  [
    "elite",
    "Cosmos",
    "NVIDIA/Cosmos",
    "cuda",
    "video",
    "/animation-studio",
    "Evaluate one world-model example on synthetic material if hardware permits.",
    "Оцени пример модели мира на синтетическом материале при подходящем GPU.",
    "Оціни приклад моделі світу на синтетичних даних за наявності GPU.",
    "Oceń przykład modelu świata na danych syntetycznych, jeśli sprzęt pozwala."
  ],
  [
    "elite",
    "LongLive",
    "NVlabs/LongLive",
    "cuda",
    "video",
    "/animation-studio",
    "Compare continuity across longer generated sequences.",
    "Сравни согласованность длинных сгенерированных последовательностей.",
    "Порівняй узгодженість довгих згенерованих послідовностей.",
    "Porównaj spójność dłuższych wygenerowanych sekwencji."
  ],
  [
    "elite",
    "TensorRT-LLM",
    "NVIDIA/TensorRT-LLM",
    "cuda",
    "infra",
    "/ai-workspace",
    "Benchmark compatible inference and report latency and VRAM.",
    "Измерь скорость совместимого inference и расход VRAM.",
    "Виміряй швидкість сумісного inference та витрати VRAM.",
    "Zmierz opóźnienie zgodnej inferencji i zużycie VRAM."
  ],
  [
    "elite",
    "NeMo Guardrails",
    "NVIDIA-NeMo/Guardrails",
    "cpu",
    "security",
    "/automation-studio",
    "Test a local assistant against synthetic unwanted instructions.",
    "Проверь локального ассистента на синтетических нежелательных инструкциях.",
    "Перевір локального асистента на синтетичних небажаних інструкціях.",
    "Sprawdź lokalnego asystenta na syntetycznych niepożądanych instrukcjach."
  ],
  [
    "elite",
    "NeMo Evaluator",
    "NVIDIA-NeMo/Evaluator",
    "server",
    "security",
    "/ai-workspace",
    "Create a reproducible local evaluation with a small synthetic benchmark.",
    "Создай воспроизводимую локальную оценку на небольшом синтетическом тесте.",
    "Створи відтворювану локальну оцінку на малому синтетичному тесті.",
    "Stwórz odtwarzalną lokalną ewaluację na małym syntetycznym teście."
  ],
  [
    "elite",
    "NemoClaw",
    "NVIDIA/NemoClaw",
    "server",
    "security",
    "/automation-studio",
    "Study isolation policies and test a harmless draft-only sandbox.",
    "Изучи политики изоляции и протестируй безвредную среду черновиков.",
    "Вивчи політики ізоляції та перевір безпечне середовище чернеток.",
    "Zbadaj izolację i przetestuj bezpieczny sandbox szkiców."
  ],
  [
    "elite",
    "OpenShell",
    "ai-openshell/openshell",
    "server",
    "security",
    "/automation-studio",
    "Define denied network and filesystem actions in a local test sandbox.",
    "Задай запрет сетевых и файловых действий в локальном тестовом sandbox.",
    "Задай заборону мережевих і файлових дій у локальній пісочниці.",
    "Zablokuj działania sieciowe i plikowe w lokalnym sandboxie."
  ],
  [
    "elite",
    "Garak",
    "NVIDIA/garak",
    "cpu",
    "security",
    "/ai-workspace",
    "Evaluate only your own local model using synthetic prompts.",
    "Оцени только собственную локальную модель синтетическими промптами.",
    "Оціни лише власну локальну модель синтетичними промптами.",
    "Oceń wyłącznie własny lokalny model syntetycznymi promptami."
  ],
  [
    "elite",
    "Warp",
    "NVIDIA/warp",
    "gpu",
    "3d",
    "/openmvs-lab",
    "Run a small simulation and measure its reproducibility.",
    "Запусти небольшую симуляцию и проверь воспроизводимость.",
    "Запусти малу симуляцію й перевір відтворюваність.",
    "Uruchom małą symulację i sprawdź odtwarzalność."
  ],
  [
    "elite",
    "Audio2Face SDK",
    "NVIDIA/Audio2Face-3D-SDK",
    "cuda",
    "human",
    "/animation-studio",
    "Study the SDK and test a permitted audio-to-face example locally.",
    "Изучи SDK и локально проверь разрешённый пример анимации лица.",
    "Вивчи SDK і локально перевір дозволений приклад анімації обличчя.",
    "Przeanalizuj SDK i lokalnie przetestuj dozwolony przykład animacji twarzy."
  ]
]
def catalog(progress,lang="en"):
    if not isinstance(lang,str) or lang not in LANGS:lang="en"
    plan=progress.get("plan")
    rank=PLANS.index(plan) if progress.get("access") and plan in PLANS else -1
    if progress.get("owner_preview"):rank=3
    index=LANGS.index(lang)
    groups=[]
    for level in PLANS:
        selected=[r for r in ROWS if r[0]==level]
        allowed=PLANS.index(level)<=rank
        items=[]
        if allowed:
            for tier,name,repo,mode,category,academy,*tasks in selected:
                items.append({"name":name,"github":"https://github.com/"+repo,"mode":mode,"category":category,"academy":academy,"task":tasks[index],"status":"external_reference","commercial_license":"review_required"})
        groups.append({"plan":level,"count":len(selected),"unlocked":allowed,"items":items})
    return {"version":"2027.1","total":len(ROWS),"groups":groups,"hosted_inference":False,"paid_api_required":False}
def student_catalog(token,lang):
    from learning import student_progress
    return catalog(student_progress(token),lang)
