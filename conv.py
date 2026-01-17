import base64

import win32clipboard

def copy_to_clipboard(text):
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()

with open("copy-white-small.png", "rb") as f:
    data = f.read()

encoded = base64.b64encode(data).decode("ascii")
copy_to_clipboard(encoded)
print("done")



