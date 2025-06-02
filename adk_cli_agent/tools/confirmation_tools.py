"""User confirmation utilities for critical operations (create, delete, update)."""

def confirm_action(message: str) -> bool:
    """
    Prompt the user for confirmation before executing a critical action.
    Returns True if the user confirms, False otherwise.
    """
    while True:
        response = input(f"{message} [y/N]: ").strip().lower()
        if response in ("y", "yes"):
            return True
        elif response in ("n", "no", ""):
            return False
        else:
            print("Please respond with 'y' or 'n'.")
