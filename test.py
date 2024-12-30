import win32api

# Get the current username
username = win32api.GetUserName()
print(f"Current User: {username}")
