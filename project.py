import csv
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from fpdf import FPDF
from fpdf.fonts import FontFace


BOLD = "\033[1m"
UNDER = "\033[4m"
RESET = "\033[0m"

def main():
    # UPLOAD TRANSACTIONS
    uploaded_transactions = input(f"{BOLD}Upload the file with the transactions: {RESET}")
    transactions = upload_transactions(uploaded_transactions)

    fix_labels(transactions)

    # AMOUNT BY CATEGORIES
    parent_category_totals, parent_category_count = accumulate(transactions, "Parent Category")
    category_totals, category_count = accumulate(transactions, "Category")

    #print("Spending by Parent Category")
    #print("\n", parent_category_totals)

    #print("Spending by Category")
    #print("\n", category_totals)

    # OVERALL METRICS
    income, spending, parent_reimbursement = total_income_spending(transactions)
    expenses = round(spending - parent_reimbursement, 2)

    #print("\n")
    #print(f"Income: {income}")
    #print(f"Spending: {spending}")
    #print(f"Expenses: {expenses}")

    # CHARTS
    spending_categories_totals = only_spending_dictionary(category_totals)
    pie_chart(spending_categories_totals, "Spending by Category")
    bar_chart(income, spending, parent_reimbursement, expenses)

    spending_transactions = only_spending_transactions(transactions)
    timeline(spending_transactions)

    # LARGEST SPENDING CATEGORY
    largest_spending_category = max(spending_categories_totals, key = spending_categories_totals.get)
    largest_spending_string = f"{largest_spending_category} - ${spending_categories_totals[largest_spending_category]}"

    # LARGEST FREQUENCY CATEGORY
    spending_categories_count = only_spending_dictionary(category_count)
    most_frequent_spending_category = max(spending_categories_count, key = spending_categories_count.get)
    frequency_string = f"{most_frequent_spending_category} - {spending_categories_count[most_frequent_spending_category]}"


    # GROUP ANALYSIS
    selection = input("\nWhich category would you like to analyze? ").title()


    # Classifications that are both Parent Categories and Categories
    duplicates = ["Business Services", "Shopping", "Transfer", "Food & Dining", "Miscellaneous" ]

    if selection not in duplicates:
        table_info = category_analysis(transactions, "Category", selection)
    else:
        category_classification = input("Parent Category or Category? ").title()
        table_info = category_analysis(transactions, category_classification, selection)

    make_pdf(largest_spending_string, frequency_string, selection, table_info)




def upload_transactions(csv_file):
    """Loads and cleans transaction data from a CSV file.

    Parses each row into a dictionary, converts the Date column to a date object,
    removes internal transfer transactions, and relabels certain special-case
    transactions (parent reimbursements, Venmo income).

    Args:
        csv_file: Path to the CSV file containing transaction data.

    Returns:
        A list of dictionaries, where each dictionary represents one cleaned transaction.
    """

    results = []
    with open(csv_file) as file:
              reader = csv.DictReader(file)
              for row in reader:
                string_date = row["Date"]
                results.append({"Date": datetime.strptime(string_date, "%m/%d/%Y").date(), "Description": row["Description"], "Original Description": row["Original Description"], "Amount": row["Amount"], "Type":row["Type"],	"Parent Category":row["Parent Category"], "Category":row["Category"]})

    cleaned_results = []
    for transaction in results:
        if not re.search('Transfer To Share|Transfer From Account', transaction["Description"], re.IGNORECASE):
            cleaned_results.append(transaction)

        if re.search("Deposit Home Banking Transfer  / From RODER", transaction["Original Description"], re.IGNORECASE):
            transaction["Category"] = "Parent Reimbursement"

        if re.search("Transfer From Venmo", transaction["Description"], re.IGNORECASE):
            transaction["Category"] = "Income"
            transaction["Parent Category"] = "Income"

    return cleaned_results


