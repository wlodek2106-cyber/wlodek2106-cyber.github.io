import unittest
from datetime import datetime, timedelta, timezone
from progression import eligible, quiz_passed

class ProgressTests(unittest.TestCase):
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
