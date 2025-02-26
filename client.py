import socket
import json
import customtkinter as ctk
from tkinter import messagebox
import tkinter
from PIL import Image ,ImageTk

HOST = '127.0.0.1'
PORT = 12345

def reverse_hebrew_text(text):
    """מתקן את סדר המילים בעברית."""
    return " ".join(text.split()[::-1])

class JobClient(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("משרות לוח")
        self.geometry("600x500")
        ctk.set_appearance_mode("dark")


        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.connection.connect((HOST, PORT))
        except ConnectionRefusedError:
            messagebox.showerror("שגיאה", "לא ניתן להתחבר לשרת")
            self.destroy()
            return

        self.show_main_menu()
        self.add_images()

    def add_images(self):

        left_img = Image.open("photos/ashdod.png")
        right_img = Image.open("photos/mekif.png")

        left_ctk_img = ctk.CTkImage(light_image=left_img, size=(50, 50))
        right_ctk_img = ctk.CTkImage(light_image=right_img, size=(50, 50))

        self.left_label = ctk.CTkLabel(self, image=left_ctk_img, text="")
        self.left_label.place(x=10, y=10)

        self.right_label = ctk.CTkLabel(self, image=right_ctk_img, text="")
        self.right_label.place(x=540, y=10)

    def clear_window(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_main_menu(self):
        self.clear_window()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="ברוך הבא ללוח המשרות", font=("Arial", 18), anchor="e", justify="right").pack(pady=10)

        ctk.CTkButton(frame, text="כמעסיק רישום", command=lambda: self.show_job_form("מעסיק"), anchor="e").pack(pady=5)
        ctk.CTkButton(frame, text="כהתנדבות רישום", command=lambda: self.show_job_form("התנדבות"), anchor="e").pack(pady=5)
        ctk.CTkButton(frame, text="משרות ללוח כניסה", command=self.start_job_board, anchor="e").pack(pady=5)

    def show_job_form(self, job_type):
        self.clear_window()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text=f"רישום {job_type}", font=("Arial", 18), anchor="e", justify="right").pack(pady=10)

        self.place_entry = ctk.CTkEntry(frame, placeholder_text="מקום שם", justify="right")
        self.place_entry.pack(pady=5)
        self.desc_entry = ctk.CTkEntry(frame, placeholder_text="תיאור", justify="right")
        self.desc_entry.pack(pady=5)

        additional_fields = {}

        if job_type == "מעסיק":
            additional_fields['job_type'] = ctk.CTkEntry(frame, placeholder_text="עבודה סוג", justify="right")
            additional_fields['requirements'] = ctk.CTkEntry(frame, placeholder_text="תפקיד דרישות", justify="right")
            additional_fields['salary'] = ctk.CTkEntry(frame, placeholder_text="משוער שכר טווח", justify="right")
        else:
            additional_fields['hours'] = ctk.CTkEntry(frame, placeholder_text="פעילות שעות", justify="right")
            additional_fields['audience'] = ctk.CTkEntry(frame, placeholder_text="יעד קהל", justify="right")

        for entry in additional_fields.values():
            entry.pack(pady=5)

        self.additional_fields = additional_fields

        ctk.CTkButton(frame, text="פרסם", command=lambda: self.post_job(job_type), anchor="e").pack(pady=10)
        ctk.CTkButton(frame, text="חזרה", command=self.show_main_menu, anchor="e").pack(pady=10)

    def post_job(self, job_type):
        job = {"type": job_type, "place": self.place_entry.get(), "description": self.desc_entry.get()}
        for key, entry in self.additional_fields.items():
            job[key] = entry.get()

        if not job["place"] or not job["description"]:
            messagebox.showerror("שגיאה", "יש למלא את כל השדות")
            return

        try:
            self.connection.sendall(json.dumps(job, ensure_ascii=False).encode('utf-8'))
            response = self.connection.recv(4096).decode('utf-8')
            response_data = json.loads(response)

            if response_data.get("status") == "success":
                messagebox.showinfo("הצלחה", "המשרה פורסמה בהצלחה!")
                self.show_main_menu()
            else:
                messagebox.showerror("שגיאה", "שגיאה בפרסום המשרה")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליחת נתונים: {e}")

    def submit_private_registration(self):
        """שולח את הנתונים של האדם הפרטי עם טקסט הפוך נכון בעברית"""
        person_data = {
            "type": "אדם פרטי",
            "fullname": reverse_hebrew_text(self.fullname_entry.get()),
            "age": self.age_entry.get(),
            "phone": self.phone_entry.get(),
            "occupation": reverse_hebrew_text(self.occupation_entry.get()),
            "extra_info": reverse_hebrew_text(self.extra_info_entry.get())
        }

        if not all(person_data.values()):
            messagebox.showerror("שגיאה", "יש למלא את כל השדות")
            return

        try:
            self.connection.sendall(json.dumps(person_data, ensure_ascii=False).encode('utf-8'))
            response = self.connection.recv(4096).decode('utf-8')
            if json.loads(response).get("status") == "success":
                messagebox.showinfo("הצלחה", "נרשמת בהצלחה!")
                self.show_main_menu()
            else:
                messagebox.showerror("שגיאה", "שגיאה ברישום")
        except Exception as e:
            messagebox.showerror("שגיאה", f"שגיאה בשליחת נתונים: {e}")

    def start_job_board(self):
        """מציג את לוח המשרות עם טקסט הפוך נכון בעברית"""
        self.clear_window()
        frame = ctk.CTkFrame(self)
        frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(frame, text="לוח משרות", font=("Arial", 18), anchor="e", justify="right").pack(pady=10)

        job_list = ctk.CTkTextbox(frame, width=550, height=300)
        job_list.pack(pady=10)

        try:
            self.connection.sendall(json.dumps({"request": "get_jobs"}).encode('utf-8'))
            data = self.connection.recv(4096).decode('utf-8')
            jobs = json.loads(data)

            if not jobs:
                job_list.insert("end", "אין משרות זמינות כרגע\n")
            else:
                for job in jobs:
                    job_text = f"{reverse_hebrew_text(job['description'])} :{reverse_hebrew_text(job['place'])} - {job['type']}\n"
                    if job['type'] == "מעסיק" and 'job_type' in job:
                        job_text += f"{job.get('job_type', '')} :עבודה סוג \n"
                        job_text += f"{job.get('requirements', '')} :דרישות\n"
                        job_text += f"{job.get('salary', '')} :שכר\n"
                    elif job['type'] == "התנדבות" and 'hours' in job:
                        job_text += f"{job.get('hours', '')} :שעות\n"
                        job_text += f"{job.get('audience', '')} :יעד קהל\n"

                    job_text += "-" * 50 + "\n"
                    job_list.insert("end", job_text)
        except Exception as e:
            job_list.insert("end", f"שגיאה בטעינת המשרות: {str(e)}\n")

        ctk.CTkButton(frame, text="חזרה", command=self.show_main_menu).pack(pady=10)

if __name__ == "__main__":
    client_app = JobClient()
    client_app.mainloop()
