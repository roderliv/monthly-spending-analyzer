# MONTHLY SPENDING ANALYZER
#### Video Demo: (https://youtu.be/JRg3LNQd3qU)
#### Description:

Monthly Spending Analyzer is a command-line Python program that takes a raw bank transaction CSV export, cleans and categorizes it, and produces a polished PDF report summarizing a user's monthly spending. I built this project because I wanted a hands-on way to actually understand my own spending habits each month, rather than relying on my bank's built-in (and fairly limited) reporting tools.

#### What it does

When you run project.py, the program walks through the following pipeline:

Uploads and cleans the transaction data. The user is prompted for the path to a CSV file containing their monthly transactions (columns: Date, Description, Original Description, Amount, Type, Parent Category, Category). The program parses each row into a dictionary, converts the date into an actual date object, filters out internal savings-to-checking transfers that shouldn't count as spending, and automatically relabels a few special-case transactions (like reimbursements from a parent, or incoming Venmo payments) based on patterns found in the transaction descriptions using regular expressions.
Fills in missing categories. Bank exports often leave some transactions "Uncategorized." The program walks the user through each uncategorized transaction one at a time, showing the transaction's description, original description, and amount, along with a list of previously used categories. The user types in a category, and if that category has been seen before (either from the original data or from an earlier fix during this same run), the matching parent category is filled in automatically. The user only has to specify a parent category the first time a brand-new category appears; that relationship is remembered for the rest of the run.
Calculates totals. The program aggregates total dollar amounts and transaction counts by both Category and Parent Category, and separately calculates overall income, total spending, and net expenses (spending minus any reimbursements received).
Builds visualizations. Using matplotlib, the program generates three charts, each saved as its own PNG: a pie chart of spending broken down by category (large slices are labeled directly on the chart, and every category is labeled in an accompanying legend), a bar chart comparing income, spending, reimbursements, expenses, and net change, and a line chart tracking total spending by day across the month.
Identifies key insights. The program automatically determines the largest spending category (by dollar amount) and the most frequent spending category (by transaction count), excluding non-spending categories like income and reimbursements from both calculations.
Offers a deep dive. The user can optionally type in a specific category or parent category to investigate further. If they do, the program filters all transactions matching that selection down to a list the PDF can display in detail.
Generates a PDF report. Using fpdf2, the program compiles everything above into a single PDF: a title banner, the pie chart, the bar chart and timeline chart side by side, the largest/most frequent spending category summaries, and, if the user requested it, a table listing every transaction (date, description, amount) under their chosen category.

#### Files
project.py — Contains main() and all supporting functions: CSV parsing and cleanup, interactive category correction, aggregation logic, chart generation, and PDF assembly. Functions are organized in roughly the order they're used by main(): data loading and cleaning first, then aggregation and filtering, then chart-building, then PDF generation last.
test_project.py — Contains pytest-compatible unit tests for several of the project's core data-processing functions. I specifically chose functions that take structured data in and return structured data out, with no input() calls or file reading involved, since those are the functions that can be tested reliably against hand-built sample data and hand-calculated expected results.
requirements.txt — Lists the external packages this project depends on (matplotlib and fpdf2) so they can be installed with pip install -r requirements.txt.
