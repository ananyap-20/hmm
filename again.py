import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import scrolledtext
import sys
import io
from ttkthemes import ThemedTk
import customtkinter as ctk
import inspect
import time
import threading
from typing import Dict, List, Any
import json
import traceback
from datetime import datetime

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

class AdvancedDebugger:
    def __init__(self):
        self.breakpoints = set()
        self.current_line = 0
        self.variables = {}
        self.call_stack = []
        self.is_debugging = False
        self.execution_history = []
        self.current_frame = None
        
    def toggle_breakpoint(self, line_number: int):
        if line_number in self.breakpoints:
            self.breakpoints.remove(line_number)
            return False
        else:
            self.breakpoints.add(line_number)
            return True
            
    def step_over(self, code: str):
        try:
            lines = code.split('\n')
            if self.current_line < len(lines):
                line = lines[self.current_line]
                if self.current_line in self.breakpoints:
                    self.is_debugging = True
                    self.variables = self._get_local_variables()
                    self.call_stack = self._get_call_stack()
                    self.execution_history.append({
                        'line': self.current_line,
                        'code': line,
                        'variables': self.variables.copy(),
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    return "breakpoint"
                else:
                    output = io.StringIO()
                    sys.stdout = output
                    exec(line, globals())
                    sys.stdout = sys.__stdout__
                    
                    self.variables = self._get_local_variables()
                    self.call_stack = self._get_call_stack()
                    
                    self.execution_history.append({
                        'line': self.current_line,
                        'code': line,
                        'output': output.getvalue(),
                        'variables': self.variables.copy(),
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    })
                    
                self.current_line += 1
                return True
            return False
        except Exception as e:
            return str(e)
            
    def _get_local_variables(self) -> Dict[str, Any]:
        frame = inspect.currentframe()
        variables = {}
        if frame:
            variables = frame.f_locals
        return variables
        
    def _get_call_stack(self) -> List[str]:
        stack = []
        frame = inspect.currentframe()
        while frame:
            frame_info = inspect.getframeinfo(frame)
            stack.append(f"{frame_info.filename}:{frame_info.function}:{frame_info.lineno}")
            frame = frame.f_back
        return stack

class ModernOutputConsole:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent, fg_color="#1e1e1e")
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # Title bar
        self.title_bar = ctk.CTkFrame(self.frame, fg_color="#2d2d2d", height=40)
        self.title_bar.pack(fill="x", pady=(0, 5))
        
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="Output Console",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=10)
        
        # Clear button
        self.clear_button = ctk.CTkButton(
            self.title_bar,
            text="Clear",
            width=80,
            height=30,
            font=ctk.CTkFont(family="Helvetica", size=12),
            command=self.clear,
            fg_color="#2d2d2d",
            hover_color="#3d3d3d"
        )
        self.clear_button.pack(side="right", padx=10)
        
        # Console area
        self.console = ctk.CTkTextbox(
            self.frame,
            height=200,
            font=ctk.CTkFont(family="Consolas", size=14),
            fg_color="#1e1e1e",
            text_color="#ffffff"
        )
        self.console.pack(fill="x", padx=10, pady=5)
        
    def log(self, message: str, level: str = "info"):
        timestamp = datetime.now().strftime('%H:%M:%S')
        color = {
            "info": "#ffffff",
            "success": "#28a745",
            "error": "#dc3545",
            "warning": "#ffc107",
            "debug": "#17a2b8"
        }.get(level, "#ffffff")
        
        self.console.insert("end", f"[{timestamp}] ", "timestamp")
        self.console.insert("end", f"{message}\n", level)
        self.console.tag_config("timestamp", foreground="#888888")
        self.console.tag_config(level, foreground=color)
        self.console.see("end")
        
    def clear(self):
        self.console.delete("1.0", "end")

