from learning import require_lesson
from pathlib import Path
import json

def guidance(token,day,mode):
    require_lesson(token,day)
    if day==1:
        from lesson01 import LESSON
        theory=LESSON["sections"]
        assignment=theory[-1]
    else:
        name="lessons02_06.json" if day<=6 else "lessons07_30.json"
        lesson=next(x for x in json.loads(Path(__file__).with_name(name).read_text()) if x["day"]==day)
        theory=[lesson["theory"]]
        assignment=lesson["assignment"]
    if mode=="review":
        return {"mode":"guided_review","material":theory,"steps":["Explain the main idea in your own words.","Give an original example.","Identify a limitation and explain how to verify the result."]}
    if mode=="practice":
        return {"mode":"guided_practice","assignment":assignment,"steps":["Write a brief with measurable criteria.","Produce a first draft.","Check quality, factual claims and usage rights.","Revise and document your changes."]}
    raise ValueError("Unknown guidance mode")