def fix_labels(transactions_list):
    """Prompts the user to recategorize any transactions currently marked "Uncategorized".

    Updates each uncategorized transaction's Category and Parent Category in place,
    using previously seen category/parent-category relationships when possible.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.
    """

    relationships = build_category_lookup(transactions_list)

    category_groups = list_of_groups(transactions_list, "Category")
    category_groups.remove("Uncategorized")

    print()
    print(f"{BOLD}UPDATE UNCATEGORIZED TRANSACTIONS{RESET}")
    for transaction in transactions_list:
        if transaction["Category"] == "Uncategorized":
            print(f'\nTransaction Description: {BOLD}{transaction["Description"]}{RESET} \nOriginal Description: {transaction["Original Description"]} \nAmount: {transaction["Amount"]}\n')

            # Update Category
            print(f"{UNDER}Common Categories: {RESET}")
            category_result = ", ".join(category_groups)
            print(category_result)

            new_category = input(f"{BOLD}What should the CATEGORY be? {RESET}").title()
            if new_category:
                transaction["Category"] = new_category
                if new_category not in category_groups:
                    category_groups.append(new_category)
            else:
                continue

            # Update Parent Category
            if transaction["Category"] in relationships:
                transaction["Parent Category"] = relationships[transaction["Category"]]
            else:
                print(f"{UNDER}\n Common Parent Categories: {RESET}")
                parent_category_groups = list_of_groups(transactions_list, "Parent Category")
                parent_category_groups.remove("Uncategorized")
                parent_category_result = ", ".join(parent_category_groups)
                print(parent_category_result)

                new_parent_category = input(f"{BOLD}What should the PARENT CATEGORY be? {RESET}").title()
                if new_parent_category:
                    transaction["Parent Category"] = new_parent_category
                else:
                    continue

                relationships[new_category] = new_parent_category

def list_of_groups(transactions_list, selection):
    """Returns a list of unique categories or parent categories.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.
        selection: Either "Category" or "Parent Category".

    Returns:
        A list of unique classification values, with "Miscellaneous" appended as a fallback option.
    """

    groups = []
    for transaction in transactions_list:
        if transaction[selection] not in groups:
            groups.append(transaction[selection])

    # Provide a miscellaneous option
    groups.append("Miscellaneous")

    return groups

def build_category_lookup(transactions_list):
    """Builds a mapping from each category to its corresponding parent category.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.

    Returns:
        A dictionary mapping each category to its parent category.
    """

    lookup = {}

    for transaction in transactions_list:
        child_category = transaction["Category"].title()
        if child_category not in lookup:
            lookup[child_category] = transaction["Parent Category"].title()

    return lookup

def accumulate(transactions_list, label):
    """Calculates total spending and transaction frequency per category.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.
        label: Either "Parent Category" or "Category".

    Returns:
        A tuple of two dictionaries:
            totals: Maps each category/parent category to its total dollar amount.
            counts: Maps each category/parent category to its number of transactions.
    """

    totals = {}
    counts = {}

    for transaction in transactions_list:
        type = transaction[label]
        if type in totals:
            totals[type] += float(transaction["Amount"])
        else:
            totals[type] = float(transaction["Amount"])

        if type in counts:
            counts[type] += 1
        else:
            counts[type] = 1

    for key in totals:
        totals[key] = round(totals[key], 2)

    return totals, counts

def total_income_spending(transactions_list):
    """Calculates overall income, spending, and parent reimbursement totals.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.

    Returns:
        A tuple of three floats: (income, spending, parent_reimbursement), each rounded to 2 decimal places.
    """
    income = 0
    spending = 0
    parent_reimbursement = 0
    spending_parent_categories = ["Auto & Transport", "Business Services", "Food & Dining", "Health & Fitness", "Shopping", "Miscellaneous"]

    for transaction in transactions_list:
        if transaction["Parent Category"] in spending_parent_categories:
            spending += float(transaction["Amount"])

        if transaction["Parent Category"] == "Income":
            income += float(transaction["Amount"])

        # Parent Category == Transfer
        if transaction["Parent Category"] == "Transfer":
            if transaction["Category"] == "Parent Reimbursement":
                parent_reimbursement += float(transaction["Amount"])
            else:
                spending += float(transaction["Amount"])

    return round(income, 2), round(spending, 2), round(parent_reimbursement, 2)

