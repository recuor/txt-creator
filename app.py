import os
import re
import json
import tkinter as tk
from tkinter import filedialog, messagebox


class TextFileCreatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("텍스트 파일 일괄 생성기")
        self.root.geometry("520x350")
        self.root.resizable(False, False)

        # 기본 저장 폴더: Documents
        self.default_dir = os.path.join(
            os.path.expanduser("~"),
            "Documents"
        )

        # 설정 파일 저장 폴더
        self.settings_dir = os.path.join(
            os.getenv("APPDATA", os.path.expanduser("~")),
            "TextFileCreator"
        )

        self.settings_file = os.path.join(
            self.settings_dir,
            "settings.json"
        )

        # 이전에 사용한 저장 폴더 불러오기
        self.save_dir = self.load_settings()

        self.setup_ui()

    def load_settings(self):
        """이전에 저장한 폴더 경로를 불러옵니다."""

        try:
            if os.path.exists(self.settings_file):
                with open(
                    self.settings_file,
                    "r",
                    encoding="utf-8"
                ) as file:
                    settings = json.load(file)

                saved_dir = settings.get("save_dir", "")

                if saved_dir:
                    return saved_dir

        except Exception:
            pass

        return self.default_dir

    def save_settings(self):
        """현재 저장 폴더를 저장합니다."""

        try:
            os.makedirs(
                self.settings_dir,
                exist_ok=True
            )

            settings = {
                "save_dir": self.save_dir
            }

            with open(
                self.settings_file,
                "w",
                encoding="utf-8"
            ) as file:
                json.dump(
                    settings,
                    file,
                    ensure_ascii=False,
                    indent=4
                )

        except Exception:
            pass

    def setup_ui(self):
        # 저장 폴더 영역
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(
            fill="x",
            padx=15,
            pady=(15, 5)
        )

        tk.Label(
            dir_frame,
            text="저장 디렉토리:",
            font=("맑은 고딕", 9, "bold")
        ).pack(anchor="w")

        dir_sub_frame = tk.Frame(dir_frame)
        dir_sub_frame.pack(
            fill="x",
            pady=5
        )

        self.dir_entry = tk.Entry(
            dir_sub_frame,
            font=("맑은 고딕", 9)
        )

        self.dir_entry.insert(
            0,
            self.save_dir
        )

        self.dir_entry.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 5)
        )

        btn_browse = tk.Button(
            dir_sub_frame,
            text="폴더 찾기",
            command=self.browse_directory
        )

        btn_browse.pack(side="right")

        # 파일명 입력 영역
        input_frame = tk.Frame(self.root)
        input_frame.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=5
        )

        tk.Label(
            input_frame,
            text="생성할 파일명 목록 (, 또는 ; 또는 줄바꿈으로 구분):",
            font=("맑은 고딕", 9, "bold")
        ).pack(anchor="w")

        self.text_input = tk.Text(
            input_frame,
            height=7,
            font=("맑은 고딕", 10)
        )

        self.text_input.pack(
            fill="both",
            expand=True,
            pady=5
        )

        # 버튼 영역
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(
            fill="x",
            padx=15,
            pady=(5, 15)
        )

        btn_new = tk.Button(
            btn_frame,
            text="NEW (초기화)",
            width=12,
            command=self.clear_input
        )

        btn_new.pack(side="left")

        btn_create = tk.Button(
            btn_frame,
            text="TXT 파일 생성",
            width=15,
            command=self.create_files
        )

        btn_create.pack(side="right")

    def browse_directory(self):
        """저장 폴더를 선택합니다."""

        selected_dir = filedialog.askdirectory(
            initialdir=self.save_dir
        )

        if selected_dir:
            self.save_dir = selected_dir

            self.dir_entry.delete(
                0,
                tk.END
            )

            self.dir_entry.insert(
                0,
                self.save_dir
            )

            # 선택한 폴더를 즉시 저장
            self.save_settings()

    def clear_input(self):
        """파일명 입력창을 초기화합니다."""

        self.text_input.delete(
            "1.0",
            tk.END
        )

    def sanitize_filename(self, filename):
        """Windows에서 사용할 수 없는 문자를 제거합니다."""

        return re.sub(
            r'[\\/*?:"<>|]',
            "_",
            filename
        ).strip()

    def create_files(self):
        """TXT 파일을 일괄 생성합니다."""

        raw_text = self.text_input.get(
            "1.0",
            tk.END
        ).strip()

        current_dir = self.dir_entry.get().strip()

        if not raw_text:
            messagebox.showwarning(
                "경고",
                "생성할 파일명을 입력해주세요."
            )
            return

        if not current_dir:
            messagebox.showwarning(
                "경고",
                "저장 폴더를 선택해주세요."
            )
            return

        # 현재 폴더를 설정으로 저장
        self.save_dir = current_dir
        self.save_settings()

        # 저장 폴더가 없으면 생성
        try:
            os.makedirs(
                current_dir,
                exist_ok=True
            )
        except Exception as error:
            messagebox.showerror(
                "오류",
                f"저장 폴더를 생성할 수 없습니다.\n\n{error}"
            )
            return

        # 쉼표, 세미콜론, 줄바꿈으로 분리
        items = re.split(
            r"[,;\n]",
            raw_text
        )

        created_count = 0
        skipped_count = 0

        for item in items:
            filename = item.strip()

            if not filename:
                continue

            safe_filename = self.sanitize_filename(
                filename
            )

            if not safe_filename:
                skipped_count += 1
                continue

            # .txt 확장자가 이미 있는 경우 중복 추가하지 않음
            if not safe_filename.lower().endswith(".txt"):
                safe_filename += ".txt"

            file_path = os.path.join(
                current_dir,
                safe_filename
            )

            try:
                # 기존 파일은 덮어쓰지 않음
                if os.path.exists(file_path):
                    skipped_count += 1
                else:
                    with open(
                        file_path,
                        "w",
                        encoding="utf-8"
                    ):
                        pass

                    created_count += 1

            except Exception:
                skipped_count += 1

        messagebox.showinfo(
            "완료",
            "작업이 완료되었습니다.\n\n"
            f"생성된 파일: {created_count}개\n"
            f"건너뛴 파일: {skipped_count}개\n\n"
            f"저장 경로:\n{current_dir}"
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TextFileCreatorApp(root)
    root.mainloop()
