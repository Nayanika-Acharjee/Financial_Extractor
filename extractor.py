import re

LINE_ITEMS = {
    "Revenue": ["revenue", "turnover", "total income"],
    "Operating Expenses": ["operating expenses", "operating costs"],
    "Net Income": ["net income", "profit after tax", "PAT"]
}

def extract_financial_data(text):
    results = {}

    # detect year columns (simple pattern)
    years = re.findall(r'20\d{2}', text)
    years = sorted(list(set(years)))[:2]  # keep 2 years for simplicity

    for item, keywords in LINE_ITEMS.items():
        for keyword in keywords:
            pattern = rf"{keyword}.*?([\d,]+)"
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                results[item] = match.group(1).replace(",", "")
                break
        if item not in results:
            results[item] = ""

    return results
