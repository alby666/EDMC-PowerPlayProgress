class EntryManager:
    def __init__(self):
        self.entries = []

    def add_entry(self, entry: dict) -> None:
        if isinstance(entry.get('value'), str):  # Check if the 'value' is a string
            self.entries.append(entry['value'])
            # Keep only the last 10 entries
            if len(self.entries) > 10:
                self.entries = self.entries[-10:]
            print(f"Entry added: {entry['value']}")
        else:
            print("Error: Entry value must be a string.")

# Example usage
manager = EntryManager()
for i in range(12):  # Adding 12 entries to demonstrate the behavior
    manager.add_entry({'value': f'example{i + 1}'})
    
print(manager.entries)  # Will display only the last 10 entries

print(manager.entries[0])