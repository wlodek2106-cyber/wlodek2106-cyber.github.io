"""Transparent matching by course milestones and approved service category. No external AI."""
TOPICS={"design":(7,8,9,13,16,19,20),"video":(10,11,12,14,15,17,21),"audio":(12,17),"web":(31,32,33,34,35,36,37,38,39,40),"automation":(22,23,24,41,42,43,44,45),"marketing":(18,19,20,26,27,28,29),"other":()}

def rank(jobs,completed,approved_category=None):
    passed=set(completed)
    result=[]
    for j in jobs:
        relevant=TOPICS.get(j["category"],())
        count=len(passed.intersection(relevant))
        approved=j["category"]==approved_category
        if count or approved:
            result.append({**j,"matched_lessons":count,"service_match":approved})
    return sorted(result,key=lambda j:(-int(j["service_match"]),-j["matched_lessons"],-j["id"]))[:30]