def only_spending_dictionary(dictionary):
    """Filters a totals dictionary down to categories that represent actual spending.

    Args:
        dictionary: Dictionary of category names mapped to totals (amounts or counts).

    Returns:
        A new dictionary excluding non-spending categories (income, reimbursements, etc.).
    """
    # Categories that do not represent spending
    excluded_categories = ['Dividend & Cap Gains', 'Parent Reimbursement', 'Income', 'Paycheck']

    spending_dictionary = {}
    for category in dictionary:
        if category not in excluded_categories:
            spending_dictionary[category] = dictionary[category]

    return spending_dictionary

def only_spending_transactions(transactions_list):
    """Filters a transaction list down to transactions that represent actual spending.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.

    Returns:
        A list of dictionaries containing only transactions whose Category is not
        an excluded non-spending category.
    """
    spending_transaction_list = []
    # Categories that do not represent spending
    excluded_categories = ['Dividend & Cap Gains', 'Parent Reimbursement', 'Income', 'Paycheck']

    for transaction in transactions_list:
        if transaction["Category"] not in excluded_categories:
            spending_transaction_list.append(transaction)

    return spending_transaction_list


def pie_chart(spending_dictionary, title):
    """Creates and saves a pie chart of spending by category.

    Large slices are labeled directly on the chart; all slices are labeled in the legend.
    Saves the chart to "chart.png".

    Args:
        spending_dictionary: Dictionary mapping category names to total dollar amounts.
        title: Title to display on the chart.
    """

    values = spending_dictionary.values()
    total_spending = sum(values)

    legend_labels = []
    pie_labels = []

    for category in spending_dictionary:
        label = f"{category} - ${spending_dictionary[category]:.2f}"
        legend_labels.append(label)

        if spending_dictionary[category] > 0.03*total_spending:
            pie_labels.append(label)
        else:
            pie_labels.append("")

    plt.pie(values, labels = pie_labels)
    plt.title(title)

    plt.legend(legend_labels, loc="center left", bbox_to_anchor=(1.5, 0.5))

    plt.savefig("chart.png", bbox_inches="tight")
    plt.close()

def bar_chart(income, spending, parent_reimbursement, expenses):
    """Creates and saves a bar chart comparing income, spending, reimbursement, and net change.

    Saves the chart to "bar.png".

    Args:
        income: Total income for the period.
        spending: Total spending for the period.
        parent_reimbursement: Total parent reimbursement amount.
        expenses: Total expenses (spending minus reimbursement).
    """

    labels = ["Income", "Spending", "Parent \n Reimbursement", "Expenses", "Net Change"]
    net_change = income + parent_reimbursement - spending
    values = [income, spending, parent_reimbursement, expenses, net_change]

    fig, ax = plt.subplots()
    bar_container = ax.bar(labels, values, color="pink")
    ax.set(ylabel='Amount Spent $', title='Monthly Spending')
    ax.bar_label(bar_container, fmt='${:,.2f}')
    plt.savefig('bar.png', bbox_inches="tight")
    plt.close()


