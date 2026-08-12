import os
import sys
import json
import re
import datetime
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk

# Windows registry for auto-start
try:
    import winreg
except ImportError:
    winreg = None

# DPI Awareness for crisp UI on Windows
try:
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    pass

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DEFAULT_CWD = r"C:\Users\aceyo"
BRAIN_DIR = r"C:\Users\aceyo\.gemini\antigravity-cli\brain"
APP_TITLE = "Antigravity CLI Launcher"
REG_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
REG_APP_NAME = "AntigravityLauncher"

class SessionParser:
    @staticmethod
    def get_all_sessions(brain_dir=BRAIN_DIR):
        sessions = []
        if not os.path.exists(brain_dir):
            return sessions

        try:
            folders = os.listdir(brain_dir)
        except Exception:
            return sessions

        for folder in folders:
            folder_path = os.path.join(brain_dir, folder)
            if not os.path.isdir(folder_path):
                continue
            
            t_file = os.path.join(folder_path, '.system_generated', 'logs', 'transcript.jsonl')
            mtime = os.path.getmtime(folder_path)
            if os.path.exists(t_file):
                mtime = os.path.getmtime(t_file)
            
            mtime_dt = datetime.datetime.fromtimestamp(mtime)
            mtime_str = mtime_dt.strftime('%Y-%m-%d %H:%M:%S')

            title = "(대화 기록 없음)"
            msg_count = 0
            user_prompts = []

            if os.path.exists(t_file):
                try:
                    with open(t_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            msg_count += 1
                            try:
                                data = json.loads(line)
                            except Exception:
                                continue

                            if data.get('type') == 'USER_INPUT':
                                raw_content = data.get('content', '')
                                match = re.search(r'<USER_REQUEST>\s*(.*?)\s*</USER_REQUEST>', raw_content, re.DOTALL)
                                if match:
                                    req_text = match.group(1).strip()
                                else:
                                    req_text = raw_content.strip()
                                
                                # Clean line breaks for single line title preview
                                req_single = ' '.join(req_text.splitlines())
                                if req_single:
                                    user_prompts.append(req_text)
                                    if title == "(대화 기록 없음)":
                                        title = req_single
                except Exception as e:
                    title = f"로그 읽기 오류: {e}"

            sessions.append({
                'id': folder,
                'title': title[:120] if title else "새 세션",
                'mtime': mtime,
                'mtime_str': mtime_str,
                'msg_count': msg_count,
                'prompt_count': len(user_prompts),
                'user_prompts': user_prompts,
                'folder_path': folder_path
            })

        sessions.sort(key=lambda x: x['mtime'], reverse=True)
        return sessions

class LauncherApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(APP_TITLE)
        self.geometry("1024 x 700")
        self.minsize(850, 600)

        # Set window icon if available
        self.icon_png_path = os.path.join(os.path.dirname(__file__), "icon.png")
        self.icon_ico_path = os.path.join(os.path.dirname(__file__), "icon.ico")
        if os.path.exists(self.icon_ico_path):
            try:
                self.iconbitmap(self.icon_ico_path)
            except Exception:
                pass

        # App State
        self.current_cwd = DEFAULT_CWD if os.path.exists(DEFAULT_CWD) else os.path.expanduser("~")
        self.sessions = []
        self.filtered_sessions = []
        self.use_wt = tk.BooleanVar(value=False)
        self.skip_perm = tk.BooleanVar(value=True)
        self.auto_start = tk.BooleanVar(value=self.check_auto_start_status())

        self.setup_ui()
        self.load_sessions()

    def check_auto_start_status(self):
        if not winreg:
            return False
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_READ)
            val, _ = winreg.QueryValueEx(key, REG_APP_NAME)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def toggle_auto_start(self):
        if not winreg:
            messagebox.showerror("오류", "Windows 레지스트리 모듈을 찾을 수 없습니다.")
            return

        exe_path = self.get_app_executable_cmd()
        enable = self.auto_start.get()

        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, REG_RUN_KEY, 0, winreg.KEY_ALL_ACCESS)
            if enable:
                winreg.SetValueEx(key, REG_APP_NAME, 0, winreg.REG_SZ, exe_path)
                messagebox.showinfo("설정 완료", "Windows 부팅 시 자동 실행 설정이 등록되었습니다.")
            else:
                try:
                    winreg.DeleteValue(key, REG_APP_NAME)
                    messagebox.showinfo("설정 완료", "Windows 부팅 시 자동 실행이 해제되었습니다.")
                except FileNotFoundError:
                    pass
            winreg.CloseKey(key)
        except Exception as e:
            messagebox.showerror("오류", f"자동 실행 설정 변경 실패: {e}")

    def get_app_executable_cmd(self):
        if getattr(sys, 'frozen', False):
            return f'"{sys.executable}"'
        else:
            return f'"{sys.executable}" "{os.path.abspath(__file__)}"'

    def setup_ui(self):
        # Grid Configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ---------------- TOP HEADER ----------------
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1E1E2E")
        header_frame.grid(row=0, column=0, padx=15, pady=(15, 10), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        # Logo / Icon
        logo_label = ctk.CTkLabel(
            header_frame, 
            text="⚡ Antigravity CLI Launcher", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color="#89B4FA"
        )
        logo_label.grid(row=0, column=0, padx=15, pady=12, sticky="w")

        # Subtitle / Status
        status_label = ctk.CTkLabel(
            header_frame, 
            text="PowerShell 기반 자동 실행 & 과거 세션 복원 관리자", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color="#A6ADC8"
        )
        status_label.grid(row=0, column=1, padx=10, pady=12, sticky="w")

        # Header Buttons (Refresh & Appearance)
        btn_refresh = ctk.CTkButton(
            header_frame, 
            text="🔄 목록 새로고침", 
            width=120, 
            fg_color="#313244", 
            hover_color="#45475A",
            command=self.load_sessions
        )
        btn_refresh.grid(row=0, column=2, padx=(5, 15), pady=12, sticky="e")

        # ---------------- QUICK CONTROLS ----------------
        control_frame = ctk.CTkFrame(self, corner_radius=10)
        control_frame.grid(row=1, column=0, padx=15, pady=5, sticky="ew")
        control_frame.grid_columnconfigure(1, weight=1)

        # Row 0: Working Directory
        lbl_dir = ctk.CTkLabel(control_frame, text="작업 디렉토리:", font=ctk.CTkFont(weight="bold"))
        lbl_dir.grid(row=0, column=0, padx=(15, 5), pady=10, sticky="w")

        self.entry_cwd = ctk.CTkEntry(control_frame, font=ctk.CTkFont(family="Consolas", size=13))
        self.entry_cwd.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.entry_cwd.insert(0, self.current_cwd)

        btn_browse = ctk.CTkButton(control_frame, text="📁 찾아보기", width=90, fg_color="#45475A", command=self.browse_dir)
        btn_browse.grid(row=0, column=2, padx=(5, 15), pady=10)

        # Row 1: Action Buttons & Options
        action_box = ctk.CTkFrame(control_frame, fg_color="transparent")
        action_box.grid(row=1, column=0, columnspan=3, padx=15, pady=(0, 10), sticky="ew")
        action_box.grid_columnconfigure(3, weight=1)

        btn_new_session = ctk.CTkButton(
            action_box, 
            text="🚀 새 세션 바로 실행 (agy)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#A6E3A1", 
            hover_color="#94E2D5", 
            text_color="#11111B",
            height=38,
            command=lambda: self.launch_agy()
        )
        btn_new_session.grid(row=0, column=0, padx=(0, 10), pady=5)

        btn_cont_session = ctk.CTkButton(
            action_box, 
            text="⏩ 최근 세션 이어하기 (agy -c)", 
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#89B4FA", 
            hover_color="#B4BEFE", 
            text_color="#11111B",
            height=38,
            command=lambda: self.launch_agy(continue_latest=True)
        )
        btn_cont_session.grid(row=0, column=1, padx=5, pady=5)

        chk_skip_perm = ctk.CTkCheckBox(
            action_box, 
            text="🤖 AUTO 모드 (권한 자동 승인 --dangerously-skip-permissions)", 
            variable=self.skip_perm,
            font=ctk.CTkFont(size=12, weight="bold")
        )
        chk_skip_perm.grid(row=0, column=2, padx=15, pady=5)

        # ---------------- SESSION LIST AREA ----------------
        list_container = ctk.CTkFrame(self, corner_radius=10)
        list_container.grid(row=2, column=0, padx=15, pady=10, sticky="nsew")
        list_container.grid_columnconfigure(0, weight=1)
        list_container.grid_rowconfigure(1, weight=1)

        # Search Bar & Session Count
        search_frame = ctk.CTkFrame(list_container, fg_color="transparent")
        search_frame.grid(row=0, column=0, padx=15, pady=(12, 5), sticky="ew")
        search_frame.grid_columnconfigure(0, weight=1)

        self.entry_search = ctk.CTkEntry(
            search_frame, 
            placeholder_text="🔍 과거 세션 제목, ID, 질의 내용 실시간 검색...", 
            font=ctk.CTkFont(size=13)
        )
        self.entry_search.grid(row=0, column=0, padx=(0, 10), sticky="ew")
        self.entry_search.bind("<KeyRelease>", self.on_search)

        self.lbl_count = ctk.CTkLabel(search_frame, text="0개 세션 중 0개 표시", font=ctk.CTkFont(size=12), text_color="#A6ADC8")
        self.lbl_count.grid(row=0, column=1, padx=5, sticky="e")

        # Scrollable Frame for Sessions
        self.scroll_sessions = ctk.CTkScrollableFrame(list_container, fg_color="transparent")
        self.scroll_sessions.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="nsew")
        self.scroll_sessions.grid_columnconfigure(0, weight=1)

        # ---------------- BOTTOM FOOTER ----------------
        footer_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#181825")
        footer_frame.grid(row=3, column=0, padx=15, pady=(0, 15), sticky="ew")
        footer_frame.grid_columnconfigure(3, weight=1)

        chk_autostart = ctk.CTkCheckBox(
            footer_frame, 
            text="🚀 Windows 부팅 시 자동 실행", 
            variable=self.auto_start,
            command=self.toggle_auto_start,
            font=ctk.CTkFont(size=12)
        )
        chk_autostart.grid(row=0, column=0, padx=15, pady=10)

        btn_desktop_lnk = ctk.CTkButton(
            footer_frame, 
            text="📌 바탕화면 바로가기 생성", 
            width=160, 
            fg_color="#313244", 
            hover_color="#45475A",
            command=self.create_desktop_shortcut
        )
        btn_desktop_lnk.grid(row=0, column=1, padx=5, pady=10)

        btn_start_menu = ctk.CTkButton(
            footer_frame, 
            text="⭐ 시작 메뉴 바로가기 생성", 
            width=160, 
            fg_color="#313244", 
            hover_color="#45475A",
            command=self.create_start_menu_shortcut
        )
        btn_start_menu.grid(row=0, column=2, padx=5, pady=10)

        lbl_path_info = ctk.CTkLabel(
            footer_frame, 
            text=f"Brain 경로: {BRAIN_DIR}", 
            font=ctk.CTkFont(family="Consolas", size=11), 
            text_color="#6C7086"
        )
        lbl_path_info.grid(row=0, column=3, padx=15, pady=10, sticky="e")

    def browse_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.entry_cwd.get())
        if chosen:
            self.entry_cwd.delete(0, tk.END)
            self.entry_cwd.insert(0, chosen)
            self.current_cwd = chosen

    def load_sessions(self):
        self.sessions = SessionParser.get_all_sessions()
        self.render_sessions(self.sessions)

    def on_search(self, event=None):
        query = self.entry_search.get().strip().lower()
        if not query:
            self.render_sessions(self.sessions)
            return

        filtered = []
        for s in self.sessions:
            if query in s['id'].lower() or query in s['title'].lower() or any(query in p.lower() for p in s['user_prompts']):
                filtered.append(s)

        self.render_sessions(filtered)

    def render_sessions(self, session_list):
        # Clear previous widgets
        for widget in self.scroll_sessions.winfo_children():
            widget.destroy()

        total_cnt = len(self.sessions)
        shown_cnt = len(session_list)
        self.lbl_count.configure(text=f"총 {total_cnt}개 세션 중 {shown_cnt}개 표시")

        if not session_list:
            lbl_empty = ctk.CTkLabel(
                self.scroll_sessions, 
                text="검색 결과 또는 저장된 과거 세션이 없습니다.", 
                font=ctk.CTkFont(size=14),
                text_color="#6C7086"
            )
            lbl_empty.pack(pady=40)
            return

        for idx, s in enumerate(session_list):
            card = ctk.CTkFrame(self.scroll_sessions, corner_radius=8, fg_color="#1E1E2E" if idx % 2 == 0 else "#181825")
            card.pack(fill="x", padx=5, pady=4)
            card.grid_columnconfigure(0, weight=1)

            # Top Title
            title_lbl = ctk.CTkLabel(
                card, 
                text=s['title'], 
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
                anchor="w",
                text_color="#F5E0DC"
            )
            title_lbl.grid(row=0, column=0, padx=12, pady=(10, 2), sticky="ew")

            # Meta Info (Date, ID, Msg count)
            meta_str = f"🕒 {s['mtime_str']}  |  🆔 {s['id']}  |  💬 프롬프트 {s['prompt_count']}회 ({s['msg_count']}개 로그)"
            meta_lbl = ctk.CTkLabel(
                card, 
                text=meta_str, 
                font=ctk.CTkFont(family="Consolas", size=11),
                anchor="w",
                text_color="#9399B2"
            )
            meta_lbl.grid(row=1, column=0, padx=12, pady=(0, 10), sticky="ew")

            # Buttons Container
            btn_frame = ctk.CTkFrame(card, fg_color="transparent")
            btn_frame.grid(row=0, column=1, rowspan=2, padx=10, pady=8, sticky="e")

            btn_run = ctk.CTkButton(
                btn_frame, 
                text="▶️ 이 세션 이어하기", 
                width=135,
                height=32,
                fg_color="#F5C2E7", 
                hover_color="#CBA6F7", 
                text_color="#11111B",
                font=ctk.CTkFont(weight="bold"),
                command=lambda sid=s['id']: self.launch_agy(conversation_id=sid)
            )
            btn_run.pack(side="left", padx=4)

            btn_copy = ctk.CTkButton(
                btn_frame, 
                text="📋 ID 복사", 
                width=75,
                height=32,
                fg_color="#313244",
                hover_color="#45475A",
                command=lambda sid=s['id']: self.copy_to_clipboard(sid)
            )
            btn_copy.pack(side="left", padx=4)

            btn_folder = ctk.CTkButton(
                btn_frame, 
                text="📁 로그 폴더", 
                width=85,
                height=32,
                fg_color="#313244",
                hover_color="#45475A",
                command=lambda fpath=s['folder_path']: os.startfile(fpath)
            )
            btn_folder.pack(side="left", padx=4)

            btn_detail = ctk.CTkButton(
                btn_frame, 
                text="🔍 대화 보기", 
                width=85,
                height=32,
                fg_color="#313244",
                hover_color="#45475A",
                command=lambda sess=s: self.show_session_detail(sess)
            )
            btn_detail.pack(side="left", padx=4)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("복사 완료", f"클립보드에 복사되었습니다:\n{text}")

    def show_session_detail(self, session):
        detail_win = ctk.CTkToplevel(self)
        detail_win.title(f"세션 상세 정보 - {session['id'][:8]}")
        detail_win.geometry("750 x 550")
        detail_win.transient(self)
        detail_win.grab_set()

        lbl_header = ctk.CTkLabel(
            detail_win, 
            text=f"세션 ID: {session['id']}", 
            font=ctk.CTkFont(family="Consolas", size=14, weight="bold")
        )
        lbl_header.pack(anchor="w", padx=20, pady=(15, 5))

        lbl_date = ctk.CTkLabel(detail_win, text=f"마지막 수정 시각: {session['mtime_str']}", text_color="#A6ADC8")
        lbl_date.pack(anchor="w", padx=20, pady=(0, 10))

        tb = ctk.CTkTextbox(detail_win, font=ctk.CTkFont(family="Consolas", size=12))
        tb.pack(fill="both", expand=True, padx=20, pady=10)

        tb.insert("1.0", f"=== 첫번째 제목 / 요청 ===\n{session['title']}\n\n")
        tb.insert("end", f"=== 질문/프롬프트 기록 (총 {len(session['user_prompts'])}회) ===\n\n")

        for idx, prompt in enumerate(session['user_prompts'], 1):
            tb.insert("end", f"[{idx}] {prompt}\n" + "-"*60 + "\n\n")

        tb.configure(state="disabled")

        btn_close = ctk.CTkButton(detail_win, text="닫기", width=100, command=detail_win.destroy)
        btn_close.pack(pady=12)

    def launch_agy(self, conversation_id=None, continue_latest=False):
        cwd = self.entry_cwd.get().strip()
        if not os.path.exists(cwd):
            messagebox.showerror("오류", f"작업 디렉토리가 존재하지 않습니다:\n{cwd}")
            return

        cmd_parts = ["agy"]

        if conversation_id:
            cmd_parts.extend(["--conversation", conversation_id])
        elif continue_latest:
            cmd_parts.append("-c")

        if self.skip_perm.get():
            cmd_parts.append("--dangerously-skip-permissions")

        full_cmd_str = " ".join(cmd_parts)

        # Build PowerShell invocation
        # PowerShell command will change directory then run agy
        ps_command = f"Set-Location '{cwd}'; Write-Host '🚀 Antigravity CLI 시작 중... ({full_cmd_str})' -ForegroundColor Cyan; {full_cmd_str}"

        try:
            # Creation flags to launch PowerShell in a separate external console window
            subprocess.Popen(
                ["powershell.exe", "-NoExit", "-Command", ps_command],
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                cwd=cwd
            )
        except Exception as e:
            messagebox.showerror("실행 실패", f"PowerShell 실행 도중 오류가 발생했습니다:\n{e}")

    def create_desktop_shortcut(self):
        self.create_lnk_shortcut(os.path.join(os.path.expanduser("~"), "Desktop"))

    def create_start_menu_shortcut(self):
        start_menu = os.path.join(os.environ.get("APPDATA", ""), r"Microsoft\Windows\Start Menu\Programs")
        self.create_lnk_shortcut(start_menu)

    def create_lnk_shortcut(self, target_folder):
        if not os.path.exists(target_folder):
            messagebox.showerror("오류", "대상 경로를 찾을 수 없습니다.")
            return

        lnk_path = os.path.join(target_folder, "Antigravity Launcher.lnk")

        try:
            # Use PowerShell WScript.Shell to create .lnk shortcut without extra pip dependencies
            target_exe = sys.executable
            if getattr(sys, 'frozen', False):
                target_cmd = f'$shortcut.TargetPath = "{sys.executable}"'
                icon_cmd = f'$shortcut.IconLocation = "{sys.executable}"'
            else:
                target_cmd = f'$shortcut.TargetPath = "{sys.executable}"; $shortcut.Arguments = `"{os.path.abspath(__file__)}`"'
                icon_path = self.icon_ico_path if os.path.exists(self.icon_ico_path) else sys.executable
                icon_cmd = f'$shortcut.IconLocation = "{icon_path}"'

            ps_script = f'''
            $ws = New-Object -ComObject WScript.Shell
            $shortcut = $ws.CreateShortcut("{lnk_path}")
            {target_cmd}
            $shortcut.WorkingDirectory = "{os.path.dirname(os.path.abspath(__file__))}"
            {icon_cmd}
            $shortcut.Description = "Antigravity CLI Session Launcher"
            $shortcut.Save()
            '''

            subprocess.run(["powershell", "-Command", ps_script], check=True, capture_output=True)
            messagebox.showinfo("바로가기 생성 완료", f"바로가기가 정상적으로 생성되었습니다:\n{lnk_path}")
        except Exception as e:
            messagebox.showerror("오류", f"바로가기 생성 실패: {e}")

if __name__ == "__main__":
    app = LauncherApp()
    app.mainloop()
