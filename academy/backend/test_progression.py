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
    def test_quiz(self):
        key={str(i):"a" for i in range(10)}
        self.assertTrue(quiz_passed({**key,"0":"b","1":"b"},key))
        self.assertFalse(quiz_passed({**key,"0":"b","1":"b","2":"b"},key))
        self.assertFalse(quiz_passed({},key))
if __name__ == "__main__":
    unittest.main()