def timeline(spending_transactions):
    """Creates and saves a line chart of total spending per day.

    Args:
        spending_transactions: List of dictionaries, where each dictionary represents
            one spending transaction (with a "Date" and "Amount").
    """

    sorted_spending_transactions = sorted(spending_transactions, key = lambda date: date["Date"])

    daily_spending = {}
    for transaction in sorted_spending_transactions:
        if transaction["Date"] in daily_spending:
            daily_spending[transaction["Date"]] += float(transaction["Amount"])
        else:
            daily_spending[transaction["Date"]] = float(transaction["Amount"])

    date = daily_spending.keys()
    amount = daily_spending.values()

    plt.plot(date, amount, color="hotpink")

    ax = plt.gca()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d'))

    plt.title("Total Spending by Day")
    plt.xlabel("Day")
    plt.ylabel("Amount Spent $")
    plt.savefig("timeline.png", bbox_inches="tight")
    plt.close()


def category_analysis(transactions_list, category_classification, selection):
    """Filters transactions matching a specific category or parent category.

    Args:
        transactions_list: List of dictionaries, where each dictionary represents one transaction.
        category_classification: Either "Category" or "Parent Category".
        selection: The specific category value to filter by.

    Returns:
        A list of dictionaries containing only the transactions matching the given selection.
    """


    selectioned_transactions = []

    for transaction in transactions_list:
        if transaction[category_classification] == selection:
            selectioned_transactions.append(transaction)

    return selectioned_transactions

def make_pdf(largest_spending_string, frequency_string, selection, table_info):
    """Builds and saves a PDF summary report of monthly spending.

    Includes a title, pie chart, bar chart, timeline chart, largest/most frequent
    spending category summaries, and an optional detailed transaction table if a
    specific category was selected.

    Args:
        largest_spending_string: Formatted string naming the largest spending category and amount.
        frequency_string: Formatted string naming the most frequent spending category and count.
        selection: The specific category the user chose to analyze, or an empty string if none.
        table_info: List of dictionaries representing transactions to include in the detailed table.
    """

    pdf = FPDF()
    pdf.add_page()

    # TITLE
    pdf.set_fill_color(255, 192, 203)   # light pink (RGB)
    pdf.set_draw_color(219, 112, 147)   # darker pink (RGB)
    pdf.set_font('Helvetica', style='B', size=22)
    pdf.cell(w=190, h=10, text="Monthly Spending", align = "C", fill=True, border=1)

    # CHARTS
    pdf.image(name = "chart.png", x = 10, y = 24, w = 180)
    pdf.image(name = "bar.png", x = 10, y = 105, w = 90)
    pdf.image(name = "timeline.png", x = 110, y = 105, w = 90)

    # LARGEST AND MOST FREQUENCT AMOUNTS
    pdf.set_font(family='Helvetica', style='B', size=12)

    pdf.set_xy(x=10, y=178)
    pdf.cell(text='Largest Spending Category: ', align = 'L')
    pdf.set_xy(x=10, y=185)
    pdf.cell(text='Most Frequent Spending Category: ', align = 'L')

    pdf.set_font(family='Helvetica', size=12)
    pdf.set_xy(x=70, y=178)
    pdf.cell(text=largest_spending_string, align = 'L')
    pdf.set_xy(x=85, y=185)
    pdf.cell(text=frequency_string, align = 'L')


    if selection != "":

        # DETAILED REPORT
        pdf.set_font(family='Helvetica', style='B', size=16)
        pdf.set_xy(x=10, y=195)

        pdf.cell(w=190, text=f"{selection} Transactions", align = 'C')

        pdf.set_xy(x=10, y=205)
        pdf.set_font(family='Helvetica', size=12)

        # rows is a list of lists
        rows = [["Date", "Description", "Amount"]]
        for transaction in table_info:
            rows.append([transaction["Date"], transaction["Description"], f"${float(transaction['Amount']):.2f}"])

        pdf.set_fill_color(255, 255, 255)   # reset to white

        with pdf.table(text_align = 'LEFT', headings_style=FontFace(fill_color=(255, 192, 203), emphasis="BOLD")) as table:
            for row_data in rows:
                row = table.row()
                for item in row_data:
                    row.cell(str(item))

    pdf.output("monthly_spending_report.pdf")


if __name__ == "__main__":
    main()
