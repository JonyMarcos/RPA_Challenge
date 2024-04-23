import re

def check_money_related(title, description):
    """Checks if title or description contains money-related keywords."""
    try:
        money_keywords = ["\$[\d,]+(?:\.\d+)?(?:[KMB]?(?:illion|illion|thousand))?", "dollars", "USD"]
        title_contains_money = any(re.search(keyword, title, re.IGNORECASE) for keyword in money_keywords)
        description_contains_money = any(re.search(keyword, description, re.IGNORECASE) for keyword in money_keywords)
        
        return title_contains_money, description_contains_money
    except Exception as e:
        print(f"Error while checking money-related keywords: {e}")

# Test input
title = input("Enter the title: ")
description = input("Enter the description: ")

# Check if title or description contains money-related keywords
title_result, description_result = check_money_related(title, description)

# Print the results
print(f"Title contains money-related keywords: {title_result}")
print(f"Description contains money-related keywords: {description_result}")
