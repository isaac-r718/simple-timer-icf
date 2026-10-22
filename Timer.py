import time
import tkinter as tk
import tkinter.font as tkfont
from pathlib import Path


BACKGROUND = "#1f1f1f"
WHITE = "#ffffff"
RED = "#f44336"
GREEN = "#4caf50"
BLUE = "#2196f3"
ORANGE = "#ff9800"
FONT = "Helvetica"


class TimerState:
    def __init__(self):
        self.initial_seconds = 0
        self.remaining_seconds = 0.0
        self.overtime_seconds = 0.0
        self.overtime_started = False
        self.running = False

    def set_duration(self, seconds):
        self.initial_seconds = max(0, int(seconds))
        self.remaining_seconds = float(self.initial_seconds)

    def start(self):
        if self.remaining_seconds <= 0:
            self.overtime_started = True
        self.running = True

    def advance(self, elapsed):
        if not self.running or elapsed <= 0:
            return

        elapsed = float(elapsed)
        overtime_was_started = self.overtime_started
        time_after_countdown = elapsed
        if self.remaining_seconds > 0:
            countdown = min(self.remaining_seconds, elapsed)
            self.remaining_seconds -= countdown
            time_after_countdown -= countdown

        if self.remaining_seconds <= 0:
            self.remaining_seconds = 0.0
            if not self.overtime_started:
                self.overtime_started = True
                self.overtime_seconds += time_after_countdown

        if overtime_was_started:
            self.overtime_seconds += elapsed

    def adjust(self, seconds):
        self.remaining_seconds = max(0.0, self.remaining_seconds + seconds)
        if self.running and self.remaining_seconds == 0:
            self.overtime_started = True

    def reset(self):
        self.remaining_seconds = float(self.initial_seconds)
        self.overtime_seconds = 0.0
        self.overtime_started = False
        self.running = False


