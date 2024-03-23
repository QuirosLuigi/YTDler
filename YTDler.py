import tkinter as tk
from pytube import YouTube
from tkinter import messagebox, filedialog
import os
import subprocess
from tkinter.ttk import Combobox


class YTDownloader(tk.Tk):
    """
    A GUI application for downloading YouTube videos.

    Attributes:
        url_input_var (tk.StringVar): Variable to store the YouTube URL input.
        quality_var (tk.StringVar): Variable to store the selected video quality.
        format_var (tk.StringVar): Variable to store the selected video format.
        folder_path_var (tk.StringVar): Variable to store the selected folder path for saving the downloaded video.
    """

    def __init__(self):
        super().__init__()

        self.url_input_var = tk.StringVar(self)
        self.quality_var = tk.StringVar(self)
        self.format_var = tk.StringVar(self)
        self.folder_path_var = tk.StringVar(self)

        self.create_widgets()
        self.url_input_var.trace_add("write", lambda *args: self.update_options())
        self.title("Lui's YT Downloader")

    def create_widgets(self):
        """
        Create the GUI widgets.
        """
        self.configure(bg='#202124')  # Set the background color to dark
        self.geometry('500x400')  # Set the minimum window size
        self.minsize(500, 400)  # Set the minimum window size

        # Create a label for the YouTube URL input
        url_label = tk.Label(self, text="YouTube URL:", bg='#202124', fg='#E8EAED')
        url_label.pack(pady=(20, 10))

        # Create an entry field for the YouTube URL input
        url_entry = tk.Entry(self, textvariable=self.url_input_var, bd=0, fg='#E8EAED', bg='#5F6368')
        url_entry.pack(ipady=10, fill='x', padx=20)

        # Create a label for the video quality selection
        quality_label = tk.Label(self, text="Quality:", bg='#202124', fg='#E8EAED')
        quality_label.pack(pady=(20, 10))


        # Create a dropdown menu for the video quality selection
        self.quality_menu = tk.OptionMenu(self, self.quality_var, '')
        self.quality_menu.config(bg='#5F6368', fg='#E8EAED', bd=0)
        self.quality_menu.pack(ipady=5, fill='x', padx=20)
       

        # Create a label for the video format selection
        format_label = tk.Label(self, text="Format:", bg='#202124', fg='#E8EAED')
        format_label.pack(pady=(20, 10))

        # Create a dropdown menu for the video format selection
        self.format_menu = tk.OptionMenu(self, self.format_var, '')
        self.format_menu.config(bg='#5F6368', fg='#E8EAED', bd=0)  # Adjust the width to match the input box
        self.format_menu.pack(ipady=5, fill='x', padx=20)

        # Create a label for the folder path selection
        self.folder_path_label = tk.Label(self, text="Folder Path: Please provide file directory", bg='#202124', fg='#E8EAED')
        self.folder_path_label.pack(pady=(20, 10))


        # Create a button for browsing the folder path
        browse_button = tk.Button(self, text="Browse", command=self.browse_directory, bg='#3C4043', fg='#E8EAED', bd=0)
        browse_button.pack(ipady=5, fill='x', padx=20)

        # Create a button for starting the video download
        download_button = tk.Button(self, text="Download", command=self.download_video, bg='#4285F4', fg='#E8EAED', bd=0)
        download_button.pack(ipady=5, fill='x', padx=20, pady=(10, 20))

    def update_options(self):
        """
        Update the available options for video format and quality based on the YouTube URL input.
        """
        url = self.url_input_var.get()
        try:
            yt = YouTube(url)
            formats = set(stream.mime_type.split('/')[1] for stream in yt.streams)
            qualities = sorted(set(stream.resolution for stream in yt.streams if stream.resolution), key=lambda x: int(x[:-1]) if x[:-1].isdigit() else 0)
            
            # Check if the format or quality has changed
            if self.format_var.get() not in formats or self.quality_var.get() not in qualities:
                self.format_var.set('')  # clear value
                self.quality_var.set('')  # clear value
                self.format_menu['menu'].delete(0, 'end')
                self.quality_menu['menu'].delete(0, 'end')
            
            for format in formats:
                self.format_menu['menu'].add_command(label=format, command=tk._setit(self.format_var, format))
            for quality in qualities:
                self.quality_menu['menu'].add_command(label=quality, command=tk._setit(self.quality_var, quality))
            
            self.quality_var.trace_add("write", self.update_format_options)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def update_format_options(self, *args):
        """
        Update the available options for video format based on the selected quality.
        """
        selected_quality = self.quality_var.get()
        if selected_quality:
            selected_quality = int(selected_quality[:-1]) if selected_quality[:-1].isdigit() else 0
            self.format_menu['menu'].delete(0, 'end')
            if selected_quality > 1080:
                formats = ['webm']
            else:
                formats = ['mp4', 'webm']
            for format in formats:
                self.format_menu['menu'].add_command(label=format, command=tk._setit(self.format_var, format))
            self.format_var.set('')  # clear value

    def clear_format(self):
        self.format_var.set('')  # clear value

    def download_video(self):
        """
        Download the selected YouTube video with the best available audio and chosen format to the specified folder path.
        """
        url = self.url_input_var.get()
        quality = self.quality_var.get()
        format = self.format_var.get()
        folder_path = self.folder_path_var.get()

        if not folder_path:
            messagebox.showinfo("Error", "Please provide file directory")
            return

        try:
            # Get the YouTube object
            yt = YouTube(url)

            # Filter streams based on format (optional)
            if format:
                streams = yt.streams.filter(file_extension=format)
                # Pick the first stream based on quality if format filtering is used
                video_stream = streams.filter(res=quality).first()
            else:
                # If format is not specified, get the best available progressive stream (progressive streams typically include audio)
                video_stream = yt.streams.filter(progressive=True).order_by('abr').desc().first()

            # Get the best audio stream
            audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()

            # Check if a stream is found
            if video_stream is not None and audio_stream is not None:
                # Download the video and audio streams
                video_stream.download(folder_path, filename='video.' + format)
                audio_stream.download(folder_path, filename='audio.mp4')

                # Combine the video and audio streams using ffmpeg
                video_path = os.path.join(folder_path, 'video.' + format)
                audio_path = os.path.join(folder_path, 'audio.mp4')
                final_path = os.path.join(folder_path, 'final.' + format)

                # Create a command for ffmpeg to combine the video and audio
                command = f"ffmpeg -i {video_path} -i {audio_path} -c copy -map 0:v -map 1:a {final_path}"
                #command = f"ffmpeg -i {video_path} -i {audio_path} -c:v copy -c:a aac {final_path}"

                # Execute the command
                subprocess.call(command, shell=True)

                # Delete the video and audio files after merging
                os.remove(video_path)
                os.remove(audio_path)

                messagebox.showinfo("Success", "Download complete")
            else:
                messagebox.showerror("Error", "No stream matches the selected format and quality")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def browse_directory(self):
        """
        Open a file dialog to browse and select the folder path for saving the downloaded video.
        """
        folder_path = filedialog.askdirectory()
        self.folder_path_var.set(folder_path)
        self.folder_path_label.config(text=f"Folder Path: {folder_path if folder_path else 'Please provide file directory'}")


if __name__ == "__main__":
    app = YTDownloader()
    app.mainloop()