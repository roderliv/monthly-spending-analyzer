from project.project import only_spending_transactions
from project.project import only_spending_dictionary
from project.project import accumulate
from project.project import total_income_spending


transactions_list = [
    {"Date": "01/01/2026", "Description": "Test1", "Amount": "100", "Type": "Debit", "Parent Category": "Food & Dining", "Category": "Groceries"},
    {"Date": "01/02/2026", "Description": "Test2", "Amount": "50", "Type": "Debit", "Parent Category": "Food & Dining", "Category": "Restaurants"},
    {"Date": "01/03/2026", "Description": "Test3", "Amount": "200", "Type": "Credit", "Parent Category": "Income", "Category": "Paycheck"},
    {"Date": "01/04/2026", "Description": "Test4", "Amount": "30", "Type": "Debit", "Parent Category": "Shopping", "Category": "Shopping"},
    {"Date": "01/05/2026", "Description": "Test5", "Amount": "20", "Type": "Debit", "Parent Category": "Food & Dining", "Category": "Groceries"},
]

only_spending_transactions_list = [
    {"Date": "01/01/2026", "Description": "Test1", "Amount": "100", "Type": "Debit", "Parent Category": "Food & Dining", "Category": "Groceries"},
    {"Date": "01/02/2026", "Description": "Test2", "Amount": "50", "Type": "Debit", "Parent Category": "Food & Dining", "Category": "Restaurants"},
    {"Date": "01/04/2026", "Description": "Test4", "Amount": "30", "Type": "Debit", "Parent Category": "Shopping", "Category": "Shopping"},
    {"Date": "01/05/2026", "Description": "Test5", "Amount": "20", "Type": "Debit", "Parent Category": "Food & Dining", "Category": "Groceries"},
]

accumulate_category_total = {"Groceries" : 120, "Restaurants" : 50, "Paycheck" : 200, "Shopping" : 30}
accumulate_category_count = {"Groceries" : 2, "Restaurants" : 1, "Paycheck" : 1, "Shopping" : 1}
income = 200
spending = 200
parent_reimbursement = 0

def test_only_spending_transactions():
    assert only_spending_transactions(transactions_list) == only_spending_transactions_list

def test_only_spending_dictionary():
    assert only_spending_dictionary(accumulate_category_total) == {"Groceries" : 120, "Restaurants" : 50, "Shopping" : 30}

def test_accumulate():
    assert accumulate(transactions_list, "Category") == (accumulate_category_total, accumulate_category_count)

def test_total_income_spending():
    assert total_income_spending(transactions_list) == (income, spending, parent_reimbursement)
