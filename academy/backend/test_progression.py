import unittest
from datetime import datetime, timedelta, timezone
from progression import eligible, quiz_passed

class ProgressTests(unittest.TestCase):
    def setUp(self):
        self.t = datetime(2026,11,24,tzinfo=timezone.utc)
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
    def test_quiz(self):
        key={str(i):"a" for i in range(10)}
        self.assertTrue(quiz_passed({**key,"0":"b","1":"b"},key))
        self.assertFalse(quiz_passed({**key,"0":"b","1":"b","2":"b"},key))
        self.assertFalse(quiz_passed({},key))
if __name__ == "__main__":
    unittest.main()