class CodeEditor:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent, fg_color="#2d2d2d")
        self.frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Title bar
        self.title_bar = ctk.CTkFrame(self.frame, fg_color="#1e1e1e", height=40)
        self.title_bar.pack(fill="x", pady=(0, 5))
        
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="Code Editor",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=10)
        
        # Editor container
        self.editor_container = ctk.CTkFrame(self.frame, fg_color="#2d2d2d")
        self.editor_container.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Line numbers
        self.line_numbers = tk.Text(
            self.editor_container,
            width=4,
            padx=3,
            takefocus=0,
            border=0,
            background="#1e1e1e",
            foreground="#888888",
            font=("Consolas", 14)
        )
        self.line_numbers.pack(side="left", fill="y")
        
        # Editor
        self.editor = scrolledtext.ScrolledText(
            self.editor_container,
            height=20,
            width=100,
            font=("Consolas", 14),
            bg="#2d2d2d",
            fg="#ffffff",
            insertbackground="#ffffff",
            selectbackground="#007AFF",
            selectforeground="#ffffff"
        )
        self.editor.pack(side="left", fill="both", expand=True)
        
        # Bind events
        self.editor.bind("<Key>", self._on_key_press)
        self.editor.bind("<MouseWheel>", self._on_mouse_wheel)
        
    def _on_key_press(self, event):
        self._update_line_numbers()
        
    def _on_mouse_wheel(self, event):
        self._update_line_numbers()
        
    def _update_line_numbers(self):
        self.line_numbers.delete("1.0", "end")
        line_count = self.editor.get("1.0", "end-1c").count("\n") + 1
        for i in range(1, line_count + 1):
            self.line_numbers.insert("end", f"{i}\n")
            
    def highlight_current_line(self, line_number):
        self.editor.tag_remove("current_line", "1.0", "end")
        self.editor.tag_add("current_line", f"{line_number}.0", f"{line_number}.end")
        self.editor.tag_config("current_line", background="#3d3d3d")

class VariableInspector:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent, fg_color="#2d2d2d")
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # Title bar
        self.title_bar = ctk.CTkFrame(self.frame, fg_color="#1e1e1e", height=40)
        self.title_bar.pack(fill="x", pady=(0, 5))
        
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="Variable Inspector",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=10)
        
        # Tree view
        self.tree = ttk.Treeview(
            self.frame,
            columns=("Name", "Type", "Value"),
            show="headings",
            style="Custom.Treeview",
            height=8
        )
        
        self.tree.heading("Name", text="Name")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Value", text="Value")
        
        # Set column widths
        self.tree.column("Name", width=150)
        self.tree.column("Type", width=100)
        self.tree.column("Value", width=200)
        
        self.tree.pack(fill="x", expand=True, padx=10, pady=5)
        
        # Custom style
        style = ttk.Style()
        style.configure(
            "Custom.Treeview",
            background="#2d2d2d",
            foreground="#ffffff",
            fieldbackground="#2d2d2d",
            font=("Consolas", 12)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#1e1e1e",
            foreground="#ffffff",
            font=("Helvetica", 12, "bold")
        )
        
    def update_variables(self, variables: Dict[str, Any]):
        self.tree.delete(*self.tree.get_children())
        for name, value in variables.items():
            self.tree.insert("", "end", values=(name, type(value).__name__, str(value)))

