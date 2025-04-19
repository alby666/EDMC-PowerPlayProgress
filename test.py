def sample_program():
    items = []  # Initialize an empty list
    # Add 12 items
    for i in range(1, 13):  # Loop from 1 to 12
        new_item = f"Item {i}"  # Create a new item (e.g., "Item 1", "Item 2", etc.)
        
        # Add the new item to the front of the list
        items.insert(0, new_item)
        
        # Ensure the list doesn't exceed 10 items
        if len(items) > 10:
            items.pop()  # Remove the oldest item (last in the list)
        
        print(f"After adding '{new_item}': {items}")

# Run the program
sample_program()