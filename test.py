import win32api

# Get the current user name
username = win32api.GetUserName()
print(f"Current User: {username}")
