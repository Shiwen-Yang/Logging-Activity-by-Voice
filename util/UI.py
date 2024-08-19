import tkinter as tk
import sqlite3
import sounddevice as sd
import numpy as np
import os
import wave
from tkinter import ttk, messagebox
from util.validator import *
from util.recording_processing import *

class DatabaseApp(tk.Tk):
    def __init__(self, database_path, table_names):
        super().__init__()
        self.database = database_path
        self.table_names = table_names
        self.title("Database Entry")
        self.geometry("400x400")

        # Configure the grid to have multiple columns
        self.grid_columnconfigure(0, weight=1)  # Dropdown column
        self.grid_columnconfigure(1, weight=0)  # Buttons column
        self.grid_columnconfigure(2, weight=0)  # Buttons column

        # Configure rows to expand
        self.grid_rowconfigure(2, weight=1)  # The row containing the entry_frame

        # Dropdown menu to select a table
        self.table_label = tk.Label(self, text="Select Table:")
        self.table_label.grid(row=0, column=0, pady=5, padx=10, sticky="w")

        self.table_var = tk.StringVar(self)
        self.table_dropdown = ttk.Combobox(self, textvariable=self.table_var, values=self.table_names)
        self.table_dropdown.bind("<<ComboboxSelected>>", self.create_entry_fields)
        self.table_dropdown.grid(row=1, column=0, pady=5, padx=10, sticky="w")


        # Create a notebook widget
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=2, column=0, columnspan=3, pady=5, padx=10, sticky="nsew")

        # Create the first tab for data entry
        self.entry_frame = tk.Frame(self.notebook)
        self.entry_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame.grid_rowconfigure(0, weight=1)
        self.notebook.add(self.entry_frame, text="Data Entry")
        
        # Submit button
        self.submit_button = tk.Button(self, text="Submit Entry", command=self.submit_entry)
        self.submit_button.grid(row=1, column=1, pady=5, padx=(10, 5), sticky="e")

        # Create the second tab to display the latest entry
        self.display_frame = tk.Frame(self.notebook)
        self.display_frame.grid_columnconfigure(0, weight=1)
        self.display_frame.grid_rowconfigure(0, weight=1)
        self.notebook.add(self.display_frame, text="Latest Entry")
        
        # Undo button
        self.undo_button = tk.Button(self, text="Undo Entry", command=self.undo_entry)
        self.undo_button.grid(row=1, column=2, pady=5, padx=(5, 10), sticky="w")
        
        # Create a Treeview widget to display the latest data entry
        self.tree = ttk.Treeview(self.display_frame, columns=(), show="headings")
        self.tree.grid(row=0, column=0, pady=5, padx=5, sticky="nsew")
                
        # Create the third tab for voice entry
        self.voice_entry_frame = tk.Frame(self.notebook)
        self.voice_entry_frame.grid_columnconfigure(0, weight=1)
        self.voice_entry_frame.grid_rowconfigure(0, weight=1)
        self.notebook.add(self.voice_entry_frame, text="Activity Voice Entry")

        #create the frame for voice entry
        self.controls_frame = tk.Frame(self.voice_entry_frame)
        self.controls_frame.grid(row=0, column=0, pady=2, padx=5, sticky="w")  

        # Push-to-Talk Button and Check Box on the Same Row
        self.push_to_talk_button = tk.Button(self.controls_frame, text="Press to Record")
        self.push_to_talk_button.pack(side="left", padx=5)

        self.checkbox_var = tk.BooleanVar()
        self.checkbox = tk.Checkbutton(self.controls_frame, text="Auto Commit", variable=self.checkbox_var)
        self.checkbox.pack(side="left", padx=5)

        # Treeview for displaying the transcription details
        self.transcript_tree = ttk.Treeview(self.voice_entry_frame, columns=list(columns.keys()), show="headings")
        self.transcript_tree.grid(row=1, column=0, pady=2, padx=5, sticky="nsew")

        # Define the column headings and configure the columns
        for col, props in columns.items():
            heading_text = props["text"]
            width = calculate_width(heading_text)
            self.transcript_tree.heading(col, text=heading_text)
            self.transcript_tree.column(col, width=width)

        # Adjust column and row weights to allow the text box to expand
        self.voice_entry_frame.grid_columnconfigure(0, weight=1)
        self.voice_entry_frame.grid_rowconfigure(1, weight=1)

        # Click to the push-to-talk button
        self.push_to_talk_button.bind("<ButtonPress-1>", self.start_recording)
        self.push_to_talk_button.bind("<ButtonRelease-1>", self.stop_recording)
        
        # Create the fourth tab for creating voice samples
        self.voice_sampling_frame = tk.Frame(self.notebook)
        self.voice_sampling_frame.grid_columnconfigure(0, weight=1)
        self.voice_sampling_frame.grid_rowconfigure(0, weight=1)
        self.notebook.add(self.voice_sampling_frame, text="Voice Sampling")

        # Create the frame for voice entry
        self.sampling_frame = tk.Frame(self.voice_sampling_frame)
        self.sampling_frame.grid(row=0, column=0, pady=2, padx=5, sticky="w")

        # Add an entry widget for the user to input the name of the recording
        self.recording_name_label = tk.Label(self.sampling_frame, text="My name is:")
        self.recording_name_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        self.recording_name_entry = tk.Entry(self.sampling_frame)
        self.recording_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        # Add instruction label to the sampling frame
        self.instruction_label = tk.Label(self.sampling_frame, text="Please try to talk for 10 seconds.")
        self.instruction_label.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Add the voice sampling button
        self.voice_sampling_button = tk.Button(self.sampling_frame, text="Press to Record")
        self.voice_sampling_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # Adjust column and row weights to allow the text box to expand
        self.voice_sampling_frame.grid_columnconfigure(0, weight=1)
        self.voice_sampling_frame.grid_rowconfigure(1, weight=1)

        # Bind button events to start and stop sampling methods
        self.voice_sampling_button.bind("<ButtonPress-1>", self.start_sampling)
        self.voice_sampling_button.bind("<ButtonRelease-1>", self.stop_sampling)
        
        
        # Store the last entry
        self.last_inserted_id = {}
        
    def update_treeview(self):
        
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        selected_table = self.table_var.get()

        # Clear existing rows and columns in the Treeview
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = []

        # Check if there are any recorded entries for the selected table
        if selected_table in self.last_inserted_id:
            ids_to_display = self.last_inserted_id[selected_table]

            # Calculate the optimal column widths
            column_widths = calculate_optimal_column_width(cursor, selected_table)

            # Fetch the column names and set up the Treeview columns
            cursor.execute(f"SELECT * FROM {selected_table} LIMIT 1")
            row_data = cursor.fetchone()

            if row_data:
                columns = [desc[0] for desc in cursor.description]
                self.tree["columns"] = columns
                for col in columns:
                    self.tree.heading(col, text=col)
                    self.tree.column(col, width=column_widths.get(col, 100), anchor="w")  # Default width if not calculated

            if isinstance(ids_to_display, int):
                ids_to_display = [ids_to_display]
            # Fetch and display each recorded entry from the last_inserted_id dictionary
            for row_id in ids_to_display:
                cursor.execute(f"SELECT * FROM {selected_table} WHERE rowid = ?", (row_id,))
                row_data = cursor.fetchone()
                if row_data:
                    self.tree.insert("", "end", values=row_data)
                    
                    # Close the cursor and connection
            cursor.close()
            conn.close()



    def create_entry_fields(self, event=None):
        
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        # Clear previous widgets
        for widget in self.entry_frame.winfo_children():
            widget.destroy()

        # Get selected table name and columns
        selected_table = self.table_var.get()
        cursor.execute(f"PRAGMA table_info({selected_table})")
        columns_info = cursor.fetchall()
        columns = [item[1] for item in columns_info]

        # Create a Canvas widget with a vertical scrollbar
        self.canvas = tk.Canvas(self.entry_frame)
        self.scrollbar = tk.Scrollbar(self.entry_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas.grid(row=0, column=0, pady=5, padx=10, sticky="nsew")
        self.scrollbar.grid(row=0, column=1, sticky="ns")

        # Configure the canvas to expand within the entry_frame
        self.entry_frame.grid_columnconfigure(0, weight=1)
        self.entry_frame.grid_rowconfigure(0, weight=1)

        # Create a Frame inside the Canvas for entry widgets
        self.inner_frame = tk.Frame(self.canvas)
        self.canvas.create_window((0, 0), window=self.inner_frame, anchor="nw")

        self.inner_frame.grid_columnconfigure(0, weight=1)
        self.inner_frame.grid_columnconfigure(1, weight=1)

        self.entry_widgets = {}
        auto_increment = has_autoincrement(cursor, selected_table)
        for i, column in enumerate(columns):
            is_primary_key = columns_info[i][5]
         # Skip primary key entry if AUTOINCREMENT is enabled
            if auto_increment and is_primary_key:
                continue
            tk.Label(self.inner_frame, text=column, anchor="e").grid(row=i, column=0, pady=5, padx=(20, 10), sticky="e")
            entry = tk.Entry(self.inner_frame)
            entry.grid(row=i, column=1, pady=5, padx=(10, 20), sticky="w")
            self.entry_widgets[column] = entry

        # Adjust grid and update scroll region
        self.inner_frame.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        # Handle scrollbar visibility and scrolling
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.bind("<Configure>", self._on_canvas_configure(None))
        self.update_treeview()
        
        cursor.close()
        conn.close()

    def _on_canvas_configure(self, event):
        # Update the scroll region and handle scrollbar visibility
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        if self.canvas.bbox("all")[3] > self.canvas.winfo_height():
            self.scrollbar.grid(row=0, column=1, sticky="ns")
            self.canvas.bind_all("<MouseWheel>", lambda event: self.canvas.yview_scroll(int(-1*(event.delta/120)), "units"))
        else:
            self.scrollbar.grid_forget()
            self.canvas.unbind_all("<MouseWheel>")


    def submit_entry(self):
        
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        
        selected_table = self.table_var.get()
        
        # Get column types
        cursor.execute(f"PRAGMA table_info({selected_table})")
        # column_info = self.cursor.fetchall()  # Fetch column information
        
        entered_data = {column: entry.get() for column, entry in self.entry_widgets.items()}
        
        # Validate each entry based on the expected type
        validation_error = validate_entry(cursor, selected_table, entered_data)
        if validation_error:
            messagebox.showwarning("Invalid Entry", validation_error)
            return

        columns = ', '.join(entered_data.keys())
        placeholders = ', '.join(['?'] * len(entered_data))
        sql = f"INSERT INTO {selected_table} ({columns}) VALUES ({placeholders})"

        try:
            cursor.execute(sql, list(entered_data.values()))
            # Append lastrowid to the corresponding table in the dictionary
            if selected_table not in self.last_inserted_id:
                self.last_inserted_id[selected_table] = []
            
            ids_to_display = self.last_inserted_id[selected_table]
            if isinstance(ids_to_display, int):
                ids_to_display = [ids_to_display]
            ids_to_display.append(cursor.lastrowid)
            cursor.connection.commit()
            self.update_treeview()

            for entry in self.entry_widgets.values():
                entry.delete(0, tk.END)
            play_sound_in_background()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")
        cursor.close()
        conn.close()


    def undo_entry(self):
        conn = sqlite3.connect(self.database)
        cursor = conn.cursor()
        # Get the selected table
        selected_table = self.table_var.get()

        # Get selected items from the Treeview
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "No entry selected to undo.")
            return

        for item in selected_items:
            # Get the values of the selected row
            item_values = self.tree.item(item, "values")
            # Assuming the row ID is in the first column
            row_id = item_values[0]

            # Prepare the SQL DELETE statement
            sql = f"DELETE FROM {selected_table} WHERE rowid = ?"

            # Execute the DELETE statement
            cursor.execute(sql, (row_id,))

            # Remove the item from the Treeview
            self.tree.delete(item)

        # Commit the transaction to save the changes
        cursor.connection.commit()
        cursor.close()
        conn.close()

        # Notify the user that the undo was successful
        messagebox.showinfo("Success", "Selected entries have been successfully undone.")
        
    def audio_callback(self, indata, frames, time, status):
        if hasattr(self, 'recording_data'):
            self.recording_data.append(indata.copy())

    def start_recording(self, event=None):
        self.push_to_talk_button.config(text = "Recording...")
        if not hasattr(self, 'recording') or not self.recording:
            self.recording = True
            print("Recording started...")
            self.push_to_talk_button.config(relief=tk.SUNKEN)  # Indicate recording state

            # Initialize recording parameters
            self.fs = 16000  # Sample rate
            self.recording_data = []

            # Start recording with callback
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_callback)
            self.stream.start()
            
    def insert_transcript_treeview(self, dic):
        # Insert into Treeview
        self.transcript_tree.insert('', 'end', values=(dic["speaker"], dic["date"], dic["time"], dic["activity"], dic["details"], dic["transcript"]))

        # Start a new thread to handle database operations
        def database_operations():
            # Open a new connection in this thread
            conn = sqlite3.connect(self.database)  # Replace 'your_database.db' with your actual database file path
            cursor = conn.cursor()

            # Look up member_id using speaker's name
            cursor.execute("SELECT member_id FROM Team WHERE first_name = ?", (dic["speaker"],))
            member_id = cursor.fetchone()
            
            if member_id:
                member_id = member_id[0]
            else:
                print(f"Team ID not found for speaker: {dic['speaker']}")
                cursor.close()
                conn.close()
                return

            # Prepare the data for the Activity table
            activity_type = dic["activity"]
            activity_time_str = f"{dic['date']} {dic['time']}"
            activity_time = datetime.datetime.strptime(activity_time_str, "%m/%d/%Y %H:%M:%S")
            notes = dic["details"]

            # Prepare the SQL query
            sql_query = """
            INSERT INTO Activity (member_id, activity_type, activity_time, notes)
            VALUES (?, ?, ?, ?)
            """
            sql_params = (member_id, activity_type, activity_time, notes)

            # Check if auto-commit is enabled
            if self.checkbox_var.get():  # Auto-commit is enabled
                cursor.execute(sql_query, sql_params)
                conn.commit()
                # Store the last inserted activity_id
                self.last_inserted_id['Activity'] = cursor.lastrowid
                self.update_treeview()
                print("SQL query committed to the database.")
            else:  # Auto-commit is disabled, save the query to a file
                with open("support_files/uncommitted.txt", "a") as f:
                    f.write(f"{sql_query} -- {sql_params}\n")
                print("SQL query added to uncommitted.txt")

            # Close the cursor and connection
            cursor.close()
            conn.close()

        # Run the database operations in a separate thread
        db_thread = threading.Thread(target=database_operations)
        db_thread.start()

    def stop_recording(self, event=None):
        self.push_to_talk_button.config(text="Push-to-Talk")
        if hasattr(self, 'recording') and self.recording:
            self.recording = False
            print("Recording stopped...")
            self.push_to_talk_button.config(relief=tk.RAISED)  # Reset button state

            # Stop the recording stream
            self.stream.stop()
            self.stream.close()

            # Convert the list of numpy arrays to a single array
            recorded_data = np.concatenate(self.recording_data, axis=0)

            # Normalize the audio to increase volume 
            max_val = np.max(np.abs(recorded_data))
            if max_val > 0:
            # Scale to int16 range
                recorded_data = ((recorded_data / max_val) * 32767).astype(np.int16)  

            # Create a unique filename using the current timestamp
            filename = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") + ".wav"
            filepath = os.path.join("recordings", filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            # Save the recording to the "recordings" folder
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(self.fs)
                wf.writeframes(recorded_data.tobytes())

            print(f"Recording saved to {filepath}")
            processing_thread = threading.Thread(target=processing_recording, args=(filepath, self.insert_transcript_treeview))
            processing_thread.start()
            
    def start_sampling(self, event=None):
        self.voice_sampling_button.config(text="Recording...")
        if not hasattr(self, 'sampling') or not self.sampling:
            self.sampling = True
            print("Voice sampling started...")
            self.voice_sampling_button.config(relief=tk.SUNKEN)  # Indicate recording state

            # Initialize recording parameters
            self.fs = 16000  # Sample rate
            self.sampling_data = []

            # Start recording with callback
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_sampling_callback)
            self.stream.start()

    def audio_sampling_callback(self, indata, frames, time, status):
        if hasattr(self, 'sampling_data'):
            self.sampling_data.append(indata.copy())
    def stop_sampling(self, event=None):
        self.voice_sampling_button.config(text="Press to Record")
        if hasattr(self, 'sampling') and self.sampling:
            self.sampling = False
            print("Voice sampling stopped...")
            self.voice_sampling_button.config(relief=tk.RAISED)  # Reset button state

            # Stop the recording stream
            self.stream.stop()
            self.stream.close()

            # Convert the list of numpy arrays to a single array
            recorded_data = np.concatenate(self.sampling_data, axis=0)

            # Normalize the audio to increase volume 
            max_val = np.max(np.abs(recorded_data))
            if max_val > 0:
                recorded_data = ((recorded_data / max_val) * 32767).astype(np.int16)  # Scale to int16 range

            # Get the recording name from the entry widget
            recording_name = self.recording_name_entry.get().strip()
            if not recording_name:
                recording_name = "Unnamed_Sample"  # Default name if no input

            # Create the "sample_recordings" folder if it doesn't exist
            os.makedirs("sample_recordings", exist_ok=True)

            # Create a unique filename using the recording name
            filename = f"{recording_name}.wav"
            filepath = os.path.join("sample_recordings", filename)

            # Save the recording to the "sample_recordings" folder
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)  # 2 bytes per sample (16-bit)
                wf.setframerate(self.fs)
                wf.writeframes(recorded_data.tobytes())

            print(f"Recording saved to {filepath}")