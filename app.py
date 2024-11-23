import os
import pandas as pd
import tkinter as tk
from tkinter import ttk
import time
import random


class DataProcessor:

    def __init__(self, data_folder, participant_info_file):
        self.data_folder = data_folder
        self.participant_info_file = participant_info_file

    def get_user_ids(self):
        if not os.path.exists(self.participant_info_file):
            raise FileNotFoundError(f"{self.participant_info_file} not found.")
        
        participant_info = pd.read_csv(self.participant_info_file)
        if 'SID' not in participant_info.columns:
            raise ValueError("Participant info file must contain 'SID' column.")
        
        return participant_info['SID'].tolist()

    def load_data(self, sid, chunksize=10**6):
        file_name = f"{sid}_whole_df.csv"
        file_path = os.path.join(self.data_folder, file_name)
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_name} not found in {self.data_folder}.")
        
        for chunk in pd.read_csv(file_path, chunksize=chunksize):
            yield chunk

    def analyze_data(self, sid, chunksize=10**6):
        results = {
            'Total Rows': 0,
            'Mean HR': 0,
            'Mean Temp': 0,
            'Sleep Stage Distribution': {}
        }
        total_hr = 0
        total_temp = 0
        sleep_stage_counts = {}
        num_chunks = 0

        for chunk in self.load_data(sid, chunksize):
            results['Total Rows'] += len(chunk)
            total_hr += chunk['HR'].mean()
            total_temp += chunk['TEMP'].mean()
            
            # Count sleep stages
            stage_counts = chunk['Sleep_Stage'].value_counts().to_dict()
            for stage, count in stage_counts.items():
                sleep_stage_counts[stage] = sleep_stage_counts.get(stage, 0) + count
            
            num_chunks += 1

        # Aggregate results
        results['Mean HR'] = total_hr / num_chunks
        results['Mean Temp'] = total_temp / num_chunks
        results['Sleep Stage Distribution'] = sleep_stage_counts

        return results


class DataVisualizer:

    def __init__(self, root, processor):
        self.root = root
        self.processor = processor
        self.create_main_screen()

    def create_main_screen(self):
        self.root.geometry("1000x700")
        self.root.title("Data Analysis Project by Tanha 🌈")

        # Gradient background
        gradient_frame = tk.Canvas(self.root)
        gradient_frame.pack(fill="both", expand=True)

        colors = ["#ff7eb3", "#ff758f", "#ffa56b", "#ffcc5c", "#ffff73"]
        for i, color in enumerate(colors):
            gradient_frame.create_rectangle(0, i * 140, 1000, (i + 1) * 140, fill=color, outline="")

        # Header
        gradient_frame.create_text(500, 50, text="Data Analysis Project", font=("Comic Sans MS", 24, "bold"), fill="#222222")
        gradient_frame.create_text(500, 100, text="Created by: Tanha ✨", font=("Comic Sans MS", 16), fill="#444444")

        # Button to start analysis
        start_button = tk.Button(self.root, text="Analyze Data", command=self.start_analysis, font=("Comic Sans MS", 14), bg="#6f9fd8", fg="black")
        start_button.place(x=430, y=150)

        # Treeview for displaying results
        self.tree = ttk.Treeview(self.root, columns=("SID", "Total Rows", "Mean HR", "Mean Temp"), show="headings")
        self.tree.place(x=50, y=250, width=900, height=400)

        # Define column headings
        self.tree.heading("SID", text="User ID")
        self.tree.heading("Total Rows", text="Total Rows")
        self.tree.heading("Mean HR", text="Mean HR (bpm)")
        self.tree.heading("Mean Temp", text="Mean Temp (°C)")

    def start_analysis(self):
        """
        Perform analysis for all users with colorful progress messages.
        """
        user_ids = self.processor.get_user_ids()
        total_users = len(user_ids)
        progress = 0

        # Progress window
        progress_window = tk.Toplevel(self.root)
        progress_window.geometry("400x200")
        progress_window.title("Analyzing Data... 🌟")
        progress_window.configure(bg="#ffe4e1")

        progress_label = tk.Label(progress_window, text="Starting analysis... 🎉", font=("Comic Sans MS", 14), bg="#ffe4e1")
        progress_label.pack(pady=20)

        progress_bar = ttk.Progressbar(progress_window, length=300, mode="determinate")
        progress_bar.pack(pady=10)
        progress_bar["maximum"] = total_users

        for sid in user_ids:
            progress_label.config(text=f"Analyzing User {sid}... 🌈✨")
            progress += 1
            progress_bar["value"] = progress
            progress_window.update()

            # Simulate processing time
            time.sleep(random.uniform(0.5, 1.5))

            try:
                analysis_results = self.processor.analyze_data(sid)

                # Extract key results
                total_rows = analysis_results['Total Rows']
                mean_hr = round(analysis_results['Mean HR'], 2)
                mean_temp = round(analysis_results['Mean Temp'], 2)

                # Add results to the Treeview
                self.tree.insert("", "end", values=(sid, total_rows, mean_hr, mean_temp))

            except Exception as e:
                tk.messagebox.showerror("Error", f"Error analyzing data for SID {sid}: {e}")

        progress_label.config(text="All Done! Analysis Complete 🥳")
        time.sleep(2)
        progress_window.destroy()


def main():
    # Define folder paths
    data_folder = "./data"  # Path to data folder
    participant_info_file = "./participant_info.csv"  # Path to participant info

    # Verify paths
    if not os.path.isdir(data_folder):
        raise FileNotFoundError(f"Invalid data folder path: {data_folder}")
    if not os.path.isfile(participant_info_file):
        raise FileNotFoundError(f"Invalid participant info file path: {participant_info_file}")

    # Create a DataProcessor instance
    processor = DataProcessor(data_folder, participant_info_file)

    # Start the Tkinter application
    root = tk.Tk()
    visualizer = DataVisualizer(root, processor)
    root.mainloop()


if __name__ == "__main__":
    main()