class CallStackViewer:
    def __init__(self, parent):
        self.frame = ctk.CTkFrame(parent, fg_color="#2d2d2d")
        self.frame.pack(fill="x", padx=10, pady=5)
        
        # Title bar
        self.title_bar = ctk.CTkFrame(self.frame, fg_color="#1e1e1e", height=40)
        self.title_bar.pack(fill="x", pady=(0, 5))
        
        self.title_label = ctk.CTkLabel(
            self.title_bar,
            text="Call Stack",
            font=ctk.CTkFont(family="Helvetica", size=16, weight="bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(side="left", padx=10)
        
        # List box
        self.listbox = tk.Listbox(
            self.frame,
            bg="#2d2d2d",
            fg="#ffffff",
            selectmode="single",
            font=("Consolas", 12),
            height=8
        )
        self.listbox.pack(fill="x", expand=True, padx=10, pady=5)
        
    def update_stack(self, stack: List[str]):
        self.listbox.delete(0, tk.END)
        for frame in stack:
            self.listbox.insert(tk.END, frame)

def run_code():
    code = code_input.get("1.0", "end-1c")
    
    output = io.StringIO()
    sys.stdout = output

    try:
        exec(code, globals())
        output_console.log(output.getvalue() or "Execution successful!", "success")
    except Exception as e:
        error_msg = f"Error: {str(e)}\n{traceback.format_exc()}"
        output_console.log(error_msg, "error")

    sys.stdout = sys.__stdout__

def debug_code():
    code = code_input.get("1.0", "end-1c")
    debugger.is_debugging = True
    debugger.current_line = 0
    output_console.clear()
    output_console.log("Starting debug session...", "info")
    output_console.log("Click on line numbers to set breakpoints", "info")
    output_console.log("Press 'Debug Code' to step through the code", "info")
    
    def debug_step():
        if debugger.is_debugging:
            result = debugger.step_over(code)
            if isinstance(result, str):  # Error occurred
                output_console.log(result, "error")
                debugger.is_debugging = False
            elif result == "breakpoint":  # Hit a breakpoint
                variable_inspector.update_variables(debugger.variables)
                call_stack_viewer.update_stack(debugger.call_stack)
                output_console.log(f"Breakpoint hit at line {debugger.current_line}", "debug")
                code_editor.highlight_current_line(debugger.current_line + 1)
                main_window.after(1000, debug_step)  # Cool transition delay
            elif result:  # More lines to execute
                variable_inspector.update_variables(debugger.variables)
                call_stack_viewer.update_stack(debugger.call_stack)
                output_console.log(f"Executing line {debugger.current_line}", "debug")
                code_editor.highlight_current_line(debugger.current_line + 1)
                main_window.after(100, debug_step)  # Faster execution for non-breakpoint lines
            else:  # Execution complete
                output_console.log("Debugging complete!", "success")
                debugger.is_debugging = False
    
    debug_step()

def toggle_breakpoint(event):
    try:
        line_number = int(code_input.index(f"@{event.x},{event.y}").split('.')[0])
        is_breakpoint = debugger.toggle_breakpoint(line_number)
        
        if is_breakpoint:
            code_input.tag_add("breakpoint", f"{line_number}.0", f"{line_number}.end")
            code_input.tag_config("breakpoint", background="#ff4444")
            output_console.log(f"Breakpoint added at line {line_number}", "info")
        else:
            code_input.tag_remove("breakpoint", f"{line_number}.0", f"{line_number}.end")
            output_console.log(f"Breakpoint removed at line {line_number}", "info")
    except:
        pass

def get_alternate_solution():
    alternate_code = """
# Alternate Solution generated by AI (this is a placeholder)
def alternate_solution():
    print('This is an alternate approach!')
"""
    code_input.delete("1.0", "end-1c")
    code_input.insert("1.0", alternate_code)
    output_console.log("Alternate solution has been inserted!", "info")

def login_screen():
    def validate_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            login_window.destroy()
            main_program_screen()
        else:
            messagebox.showerror("Login", "Invalid username or password")

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    login_window = ctk.CTk()
    login_window.title("Python IDE Pro - Advanced Debugger")
    login_window.geometry("600x500")
    login_window.configure(fg_color="#1a1a1a")

    login_frame = ctk.CTkFrame(login_window, fg_color="#1a1a1a")
    login_frame.pack(padx=40, pady=40, fill="both", expand=True)

    title_label = ctk.CTkLabel(
        login_frame,
        text="Python IDE Pro",
        font=ctk.CTkFont(family="Helvetica", size=32, weight="bold"),
        text_color="#ffffff"
    )
    title_label.pack(pady=20)

    subtitle_label = ctk.CTkLabel(
        login_frame,
        text="Advanced Python Development Environment",
        font=ctk.CTkFont(family="Helvetica", size=16),
        text_color="#888888"
    )
    subtitle_label.pack(pady=10)

    username_label = ctk.CTkLabel(
        login_frame,
        text="Username",
        font=ctk.CTkFont(family="Helvetica", size=14),
        text_color="#ffffff"
    )
    username_label.pack(pady=5)
    
    username_entry = ctk.CTkEntry(
        login_frame,
        width=300,
        height=40,
        font=ctk.CTkFont(family="Helvetica", size=14),
        placeholder_text="Enter username"
    )
    username_entry.pack(pady=5)
    
    password_label = ctk.CTkLabel(
        login_frame,
        text="Password",
        font=ctk.CTkFont(family="Helvetica", size=14),
        text_color="#ffffff"
    )
    password_label.pack(pady=5)
    
    password_entry = ctk.CTkEntry(
        login_frame,
        width=300,
        height=40,
        font=ctk.CTkFont(family="Helvetica", size=14),
        placeholder_text="Enter password",
        show="●"
    )
    password_entry.pack(pady=5)
    
    login_button = ctk.CTkButton(
        login_frame,
        text="Login",
        width=200,
        height=40,
        font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
        command=validate_login,
        fg_color="#007AFF",
        hover_color="#0056b3"
    )
    login_button.pack(pady=30)
    
    login_window.mainloop()

def main_program_screen():
    global code_input, debugger, output_console, variable_inspector, call_stack_viewer, main_window, code_editor

    main_window = ctk.CTk()
    main_window.title("Python IDE Pro - Advanced Debugger")
    main_window.geometry("1400x900")
    main_window.configure(fg_color="#1a1a1a")

    debugger = AdvancedDebugger()

    main_container = ctk.CTkFrame(main_window, fg_color="#1a1a1a")
    main_container.pack(padx=20, pady=20, fill="both", expand=True)

    title_frame = ctk.CTkFrame(main_container, fg_color="#1a1a1a", height=60)
    title_frame.pack(fill="x", pady=(0, 20))

    title_label = ctk.CTkLabel(
        title_frame,
        text="Python IDE Pro - Advanced Debugger",
        font=ctk.CTkFont(family="Helvetica", size=24, weight="bold"),
        text_color="#ffffff"
    )
    title_label.pack(side="left", padx=20)

    # Create left and right panels
    left_panel = ctk.CTkFrame(main_container, fg_color="#2d2d2d")
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

    right_panel = ctk.CTkFrame(main_container, fg_color="#2d2d2d")
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

    # Code editor section
    code_editor = CodeEditor(left_panel)
    code_input = code_editor.editor
    code_input.bind("<Button-1>", toggle_breakpoint)

    # Button container
    button_frame = ctk.CTkFrame(left_panel, fg_color="#1a1a1a")
    button_frame.pack(fill="x", pady=(0, 20))

    run_button = ctk.CTkButton(
        button_frame,
        text="▶ Run Code",
        width=150,
        height=40,
        font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
        command=run_code,
        fg_color="#28a745",
        hover_color="#218838"
    )
    run_button.pack(side="left", padx=10)

    debug_button = ctk.CTkButton(
        button_frame,
        text="🐞 Debug Code",
        width=150,
        height=40,
        font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
        command=debug_code,
        fg_color="#007AFF",
        hover_color="#0056b3"
    )
    debug_button.pack(side="left", padx=10)

    ai_button = ctk.CTkButton(
        button_frame,
        text="🤖 AI Solution",
        width=150,
        height=40,
        font=ctk.CTkFont(family="Helvetica", size=14, weight="bold"),
        command=get_alternate_solution,
        fg_color="#6f42c1",
        hover_color="#5a32a3"
    )
    ai_button.pack(side="left", padx=10)

    # Right panel components
    variable_inspector = VariableInspector(right_panel)
    call_stack_viewer = CallStackViewer(right_panel)
    output_console = ModernOutputConsole(right_panel)

    main_window.mainloop()

if __name__ == "__main__":
    login_screen()
