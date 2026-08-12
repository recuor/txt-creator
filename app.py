import os
import re
import tkinter as tk
from tkinter import filedialog, messagebox


class TextFileCreatorApp:

    def __init__(self, root):
        self.root = root
        self.root.title("텍스트 파일 일괄 생성기")
        self.root.geometry("520x350")
        self.root.resizable(False, False)

        # 기본 저장 디렉토리 (사용자 Documents/문서 폴더)
        self.default_dir = os.path.join(os.path.expanduser("~"), "Documents")
        self.save_dir = self.default_dir

        self.setup_ui()

    def setup_ui(self):
        # 1. 저장 디렉토리 선택 영역
        dir_frame = tk.Frame(self.root)
        dir_frame.pack(fill="x", padx=15, pady=(15, 5))

        tk.Label(dir_frame, text="저장 디렉토리:", font=("맑은 고딕", 9, "bold")).pack(
            anchor="w"
        )

        dir_sub_frame = tk.Frame(dir_frame)
        dir_sub_frame.pack(fill="x", pady=5)

        self.dir_entry = tk.Entry(dir_sub_frame, font=("맑은 고딕", 9))
        self.dir_entry.insert(0, self.save_dir)
        self.dir_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))

        btn_browse = tk.Button(
            dir_sub_frame, text="폴더 찾기", command=self.browse_directory
        )
        btn_browse.pack(side="right")

        # 2. 문자열 입력 영역
        input_frame = tk.Frame(self.root)
        input_frame.pack(fill="both", expand=True, padx=15, pady=5)

        tk.Label(
            input_frame,
            text="생성할 파일명 목록 (, 또는 ; 로 구분):",
            font=("맑은 고딕", 9, "bold"),
        ).pack(anchor="w")

        self.text_input = tk.Text(input_frame, height=7, font=("맑은 고딕", 10))
        self.text_input.pack(fill="both", expand=True, pady=5)

        # 3. 버튼 영역 (NEW, 파일 생성)
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(fill="x", padx=15, pady=(5, 15))

        # NEW 버튼 (초기화)
        btn_new = tk.Button(
            btn_frame,
            text="NEW (초기화)",
            width=12,
            bg="#f0f0f0",
            command=self.clear_input,
        )
        btn_new.pack(side="left")

        # 파일 생성 버튼
        btn_create = tk.Button(
            btn_frame,
            text="TXT 파일 생성",
            width=15,
            bg="#2b579a",
            fg="white",
            font=("맑은 고딕", 9, "bold"),
            command=self.create_files,
        )
        btn_create.pack(side="right")

    def browse_directory(self):
        """저장 디렉토리 변경"""
        selected_dir = filedialog.askdirectory(initialdir=self.save_dir)
        if selected_dir:
            self.save_dir = selected_dir
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, self.save_dir)

    def clear_input(self):
        """입력창 내용 지우기 (NEW 버튼 기능)"""
        self.text_input.delete("1.0", tk.END)

    def sanitize_filename(self, filename):
        """윈도우 파일명으로 사용할 수 없는 특수문자 제거/대체"""
        return re.sub(r'[\\/*?:"<>|]', "_", filename).strip()

    def create_files(self):
        """TXT 파일 일괄 생성"""
        raw_text = self.text_input.get("1.0", tk.END).strip()
        current_dir = self.dir_entry.get().strip()

        if not raw_text:
            messagebox.showwarning("경고", "생성할 문자열을 입력해주세요.")
            return

        if not os.path.exists(current_dir):
            try:
                os.makedirs(current_dir, exist_ok=True)
            except Exception as e:
                messagebox.showerror(
                    "오류", f"디렉토리를 생성할 수 없습니다:\n{e}"
                )
                return

        # 쉼표(,) 및 세미콜론(;) 기준으로 문자열 분리 (줄바꿈도 포함)
        items = re.split(r"[,;\n]", raw_text)

        created_count = 0
        skipped_count = 0

        for item in items:
            filename = item.strip()
            if not filename:
                continue

            # 파일명 특수문자 정제
            safe_filename = self.sanitize_filename(filename)
            if not safe_filename:
                skipped_count += 1
                continue

            file_path = os.path.join(current_dir, f"{safe_filename}.txt")

            try:
                # 빈 txt 파일 생성 (이미 존재하는 경우 덮어쓰지 않음)
                if not os.path.exists(file_path):
                    with open(file_path, "w", encoding="utf-8") as f:
                        pass
                    created_count += 1
                else:
                    skipped_count += 1
            except Exception as e:
                skipped_count += 1

        messagebox.showinfo(
            "완료",
            f"작업이 완료되었습니다.\n\n- 생성된 파일: {created_count}개\n- 건너뛴 파일 (중복/오류): {skipped_count}개\n- 저장 경로: {current_dir}",
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = TextFileCreatorApp(root)
    root.mainloop()
