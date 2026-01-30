#!/usr/bin/env python3
"""
WhatsApp Message Sender - GUI Application
A graphical user interface for sending WhatsApp messages using Twilio API.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from twilio.rest import Client


class WhatsAppSenderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Silver Tier - WhatsApp Message Sender")
        self.root.geometry("600x500")
        self.root.resizable(True, True)

        # Configure styles
        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Create main frame
        main_frame = ttk.Frame(root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(main_frame, text="WhatsApp Message Sender", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))

        # Credentials info
        ttk.Label(main_frame, text="Credentials:", font=("Arial", 10, "bold")).grid(row=1, column=0, sticky=tk.W, pady=5)
        self.credentials_info = ttk.Label(main_frame, text="Using environment variables (TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN)", foreground="blue")
        self.credentials_info.grid(row=1, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Check credentials button
        self.check_creds_button = ttk.Button(main_frame, text="Check Credentials", command=self.check_credentials)
        self.check_creds_button.grid(row=2, column=1, sticky=tk.W, pady=5, padx=(10, 0))

        # Recipient Number
        ttk.Label(main_frame, text="Recipient Number:").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.number_var = tk.StringVar(value="+923349739727")  # Pre-filled with your number
        self.number_entry = ttk.Entry(main_frame, textvariable=self.number_var, width=50)
        self.number_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=5, padx=(10, 0))
        ttk.Label(main_frame, text="(Format: +1234567890)", foreground="gray").grid(row=4, column=1, sticky=tk.W, padx=(10, 0))

        # Message
        ttk.Label(main_frame, text="Message:").grid(row=5, column=0, sticky=(tk.W, tk.N), pady=5)

        # Create a frame for the text widget and scrollbar
        text_frame = ttk.Frame(main_frame)
        text_frame.grid(row=5, column=1, rowspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=5, padx=(10, 0))
        main_frame.rowconfigure(5, weight=1)
        text_frame.columnconfigure(0, weight=1)
        text_frame.rowconfigure(0, weight=1)

        self.message_text = scrolledtext.ScrolledText(
            text_frame,
            height=8,
            width=40,
            wrap=tk.WORD,
            font=("Arial", 10)
        )
        self.message_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Quick message buttons
        quick_msg_frame = ttk.Frame(main_frame)
        quick_msg_frame.grid(row=7, column=0, columnspan=2, pady=10)

        ttk.Button(quick_msg_frame, text="Hi", command=lambda: self.set_message("hi")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_msg_frame, text="How are you?", command=lambda: self.set_message("how are you")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_msg_frame, text="Good Morning", command=lambda: self.set_message("Good morning!")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_msg_frame, text="Thank You", command=lambda: self.set_message("Thank you!")).pack(side=tk.LEFT, padx=5)
        ttk.Button(quick_msg_frame, text="Clear", command=lambda: self.message_text.delete(1.0, tk.END)).pack(side=tk.LEFT, padx=5)

        # Send button
        self.send_button = ttk.Button(
            main_frame,
            text="Send WhatsApp Message",
            command=self.send_message_threaded,
            style="Accent.TButton"
        )
        self.send_button.grid(row=8, column=0, columnspan=2, pady=20)

        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), padx=10, pady=5)

        # Status label
        self.status_var = tk.StringVar(value="Ready to send message")
        self.status_label = ttk.Label(main_frame, textvariable=self.status_var, foreground="blue")
        self.status_label.grid(row=10, column=0, columnspan=2, pady=5)

        # Response text area
        response_frame = ttk.LabelFrame(main_frame, text="Response", padding="5")
        response_frame.grid(row=11, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        main_frame.rowconfigure(11, weight=1)
        response_frame.columnconfigure(0, weight=1)
        response_frame.rowconfigure(0, weight=1)

        self.response_text = scrolledtext.ScrolledText(
            response_frame,
            height=6,
            width=60,
            wrap=tk.WORD,
            state=tk.DISABLED
        )
        self.response_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Load credentials from environment if available
        self.load_credentials()

    def load_credentials(self):
        """Load credentials from environment variables if available."""
        import os
        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        # Update UI to reflect credential status
        if self.account_sid and self.auth_token:
            self.credentials_info.config(text="Using environment variables (Credentials found)", foreground="green")
        else:
            self.credentials_info.config(text="Using environment variables (Credentials NOT found!)", foreground="red")

    def check_credentials(self):
        """Check if credentials are available."""
        import os
        account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        auth_token = os.getenv("TWILIO_AUTH_TOKEN")

        if account_sid and auth_token:
            self.credentials_info.config(text="Using environment variables (Credentials found)", foreground="green")
            messagebox.showinfo("Credentials Check", "Credentials are properly set in environment variables!")
        else:
            self.credentials_info.config(text="Using environment variables (Credentials NOT found!)", foreground="red")
            messagebox.showwarning("Credentials Check", "Credentials NOT found! Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables.")


    def toggle_password_visibility(self):
        """Toggle the visibility of the auth token."""
        if self.show_password_var.get():
            self.auth_token_entry.config(show="")
        else:
            self.auth_token_entry.config(show="*")

    def set_message(self, message):
        """Set a predefined message."""
        self.message_text.delete(1.0, tk.END)
        self.message_text.insert(tk.END, message)

    def send_message_threaded(self):
        """Send message in a separate thread to prevent GUI freezing."""
        self.send_button.config(state=tk.DISABLED)
        self.progress.start()
        self.status_var.set("Sending message...")

        thread = threading.Thread(target=self.send_message)
        thread.daemon = True
        thread.start()

    def send_message(self):
        """Send the WhatsApp message using Twilio API."""
        try:
            # Get credentials from environment variables
            account_sid = self.account_sid
            auth_token = self.auth_token

            # Get other values from GUI
            to_number = self.number_var.get().strip()
            message_body = self.message_text.get(1.0, tk.END).strip()

            # Validate inputs
            if not account_sid or not auth_token:
                self.update_gui(lambda: messagebox.showerror("Error", "Credentials not found! Please set TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN environment variables"))
                return

            if not to_number:
                self.update_gui(lambda: messagebox.showerror("Error", "Please enter recipient number"))
                return

            if not to_number.startswith('+'):
                self.update_gui(lambda: messagebox.showerror("Error", "Phone number must start with + followed by country code"))
                return

            if not message_body:
                self.update_gui(lambda: messagebox.showerror("Error", "Please enter a message"))
                return

            # Initialize Twilio client
            client = Client(account_sid, auth_token)

            # Send WhatsApp message
            message = client.messages.create(
                body=message_body,
                from_='whatsapp:+14155238886',  # Twilio's WhatsApp Sandbox number
                to=f'whatsapp:{to_number}'
            )

            # Update GUI with success message
            response = f"✅ Message sent successfully!\n"
            response += f"SID: {message.sid}\n"
            response += f"Status: {message.status}\n"
            response += f"To: {to_number}\n"
            response += f"Message: {message_body}\n"
            response += f"Timestamp: {message.date_sent}\n"

            self.update_response(response)
            self.update_gui(lambda: self.status_var.set(f"Message sent successfully! SID: {message.sid}"))

        except Exception as e:
            error_msg = f"❌ Error sending message: {str(e)}"
            self.update_response(error_msg)
            self.update_gui(lambda: self.status_var.set(f"Error: {str(e)}"))
            self.update_gui(lambda: messagebox.showerror("Error", str(e)))

        finally:
            # Update GUI in main thread
            self.update_gui(lambda: self.progress.stop())
            self.update_gui(lambda: self.send_button.config(state=tk.NORMAL))

    def update_response(self, text):
        """Update the response text area."""
        def update():
            self.response_text.config(state=tk.NORMAL)
            self.response_text.delete(1.0, tk.END)
            self.response_text.insert(tk.END, text)
            self.response_text.config(state=tk.DISABLED)
        self.update_gui(update)

    def update_gui(self, func):
        """Safely update GUI from a different thread."""
        self.root.after(0, func)


def main():
    root = tk.Tk()
    app = WhatsAppSenderGUI(root)

    # Center the window on screen
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")

    root.mainloop()


if __name__ == "__main__":
    main()