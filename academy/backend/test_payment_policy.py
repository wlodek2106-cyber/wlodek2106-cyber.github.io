import unittest
from unittest.mock import patch
from payment_policy import quote, validate_amount, TREASURY, USDC_MINT

class PaymentPolicyTests(unittest.TestCase):
    def test_closed(self):
        with patch.dict("os.environ", {"ACADEMY_PAYMENTS_ENABLED":"false"}):
            with self.assertRaises(PermissionError):
                quote("starter","USDC")

    def test_prices(self):
        with patch.dict("os.environ", {"ACADEMY_PAYMENTS_ENABLED":"true"}):
            for plan,price in (("starter",199),("pro",499),("vip",999)):
                q=quote(plan,"USDC")
                self.assertEqual(q["amount_atomic"],price*1000000)
                self.assertEqual(q["recipient"],TREASURY)
                self.assertEqual(q["mint"],USDC_MINT)

    def test_referral_discount(self):
        from solana_pay import payment_url
        from urllib.parse import parse_qs,urlsplit
        with patch.dict("os.environ", {"ACADEMY_PAYMENTS_ENABLED":"true"}):
            for plan,atomic,amount in (("starter",189050000,"189.05"),("pro",474050000,"474.05"),("vip",949050000,"949.05")):
                self.assertEqual(quote(plan,"USDC",True)["amount_atomic"],atomic)
                url=payment_url(plan,"1"*32,atomic)
                self.assertEqual(parse_qs(urlsplit(url).query)["amount"],[amount])
                with self.assertRaises(ValueError): payment_url(plan,"1"*32,atomic-1)
    def test_sol_without_quote(self):
        with patch.dict("os.environ", {"ACADEMY_PAYMENTS_ENABLED":"true"}):
            with self.assertRaises(PermissionError):
                quote("vip","SOL")

    def test_exact_amount(self):
        self.assertTrue(validate_amount(199000000,199000000))
        for amount in (0,198999999,199000001,199000000.0,True):
            self.assertFalse(validate_amount(199000000,amount))

    def test_invalid_plan(self):
        with self.assertRaises(ValueError):
            quote("unknown","USDC")

if __name__=="__main__":
    unittest.main()
