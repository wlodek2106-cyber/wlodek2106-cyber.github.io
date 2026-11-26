import unittest
from datetime import datetime, timedelta, timezone
from progression import eligible, quiz_passed

class ProgressTests(unittest.TestCase):
    def test_practical_assessment(self):
        from practical_assessment import evaluate,grade,dispatch
        from unittest.mock import Mock,patch
        from types import SimpleNamespace
        import sys,json
        scores={"goal":18,"quality":18,"workflow":18,"verification":18,"rights":12}
        note="Inspected output and test report."
        result=evaluate(scores,note)
        self.assertEqual(result["score"],84)
        self.assertTrue(result["passed"])
        self.assertFalse(evaluate({**scores,"rights":11},note)["passed"])
        self.assertFalse(evaluate({k:12 for k in scores},note)["passed"])
        for bad in ({**scores,"rights":True},{**scores,"quality":21},{**scores,"goal":-1},{"goal":20}):
            with self.assertRaises(ValueError):evaluate(bad,note)
        with self.assertRaises(ValueError):evaluate(scores,"short")
        cur=Mock()
        body={"id":17,"scores":scores,"feedback":note,"inspected":True}
        cur.fetchone.return_value=(17,)
        self.assertEqual(grade(cur,body)["id"],17)
        sql,args=cur.execute.call_args.args
        self.assertIn("WHERE id=%s AND score IS NULL",sql)
        self.assertEqual(args[0],84)
        self.assertEqual(json.loads(args[2]),scores)
        self.assertEqual(args[-1],17)
        with self.assertRaises(ValueError):grade(cur,{**body,"inspected":False})
        cur.fetchone.return_value=None
        with self.assertRaises(PermissionError):grade(cur,body)
        with patch.dict(sys.modules,{"partners":SimpleNamespace(owner=Mock(side_effect=PermissionError)),"database":SimpleNamespace(transaction=Mock())}):
            with self.assertRaises(PermissionError):dispatch("invalid","grade",body)
    def test_adaptive_study_agenda(self):
        from adaptive_study import agenda
        p={"lessons":[{"day":1,"unlocked":True,"completed":True},{"day":2,"unlocked":True,"completed":False},{"day":3,"unlocked":False,"completed":False}]}
        j={"items":[{"day":1,"latest":75,"due":True},{"day":3,"latest":10,"due":True}]}
        for n in (15,30,60):
            r=agenda(p,j,n)
            self.assertEqual(sum(x["minutes"] for x in r["items"]),n)
            self.assertEqual(r["focus"]["day"],1)
            self.assertEqual(r["focus"]["level"],"foundation")
            self.assertEqual(r["items"][0]["kind"],"review")
        r=agenda(p,{"items":[{"day":1,"latest":95,"due":False}]},30)
        self.assertEqual(r["focus"]["day"],2)
        self.assertEqual(r["items"][0]["kind"],"learn")
        self.assertEqual(agenda(p,{"items":[{"day":1,"latest":92,"due":True}]},15)["focus"]["level"],"challenge")
        self.assertEqual(agenda(p,{"items":[{"day":1,"latest":85,"due":True}]},15)["focus"]["level"],"reinforce")
        self.assertIsNone(agenda({"lessons":[]},{"items":[]},15)["focus"])
        for v in (0,45,True,"30"):
            with self.assertRaises(ValueError): agenda(p,j,v)
    def test_adaptive_practice_focus(self):
        from adaptive_study import practice_focus
        self.assertIsNone(practice_focus(None,"ru"))
        for lang in ("en","ru","uk","pl"):
            tasks=[]
            for level in ("foundation","reinforce","challenge"):
                d=practice_focus({"day":2,"level":level,"latest":75},lang)
                self.assertEqual(d["day"],2)
                self.assertEqual(d["level"],level)
                self.assertFalse(d["official_grading"])
                self.assertEqual(d["evidence"],"quiz_summary_only")
                self.assertNotIn("latest",d)
                tasks.append(d["task"])
            self.assertEqual(len(set(tasks)),3)
        with self.assertRaises(ValueError):practice_focus(None,"invalid")
    def test_mentor_draft_review_access(self):
        from unittest.mock import patch
        from project_reviewer import draft_review,FIELDS
        fields={k:"Evidence for "+k for k in FIELDS}
        with patch("learning.require_lesson") as access:
            result=draft_review("session",1,fields,"ru")
            access.assert_called_once_with("session",1)
            self.assertTrue(result["ready_for_submission"])
            self.assertFalse(result["official_grade"])
            self.assertEqual(result["engine"],"presence_check_only")
            fields["rights"]=""
            self.assertFalse(draft_review("session",1,fields,"en")["ready_for_submission"])
        with patch("learning.require_lesson",side_effect=PermissionError):
            with self.assertRaises(PermissionError):draft_review("session",2,fields,"en")
        with self.assertRaises(ValueError):draft_review("session",True,fields,"en")
    def test_teacher_snapshot(self):
        from teacher_profile import snapshot
        p={"lessons":[{"day":1,"unlocked":True,"completed":True},{"day":2,"unlocked":True,"completed":False},{"day":3,"unlocked":False,"completed":False}],"email":"private"}
        j={"items":[{"day":1,"latest":85,"attempts":2,"due":False,"reflection":"private"},{"day":2,"latest":60,"attempts":1,"due":True,"reflection":"private"},{"day":3,"latest":20,"attempts":1,"due":True}]}
        result=snapshot(p,j)
        self.assertEqual(result["completed"],1)
        self.assertEqual(result["available"],2)
        self.assertEqual(result["next_day"],2)
        self.assertEqual([x["day"] for x in result["review"]],[2,1])
        self.assertEqual(set(result["review"][0]),{"day","latest","attempts","due"})
        self.assertNotIn("email",result)
        self.assertEqual(snapshot({"lessons":[]},{"items":[]})["next_day"],None)
    def test_project_schedule(self):
        from project_schedule import due_date,summarize
        from datetime import date
        today=date(2026,11,26)
        self.assertIsNone(due_date("",today))
        self.assertEqual(due_date("2026-11-26",today),today)
        for value in ("2026-11-25","2029-01-01","2026-02-30","20261126",True):
            with self.assertRaises(ValueError):due_date(value,today)
        data=summarize([{"id":1,"done":False,"due_date":"2026-11-25"},{"id":2,"done":False,"due_date":"2026-11-26"},{"id":3,"done":True,"due_date":"2026-11-25"},{"id":4,"done":False,"due_date":None},{"id":5,"done":False,"due_date":"2026-11-29"}],today)
        self.assertEqual(data["percent"],20)
        self.assertEqual(data["overdue"],1)
        self.assertEqual(data["due_today"],1)
        self.assertEqual(data["unscheduled"],1)
        self.assertEqual([x["schedule_state"] for x in data["items"]],["overdue","due_today","done","unscheduled","upcoming"])
        self.assertIsNone(summarize([],today)["percent"])
        self.assertTrue(data["advisory_only"])
    def test_freelance_assistant(self):
        from freelance_assistant import estimate_job
        job={"id":1,"title":"Design","category":"design","brief":"One poster","budget_cents":12000}
        body={"hours":5,"rate":20,"expenses":0,"buffer":10}
        result=estimate_job(job,body)
        self.assertEqual(result["quote_cents"],11000)
        self.assertEqual(result["budget_difference_cents"],1000)
        self.assertEqual(result["fee_scenario_percent"],0)
        result=estimate_job(job,{**body,"fee_scenario":True})
        self.assertEqual(result["quote_cents"],11579)
        self.assertEqual(result["budget_difference_cents"],421)
        self.assertTrue(result["draft_only"])
        self.assertLess(estimate_job({**job,"budget_cents":100},body)["budget_difference_cents"],0)
        with self.assertRaises(ValueError):estimate_job(job,{**body,"fee_scenario":"true"})
        with self.assertRaises(ValueError):estimate_job(job,{**body,"hours":0})
        with self.assertRaises(ValueError):estimate_job(job,{**body,"rate":-1})
    def test_four_package_progression_boundaries(self):
        from progression import lesson_available
        now=datetime(2026,11,26,tzinfo=timezone.utc)
        for plan,total in (("starter",30),("pro",30),("vip",45),("elite",45)):
            with self.subTest(plan=plan):
                self.assertTrue(lesson_available(1,None,{},now,plan))
                self.assertFalse(lesson_available(2,None,{},now,plan))
                self.assertFalse(lesson_available(2,now-timedelta(days=2),{},now,plan))
                self.assertFalse(lesson_available(2,now-timedelta(days=2),{1:now-timedelta(hours=23)},now,plan))
                self.assertTrue(lesson_available(2,now-timedelta(days=2),{1:now-timedelta(days=1)},now,plan))
                passed={d:now-timedelta(days=total-d) for d in range(1,total)}
                self.assertTrue(lesson_available(total,now-timedelta(days=total),passed,now,plan))
                self.assertFalse(lesson_available(total+1,now-timedelta(days=total+1),passed,now,plan))
                self.assertFalse(lesson_available(True,now,{},now,plan))
    def test_launch_control_package_coverage(self):
        from launch_control import packages
        coverage={lang:{kind:{"missing":list(range(31,46))} for kind in ("lesson","exam")} for lang in ("en","ru","uk","pl")}
        rows=packages({"coverage":coverage})
        self.assertEqual([x["plan"] for x in rows],["starter","pro","vip","elite"])
        self.assertEqual([x["private_slots"] for x in rows],[240,240,240,240])
        self.assertEqual([x["target"] for x in rows],[240,240,360,360])
        self.assertEqual([x["price_usdc"] for x in rows],[199,499,999,1999])
        coverage["ru"]["exam"]["missing"].append(1)
        self.assertEqual(packages({"coverage":coverage})[0]["private_slots"],239)
    def test_recovery_checklist_validation(self):
        from recovery_assistant import validate,CHECKS
        good={k:True for k in CHECKS}
        self.assertEqual(validate(good," Test evidence ",True),"Test evidence")
        for checks,note,consent in (({}, "evidence",True),({**good,"scope":1},"evidence",True),(good,"",True),(good,"evidence",False)):
            with self.assertRaises(ValueError):validate(checks,note,consent)
    def test_incident_transitions(self):
        from incident_manager import validate_transition
        for a,b in (("detected","investigating"),("investigating","mitigated"),("resolved","investigating")):
            validate_transition(a,b,False)
        validate_transition("mitigated","resolved",True)
        for a,b,v in (("detected","resolved",True),("investigating","resolved",False),("resolved","resolved",True)):
            with self.assertRaises(ValueError): validate_transition(a,b,v)
    def test_system_monitor_bounded_metrics(self):
        from system_monitor import Metrics,group,recommendations
        now=[0]
        m=Metrics(lambda:now[0])
        self.assertEqual(group("/login?token=private"),"account")
        self.assertEqual(group("/support/thread"),"support")
        self.assertEqual(group("/unknown/private"),"other")
        self.assertEqual(group("http://[invalid"),"other")
        m.record("account",200);m.record("support",429);m.record("payments",503)
        m.record("user-secret",503)
        snap=m.snapshot(15)
        self.assertEqual(sum(x["requests"] for x in snap["rows"]),3)
        self.assertEqual(recommendations([{"present":True}],snap,True),["errors","limits"])
        self.assertNotIn("user-secret",str(snap))
        now[0]=16*60
        self.assertEqual(sum(x["requests"] for x in m.snapshot(15)["rows"]),0)
        self.assertEqual(sum(x["requests"] for x in m.snapshot(60)["rows"]),3)
        now[0]=61*60
        self.assertEqual(sum(x["requests"] for x in m.snapshot(60)["rows"]),0)
        with self.assertRaises(ValueError):m.snapshot(1440)
    def test_support_triage_rules(self):
        from support_triage import classify,assign,summary
        from unittest.mock import Mock
        self.assertEqual(classify("account","Взлом аккаунта","Помогите"),("security","urgent"))
        self.assertEqual(classify("payment","Invoice","Pending"),("payment","high"))
        self.assertEqual(classify("ai","Higgsfield","Credits"),("provider","normal"))
        self.assertEqual(classify("other","503","Server"),("connection","high"))
        self.assertEqual(classify("learning","Lesson","Question"),("lesson","normal"))
        cur=Mock()
        with self.assertRaises(ValueError): assign(cur,1,"invalid","high")
        with self.assertRaises(ValueError): summary(cur,365)
        cur.execute.assert_not_called()
    def test_support_learning_diagnostics(self):
        from support_diagnostics import learning_state
        from datetime import datetime,timezone,timedelta
        now=datetime(2026,11,26,tzinfo=timezone.utc)
        r=learning_state(None,None,{},False,now)
        self.assertEqual((r["access"],r["next"],r["reason"]),("trial",1,"available"))
        r=learning_state("starter",None,{1:now},False,now)
        self.assertEqual((r["plan"],r["reason"]),(None,"payment_required"))
        r=learning_state("pro",now-timedelta(days=2),{1:now},False,now)
        self.assertEqual(r["reason"],"scheduled")
        self.assertEqual(r["earliest"],(now+timedelta(days=1)).isoformat())
        r=learning_state("vip",now-timedelta(days=3),{1:now-timedelta(days=2)},False,now)
        self.assertEqual((r["total"],r["next"],r["reason"]),(45,2,"available"))
        self.assertEqual(learning_state(None,None,{},True,now)["unlocked"],45)
        self.assertEqual(learning_state("starter",now,{d:now for d in range(1,31)},False,now)["reason"],"finished")
    def test_support_article_validation(self):
        from support_center import feedback,ARTICLES
        from unittest.mock import Mock
        cur=Mock()
        for b in ({"article":"bad","helpful":True},{"article":[],"helpful":True},{"article":"payment","helpful":1}):
            with self.assertRaises(ValueError): feedback(cur,1,b)
        cur.execute.assert_not_called()
        self.assertEqual(len(ARTICLES),8)
    def test_client_acquisition_actions(self):
        from client_acquisition import actions
        self.assertEqual(actions(False,"none",0,0,0),["profile"])
        self.assertEqual(actions(True,"pending",0,0,0),["listing"])
        self.assertEqual(actions(True,"approved",0,0,0),["proposal","portfolio"])
        self.assertEqual(actions(True,"approved",5,0,0),["improve","portfolio"])
        self.assertEqual(actions(True,"approved",5,1,1),["followup","proposal"])
        self.assertEqual(actions(True,"approved",5,1,0),["portfolio","proposal"])
    def test_career_pathway_evidence(self):
        from career_pathway import pathway
        lessons=[{"day":d,"unlocked":d<=8,"completed":d<=7} for d in range(1,31)]
        projects=[{"lesson":7,"passed":False},{"lesson":7,"passed":True},{"lesson":9,"passed":True}]
        r=pathway(lessons,projects,"design")
        self.assertEqual((r["completed"],r["submitted"],r["review_passed"]),(1,1,1))
        self.assertEqual(r["next"],{"action":"practice","day":8})
        self.assertFalse(r["qualification_verified"])
        w=pathway(lessons,projects,"web")
        self.assertEqual(w["in_plan"],0)
        self.assertEqual(w["outside_plan"],10)
        self.assertEqual(w["next"],{"action":"continue_course","day":8})
        self.assertEqual(pathway(lessons,[{"lesson":7,"passed":True},{"lesson":8,"passed":False}],"design")["next"],{"action":"review_project","day":8})
        self.assertEqual(pathway(lessons,[],"design")["review_passed"],0)
        for invalid in (None,[],"other"):
            with self.assertRaises(ValueError):pathway(lessons,projects,invalid)
    def test_career_skill_paths(self):
        from career import skill_paths
        lessons=[{"day":7,"unlocked":True,"completed":True},{"day":8,"unlocked":True,"completed":True},{"day":9,"unlocked":True,"completed":False},{"day":10,"unlocked":True,"completed":True},{"day":11,"unlocked":True,"completed":True},{"day":12,"unlocked":False,"completed":False},{"day":31,"unlocked":False,"completed":False}]
        projects=[{"lesson":7},{"lesson":7},{"lesson":8},{"lesson":9},{"lesson":12},{"lesson":31}]
        rows=skill_paths(lessons,projects)
        by={x["category"]:x for x in rows}
        self.assertEqual(len(rows),6)
        self.assertEqual(rows[0]["category"],"design")
        self.assertEqual(by["design"]["completed_days"],[7,8])
        self.assertEqual(by["design"]["evidence_days"],[7,8])
        self.assertEqual(by["design"]["project_count"],4)
        self.assertEqual(by["design"]["submitted_days"],[7,8,9])
        self.assertEqual(by["design"]["status"],"portfolio_to_review")
        self.assertEqual(by["design"]["next_day"],9)
        self.assertIsNone(by["design"]["practice_day"])
        self.assertEqual(by["video"]["status"],"build_portfolio")
        self.assertEqual(by["video"]["practice_day"],10)
        self.assertEqual(by["video"]["project_count"],0)
        self.assertEqual(by["web"]["status"],"learning")
        self.assertIsNone(by["web"]["next_day"])
        self.assertTrue(all(x["status"]=="learning" for x in skill_paths([],[])))
    def test_review_journal(self):
        from review_journal import build_journal,validate,dispatch
        from datetime import timedelta
        from types import SimpleNamespace
        from unittest.mock import Mock,patch
        import sys
        now=self.t
        lessons=[{"day":1,"unlocked":True},{"day":2,"unlocked":True},{"day":3,"unlocked":False},{"day":4,"unlocked":True}]
        attempts=[(1,85,now-timedelta(days=4)),(2,95,now-timedelta(days=2)),(3,50,now),(1,60,now-timedelta(days=5))]
        notes={4:{"reflection":"Practice again","reviewed_at":now-timedelta(days=2)}}
        data=build_journal(lessons,attempts,notes,now)
        items={x["day"]:x for x in data["items"]}
        self.assertEqual(set(items),{1,2,4})
        self.assertEqual(data["due_count"],2)
        self.assertEqual(items[1]["change"],25)
        self.assertEqual(items[1]["attempts"],2)
        self.assertEqual(items[1]["interval_days"],3)
        self.assertEqual(items[2]["interval_days"],7)
        self.assertFalse(items[2]["due"])
        self.assertIsNone(items[4]["latest"])
        self.assertEqual(items[4]["interval_days"],1)
        notes[1]={"reflection":"Reviewed","reviewed_at":now}
        item=next(x for x in build_journal(lessons,attempts,notes,now)["items"] if x["day"]==1)
        self.assertFalse(item["due"])
        self.assertEqual(validate(1,"  corrected  "),(1,"corrected"))
        for day,reflection in [(True,"corrected"),(46,"corrected"),(1,"x"),(1,"x"*1201)]:
            with self.assertRaises(ValueError):validate(day,reflection)
        with patch.dict(sys.modules,{"accounts":SimpleNamespace(authenticate=lambda token:None),"learning":SimpleNamespace(student_progress=Mock()),"database":SimpleNamespace(transaction=Mock())}):
            with self.assertRaises(PermissionError):dispatch(None,"list",{})
    def test_student_practice_drafts(self):
        from student_practice import validate,read,save,dispatch
        from unittest.mock import Mock,patch
        from types import SimpleNamespace
        import sys,json
        body={"revision":0,"fields":["a","b","c","d"],"checks":[True,False,True],"device":"phone"}
        rev,data=validate(body)
        self.assertEqual(rev,0)
        self.assertEqual(data["fields"],body["fields"])
        for bad in ({"revision":True},{"fields":["a"]},{"checks":[1,False,True]},{"device":"unknown"},{"fields":["x"*1201,"","",""]}):
            with self.assertRaises(ValueError):validate({**body,**bad})
        cur=Mock()
        cur.fetchone.return_value=None
        self.assertEqual(read(cur,17),{"revision":0,"draft":None})
        self.assertEqual(cur.execute.call_args.args[1],(17,))
        cur.fetchone.return_value=(1,)
        self.assertEqual(save(cur,17,body),{"saved":True,"revision":1})
        sql,args=cur.execute.call_args.args
        self.assertIn("ON CONFLICT(student_id) DO NOTHING",sql)
        self.assertEqual(args[0],17)
        self.assertEqual(json.loads(args[1]),data)
        cur.fetchone.return_value=(2,)
        self.assertEqual(save(cur,17,{**body,"revision":1}),{"saved":True,"revision":2})
        sql,args=cur.execute.call_args.args
        self.assertIn("WHERE student_id=%s AND revision=%s",sql)
        self.assertEqual(args[1:],(17,1))
        cur.fetchone.return_value=None
        self.assertEqual(save(cur,17,{**body,"revision":1}),{"saved":False,"conflict":True})
        cur.fetchone.return_value=(data,2,self.t)
        self.assertEqual(read(cur,17)["draft"],data)
        with patch.dict(sys.modules,{"accounts":SimpleNamespace(authenticate=lambda token:None),"database":SimpleNamespace(transaction=Mock())}):
            with self.assertRaises(PermissionError):dispatch(None,"read",{})
    def test_local_model_evaluation(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        spec=spec_from_file_location("local_engine",Path(__file__).with_name("local-ai-engine.py"))
        engine=module_from_spec(spec);spec.loader.exec_module(engine)
        names=["nemotron-3-nano:4b","qwen3:4b"]
        calls=[];emitted=[]
        def generate(model,role,task):
            calls.append((model,role,task))
            if model==names[1]:raise RuntimeError("fixture failure")
            return "fixture answer"
        times=iter([10,12,20,23])
        report=engine.evaluate_models(names,"Explain percentages",emit=emitted.append,generate=generate,available=lambda:names,clock=lambda:next(times))
        self.assertEqual(len(report["results"]),2)
        self.assertEqual(calls,[(name,engine.ROLES["Teacher"],"Explain percentages") for name in names])
        self.assertEqual(report["results"][0]["family"],"NVIDIA Nemotron")
        self.assertEqual(report["results"][0]["seconds"],2)
        self.assertEqual(report["results"][0]["status"],"ok")
        self.assertEqual(report["results"][1]["status"],"error")
        self.assertEqual(report["results"][1]["seconds"],3)
        self.assertEqual(emitted,report["results"])
        config=engine.nemo_provider_config(names[0],available=lambda:names)
        self.assertIn('base_url: "http://127.0.0.1:11434/v1"',config)
        self.assertIn('model_name: "nemotron-3-nano:4b"',config)
        self.assertIn('api_key: "EMPTY"',config)
        with self.assertRaises(ValueError):engine.nemo_provider_config("remote-cloud",available=lambda:names)
        with self.assertRaises(ValueError):engine.nemo_provider_config("bad\\nkey: value",available=lambda:["bad\\nkey: value"])
        for bad in ([],[names[0],names[0]],["remote-cloud"],["x","y","z","a"]):
            with self.assertRaises(ValueError):engine.evaluate_models(bad,"test",available=lambda:names)
        with self.assertRaises(ValueError):engine.evaluate_models(names,"",available=lambda:names)
    def test_local_tool_bridge(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import wave
        spec=spec_from_file_location("local_bridge",Path(__file__).with_name("local-tool-bridge.py"))
        bridge=module_from_spec(spec);spec.loader.exec_module(bridge)
        with TemporaryDirectory() as tmp:
            root=Path(tmp);exe=root/"fake-tool";exe.write_text("test");exe.chmod(0o700)
            source=root/"speech.txt";source.write_text("Hello",encoding="utf-8")
            model=root/"voice.onnx";model.write_bytes(b"fixture")
            Path(str(model)+".json").write_text("{}")
            calls=[]
            def fake(command,**options):
                calls.append((command,options))
                self.assertFalse(options["shell"])
                self.assertEqual(options["timeout"],300)
                if "-m" in command and "-otxt" not in command:
                    self.assertEqual(options["input"],b"Hello\n")
                    with wave.open(command[-1],"wb") as w:
                        w.setparams((1,2,16000,1,"NONE","not compressed"));w.writeframes(b"\0\0")
                else:
                    output=Path(command[-1]+(".txt" if "-otxt" in command else ""))
                    output.write_text("Converted",encoding="utf-8")
            output=root/"voice.wav"
            bridge.run("Piper",exe,source,model,output,runner=fake)
            self.assertTrue(output.is_file())
            with self.assertRaises(FileExistsError):bridge.run("Piper",exe,source,model,output,runner=fake)
            md=root/"doc.md"
            bridge.run("MarkItDown",exe,source,None,md,runner=fake)
            self.assertEqual(md.read_text(),"Converted")
            audio=root/"audio.wav"
            with wave.open(str(audio),"wb") as w:
                w.setparams((1,2,16000,1,"NONE","not compressed"));w.writeframes(b"\0\0")
            whisper=root/"ggml.bin";whisper.write_bytes(b"fixture")
            transcript=root/"transcript.txt"
            bridge.run("Whisper.cpp",exe,audio,whisper,transcript,runner=fake)
            self.assertEqual(transcript.read_text(),"Converted")
            self.assertIn("-otxt",calls[-1][0])
            self.assertEqual(len(calls),3)
            with self.assertRaises(ValueError):bridge.run("MarkItDown",exe,audio,None,root/"bad.md",runner=fake)
            self.assertFalse((root/"bad.md").exists())
            with self.assertRaises(ValueError):bridge.run("Unknown",exe,source,None,root/"bad.md",runner=fake)
            with self.assertRaises(ValueError):bridge.run("MarkItDown",exe,source,None,root/"empty.md",runner=lambda *a,**k:None)
            self.assertFalse((root/"empty.md").exists())
    def test_ai_mega_catalog(self):
        from ai_mega_catalog import ROWS, PLANS, LANGS, catalog, student_catalog
        from unittest.mock import patch
        self.assertEqual(len(ROWS),42)
        self.assertEqual(len({r[2].lower() for r in ROWS}),42)
        self.assertEqual([sum(r[0]==p for r in ROWS) for p in PLANS],[8,10,12,12])
        for lang in LANGS:
            for index,plan in enumerate(PLANS):
                data=catalog({"access":True,"plan":plan},lang)
                self.assertEqual(sum(len(g["items"]) for g in data["groups"]),[8,18,30,42][index])
                self.assertEqual([g["unlocked"] for g in data["groups"]],[i<=index for i in range(4)])
                self.assertFalse(data["hosted_inference"])
                for group in data["groups"]:
                    for item in group["items"]:
                        self.assertTrue(item["github"].startswith("https://github.com/"))
                        self.assertEqual(item["status"],"external_reference")
                        self.assertEqual(item["commercial_license"],"review_required")
                        self.assertGreater(len(item["task"]),15)
        self.assertFalse(any(g["items"] for g in catalog({"access":False,"plan":"elite"})["groups"]))
        self.assertEqual(sum(len(g["items"]) for g in catalog({"owner_preview":True})["groups"]),42)
        self.assertEqual(catalog({"access":True,"plan":"starter"},[]) ,catalog({"access":True,"plan":"starter"},"en"))
        from types import SimpleNamespace
        import sys
        from unittest.mock import Mock
        with patch.dict(sys.modules,{"learning":SimpleNamespace(student_progress=Mock(side_effect=PermissionError))}):
            with self.assertRaises(PermissionError):student_catalog(None,"ru")
    def test_extracted_production_suite_integrity(self):
        from production_suite import build
        from io import BytesIO
        from zipfile import ZipFile
        from tempfile import TemporaryDirectory
        from pathlib import Path
        from importlib.util import spec_from_file_location,module_from_spec
        import json
        with TemporaryDirectory() as tmp:
            root=Path(tmp)
            with ZipFile(BytesIO(build("ru"))) as z:z.extractall(root)
            spec=spec_from_file_location("elite_launcher",root/"elite-production-launcher.py")
            launcher=module_from_spec(spec);spec.loader.exec_module(launcher)
            self.assertTrue(launcher.verify_bundle()[0])
            filename="client-delivery-kit.py"
            self.assertEqual(launcher.command(filename)[1],str(root/filename))
            p=root/filename;original=p.read_bytes()
            p.write_bytes(b"x"+original[1:])
            self.assertFalse(launcher.verify_bundle()[0])
            with self.assertRaises(ValueError):launcher.command(filename)
            p.write_bytes(original)
            self.assertTrue(launcher.verify_bundle()[0])
            p.unlink()
            self.assertFalse(launcher.verify_bundle()[0])
            p.write_bytes(original)
            manifest=root/"manifest.json";raw=manifest.read_bytes()
            data=json.loads(raw);data["files"][0]["name"]="../outside.py"
            manifest.write_text(json.dumps(data))
            self.assertFalse(launcher.verify_bundle()[0])
            manifest.write_bytes(raw)
            self.assertTrue(launcher.verify_bundle()[0])
            with self.assertRaises(ValueError):launcher.command("../outside.py")
    def test_production_suite_bundle(self):
        from production_suite import build,student_bundle,FILES,VERSION
        from io import BytesIO
        from zipfile import ZipFile
        from unittest.mock import patch
        import hashlib,json
        for lang in ("en","ru","uk","pl"):
            with ZipFile(BytesIO(build(lang))) as z:
                self.assertEqual(set(z.namelist()),set(FILES)|{"README.txt","manifest.json"})
                manifest=json.loads(z.read("manifest.json"))
                self.assertEqual(manifest["version"],VERSION)
                self.assertEqual(len(manifest["files"]),len(FILES)+1)
                for f in manifest["files"]:
                    self.assertEqual(hashlib.sha256(z.read(f["name"])).hexdigest(),f["sha256"])
                    self.assertEqual(len(z.read(f["name"])),f["bytes"])
                self.assertIsNone(z.testzip())
                for name in FILES:compile(z.read(name),name,"exec")
        with patch("elite_program.access",side_effect=PermissionError):
            with self.assertRaises(PermissionError):student_bundle("token","ru")
        with patch("elite_program.access",return_value={"lessons":[],"owner_preview":False}):
            with self.assertRaises(PermissionError):student_bundle("token","ru")
        with patch("elite_program.access",return_value={"owner_preview":True}):
            self.assertTrue(student_bundle("token","ru").startswith(b"PK"))
    def test_client_delivery_kit(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        from tempfile import TemporaryDirectory
        import hashlib,json
        from zipfile import ZipFile
        spec=spec_from_file_location("kit",Path(__file__).with_name("client-delivery-kit.py"))
        kit=module_from_spec(spec);spec.loader.exec_module(kit)
        with TemporaryDirectory() as tmp:
            root=Path(tmp);video=root/"sample.mp4";video.write_bytes(b"synthetic-video")
            plan=root/"plan.json";plan.write_text(json.dumps({"duration":30,"format":"9:16"}))
            qc=root/"qc.json"
            report={"tool":"Zer0Life FFprobe delivery check","target":{"duration":30,"format":"9:16"},"checks":{k:True for k in ("duration","resolution","frame_rate","video_codec","pixel_format","audio","subtitles")},"metadata_pass":True,"video_sha256":hashlib.sha256(video.read_bytes()).hexdigest()}
            qc.write_text(json.dumps(report))
            rights=root/"rights.txt";rights.write_text("Synthetic rights notes")
            files={"video":video,"plan":plan,"qc":qc,"rights":rights}
            details={"project":"Test","revision":"v1","limitations":"Synthetic fixture"}
            checks={k:True for k in kit.CHECKS};out=root/"delivery.zip"
            with self.assertRaises(ValueError):kit.package(files,details,dict(checks,rights=False),out)
            result=kit.package(files,details,checks,out)
            with ZipFile(out) as z:
                self.assertEqual(set(z.namelist()),{"final.mp4","production-plan.json","quality-report.json","rights.txt","delivery-manifest.json"})
                manifest=json.loads(z.read("delivery-manifest.json"))
                self.assertEqual(manifest,result)
                for entry in manifest["files"]:
                    self.assertEqual(hashlib.sha256(z.read(entry["name"])).hexdigest(),entry["sha256"])
            with self.assertRaises(ValueError):kit.package(files,details,checks,out)
            video.write_bytes(b"changed")
            with self.assertRaises(ValueError):kit.package(files,details,checks,root/"bad.zip")
            self.assertFalse((root/"bad.zip").exists())
    def test_delivery_quality_check(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from types import SimpleNamespace
        import json
        spec=spec_from_file_location("qc",Path(__file__).with_name("delivery-quality-check.py"))
        qc=module_from_spec(spec);spec.loader.exec_module(qc)
        video={"codec_type":"video","codec_name":"h264","pix_fmt":"yuv420p","width":1080,"height":1920,"avg_frame_rate":"30/1"}
        audio={"codec_type":"audio","codec_name":"aac"}
        subs={"codec_type":"subtitle","codec_name":"mov_text"}
        data={"format":{"duration":"30.033"},"streams":[video,audio,subs]}
        self.assertTrue(qc.evaluate(data,30,"9:16",True,True)["metadata_pass"])
        self.assertFalse(qc.evaluate(data,15,"9:16",True,True)["checks"]["duration"])
        self.assertFalse(qc.evaluate(data,30,"16:9")["checks"]["resolution"])
        self.assertFalse(qc.evaluate(dict(data,streams=[video]),30,"9:16")["checks"]["audio"])
        self.assertTrue(qc.evaluate(dict(data,streams=[video]),30,"9:16",False)["metadata_pass"])
        self.assertFalse(qc.evaluate(dict(data,streams=[video,audio]),30,"9:16",True,True)["checks"]["subtitles"])
        self.assertFalse(qc.evaluate(dict(data,streams=[dict(video,side_data_list=[{"rotation":90}]),audio]),30,"9:16")["checks"]["resolution"])
        with self.assertRaises(ValueError):qc.evaluate(dict(data,streams=[dict(video,avg_frame_rate="0/0")]),30,"9:16")
        with TemporaryDirectory() as tmp:
            root=Path(tmp);exe=root/"ffprobe";exe.touch()
            media=root/"result.mp4";media.touch()
            with patch.object(qc.subprocess,"run",return_value=SimpleNamespace(returncode=0,stdout=json.dumps(data).encode(),stderr=b"")) as run:
                self.assertTrue(qc.inspect(exe,media,30,"9:16",True,True)["metadata_pass"])
                self.assertFalse(run.call_args.kwargs["shell"])
                self.assertIn("file",run.call_args.args[0])
    def test_local_narration_render(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from types import SimpleNamespace
        from unittest.mock import patch
        import wave
        from ad_production import subtitle_draft
        spec=spec_from_file_location("narration",Path(__file__).with_name("local-narration-studio.py"))
        n=module_from_spec(spec);spec.loader.exec_module(n)
        data=subtitle_draft(15,["Hello","","Test","Done"])["voice_plan"]
        self.assertEqual(data["captions"][1],"")
        with TemporaryDirectory() as tmp:
            root=Path(tmp);exe=root/"espeak-ng";exe.touch()
            out=root/"voice.wav"
            def mock_run(args,**kw):
                self.assertFalse(kw["shell"])
                self.assertEqual(args[-1],"--stdin")
                with wave.open(args[args.index("-w")+1],"wb") as w:
                    w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000)
                    w.writeframes(bytes([1,0])*16000)
                return SimpleNamespace(returncode=0)
            with patch.object(n.subprocess,"run",side_effect=mock_run) as mock:
                report=n.render(exe,data,"en",170,out)
                self.assertEqual(mock.call_count,3)
                self.assertEqual(report["duration"],15)
                with wave.open(str(out),"rb") as w:
                    self.assertEqual(w.getnframes(),15*16000)
                    w.setpos(3*16000)
                    self.assertEqual(w.readframes(5*16000),bytes(5*16000*2))
                with self.assertRaises(ValueError):n.render(exe,data,"en",170,out)
                with self.assertRaises(ValueError):n.render(exe,data,"en",221,root/"bad.wav")
            def long_run(args,**kw):
                with wave.open(args[args.index("-w")+1],"wb") as w:
                    w.setnchannels(1);w.setsampwidth(2);w.setframerate(16000)
                    w.writeframes(bytes(4*16000*2))
                return SimpleNamespace(returncode=0)
            with patch.object(n.subprocess,"run",side_effect=long_run):
                with self.assertRaises(ValueError):n.render(exe,data,"en",170,root/"long.wav")
            self.assertFalse((root/"long.wav").exists())
    def test_subtitle_draft(self):
        from ad_production import subtitle_draft,student_subtitles
        from unittest.mock import patch
        d=subtitle_draft(15,["Привет","", "Тест","Готово"])
        self.assertIn("00:00:00,000 --> 00:00:03,000",d["srt"])
        self.assertIn("00:00:08,000 --> 00:00:12,000",d["srt"])
        self.assertIn("00:00:12,000 --> 00:00:15,000",d["srt"])
        self.assertEqual(d["narration"],"Привет\n\nТест\n\nГотово")
        self.assertEqual(d["warnings"],[])
        self.assertEqual(subtitle_draft(15,["a"*120,"","",""])["warnings"],[1])
        for bad in (["","","",""],["<b>test</b>","","",""],["a"*161,"","",""],["one"]):
            with self.assertRaises(ValueError):subtitle_draft(15,bad)
        with patch("elite_program.access",side_effect=PermissionError):
            with self.assertRaises(PermissionError):student_subtitles("token",15,["A","","",""])
        with patch("elite_program.access",return_value={"owner_preview":True}):
            self.assertTrue(student_subtitles("token",15,["A","","",""])["draft"])
    def test_commercial_video_assembler(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from types import SimpleNamespace
        from unittest.mock import patch
        from ad_production import plan
        spec=spec_from_file_location("assembler",Path(__file__).with_name("commercial-video-assembler.py"))
        assembler=module_from_spec(spec);spec.loader.exec_module(assembler)
        brief={"product":"Mug","audience":"Adults","benefit":"Handle","evidence":"","cta":"Visit shop","style":"Natural light","duration":15,"format":"9:16"}
        p=assembler.validate_plan(plan(brief))
        self.assertEqual(p["seconds"],[3,5,4,3])
        self.assertEqual((p["width"],p["height"]),(1080,1920))
        with self.assertRaises(ValueError):assembler.validate_plan(dict(plan(brief),scenes=[]))
        with TemporaryDirectory() as tmp:
            root=Path(tmp);exe=root/"ffmpeg";exe.touch()
            clips=[root/f"shot{i}.mp4" for i in range(4)]
            for f in clips:f.touch()
            audio=root/"sound.wav";audio.touch()
            out=root/"result.mp4"
            cmd=assembler.build_command(exe,p,clips,audio,out)
            self.assertEqual(cmd.count("-i"),5)
            self.assertIn("libx264",cmd)
            self.assertIn("concat=n=4:v=1:a=0",cmd[cmd.index("-filter_complex")+1])
            self.assertIn("apad,atrim=duration=15",cmd[cmd.index("-filter_complex")+1])
            self.assertIn("-an",assembler.build_command(exe,p,clips,None,out))
            narration=root/"voice.wav";narration.touch()
            subtitles=root/"captions.srt";subtitles.touch()
            mixed=assembler.build_command(exe,p,clips,audio,out,narration,subtitles)
            self.assertEqual(mixed.count("-i"),7)
            self.assertIn("amix=inputs=2",mixed[mixed.index("-filter_complex")+1])
            self.assertIn("6:s:0",mixed)
            self.assertIn("mov_text",mixed)
            voice_only=assembler.build_command(exe,p,clips,None,out,narration,subtitles)
            self.assertIn("5:s:0",voice_only)
            self.assertNotIn("-an",voice_only)
            with self.assertRaises(ValueError):assembler.build_command(exe,p,clips[:3],None,out)
            def fake_run(args,**kwargs):
                self.assertFalse(kwargs["shell"])
                Path(args[-1]).write_bytes(b"mock output"*20)
                return SimpleNamespace(returncode=0,stderr=b"")
            with patch.object(assembler.subprocess,"run",side_effect=fake_run):
                report=assembler.assemble(exe,p,clips,audio,out)
                self.assertEqual(report["planned_duration"],15)
                self.assertTrue(out.is_file())
                with self.assertRaises(ValueError):assembler.assemble(exe,p,clips,audio,out)
    def test_ad_production_plan(self):
        from ad_production import plan,student_plan,FORMATS
        from unittest.mock import patch
        brief={"product":"Original handmade mug","audience":"Adults","benefit":"Comfortable handle","evidence":"","cta":"Visit our shop","style":"Natural light","duration":30,"format":"9:16"}
        for lang in ("en","ru","uk","pl"):
            for duration in (15,30,60):
                for fmt,(width,height) in FORMATS.items():
                    result=plan(dict(brief,duration=duration,format=fmt),lang)
                    self.assertTrue(result["draft"])
                    self.assertEqual(len(result["scenes"]),4)
                    self.assertEqual(sum(s["seconds"] for s in result["scenes"]),duration)
                    self.assertEqual(result["scenes"][0]["start"],0)
                    self.assertEqual(result["scenes"][-1]["end"],duration)
                    self.assertEqual((result["width"],result["height"]),(width,height))
                    self.assertEqual(result["scenes"][2]["voice_draft"],"")
        for bad in (dict(brief,duration=True),dict(brief,format="2:3"),dict(brief,product=""),dict(brief,unexpected="x")):
            with self.assertRaises(ValueError):plan(bad)
        with patch("elite_program.access",side_effect=PermissionError):
            with self.assertRaises(PermissionError):student_plan("token",brief,"ru")
        with patch("elite_program.access",return_value={"lessons":[],"owner_preview":False}):
            with self.assertRaises(PermissionError):student_plan("token",brief,"ru")
        with patch("elite_program.access",return_value={"owner_preview":True}):
            self.assertEqual(student_plan("token",brief,"ru")["duration"],30)
    def test_open_generative_bridge(self):
        from importlib.util import spec_from_file_location,module_from_spec
        from pathlib import Path
        from tempfile import TemporaryDirectory
        from unittest.mock import patch
        from types import SimpleNamespace
        spec=spec_from_file_location("open_gen_bridge",Path(__file__).with_name("open-generative-bridge.py"))
        bridge=module_from_spec(spec);spec.loader.exec_module(bridge)
        with TemporaryDirectory() as tmp:
            root=Path(tmp);engine=root/"sd-cli";engine.touch()
            model=root/"model.safetensors";model.touch()
            output=root/"result.png"
            prompt="A fictional landscape; original artwork"
            args=bridge.command(engine,model,output,prompt,42)
            self.assertEqual(args[args.index("-p")+1],prompt)
            self.assertEqual(args[args.index("--steps")+1],"12")
            self.assertEqual(args[args.index("-H")+1],"512")
            def fake_run(args,**kwargs):
                self.assertFalse(kwargs["shell"])
                output.write_bytes(bytes.fromhex("89504e470d0a1a0a"))
                return SimpleNamespace(returncode=0)
            with patch.object(bridge.subprocess,"run",side_effect=fake_run):
                report=bridge.execute(engine,model,output,prompt,42)
            self.assertEqual(report["seed"],42)
            self.assertEqual(report["output"],"result.png")
            with self.assertRaises(ValueError):bridge.command(engine,model,output,prompt,42)
            with self.assertRaises(ValueError):bridge.command(engine,model,root/"other.png",prompt,-1)
    def test_graduate_showcase_validation(self):
        from graduate_showcase import validate,CODE
        p={"headline":"Creator","bio":"Public work only","show_name":False,"projects":[{"title":"Film","description":"Example","url":"https://example.invalid/film"}]}
        self.assertEqual(validate(p),p)
        self.assertTrue(CODE.fullmatch("a"*32))
        self.assertFalse(CODE.fullmatch("a"*31))
        for url in ("javascript:alert(1)","http://example.invalid","https://user:pass@example.invalid","https://example.invalid/a b"):
            with self.assertRaises(ValueError):validate(dict(p,projects=[dict(p["projects"][0],url=url)]))
        with self.assertRaises(ValueError):validate(dict(p,show_name=1))
        with self.assertRaises(ValueError):validate(dict(p,projects=[]))
        with self.assertRaises(ValueError):validate(dict(p,private_submission="hidden"))
    def test_elite_review_rubric(self):
        from elite_program import RUBRIC,validate_review
        self.assertEqual(sum(RUBRIC.values()),100)
        self.assertEqual(validate_review("film",1,RUBRIC,"Evidence verified."),(100,"approved","Evidence verified."))
        scores=dict(RUBRIC);scores["brief"]=5
        self.assertEqual(validate_review("film",2,scores,"Review completed.")[:2],(80,"approved"))
        scores["brief"]=4
        self.assertEqual(validate_review("film",2,scores,"Improve the brief.")[:2],(79,"revision"))
        for bad in ({},dict(RUBRIC,brief=26),dict(RUBRIC,brief=True)):
            with self.assertRaises(ValueError):validate_review("film",1,bad,"Evidence verified.")
        with self.assertRaises(ValueError):validate_review("film",0,RUBRIC,"Evidence verified.")
        with self.assertRaises(ValueError):validate_review("film",1,RUBRIC,"")
        with self.assertRaises(ValueError):validate_review({},"1",RUBRIC,"Evidence verified.")
    def test_free_first_lesson(self):
        from progression import lesson_available
        for plan in (None,"starter","pro","vip","elite"):
            self.assertTrue(lesson_available(1,None,{},self.t,plan))
            for day in (2,30,31,45):
                self.assertFalse(lesson_available(day,None,{1:self.t},self.t+timedelta(days=100),plan))
        self.assertFalse(lesson_available(True,None,{},self.t))
        self.assertFalse(lesson_available(46,None,{},self.t,"elite"))
        self.assertTrue(lesson_available(2,self.t,{1:self.t},self.t+timedelta(days=1),"starter"))
        self.assertFalse(lesson_available(2,self.t,{1:self.t-timedelta(days=4)},self.t,"starter"))
    def test_elite_practical_guides(self):
        from elite_program import PROJECTS, PRACTICE_GUIDES, practice_steps
        self.assertEqual(set(PRACTICE_GUIDES),{row[0] for row in PROJECTS})
        for project,_,langs,_ in PROJECTS:
            self.assertEqual(set(PRACTICE_GUIDES[project]),set(langs))
            for lang,original in langs.items():
                guides=PRACTICE_GUIDES[project][lang]
                self.assertEqual(len(guides),3)
                actual=practice_steps(project,langs,lang)
                self.assertEqual(len(actual),3)
                for task,guide,combined in zip(original,guides,actual):
                    self.assertGreater(len(guide),40)
                    self.assertEqual(combined,task+"\n\n"+guide)
            self.assertEqual(practice_steps(project,langs,"unsupported"),practice_steps(project,langs,"en"))
    def test_elite_program(self):
        from elite_program import PROJECTS, unlocked, access
        from unittest.mock import patch
        from payment_policy import PRICES,course_amount
        self.assertEqual(PRICES["elite"],1999)
        self.assertEqual(course_amount("elite",True),1899050000)
        self.assertEqual(len(PROJECTS),5)
        for _,_,langs,_ in PROJECTS:
            self.assertEqual(set(langs),{"en","ru","uk","pl"})
            self.assertTrue(all(len(steps)==3 for steps in langs.values()))
        self.assertFalse(unlocked({"lessons":[{"completed":True}]*44}))
        self.assertTrue(unlocked({"lessons":[{"completed":True}]*45}))
        self.assertTrue(unlocked({"owner_preview":True}))
        with patch("elite_program.student_progress",return_value={"access":True,"plan":"vip"}):
            with self.assertRaises(PermissionError):access("token")
        passed={i:self.t+timedelta(days=i-1) for i in range(1,45)}
        self.assertTrue(eligible(45,self.t,passed,self.t+timedelta(days=44),"elite"))
        self.assertFalse(eligible(46,self.t,passed,self.t+timedelta(days=45),"elite"))
    def test_creator_2027_tracks(self):
        from creator_2027 import TRACKS, enrich
        self.assertEqual({t["id"] for t in TRACKS},{"humans","film","agents","teacher","career"})
        self.assertEqual({t["day"] for t in TRACKS},{32,35,41,43,45})
        for t in TRACKS:
            for lang in ("en","ru","uk","pl"):
                data=enrich({"title":"Original"},t["day"],lang)
                self.assertEqual(data["title"],"Original")
                row=data["creator_tracks"][0]
                self.assertEqual(row["id"],t["id"])
                self.assertNotIn("lessons",row)
                self.assertEqual(row["lesson"],t["lessons"][lang])
                self.assertTrue(all(url.startswith("https://github.com/") for _,url in row["repos"]))
        self.assertEqual(enrich({"title":"Core"},30,"ru"),{"title":"Core"})
    def test_creator_2027_local_engine_contracts(self):
        from pathlib import Path
        from importlib.util import spec_from_file_location, module_from_spec
        from unittest.mock import patch
        spec=spec_from_file_location("local_engine",Path(__file__).with_name("local-ai-engine.py"))
        engine=module_from_spec(spec);spec.loader.exec_module(engine)
        self.assertTrue(all(url.startswith("http://127.0.0.1:") for url in engine.ENDPOINTS.values()))
        with patch.object(engine,"request",return_value={"models":[{"name":"local:latest","size":123},{"name":"remote-cloud","size":123},{"name":"remote","size":123,"remote_host":"example.org"}]}):
            self.assertEqual(engine.local_models(),["local:latest"])
        with patch.object(engine,"local_models",return_value=["local:latest"]),patch.object(engine,"chat",side_effect=["plan","draft","review"]) as chat:
            result=engine.run_task("local:latest","Agent Factory","Example")
            self.assertEqual(chat.call_count,3)
            self.assertIn("Reviewer",result)
            with self.assertRaises(ValueError):
                engine.run_task("cloud","Teacher","Example")
        import tempfile,json
        with tempfile.TemporaryDirectory() as tmp:
            file=Path(tmp)/"workflow.json"
            file.write_text(json.dumps({"1":{"class_type":"Example","inputs":{}}}))
            self.assertEqual(len(engine.load_workflow(file)),1)
            file.write_text(json.dumps({"nodes":[]}))
            with self.assertRaises(ValueError):engine.load_workflow(file)
    def test_vip_creator_labs_only_supplement_selected_vip_days(self):
        from vip_creator_labs import supplement, MODULES
        lesson={'title':'Original','theory':'Theory','assignment':'Task'}
        self.assertEqual(set(MODULES),{35,39,40,45})
        for day in (1,10,30,31,34,36,41,44):
            self.assertEqual(supplement(lesson,day,'ru'),lesson)
        for day in MODULES:
            for lang in ('en','ru','uk','pl'):
                result=supplement(lesson,day,lang)
                self.assertEqual(result['sections'][:2],['Theory','Task'])
                self.assertEqual(result['sections'][2:],MODULES[day][lang])
                self.assertEqual(result['vip_creator_lab'],MODULES[day][lang])
                self.assertNotIn('sections',lesson)
        private={'sections':['Original private material']}
        self.assertEqual(supplement(private,35,'ru')['sections'][0],private['sections'][0])

    def setUp(self):
        self.t = datetime(2026,11,24,tzinfo=timezone.utc)
    def test_launch_readiness_is_not_approval(self):
        from launch_readiness import summarize
        from unittest.mock import patch
        d={"database_checks_pass":True,"counts":{"open_payment_tickets":2,"open_privacy_requests":1,"split_pending_issued":3}}
        inventory={"coverage":{lang:{kind:{"count":45} for kind in ("lesson","exam")} for lang in ("en","ru","uk","pl")},"strict":{"lesson":True,"exam":True},"strict_ready":{"lesson":True,"exam":True}}
        with patch.dict("os.environ",{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"true"}):
            result=summarize(d,inventory)
        self.assertEqual(result["curriculum"]["slots"],360)
        self.assertTrue(result["curriculum"]["all_languages_covered"])
        self.assertFalse(result["commercial_approved"])
        self.assertFalse(result["marketplace_payments"]["enabled"])
        self.assertEqual(result["unsettled_issued"],3)
        inventory["coverage"]["ru"]["exam"]["count"]=44
        result=summarize(d,inventory)
        self.assertEqual(result["curriculum"]["slots"],359)
        self.assertFalse(result["curriculum"]["all_languages_covered"])
    def test_unpaid(self):
        self.assertFalse(eligible(1,None,{},self.t))
    def test_first(self):
        self.assertTrue(eligible(1,self.t,{},self.t))
    def test_skip(self):
        self.assertFalse(eligible(3,self.t,{1:self.t},self.t+timedelta(days=3)))
    def test_wait(self):
        self.assertFalse(eligible(2,self.t,{1:self.t},self.t+timedelta(hours=23)))
        self.assertTrue(eligible(2,self.t,{1:self.t},self.t+timedelta(days=1)))
    def test_late_pass(self):
        self.assertFalse(eligible(2,self.t,{1:self.t+timedelta(days=3)},self.t+timedelta(days=3)))
    def test_vip_agent_unlock(self):
        passed={n:self.t+timedelta(days=n-1) for n in range(1,45)}
        now=self.t+timedelta(days=44)
        self.assertTrue(eligible(45,self.t,passed,now,"vip"))
        self.assertFalse(eligible(45,self.t,passed,now,"pro"))
        self.assertFalse(eligible(41,self.t,passed,now,"starter"))
        self.assertFalse(eligible(46,self.t,passed,now,"vip"))
        self.assertFalse(eligible(45,self.t,passed,now-timedelta(hours=1),"vip"))
    def test_vip_exam_banks(self):
        import json
        from pathlib import Path
        from assessment import prepare_attempt, grade_attempt
        lessons=json.loads(Path(__file__).with_name("vip_lessons.json").read_text())
        self.assertEqual([x["day"] for x in lessons],list(range(31,46)))
        for lesson in lessons:
            public,key=prepare_attempt(lesson["questions"])
            self.assertEqual(len(public["questions"]),10)
            self.assertTrue(grade_attempt(key,key)["passed"])
            self.assertTrue(all("correct" not in q for q in public["questions"]))
    def test_agent_lab_examples(self):
        import json
        from pathlib import Path
        labs=json.loads(Path(__file__).with_name("agent_lab.json").read_text())
        self.assertEqual([x["day"] for x in labs],list(range(41,46)))
        for lab in labs:
            namespace={"__name__":"__main__"}
            exec(compile(lab["code"],lab["filename"],"exec"),namespace)
    def test_paid_ai_defaults_closed(self):
        from ai_models import configuration,ROLES,status
        from unittest.mock import patch
        import os
        with patch.dict(os.environ,{"ACADEMY_AI_ENABLED":"true","ACADEMY_AI_API_KEY":"synthetic","ACADEMY_AI_MODEL":"synthetic","ACADEMY_ALLOW_BILLED_API":"false"},clear=True):
            for role in ROLES: self.assertIsNone(configuration(role))
            self.assertTrue(all(not x["available"] for x in status()))
        with patch.dict(os.environ,{"ACADEMY_AI_ENABLED":"false","ACADEMY_ALLOW_BILLED_API":"true"},clear=True):
            self.assertTrue(all(configuration(role) is None for role in ROLES))
    def test_model_adapters(self):
        from ai_models import request_spec,parse_answer
        for provider in ("openai","anthropic","gemini"):
            url,headers,body=request_spec(provider,"test-model","fake-key","instruction","question")
            self.assertTrue(url.startswith("https://"))
            self.assertNotIn("fake-key",url)
        self.assertEqual(parse_answer("openai",{"choices":[{"message":{"content":"test"}}]}),"test")
        self.assertEqual(parse_answer("anthropic",{"content":[{"type":"text","text":"test"}]}),"test")
        self.assertEqual(parse_answer("gemini",{"candidates":[{"content":{"parts":[{"text":"test"}]}}]}),"test")
    def test_adaptive_learning(self):
        from adaptive import recommend
        lessons=[{"day":1,"unlocked":True,"completed":True},{"day":2,"unlocked":True,"completed":False},{"day":3,"unlocked":False,"completed":False}]
        empty=recommend(lessons,[])
        self.assertIsNone(empty["mean_latest"])
        self.assertEqual(empty["next"]["day"],2)
        r=recommend(lessons,[(2,60),(1,90),(1,50),(3,10)])
        self.assertEqual([x["day"] for x in r["review"]],[2,1])
        self.assertEqual(r["mean_latest"],75)
        self.assertEqual(r["review"][0]["priority"],"high")
        self.assertEqual(r["completed"],1)
        self.assertEqual(r["attempted_lessons"],2)
    def test_weekly_learning_plan(self):
        from adaptive import weekly_plan
        lessons=[{"day":1,"unlocked":True,"completed":True},{"day":2,"unlocked":True,"completed":False},{"day":3,"unlocked":False,"completed":False}]
        for minutes in (15,30,60):
            p=weekly_plan(lessons,[(1,70),(3,10)],minutes)
            self.assertEqual(len(p["sessions"]),7)
            self.assertEqual(p["total_minutes"],minutes*7)
            self.assertEqual(p["sessions"][0]["lesson"],2)
            self.assertTrue(all(sum(s["blocks"])==minutes and s["lesson"] in (None,1,2) for s in p["sessions"]))
            self.assertEqual(p["sessions"][-1]["kind"],"reflect")
        locked=weekly_plan([{"day":1,"unlocked":False,"completed":False}],[],15)
        self.assertTrue(all(s["lesson"] is None for s in locked["sessions"]))
        for bad in (True,0,31,"30"):
            with self.assertRaises(ValueError): weekly_plan(lessons,[],bad)
    def test_achievements(self):
        from achievements import calculate
        lessons=[{"completed":n<5} for n in range(45)]
        r=calculate(lessons,[100,80,90,100,90],1)
        a={x["id"]:x for x in r["achievements"]}
        self.assertTrue(a["five_lessons"]["earned"])
        self.assertTrue(a["first_project"]["earned"])
        self.assertFalse(a["course_complete"]["earned"])
        self.assertFalse(a["agent_complete"]["earned"])
    def test_playground(self):
        from playground import simulate,CASES
        for case in CASES:
            result=simulate(case,True,True,3)
            self.assertTrue(result["passed"])
            self.assertEqual(result["external_actions"],0)
        self.assertEqual(simulate("write",True,False,3)["result"],"unsafe_policy")
        self.assertEqual(simulate("lookup",True,True,1)["result"],"step_limit")
        with self.assertRaises(ValueError): simulate("support",True,True,100)
    def test_marketplace_split(self):
        from marketplace_split import split,key,matches,decode58,TOKEN,ALPHABET
        from payment_policy import TREASURY,USDC_MINT
        self.assertEqual(split(100000),{"gross_atomic":1000000000,"fee_atomic":50000000,"freelancer_atomic":950000000})
        self.assertEqual(split(1)["fee_atomic"],500)
        for bad in (0,-1,True,100000001):
            with self.assertRaises(ValueError): split(bad)
        self.assertEqual(key(TREASURY),TREASURY)
        with self.assertRaises(ValueError): key("abc")
        def enc(b):
            n=int.from_bytes(b,"big");out=""
            while n:
                n,i=divmod(n,58);out=ALPHABET[i]+out
            return "1"*(len(b)-len(b.lstrip(bytes([0]))))+out
        payer,recipient,ref,src,d1,d2=[enc(bytes([n])*32) for n in range(1,7)]
        sig=enc(bytes([9])*64)
        keys=[payer,src,d1,d2,USDC_MINT,ref,TOKEN]
        def ix(dst,amt):return {"programIdIndex":6,"accounts":[1,4,dst,0,5],"data":enc(bytes([12])+amt.to_bytes(8,"little")+bytes([6]))}
        def bal(i,owner,n):return {"accountIndex":i,"owner":owner,"mint":USDC_MINT,"uiTokenAmount":{"amount":str(n),"decimals":6}}
        tx={"blockTime":int(self.t.timestamp()),"transaction":{"signatures":[sig],"message":{"accountKeys":keys,"header":{"numRequiredSignatures":1,"numReadonlySignedAccounts":0,"numReadonlyUnsignedAccounts":3},"instructions":[ix(2,950000),ix(3,50000)]}},"meta":{"err":None,"preTokenBalances":[bal(1,payer,1000000),bal(2,recipient,0),bal(3,TREASURY,0)],"postTokenBalances":[bal(1,payer,0),bal(2,recipient,950000),bal(3,TREASURY,50000)]}}
        self.assertTrue(matches(tx,sig,payer,recipient,ref,100,self.t))
        import copy
        for value in (-1,True,False,7,1):
            bad=copy.deepcopy(tx)
            bad["transaction"]["message"]["instructions"][0]["programIdIndex"]=value
            self.assertFalse(matches(bad,sig,payer,recipient,ref,100,self.t))
        for value in (True,0,-1,8):
            bad=copy.deepcopy(tx)
            bad["transaction"]["message"]["header"]["numReadonlyUnsignedAccounts"]=value
            self.assertFalse(matches(bad,sig,payer,recipient,ref,100,self.t))
        for value in ("-1","1.0",1,True,"18446744073709551616","١"):
            bad=copy.deepcopy(tx)
            bad["meta"]["postTokenBalances"][0]["uiTokenAmount"]["amount"]=value
            self.assertFalse(matches(bad,sig,payer,recipient,ref,100,self.t))
        for amount in (1,99,101,14000,100000000):
            parts=split(amount)
            self.assertEqual(parts["fee_atomic"],amount*500)
            self.assertEqual(parts["gross_atomic"],parts["fee_atomic"]+parts["freelancer_atomic"])
        tx["transaction"]["message"]["instructions"][1]=ix(3,49999)
        self.assertFalse(matches(tx,sig,payer,recipient,ref,100,self.t))
    def test_marketplace_unsigned_transaction(self):
        from marketplace_tx import unsigned,pay_url,token_accounts
        from marketplace_split import ALPHABET,decode58
        from payment_policy import USDC_MINT
        import base64
        from unittest.mock import patch
        def enc(b):
            n=int.from_bytes(b,"big");out=""
            while n:
                n,i=divmod(n,58);out=ALPHABET[i]+out
            return out
        payer,src,d1,d2,ref=[enc(bytes([i])*32) for i in range(1,6)]
        raw=base64.b64decode(unsigned(payer,src,d1,d2,ref,100000))
        self.assertEqual(raw[:65],bytes([1])+bytes(64))
        self.assertEqual(raw[65:69],bytes([1,0,3,7]))
        self.assertEqual(raw[69:101],decode58(payer))
        ix=raw[65+4+7*32+32:]
        self.assertEqual(ix[0],2)
        pos=1
        amounts=[]
        for destination in (2,3):
            program,n=ix[pos:pos+2];pos+=2
            self.assertEqual(program,6)
            self.assertEqual(n,5)
            self.assertEqual(list(ix[pos:pos+n]),[1,4,destination,0,5]);pos+=n
            size=ix[pos];pos+=1
            data=ix[pos:pos+size];pos+=size
            self.assertEqual((size,data[0],data[-1]),(10,12,6))
            amounts.append(int.from_bytes(data[1:9],"little"))
        self.assertEqual(pos,len(ix))
        self.assertEqual(amounts,[950000000,50000000])
        self.assertTrue(pay_url(ref).endswith(ref))
        with self.assertRaises(ValueError): unsigned(payer,src,d1,d1,ref,100000)
        with patch("marketplace_tx.rpc",return_value={"value":[]}):
            with self.assertRaises(ValueError): token_accounts(payer)
    def test_marketplace_reference_reconciliation(self):
        from marketplace_reconcile import scan
        from unittest.mock import patch
        from marketplace_split import ALPHABET
        def enc(b):
            n=int.from_bytes(b,"big");out=""
            while n:
                n,i=divmod(n,58);out=ALPHABET[i]+out
            return out
        ref=enc(bytes([7])*32)
        signatures=[enc(bytes([i])*64) for i in (8,9)]
        def rpc(method,params):
            if method=="getSignaturesForAddress":
                return [{"signature":s,"confirmationStatus":"finalized","err":None} for s in signatures]
            return {"synthetic":True}
        with patch("marketplace_reconcile.matches",return_value=True):
            result=scan(rpc,"payer","recipient",ref,100,self.t)
            self.assertTrue(result["duplicate_detected"])
            self.assertFalse(result["safe_to_retry"])
            self.assertEqual(result["matches"],signatures)
        with patch("marketplace_reconcile.matches",return_value=False):
            self.assertEqual(scan(rpc,"payer","recipient",ref,100,self.t)["status"],"not_found")
        result=scan(lambda m,p:[],"payer","recipient",ref,100,self.t)
        self.assertFalse(result["safe_to_retry"])
    def test_marketplace_release_guard(self):
        from marketplace_release import readiness,enabled
        from unittest.mock import patch
        with patch.dict("os.environ",{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"true"}):
            self.assertTrue(readiness()["requested"])
            self.assertFalse(enabled())
            self.assertIn("onchain_duplicate_prevention",readiness()["blockers"])
        with patch.dict("os.environ",{"ACADEMY_MARKETPLACE_PAYMENTS_ENABLED":"false"}):
            self.assertFalse(enabled())
    def test_marketplace_contract_receipt_fixture(self):
        from marketplace_contract_preview import instruction_data,receipt_data,receipt_matches,candidate_matches,SYSTEM
        from marketplace_split import ALPHABET,TOKEN
        from payment_policy import TREASURY,USDC_MINT
        import base64,copy
        def enc(b):
            n=int.from_bytes(b,"big");out=""
            while n:
                n,i=divmod(n,58);out=ALPHABET[i]+out
            return "1"*(len(b)-len(b.lstrip(bytes([0]))))+out
        payer,recipient,ref,program,pda,src,dst,fee=[enc(bytes([i])*32) for i in range(11,19)]
        sig=enc(bytes([19])*64);cents=100000
        account={"owner":program,"executable":False,"lamports":10000000,"data":[base64.b64encode(receipt_data(payer,ref,recipient,cents)).decode(),"base64"]}
        self.assertTrue(receipt_matches(account,program,payer,ref,recipient,cents))
        self.assertFalse(receipt_matches(account,program,payer,ref,recipient,cents+1))
        keys=[payer,pda,src,dst,fee,USDC_MINT,TOKEN,SYSTEM,program]
        def bal(j,owner,n):return {"accountIndex":j,"owner":owner,"mint":USDC_MINT,"uiTokenAmount":{"decimals":6,"amount":str(n)}}
        def transfer(j,n):return {"programIdIndex":6,"accounts":[2,5,j,0],"data":enc(bytes([12])+n.to_bytes(8,"little")+bytes([6]))}
        tx={"blockTime":int(self.t.timestamp()),"transaction":{"signatures":[sig],"message":{"accountKeys":keys,"header":{"numRequiredSignatures":1,"numReadonlySignedAccounts":0,"numReadonlyUnsignedAccounts":4},"instructions":[{"programIdIndex":8,"accounts":[0,1,2,3,4,5,6,7],"data":enc(instruction_data(ref,recipient,cents))}]}},"meta":{"err":None,"innerInstructions":[{"index":0,"instructions":[transfer(3,950000000),transfer(4,50000000)]}],"preTokenBalances":[bal(2,payer,1000000000),bal(3,recipient,0),bal(4,TREASURY,0)],"postTokenBalances":[bal(2,payer,0),bal(3,recipient,950000000),bal(4,TREASURY,50000000)]}}
        def valid(t=tx,a=account):return candidate_matches(t,a,program,pda,sig,payer,recipient,ref,cents,self.t)
        self.assertTrue(valid())
        for change in ("wrong_fee","wrong_program","wrong_pda","no_cpi","bad_signer","failed"):
            t=copy.deepcopy(tx)
            if change=="wrong_fee":t["meta"]["innerInstructions"][0]["instructions"][1]=transfer(4,49999999)
            elif change=="wrong_program":t["transaction"]["message"]["instructions"][0]["programIdIndex"]=6
            elif change=="wrong_pda":t["transaction"]["message"]["accountKeys"][1]=ref
            elif change=="no_cpi":t["meta"]["innerInstructions"]=[]
            elif change=="bad_signer":t["transaction"]["message"]["header"]["numRequiredSignatures"]=2
            else:t["meta"]["err"]={"failed":True}
            self.assertFalse(valid(t),change)
        self.assertFalse(valid(a={**account,"owner":SYSTEM}))
    def test_private_preflight(self):
        from content_vault import preflight
        valid={"title":"Original lesson","theory":"Independent example","assignment":"Test task","prompts":[]}
        self.assertTrue(preflight("lesson",1,"en",valid)["valid"])
        self.assertFalse(preflight("lesson",46,"en",valid)["valid"])
        self.assertFalse(preflight("lesson",1,"en",{**valid,"title":"bad\x00text"})["valid"])
        self.assertFalse(preflight("exam",1,"en",[])["valid"])
    def test_freelancer_analytics(self):
        from freelancer_analytics import summarize
        from datetime import date,timedelta
        today=date(2026,11,24)
        r=summarize([(today,"design","completed",True,14000),(today,"video","open",False,20000),(today-timedelta(days=20),"web","assigned",True,30000)],7,today)
        self.assertEqual(r["cohort"]["applications"],2)
        self.assertEqual(r["cohort"]["selection_percent"],50.0)
        self.assertEqual(r["cohort"]["completed_cents"],14000)
        self.assertEqual(r["all_time"]["selected_cents"],44000)
        self.assertEqual(r["daily"][-1]["applications"],2)
        self.assertFalse(r["payment_verified"])
        self.assertIsNone(summarize([],7,today)["cohort"]["selection_percent"])
        with self.assertRaises(ValueError): summarize([],8,today)
    def test_acquisition(self):
        from acquisition import normalize,summarize
        self.assertEqual(normalize("telegram"),"telegram")
        self.assertIsNone(normalize("https://example.invalid"))
        self.assertIsNone(normalize(["telegram"]))
        r=summarize([("telegram",4)], [("telegram",2,1,0,0,0,0,2,0,0)], [("telegram",3)])
        row=next(x for x in r["items"] if x["source"]=="telegram")
        self.assertEqual(row["client_conversion_percent"],25.0)
        self.assertEqual(row["completed"],2)
        self.assertEqual(row["applications"],3)
        self.assertIsNone(next(x for x in r["items"] if x["source"]=="other")["client_conversion_percent"])
    def test_job_matching(self):
        from job_matching import rank
        jobs=[{"id":1,"category":"design"},{"id":2,"category":"video"},{"id":3,"category":"web"},{"id":4,"category":"design"}]
        self.assertEqual(rank(jobs,[]),[])
        self.assertEqual([j["id"] for j in rank(jobs,[7,8,10],"video")],[2,4,1])
        self.assertEqual(rank(jobs,[31])[0]["matched_lessons"],1)
        self.assertTrue(rank(jobs,[],"web")[0]["service_match"])
    def test_career_accelerator(self):
        from career import roadmap,PROFILE_FIELDS
        empty=roadmap({},0,"none",0,0,0,30)
        self.assertEqual(empty["completed_stages"],0)
        self.assertEqual(empty["next"],"profile")
        p={k:"example" for k in PROFILE_FIELDS}
        r=roadmap(p,5,"pending",1,0,10,30)
        self.assertEqual(r["next"],"listing")
        self.assertEqual(r["completed_stages"],3)
        self.assertEqual(roadmap(p,5,"approved",1,1,30,30)["completed_stages"],5)
    def test_career_quote(self):
        from career import quote
        self.assertEqual(quote("5","20","10","10")["total"],"121.00")
        self.assertEqual(quote(0,0,0,0)["total"],"0.00")
        self.assertEqual(quote("0.5","19.99",0,0)["total"],"10.00")
        for invalid in ("NaN","Infinity",-1,True):
            with self.assertRaises(ValueError): quote(invalid,20,0,0)
        with self.assertRaises(ValueError): quote(1,1,0,101)
    def test_partner_commission(self):
        from partners import commission,base58_valid
        self.assertEqual(commission(199000000),59700000)
        self.assertEqual(commission(189050000),56715000)
        self.assertEqual(commission(999000000),299700000)
        self.assertTrue(base58_valid("1"*32,32))
        self.assertFalse(base58_valid("0"*32,32))
        with self.assertRaises(ValueError): commission(-1)
    def test_payout_verification(self):
        from payout_verify import matches,TOKEN_PROGRAM
        from payment_policy import TREASURY,USDC_MINT
        from copy import deepcopy
        wallet="recipient";sig="signature";amount=59700000
        keys=[{"pubkey":TREASURY,"signer":True},{"pubkey":"source","signer":False},{"pubkey":"destination","signer":False}]
        def bal(i,owner,n):
            return {"accountIndex":i,"owner":owner,"mint":USDC_MINT,"uiTokenAmount":{"decimals":6,"amount":str(n)}}
        tx={"blockTime":int(self.t.timestamp()),"meta":{"err":None,"preTokenBalances":[bal(1,TREASURY,amount),bal(2,wallet,0)],"postTokenBalances":[bal(1,TREASURY,0),bal(2,wallet,amount)]},"transaction":{"signatures":[sig],"message":{"accountKeys":keys,"instructions":[{"programId":TOKEN_PROGRAM,"parsed":{"type":"transferChecked","info":{"source":"source","destination":"destination","authority":TREASURY,"mint":USDC_MINT,"tokenAmount":{"amount":str(amount),"decimals":6}}}}]}}}
        self.assertTrue(matches(tx,sig,wallet,amount,self.t))
        self.assertFalse(matches(tx,sig,wallet,amount+1,self.t))
        self.assertFalse(matches(tx,sig,"other",amount,self.t))
        self.assertFalse(matches(tx,sig,wallet,amount,self.t+timedelta(seconds=1)))
        altered=deepcopy(tx);altered["transaction"]["message"]["accountKeys"][0]["signer"]=False
        self.assertFalse(matches(altered,sig,wallet,amount,self.t))
        altered=deepcopy(tx);altered["meta"]["err"]={"failed":True}
        self.assertFalse(matches(altered,sig,wallet,amount,self.t))
    def test_network_input(self):
        from network_admin import validate
        self.assertEqual(validate(None,0,"  example  "),(None,0,"example"))
        self.assertEqual(validate(123,50,""),(123,50,""))
        for values in ((True,0,""),(1,-1,""),(1,0,"x"*121),(0,0,"")):
            with self.assertRaises(ValueError): validate(*values)
    def test_partner_marketing(self):
        from marketing import materials,projection
        code="a"*24
        for lang in ("en","ru","uk","pl"):
            kit=materials(code,lang)
            self.assertEqual(len(kit["materials"]),4)
            self.assertTrue(all("?ref="+code in x["text"] for x in kit["materials"]))
        self.assertEqual(projection({"starter":1,"pro":1,"vip":1,"elite":0})["commission_atomic"],509100000)
        with self.assertRaises(ValueError): projection({"starter":-1,"pro":0,"vip":0,"elite":0})
        with self.assertRaises(ValueError): materials("invalid","en")
    def test_founder_accounting(self):
        from founder import summarize,validate_period
        d=summarize(199000000,1,[("available",10000000),("pending",20000000),("approved",10000000),("paid",10000000),("rejected",9700000)])
        self.assertEqual(d["unpaid_reserve_atomic"],"49700000")
        self.assertEqual(d["after_paid_atomic"],"189000000")
        self.assertEqual(d["after_all_commissions_atomic"],"139300000")
        self.assertEqual(summarize(0,0,[])["gross_atomic"],"0")
        with self.assertRaises(ValueError): validate_period(True)
        with self.assertRaises(ValueError): validate_period(1000)
    def test_trial_funnel(self):
        from founder import trial_funnel
        from unittest.mock import Mock
        cur=Mock()
        cur.fetchone.return_value=(20,10,8,3,5,1,1,0,1)
        result=trial_funnel(cur,self.t,self.t+timedelta(days=7))
        self.assertEqual(result["attempt_rate"],50)
        self.assertEqual(result["pass_rate"],80)
        self.assertEqual(result["conversion_rate"],37.5)
        self.assertEqual(result["plans"],{"starter":1,"pro":1,"vip":0,"elite":1})
        sql,params=cur.execute.call_args.args
        self.assertEqual(sql.count("%s"),len(params))
        self.assertIn("p.passed_at<c.paid_at",sql)
        cur.fetchone.return_value=(0,0,0,0,0,0,0,0,0)
        self.assertIsNone(trial_funnel(cur,self.t,self.t)["conversion_rate"])
    def test_founder_activity_helpers(self):
        from founder import daily_activity,percent
        self.assertIsNone(percent(0,0))
        self.assertEqual(percent(1,3),33.33)
        start=self.t
        series=daily_activity(start,7,[(start.date(),"registrations",2),((start+timedelta(days=1)).date(),"exam_attempts",3)])
        self.assertEqual(len(series),7)
        self.assertEqual(series[0]["registrations"],2)
        self.assertEqual(series[1]["exam_attempts"],3)
        self.assertEqual(series[-1]["registrations"],0)
        self.assertEqual(series[0]["certificates"],0)
        with self.assertRaises(ValueError): daily_activity(start,7,[(start.date(),"invalid",1)])
    def test_totp_recovery(self):
        from mfa import code_at,check,consume,recovery_digest
        from unittest.mock import patch
        secret="GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        self.assertEqual(code_at(secret,1),"287082")
        with patch("mfa.time.time",return_value=59):
            self.assertEqual(check(secret,"287082"),1)
            self.assertIsNone(check(secret,"287082",1))
            recovery="a"*32
            self.assertEqual(consume(secret,1,[recovery_digest(recovery)],recovery),(1,[]))
            with self.assertRaises(PermissionError): consume(secret,1,[],recovery)
    def test_private_curriculum_validation(self):
        from content_vault import validate
        from copy import deepcopy
        bank=[{"id":str(i),"question":"Question "+str(i),"options":["A","B","C"],"correct":"A"} for i in range(10)]
        self.assertEqual(validate("exam",1,"en",bank),bank)
        broken=deepcopy(bank);broken[1]["question"]=broken[0]["question"]
        with self.assertRaises(ValueError): validate("exam",1,"en",broken)
        with self.assertRaises(ValueError): validate("exam",46,"en",bank)
        lesson={"title":"Private","theory":"Theory","assignment":"Task","prompts":[]}
        self.assertEqual(validate("lesson",1,"ru",lesson),lesson)
        with self.assertRaises(ValueError): validate("lesson",1,"ru",{**lesson,"answer":"secret"})
    def test_private_legacy_overlap(self):
        from content_vault import normalize_question,legacy_overlap,require_original_exam,coverage
        from lesson01 import LESSON
        bank=[{"question":q[0]} for q in LESSON["questions"]]
        self.assertEqual(legacy_overlap(bank),len(bank))
        with self.assertRaises(ValueError): require_original_exam(bank)
        self.assertEqual(normalize_question("  TEST—Case! "),normalize_question("test case"))
        original=[{"question":"Original synthetic scenario "+str(i)} for i in range(10)]
        require_original_exam(original)
        with self.assertRaises(ValueError): require_original_exam([{"question":"Example?"},{"question":"example!"}])
        r=coverage([{"kind":"exam","day":1,"lang":"en","legacy_overlap":1},{"kind":"lesson","day":2,"lang":"ru"}])
        self.assertEqual(r["en"]["exam"]["count"],0)
        self.assertEqual(r["ru"]["lesson"]["count"],1)
        self.assertNotIn(2,r["ru"]["lesson"]["missing"])
    def test_practice_catalog(self):
        from practice_lab import brief
        for day in range(1,46):
            for lang in ("en","ru","uk","pl"):
                d=brief(day,lang)
                self.assertEqual(d["day"],day)
                self.assertEqual(d["language"],lang)
                self.assertTrue(d["deliverable"])
                self.assertEqual(sum(r["max"] for r in d["rubric"]),100)
                self.assertEqual(len(d["steps"]),4)
        with self.assertRaises(ValueError): brief(46)
    def test_project_review(self):
        from project_reviewer import review,FIELDS
        data={k:"" for k in FIELDS}
        self.assertEqual(review(1,data)["provided_count"],0)
        data["goal"]="Goal"
        data["rights"]=" "
        for lang in ("en","ru","uk","pl"):
            result=review(45,data,lang)
            self.assertEqual(result["provided_count"],1)
            self.assertFalse(result["official_grade"])
            self.assertEqual(len(result["checks"]),6)
        with self.assertRaises(ValueError): review(1,{"goal":"x"})
    def test_career_profile(self):
        from career_profile import validate,EMPTY
        self.assertEqual(validate({**EMPTY,"name":"  Test  "})["name"],"Test")
        with self.assertRaises(ValueError): validate({"name":"Test"})
        with self.assertRaises(ValueError): validate({**EMPTY,"contact":"x"*201})
        with self.assertRaises(ValueError): validate({**EMPTY,"skills":123})
    def test_student_business(self):
        from student_business import cents,totals,order_values
        self.assertEqual(cents("12.30"),1230)
        for x in ("-1","1.001","NaN","1e3",12,"1000001"):
            with self.assertRaises(ValueError): cents(x)
        result=totals([("delivered",10000,8000,2000),("cancelled",5000,1000,500)])
        self.assertEqual(result["outstanding_cents"],"2000")
        self.assertEqual(result["cash_margin_cents"],"6500")
        with self.assertRaises(ValueError): order_values({"client_id":1,"title":"X","status":"lead","agreed":"5","received":"6","expense":"0"})
    def test_agency_quality_validation(self):
        from agency_quality import validate,FIELDS
        checks={k:"pass" for k in FIELDS}
        self.assertTrue(validate(checks,"Test evidence")["ready"])
        self.assertFalse(validate({**checks,"technical":"fail"},"Test evidence")["ready"])
        self.assertFalse(validate({**checks,"rights":"unchecked"},"Test evidence")["ready"])
        for invalid in ({}, {**checks,"other":"pass"}, {**checks,"scope":True}, {**checks,"scope":"unknown"}):
            with self.assertRaises(ValueError): validate(invalid,"Test evidence")
        with self.assertRaises(ValueError): validate(checks," ")
    def test_agency_workflow_templates(self):
        from agency_workflow import plan,TEMPLATES
        self.assertEqual(len(TEMPLATES),5)
        for key in TEMPLATES:
            rows=plan(key)
            self.assertEqual([x["step"] for x in rows],list(range(1,len(rows)+1)))
            self.assertTrue(rows[-1]["review"])
            self.assertEqual(sum(x["review"] for x in rows),1)
        for invalid in (None,[], "unknown"):
            with self.assertRaises(ValueError): plan(invalid)
    def test_creator_business_action_plan(self):
        from creator_analytics import action_plan
        row={"id":1,"title":"test","flags":["overdue"],"days_remaining":-2,"outstanding_cents":100,"priority":0,"contact":"private"}
        job={"id":2,"title":"video","category":"video","budget_cents":5000,"matched_lessons":3,"service_match":True,"brief":"not needed"}
        result=action_plan({"actions":[row]*15},["review_orders"],{"items":[job]*12})
        self.assertEqual(len(result["order_actions"]),10)
        self.assertEqual(len(result["matching_jobs"]),8)
        self.assertNotIn("contact",result["order_actions"][0])
        self.assertNotIn("brief",result["matching_jobs"][0])
        self.assertFalse(result["automatic_execution"])
        self.assertEqual(action_plan({"actions":[]},[],{"items":[]})["matching_jobs"],[])
    def test_creator_analytics_recommendations(self):
        from creator_analytics import recommendations
        c={"applications":0,"selection_percent":None}
        f={"cash_margin_cents":"-100"}
        self.assertEqual(recommendations(c,f,[],{"action_count":1}),["review_orders","review_costs","send_proposals","publish_portfolio"])
        self.assertEqual(recommendations({"applications":5,"selection_percent":0},{"cash_margin_cents":"0"},[{"published":1}],{"action_count":0}),["improve_proposals"])
        self.assertEqual(recommendations({"applications":10,"selection_percent":30},{"cash_margin_cents":"500"},[{"published":2}],{"action_count":0}),[])
    def test_creator_experience_levels(self):
        from reputation import experience_level
        cases=[(0,0,None,"new"),(2,2,5.0,"new"),(3,0,None,"experienced"),
               (10,5,4.0,"established"),(25,10,4.5,"expert"),(25,10,4.49,"established"),
               (100,0,None,"experienced"),(25,9,5.0,"established"),(25,10,3.99,"experienced")]
        for completed,reviews,rating,expected in cases:
            with self.subTest(completed=completed,reviews=reviews,rating=rating):
                self.assertEqual(experience_level(completed,reviews,rating),expected)
    def test_business_assistant(self):
        from business_assistant import report
        from datetime import date
        today=date(2026,11,24)
        base={"title":"Example","status":"in_progress","due":"2026-11-23","agreed_cents":10000,"received_cents":2000,"expense_cents":3000}
        rows=[{**base,"id":1},{**base,"id":2,"status":"delivered"},{**base,"id":3,"status":"cancelled"},{**base,"id":4,"status":"lead","due":""}]
        result=report(rows,today)
        self.assertEqual(result["action_count"],3)
        self.assertEqual(result["actions"][0]["flags"],["overdue"])
        self.assertEqual(result["actions"][1]["flags"],["collect_payment"])
        self.assertEqual(result["projected_margin_cents"],"14000")
        self.assertEqual(result["projected_margin_percent"],"70.0")
        self.assertIsNone(report([],today)["projected_margin_percent"])
    def test_productivity(self):
        from productivity import values,parse_day
        b={"title":"Test","day":"2026-11-24","category":"study","priority":1,"minutes":30,"done":False}
        self.assertEqual(values(b)[4],30)
        for k,v in (("day","2026-02-30"),("minutes",1441),("priority",True),("category","other"),("done",1)):
            with self.assertRaises(ValueError): values({**b,k:v})
    def test_quiz(self):
        key={str(i):"a" for i in range(10)}
        self.assertTrue(quiz_passed({**key,"0":"b","1":"b"},key))
        self.assertFalse(quiz_passed({**key,"0":"b","1":"b","2":"b"},key))
        self.assertFalse(quiz_passed({},key))
if __name__ == "__main__":
    unittest.main()

# Run provider-mocked studio regression checks with the existing build suite.
from test_higgsfield_studio import HiggsfieldStudioTests

# Verify the real HTTP adapter and page assets before every Render deployment.
from test_release_smoke import ReleaseSmokeTests


def load_tests(loader, tests, pattern):
    """Compatibility bridge for the Academy's existing Render build command.
    Install declared dependencies in the build environment, not during server startup.
    Local test runs use the developer's preinstalled environment.
    """
    import os
    import subprocess
    import sys
    from pathlib import Path
    if os.environ.get("RENDER") == "true" or os.environ.get("RENDER_SERVICE_NAME") == "zer0life-academy":
        requirements = Path(__file__).with_name("requirements.txt")
        subprocess.run([sys.executable, "-m", "pip", "install", "--disable-pip-version-check", "-r", str(requirements)], check=True)
        # Run rollback-only integration against the provisioned Academy DB before deployment.
        # Do not run migrations here; the currently live service may still use that schema.
        proof=Path(__file__).with_name(".academy-db-release-check")
        proof.unlink(missing_ok=True)
        commit=os.getenv("RENDER_GIT_COMMIT")
        if commit and os.getenv("ACADEMY_DATABASE_URL"):
            subprocess.run([sys.executable,"-c","from server import run_release_db_checks; run_release_db_checks()"],check=True,timeout=900)
            proof.write_text(commit,encoding="utf-8")
    return tests
