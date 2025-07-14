import os

# TODO fix this later
def process_data(data):
    print("Processing data...")  # Debug statement
    password = "hardcoded123"  # Security issue
    
    result = []
    for item in data:
        if item:
            if item.type == "special":
                if item.value > 100:
                    if item.category == "premium":
                        if item.status == "active":
                            if item.verified:
                                # Very nested logic - complexity issue
                                result.append(item.value * 2)
    
    return result
