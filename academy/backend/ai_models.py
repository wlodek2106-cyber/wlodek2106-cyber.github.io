"""Provider adapters. No requests unless a configured role is enabled and student opts in."""
import os, json, re
from urllib.request import Request, urlopen
from urllib.error import URLError

ROLES = {
    "teacher": "Explain concepts with an example, then ask the learner to explain it back.",
    "coach": "Guide deliberate practice. Identify one priority skill, a measurable exercise, and a self-check.",
    "code": "Review pasted code only. Identify concrete defects, propose minimal fixes and tests; never claim you executed it.",
    "exam": "Generate a fresh formative question, request the student's reasoning, then explain misconceptions. Never provide official exam answers.",
    "project": "Review the submitted work against the assignment. Identify strengths, evidence gaps, and three prioritized improvements. No official grading."
}
def configuration(role):
    if role not in ROLES:
        raise ValueError("Unknown tutor role")
    if os.getenv("ACADEMY_AI_ENABLED") != "true":
        return None
    suffix=role.upper()
    provider=os.getenv("ACADEMY_AI_PROVIDER_"+suffix,"openai")
    model=os.getenv("ACADEMY_AI_MODEL_"+suffix) or (os.getenv("ACADEMY_AI_MODEL") if provider=="openai" else None)
    keys={"openai":"ACADEMY_AI_API_KEY","anthropic":"ACADEMY_ANTHROPIC_API_KEY","gemini":"ACADEMY_GEMINI_API_KEY"}
    key=os.getenv(keys.get(provider,"ACADEMY_UNUSED_PROVIDER_KEY"))
    if provider not in keys or not key or not model or not re.fullmatch(r"[a-zA-Z0-9._:-]{1,120}",model):
        return None
    return provider,model,key

def status():
    return [{"role":r,"available":configuration(r) is not None,
             "provider":configuration(r)[0] if configuration(r) else None}
            for r in ROLES]

def request_spec(provider,model,key,system,question):
    headers={"Content-Type":"application/json"}
    if provider=="openai":
        headers["Authorization"]="Bearer "+key
        return "https://api.openai.com/v1/chat/completions",headers,{"model":model,"messages":[{"role":"system","content":system},{"role":"user","content":question}],"max_completion_tokens":700}
    if provider=="anthropic":
        headers.update({"x-api-key":key,"anthropic-version":"2023-06-01"})
        return "https://api.anthropic.com/v1/messages",headers,{"model":model,"system":system,"messages":[{"role":"user","content":question}],"max_tokens":700}
    if provider=="gemini":
        headers["x-goog-api-key"]=key
        return "https://generativelanguage.googleapis.com/v1beta/models/"+model+":generateContent",headers,{"system_instruction":{"parts":[{"text":system}]},"contents":[{"role":"user","parts":[{"text":question}]}],"generationConfig":{"maxOutputTokens":700}}
    raise ValueError("Invalid provider")

def parse_answer(provider,data):
    if provider=="openai":
        answer=data["choices"][0]["message"]["content"]
    elif provider=="anthropic":
        answer="\n".join(p["text"] for p in data["content"] if p.get("type")=="text")
    elif provider=="gemini":
        answer="\n".join(p["text"] for p in data["candidates"][0]["content"]["parts"] if "text" in p and not p.get("thought"))
    else:
        raise ValueError("Invalid provider")
    if not isinstance(answer,str) or not answer.strip():
        raise ValueError("Empty answer")
    return answer

def generate(config,system,question):
    provider,model,key=config
    url,headers,payload=request_spec(provider,model,key,system,question)
    req=Request(url,data=json.dumps(payload).encode(),headers=headers)
    with urlopen(req,timeout=25) as response:
        data=json.loads(response.read(1000000))
    return parse_answer(provider,data)
