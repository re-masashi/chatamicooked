import tkinter as tk
import tkinter.ttk as ttk

root = tk.Tk()
root.title("Library Management System")
root.geometry('1280x720+0+0')

message = ttk.Label(
	root, 
	text="Hello ", 
	font=("monospace", 20), 
	padding="20px",
	foreground="#1e1e1e"
)
message.pack()

try:
	# fix blurry UI issues
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(1)
except:
	# the system is not windows
	pass
finally:
    root.mainloop()