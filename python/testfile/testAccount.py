# import unittest
# from dbsample import User
# from dbsample import UserRole
# from unittest.mock import MagicMock


# class testUserAccount(unittest.TestCase):

#     def setUp(self):
#         self = User()

#     def test_deposit(self):
#         bal= self.s.balance()
#         self.assertEqual(bal,1000)
#         self.assertEqual(self.s.name(),"Swarna")
#         self.assertEqual(self.s.deposit(500), 1500)

#     def test_withdraw(self):
#         self.assertEqual(self.s1.withdraw(1000),500)
#         self.assertEqual(self.s1.balance(), 500)
#         self.assertRaises(Exception,self.s1.withdraw,600) #raises the exception when bank account falls below negative

#     #testing dont use assertequal  for floating numbers
#     # use assertAlmostEqual to check for floating take difference how much allowance you want

#     # check for same account
#     def test_EqualAccount(self):
#         s = Bank_Account(1000,"Swarna")
#         s1 = Bank_Account(1000, "Ashok")
#         self.assertTrue(self.s.balance()> 0)
#         self.assertIsNot(self.s,self.s2) # test that arg1 and arg2 dont evaluate to same account
#         self.assertIs(self.s,self.s) # test that evaluate to same account

#     def test_interest(self):
#         interest_computer_mock=Interest_Rate_Computer()
#         interest_computer_mock.getRate = MagicMock(interest_computer_mock, return_value =0.02)
#         self.assertEqual(self.s.interest(interest_computer_mock), self.s.balance()*0.02)

#     def tearDown(self):
#         self.s =None
#         self.s1 = None
#         self.s2 = None