class TimerApp:
    def __init__(self, root):
        self.root = root
        self.state = TimerState()
        self.current_screen = "welcome"
        self.fullscreen = False
        self.last_tick = None
        self.tick_job = None
        self.clock_job = None
        self.next_blink = 0.0
        self.blink_visible = True

        self.main_timer_font = tkfont.Font(
            root=self.root, family=FONT, size=96, weight="bold"
        )
        self.execution_timer_font = tkfont.Font(
            root=self.root, family=FONT, size=120, weight="bold"
        )
        self.overtime_font = tkfont.Font(
            root=self.root, family=FONT, size=48, weight="bold"
        )
        self.heading_font = tkfont.Font(
            root=self.root, family=FONT, size=32, weight="bold"
        )
        self.button_font = tkfont.Font(
            root=self.root, family=FONT, size=16, weight="bold"
        )
        self.small_font = tkfont.Font(root=self.root, family=FONT, size=12)

        self.root.title("ICF Timer")
        self.root.configure(bg=BACKGROUND)
        self.root.geometry("1080x720")
        self.root.minsize(760, 520)
        self._center_window()
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.leave_fullscreen)
        self.root.bind("<space>", self.toggle_from_keyboard)
        self.root.bind("<Return>", self.open_main_from_keyboard)
        self.root.bind("<Configure>", self._resize_ui)

        self._build_welcome_screen()
        self._build_main_screen()
        self._build_execution_screen()
        self.show_screen("welcome")
        self.root.update_idletasks()
        self._resize_ui()
        self._update_clock()

    def _center_window(self):
        self.root.update_idletasks()
        width, height = 1080, 720
        x = max(0, (self.root.winfo_screenwidth() - width) // 2)
        y = max(0, (self.root.winfo_screenheight() - height) // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def _make_screen(self):
        screen = tk.Frame(self.root, bg=BACKGROUND)
        screen.place(relx=0, rely=0, relwidth=1, relheight=1)
        return screen

    def _make_button(self, parent, text, command, color=BLUE, font_size=16):
        return tk.Button(
            parent,
            text=text,
            command=command,
            bg=color,
            fg=WHITE,
            activebackground=color,
            activeforeground=WHITE,
            disabledforeground="#aaaaaa",
            font=self.button_font,
            relief="flat",
            borderwidth=0,
            padx=18,
            pady=12,
            cursor="hand2",
        )

    def _build_welcome_screen(self):
        self.welcome_screen = self._make_screen()
        content = tk.Frame(self.welcome_screen, bg=BACKGROUND)
        content.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = Path(__file__).resolve().parent / "assets" / "ICF.png"
        if logo_path.is_file():
            self.logo_image = tk.PhotoImage(file=str(logo_path)).subsample(3, 3)
            logo_button = tk.Button(
                content,
                image=self.logo_image,
                command=self.open_main,
                bg=BACKGROUND,
                activebackground=BACKGROUND,
                borderwidth=0,
                cursor="hand2",
            )
        else:
            logo_button = tk.Button(
                content,
                text="ICF",
                command=self.open_main,
                bg=BACKGROUND,
                fg=WHITE,
                activebackground=BACKGROUND,
                activeforeground=WHITE,
                font=(FONT, 72, "bold"),
                borderwidth=0,
                cursor="hand2",
            )
        logo_button.pack()
        tk.Label(
            content,
            text="Timer ICF",
            bg=BACKGROUND,
            fg=WHITE,
            font=(FONT, 36, "bold"),
        ).pack(pady=(18, 8))
        tk.Label(
            content,
            text="Haz clic en el logo para comenzar",
            bg=BACKGROUND,
            fg="#bdbdbd",
            font=(FONT, 15),
        ).pack()

    def _build_main_screen(self):
        self.main_screen = self._make_screen()
        tk.Label(
            self.main_screen,
            text="Timer ICF",
            bg=BACKGROUND,
            fg=WHITE,
            font=self.heading_font,
        ).pack(pady=(16, 0))
        tk.Label(
            self.main_screen,
            text="Define la duración",
            bg=BACKGROUND,
            fg="#bdbdbd",
            font=self.small_font,
        ).pack(pady=(0, 4))

        self.main_time_label = tk.Label(
            self.main_screen,
            text="00:00:00",
            bg=BACKGROUND,
            fg=WHITE,
            font=self.main_timer_font,
        )
        self.main_time_label.pack(pady=(0, 4))

        controls = tk.Frame(self.main_screen, bg=BACKGROUND)
        controls.pack()
        adjustments = (
            ("+1 hora", 3600, BLUE),
            ("+10 min", 600, ORANGE),
            ("+1 min", 60, GREEN),
            ("-1 hora", -3600, BLUE),
            ("-10 min", -600, ORANGE),
            ("-1 min", -60, GREEN),
        )
        for index, (label, seconds, color) in enumerate(adjustments):
            button = self._make_button(
                controls,
                label,
                lambda amount=seconds: self.adjust_duration(amount),
                color,
            )
            button.grid(row=index // 3, column=index % 3, padx=8, pady=5, sticky="ew")
        for column in range(3):
            controls.grid_columnconfigure(column, weight=1)

        self.start_button = self._make_button(
            self.main_screen, "Iniciar timer", self.start_timer, GREEN, 20
        )
        self.start_button.pack(pady=12)
        tk.Label(
            self.main_screen,
            text="F11: pantalla completa",
            bg=BACKGROUND,
            fg="#888888",
            font=self.small_font,
        ).pack(side="bottom", pady=12)

    def _build_execution_screen(self):
        self.execution_screen = self._make_screen()
        self.execution_screen.grid_rowconfigure(1, weight=1)
        self.execution_screen.grid_columnconfigure(0, weight=1)
        header = tk.Frame(self.execution_screen, bg=BACKGROUND)
        header.grid(row=0, column=0, sticky="ew", padx=36, pady=(18, 0))
        tk.Label(
            header,
            text="Timer ICF",
            bg=BACKGROUND,
            fg=WHITE,
            font=self.heading_font,
        ).pack(side="left")
        self.clock_label = tk.Label(
            header,
            text="",
            bg=BACKGROUND,
            fg="#bdbdbd",
            font=self.small_font,
        )
        self.clock_label.pack(side="right")

        center = tk.Frame(self.execution_screen, bg=BACKGROUND)
        center.grid(row=1, column=0, sticky="nsew")
        self.execution_time_label = tk.Label(
            center,
            text="00:00:00",
            bg=BACKGROUND,
            fg=WHITE,
            font=self.execution_timer_font,
        )
        self.execution_time_label.place(
            relx=0.5, rely=0.5, anchor="center"
        )
        self.overtime_label = tk.Label(
            center,
            text="",
            bg=BACKGROUND,
            fg=WHITE,
            font=self.overtime_font,
        )
        self.overtime_label.place(relx=0.5, rely=0.2, anchor="center")

        footer = tk.Frame(self.execution_screen, bg=BACKGROUND)
        footer.grid(row=2, column=0, sticky="ew", padx=32, pady=(0, 18))
        adjustments = tk.Frame(footer, bg=BACKGROUND)
        adjustments.pack(pady=(0, 12))
        self._make_button(
            adjustments, "+1 min", lambda: self.adjust_running_timer(60), GREEN
        ).grid(row=0, column=0, padx=7, pady=4)
        self._make_button(
            adjustments, "-1 min", lambda: self.adjust_running_timer(-60), ORANGE
        ).grid(row=1, column=0, padx=7, pady=4)

        actions = tk.Frame(footer, bg=BACKGROUND)
        actions.pack()
        self.pause_button = self._make_button(
            actions, "Pausar", self.toggle_pause, BLUE, 17
        )
        self.pause_button.grid(row=0, column=0, padx=8)
        self._make_button(
            actions, "Reiniciar", self.reset_timer, ORANGE, 17
        ).grid(row=0, column=1, padx=8)
        self._make_button(
            actions, "Finalizar", self.finish_timer, RED, 17
        ).grid(row=0, column=2, padx=8)
        tk.Label(
            footer,
            text="Espacio: pausar o continuar  |  F11: pantalla completa",
            bg=BACKGROUND,
            fg="#888888",
            font=self.small_font,
        ).pack(pady=(12, 0))

    def _resize_ui(self, _event=None):
        width = max(1, self.root.winfo_width())
        height = max(1, self.root.winfo_height())
        main_size = max(32, min(240, int(min(width * 0.105, height * 0.18))))
        execution_size = max(
            32, min(240, int(min(width * 0.12, height * 0.2)))
        )
        self.main_timer_font.configure(size=main_size)
        self.execution_timer_font.configure(size=execution_size)
        self.overtime_font.configure(size=max(20, int(execution_size * 0.48)))
        self.heading_font.configure(size=max(18, min(48, int(height * 0.055))))
        self.button_font.configure(size=max(12, min(26, int(height * 0.025))))
        self.small_font.configure(size=max(10, min(18, int(height * 0.018))))

    @staticmethod
    def format_time(seconds):
        total = max(0, int(seconds))
        hours, remainder = divmod(total, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def show_screen(self, name):
        self.current_screen = name
        {"welcome": self.welcome_screen,
         "main": self.main_screen,
         "execution": self.execution_screen}[name].lift()

    def open_main(self):
        self._refresh_main_time()
        self.show_screen("main")

    def start_timer(self):
        self.state.remaining_seconds = float(self.state.initial_seconds)
        self.state.overtime_seconds = 0.0
        self.state.overtime_started = False
        self.state.start()
        self.last_tick = time.monotonic()
        self.next_blink = self.last_tick
        self.blink_visible = True
        self.pause_button.configure(text="Pausar")
        self.show_screen("execution")
        self._refresh_execution()
        self._schedule_tick()

    def _schedule_tick(self):
        if self.state.running and self.tick_job is None:
            self.tick_job = self.root.after(100, self._tick)

    def _advance_to_now(self):
        now = time.monotonic()
        if self.state.running and self.last_tick is not None:
            self.state.advance(now - self.last_tick)
            self.last_tick = now
        return now

    def _tick(self):
        self.tick_job = None
        now = self._advance_to_now()
        if now >= self.next_blink:
            self.blink_visible = not self.blink_visible
            self.next_blink = now + 0.5
        self._refresh_execution()
        self._schedule_tick()

    def adjust_duration(self, seconds):
        self.state.set_duration(self.state.initial_seconds + seconds)
        self._refresh_main_time()

    def adjust_running_timer(self, seconds):
        self._advance_to_now()
        self.state.adjust(seconds)
        self._refresh_execution()

    def toggle_pause(self):
        if self.state.running:
            self._advance_to_now()
            self.state.running = False
            if self.tick_job is not None:
                self.root.after_cancel(self.tick_job)
                self.tick_job = None
            self.pause_button.configure(text="Continuar")
        else:
            self.state.start()
            self.last_tick = time.monotonic()
            self.next_blink = self.last_tick
            self.pause_button.configure(text="Pausar")
            self._schedule_tick()
        self._refresh_execution()

    def reset_timer(self):
        if self.tick_job is not None:
            self.root.after_cancel(self.tick_job)
            self.tick_job = None
        self.state.reset()
        self.pause_button.configure(text="Continuar")
        self.blink_visible = True
        self._refresh_execution()

    def finish_timer(self):
        if self.tick_job is not None:
            self.root.after_cancel(self.tick_job)
            self.tick_job = None
        self.state.running = False
        self._refresh_main_time()
        self.show_screen("main")

    def _refresh_main_time(self):
        self.main_time_label.configure(
            text=self.format_time(self.state.initial_seconds)
        )

    def _refresh_execution(self):
        if self.state.overtime_started:
            blink_color = RED if not self.state.running or self.blink_visible else WHITE
            self.overtime_label.configure(
                text=f"+{self.format_time(self.state.overtime_seconds)}",
                fg=blink_color,
            )
            self.execution_time_label.configure(
                text=self.format_time(self.state.remaining_seconds),
                fg=blink_color,
            )
        else:
            self.execution_time_label.configure(
                text=self.format_time(self.state.remaining_seconds),
                fg=WHITE,
            )
            self.overtime_label.configure(text="")

    def _update_clock(self):
        self.clock_label.configure(text=time.strftime("%H:%M:%S"))
        self.clock_job = self.root.after(1000, self._update_clock)

    def toggle_fullscreen(self, _event=None):
        self.fullscreen = not self.fullscreen
        self.root.attributes("-fullscreen", self.fullscreen)
        return "break"

    def leave_fullscreen(self, _event=None):
        if self.fullscreen:
            self.fullscreen = False
            self.root.attributes("-fullscreen", False)
            return "break"
        return None

    def toggle_from_keyboard(self, _event=None):
        if self.current_screen == "execution":
            self.toggle_pause()
            return "break"
        return None

    def open_main_from_keyboard(self, _event=None):
        if self.current_screen == "welcome":
            self.open_main()
            return "break"
        return None


def main():
    root = tk.Tk()
    TimerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
