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
    def test_quiz(self):
        key={str(i):"a" for i in range(10)}
        self.assertTrue(quiz_passed({**key,"0":"b","1":"b"},key))
        self.assertFalse(quiz_passed({**key,"0":"b","1":"b","2":"b"},key))
        self.assertFalse(quiz_passed({},key))
if __name__ == "__main__":
    unittest.main()
