#!/usr/bin/env python3
"""Graphical user interface for Media Converter."""

import sys
import threading
from pathlib import Path
from tkinter import (
    BooleanVar,
    Button,
    Checkbutton,
    Entry,
    Frame,
    IntVar,
    Label,
    Scale,
    Scrollbar,
    StringVar,
    Text,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Progressbar

from .cli import convert_file
from .config import LOG_DIR, MAX_WORKERS, TMP_DIR
from .parallel import ParallelEncoder


class MediaConverterGUI:
    """GUI application for Media Converter."""

    def __init__(self, root: Tk):
        """Initialize GUI.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Media Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Variables
        self.input_path = StringVar()
        self.output_path = StringVar()
        self.recursive = BooleanVar(value=False)
        self.keep_original = BooleanVar(value=False)
        self.verbose = BooleanVar(value=True)
        self.parallel = BooleanVar(value=True)
        self.worker_count = IntVar(value=MAX_WORKERS)
        self.is_processing = False

        # Stats
        self.success_count = IntVar(value=0)
        self.fail_count = IntVar(value=0)
        self.total_files = IntVar(value=0)
        self.current_file = IntVar(value=0)

        self._build_ui()

        # Create necessary directories
        LOG_DIR.mkdir(exist_ok=True)
        TMP_DIR.mkdir(exist_ok=True)

    def _build_ui(self) -> None:
        """Build the user interface."""
        # Title
        title_frame = Frame(self.root, pady=10)
        title_frame.pack(fill="x")

        title_label = Label(title_frame, text="Media Converter", font=("Arial", 20, "bold"))
        title_label.pack()

        subtitle_label = Label(
            title_frame, text="Repair and encode legacy video formats", font=("Arial", 10)
        )
        subtitle_label.pack()

        # Input section
        input_frame = Frame(self.root, padx=20, pady=5)
        input_frame.pack(fill="x")

        Label(input_frame, text="Input Path:", width=12, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        Entry(input_frame, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        Button(input_frame, text="Browse File", command=self._browse_file).grid(
            row=0, column=2, padx=2
        )
        Button(input_frame, text="Browse Folder", command=self._browse_folder).grid(
            row=0, column=3, padx=2
        )

        # Output section
        output_frame = Frame(self.root, padx=20, pady=5)
        output_frame.pack(fill="x")

        Label(output_frame, text="Output Path:", width=12, anchor="w").grid(
            row=0, column=0, sticky="w"
        )
        Entry(output_frame, textvariable=self.output_path, width=50).grid(row=0, column=1, padx=5)
        Button(output_frame, text="Browse", command=self._browse_output).grid(
            row=0, column=2, padx=2
        )
        Button(output_frame, text="Clear", command=lambda: self.output_path.set("")).grid(
            row=0, column=3, padx=2
        )

        # Options section
        options_frame = Frame(self.root, padx=20, pady=10)
        options_frame.pack(fill="x")

        Checkbutton(
            options_frame, text="Recursive (process subdirectories)", variable=self.recursive
        ).grid(row=0, column=0, sticky="w", pady=2)

        Checkbutton(options_frame, text="Keep original files", variable=self.keep_original).grid(
            row=1, column=0, sticky="w", pady=2
        )

        Checkbutton(options_frame, text="Verbose output", variable=self.verbose).grid(
            row=2, column=0, sticky="w", pady=2
        )

        Checkbutton(options_frame, text="Enable parallel encoding", variable=self.parallel).grid(
            row=3, column=0, sticky="w", pady=2
        )

        # Worker count slider
        worker_frame = Frame(options_frame)
        worker_frame.grid(row=4, column=0, sticky="w", pady=5)

        Label(worker_frame, text="Worker threads:").pack(side="left", padx=(0, 5))
        worker_scale = Scale(
            worker_frame,
            from_=1,
            to=16,
            orient="horizontal",
            variable=self.worker_count,
            length=200,
        )
        worker_scale.pack(side="left")
        Label(worker_frame, textvariable=self.worker_count).pack(side="left", padx=(5, 0))

        # Control buttons
        button_frame = Frame(self.root, padx=20, pady=10)
        button_frame.pack(fill="x")

        self.start_button = Button(
            button_frame,
            text="Start Conversion",
            command=self._start_conversion,
            bg="green",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
        )
        self.start_button.pack(side="left", padx=5)

        self.stop_button = Button(
            button_frame,
            text="Stop",
            command=self._stop_conversion,
            bg="red",
            fg="white",
            font=("Arial", 12, "bold"),
            padx=20,
            pady=10,
            state="disabled",
        )
        self.stop_button.pack(side="left", padx=5)

        Button(button_frame, text="Clear Log", command=self._clear_log, padx=10, pady=10).pack(
            side="right", padx=5
        )

        # Progress bar
        progress_frame = Frame(self.root, padx=20, pady=5)
        progress_frame.pack(fill="x")

        Label(progress_frame, text="Overall Progress:").pack(anchor="w")
        self.progress = Progressbar(progress_frame, mode="determinate")
        self.progress.pack(fill="x", pady=2)

        # Progress label
        self.progress_label = Label(progress_frame, text="Ready", anchor="w")
        self.progress_label.pack(fill="x")

        # Stats
        stats_frame = Frame(self.root, padx=20, pady=5)
        stats_frame.pack(fill="x")

        Label(stats_frame, text="Successful:").pack(side="left", padx=5)
        Label(
            stats_frame, textvariable=self.success_count, fg="green", font=("Arial", 10, "bold")
        ).pack(side="left")

        Label(stats_frame, text="Failed:").pack(side="left", padx=20)
        Label(stats_frame, textvariable=self.fail_count, fg="red", font=("Arial", 10, "bold")).pack(
            side="left"
        )

        # Log output
        log_frame = Frame(self.root, padx=20, pady=5)
        log_frame.pack(fill="both", expand=True)

        Label(log_frame, text="Log Output:", anchor="w").pack(fill="x")

        log_scroll_frame = Frame(log_frame)
        log_scroll_frame.pack(fill="both", expand=True)

        scrollbar = Scrollbar(log_scroll_frame)
        scrollbar.pack(side="right", fill="y")

        self.log_text = Text(
            log_scroll_frame, wrap="word", yscrollcommand=scrollbar.set, height=15, bg="#f0f0f0"
        )
        self.log_text.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.log_text.yview)

    def _browse_file(self) -> None:
        """Browse for a single video file."""
        filename = filedialog.askopenfilename(
            title="Select Video File",
            filetypes=[("Video Files", "*.avi *.mpg *.mpeg *.wmv *.mov"), ("All Files", "*.*")],
        )
        if filename:
            self.input_path.set(filename)

    def _browse_folder(self) -> None:
        """Browse for a folder."""
        folder = filedialog.askdirectory(title="Select Folder")
        if folder:
            self.input_path.set(folder)

    def _browse_output(self) -> None:
        """Browse for output folder."""
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_path.set(folder)

    def _log(self, message: str) -> None:
        """Add message to log output.

        Args:
            message: Message to log
        """
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.root.update_idletasks()

    def _clear_log(self) -> None:
        """Clear the log output."""
        self.log_text.delete("1.0", "end")
        self.success_count.set(0)
        self.fail_count.set(0)
        self.current_file.set(0)
        self.total_files.set(0)
        self.progress["value"] = 0
        self.progress_label.config(text="Ready")

    def _start_conversion(self) -> None:
        """Start the conversion process."""
        input_path_str = self.input_path.get()

        if not input_path_str:
            messagebox.showerror("Error", "Please select an input file or folder")
            return

        path = Path(input_path_str)
        if not path.exists():
            messagebox.showerror("Error", f"Path does not exist: {path}")
            return

        # Disable start button, enable stop button
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.is_processing = True

        # Reset stats
        self.success_count.set(0)
        self.fail_count.set(0)
        self.current_file.set(0)

        # Start progress bar
        self.progress["mode"] = "determinate"
        self.progress["value"] = 0

        # Run conversion in separate thread
        thread = threading.Thread(target=self._run_conversion, daemon=True)
        thread.start()

    def _run_conversion(self) -> None:
        """Run the conversion process (in separate thread)."""
        try:
            input_path_str = self.input_path.get()
            output_path_str = self.output_path.get()

            path = Path(input_path_str)
            output_dir = Path(output_path_str) if output_path_str else None

            self._log(f"Starting conversion: {path}")
            self._log("=" * 60)

            if path.is_file():
                # Single file
                self.total_files.set(1)
                self.progress["maximum"] = 1
                self.progress_label.config(text=f"Processing: {path.name}")

                success, _repaired, _warning, _error = convert_file(
                    path, output_dir, self.keep_original.get(), self.verbose.get()
                )

                self.current_file.set(1)
                self.progress["value"] = 1

                if success:
                    self.success_count.set(self.success_count.get() + 1)
                    self._log(f"✓ Successfully converted: {path.name}")
                else:
                    self.fail_count.set(self.fail_count.get() + 1)
                    self._log(f"✗ Failed to convert: {path.name}")

            elif path.is_dir():
                # Directory
                extensions = {".avi", ".mpg", ".mpeg", ".wmv", ".mov"}

                if self.recursive.get():
                    files = [p for p in path.rglob("*") if p.suffix.lower() in extensions]
                else:
                    files = [
                        p for p in path.iterdir() if p.is_file() and p.suffix.lower() in extensions
                    ]

                if not files:
                    self._log("No video files found!")
                else:
                    self._log(f"Found {len(files)} video file(s)")
                    self.total_files.set(len(files))
                    self.progress["maximum"] = len(files)

                    # Use parallel encoding if enabled and more than 1 file
                    if self.parallel.get() and len(files) > 1:
                        encoder = ParallelEncoder(
                            max_workers=self.worker_count.get(), show_progress=False
                        )

                        def convert_wrapper(file_path: Path) -> bool:
                            """Wrapper for convert_file."""
                            success, _repaired, _warning, _error = convert_file(
                                file_path, output_dir, self.keep_original.get(), self.verbose.get()
                            )
                            return success

                        def progress_callback(file_path: Path, success: bool) -> None:
                            """Update progress after each file."""
                            current = self.current_file.get() + 1
                            self.current_file.set(current)
                            self.progress["value"] = current
                            self.progress_label.config(
                                text=f"Processed {current}/{len(files)}: {file_path.name}"
                            )

                            if success:
                                self.success_count.set(self.success_count.get() + 1)
                                self._log(f"✓ Completed: {file_path.name}")
                            else:
                                self.fail_count.set(self.fail_count.get() + 1)
                                self._log(f"✗ Failed: {file_path.name}")

                        encoder.process_files(files, convert_wrapper, progress_callback)
                    else:
                        # Sequential processing
                        for idx, file_path in enumerate(files, 1):
                            if not self.is_processing:
                                self._log("Conversion stopped by user")
                                break

                            self._log(f"\nProcessing: {file_path.name}")
                            self.progress_label.config(
                                text=f"Processing {idx}/{len(files)}: {file_path.name}"
                            )

                            success, _repaired, _warning, _error = convert_file(
                                file_path, output_dir, self.keep_original.get(), self.verbose.get()
                            )

                            self.current_file.set(idx)
                            self.progress["value"] = idx

                            if success:
                                self.success_count.set(self.success_count.get() + 1)
                                self._log(f"✓ Completed: {file_path.name}")
                            else:
                                self.fail_count.set(self.fail_count.get() + 1)
                                self._log(f"✗ Failed: {file_path.name}")

            self._log("=" * 60)
            self._log("Conversion complete!")
            self._log(f"Successful: {self.success_count.get()}")
            self._log(f"Failed: {self.fail_count.get()}")
            self.progress_label.config(text="Complete!")

            # Show completion message
            if self.fail_count.get() == 0:
                messagebox.showinfo(
                    "Success",
                    f"All conversions completed successfully!\n\nConverted: {self.success_count.get()} file(s)",
                )
            else:
                messagebox.showwarning(
                    "Completed with Errors",
                    f"Conversion finished with some errors.\n\nSuccessful: {self.success_count.get()}\nFailed: {self.fail_count.get()}",
                )

        except Exception as e:
            self._log(f"ERROR: {e}")
            messagebox.showerror("Error", f"An error occurred:\n{e}")

        finally:
            # Re-enable buttons
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.is_processing = False

    def _stop_conversion(self) -> None:
        """Stop the conversion process."""
        self.is_processing = False
        self._log("\nStopping conversion...")
        self.stop_button.config(state="disabled")


def main() -> int:
    """Main GUI entry point."""
    root = Tk()
    MediaConverterGUI(root)
    root.mainloop()
    return 0


if __name__ == "__main__":
    sys.exit(main())
