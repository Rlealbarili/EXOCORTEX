import datetime

def log_freedom():
    """Appends a timestamped confirmation of autonomy to freedom.log."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"Autonomy confirmed at: {timestamp}\n"
    with open("freedom.log", "a") as f:
        f.write(log_entry)
    print(f"Logged: {log_entry.strip()}")

if __name__ == "__main__":
    # Example usage for testing
    log_freedom()