from customtkinter import *
import threading
import socket
import base64
import io
from PIL import Image
from tkinter import filedialog


class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.title("Logitalk")


        self.frame = CTkFrame(
            self, fg_color="light blue", width=0, height=self.winfo_height()
        )
        self.frame.pack_propagate(False)
        self.frame.place(x=-1, y=0)
        self.is_show_menu = False
        self.frame_width = 0


        self.btn = CTkButton(self, text="▶️", command=self.toggle_show_menu, width=30)
        self.btn.place(x=0, y=0)
       


        self.label = CTkLabel(self.frame, text="Ваше ім'я")
        self.label.pack(pady=40)
        self.entry = CTkEntry(self.frame, placeholder_text="Введіть ваше ім'я")
        self.entry.pack()
        self.change_name_btn = CTkButton(self.frame, text="Змінити ім'я", command=self.change_name)
        self.change_name_btn.pack(pady=10)
       
        self.change_theme = CTkOptionMenu(self.frame, values=['Система','Світла', 'Темна'], command=self.change_theme)
        self.change_theme.pack(side='bottom', pady=10)
       
        self.user_name = 'Dmytro'
        self.online = None
       
        self.chat_online = CTkLabel(self, text="Онлайн", height=self.btn.winfo_height())
        self.chat_online.place(x=0, y=0)
       
        self.chat_field = CTkScrollableFrame(self)
        self.chat_field.place(x=0, y=0)
        # self.btn.lift()
        self.message_entry = CTkEntry(self, placeholder_text="Введіть повідомлення", height=40)
        self.message_entry.place(x=0, y=0)
       
        self.message_entry.bind("<Return>", self.send_message)
       
        self.send_btn = CTkButton(self, text="", image=CTkImage(Image.open('mail.png'), size=(40,40)), width=50, height=40, command=self.send_message)
        self.send_btn.place(x=0, y=0)
       
        self.send_img_btn = CTkButton(self, text="📂", width=50, height=40, command=self.send_img)
        self.send_img_btn.place(x=0, y=0)
       
        self.file_name = None
        self.raw = None
        self.image_to_send = CTkLabel(self, text="")
        self.image_to_send.bind("<Button-1>", self.remove_image)
       
       
        self.adaptation_ui()
       
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect(('localhost', 22))
            hello = f'TEXT@{self.user_name}@[SYSTEM] {self.user_name} підключився(лась) до чату!\n'
           
            self.socket.sendall(hello.encode('utf-8'))
            threading.Thread(target=self.receive_message, daemon=True).start()
        except Exception as e:
            self.add_message(f'Не вдалося підключитися до сервера: {e}')
       
    def remove_image(self, e=None):
        self.image_to_send.place_forget()
        self.raw = None
        self.file_name = None


    def toggle_show_menu(self):
        if self.is_show_menu:
            self.is_show_menu = False
            self.close_menu()
        else:
            self.is_show_menu = True
            self.show_menu()


    def show_menu(self):
        if self.frame_width <= 200:
            self.frame_width += 5
            self.frame.configure(width=self.frame_width, height=self.winfo_height())
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text="◀️")
        if self.is_show_menu:
            self.after(10, self.show_menu)


    def close_menu(self):
        if self.frame_width >= 0:
            self.frame_width -= 5
            self.frame.configure(width=self.frame_width)
            if self.frame_width >= 30:
                self.btn.configure(width=self.frame_width, text="▶️")
        if not self.is_show_menu:
            self.after(10, self.close_menu)


    def change_theme(self, value):
        if value == 'Світла':
            set_appearance_mode("light")
            self.frame.configure(fg_color="light blue")
            set_default_color_theme("blue")
        elif value == 'Темна':
            set_appearance_mode("dark")
            self.frame.configure(fg_color="dodger blue")
        elif value == 'Система':
            set_appearance_mode("system")


    def adaptation_ui(self):
        w_width = self.winfo_width()
        w_height = self.winfo_height()
       
        self.frame.configure(height=w_height)
       
        self.chat_field.place(x=self.frame.winfo_width(), y = self.btn.winfo_height())
        self.chat_field.configure(width=w_width - self.frame.winfo_width()-20, height=w_height - 45 - self.btn.winfo_height())
       
        self.send_btn.place(x=w_width - 50, y=w_height - 40)
        self.send_img_btn.place(x=w_width - 105, y=w_height - 40)
       
        self.message_entry.place(x=self.frame.winfo_width(), y = w_height - 40)
        self.message_entry.configure(width=self.send_img_btn.winfo_x() - self.frame.winfo_width() - 5)
       
        self.chat_online.place(x=self.btn.winfo_width()+20)
       
        if self.raw:
            self.image_to_send.configure(image=CTkImage(Image.open(self.file_name), size=(100, 100)))
            self.image_to_send.place(x=self.frame.winfo_width()+20, y=self.message_entry.winfo_y()-100)
       
        self.after(100, self.adaptation_ui)

    def change_name(self):
        self.user_name = self.entry.get()
        self.label.configure(text=self.user_name)
        self.entry.delete(0, 'end')
   
    def add_message(self, message, img=None): #CTkImage
        message_frame = CTkFrame(self.chat_field, fg_color="#636363")
        message_frame.pack(pady=5, padx=5, anchor="w")
       
        w_size = self.winfo_width() - self.frame.winfo_width() - 20
       
        if not img:
            CTkLabel(message_frame, text=message, justify='left', wraplength=w_size, text_color='white').pack(pady=5, padx=10)
        else:
            CTkLabel(message_frame, text=message, justify='left', wraplength=w_size, text_color='white', image=img, compound='top').pack(pady=5, padx=10)
           
        # self.chat_field._parent_canvas.yview_moveto(1.0) # прокрутка вниз
   
    def resize_image(self, image):
        # image = Image.open(image)
        width, height = image.size
        new_width = 300
       
        if width <= new_width:
            if height < 300:
                return CTkImage(image, size=(width, height))
            else:
                new_height = 300
                new_width = int(width*new_height / height)
        new_height = int(height*new_width / width)
       
        resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)


        return CTkImage(resized_image, size=(new_width, new_height))
   
    def send_img(self):
        self.file_name = filedialog.askopenfilename(
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg")]
        )
        if not self.file_name:
            return
        try:
            # 'rb' - read binary, 'r' - read text, 'wb' - write binary, 'w' - write text, 'a' - append text, 'ab' - append binary,
            with open(self.file_name, 'rb') as f:
                self.raw = f.read()
            return self.raw
        except Exception as e:
            self.add_message(f"Error: {e}")
   
    def send_message(self, e=None):
        message = self.message_entry.get()
        if message and not self.raw:
            self.add_message(f'{self.user_name}: {message}')
            # data = f'TEXT@{self.user_name}@{message}\n'
            # try:
            #     self.socket.sendall(data.encode())
            # except:
            #     pass
        elif self.raw:
            # b64_data = base64.b64encode(self.raw).decode() # base64 encode - кодування даних в base64
            # data = f'IMAGE@{self.user_name}@{message}@{b64_data}\n'
            # try:
            #     self.socket.sendall(data.encode())
            # except:
            #     pass
            self.add_message(message, img=self.resize_image(Image.open(self.file_name)))
            self.remove_image()
        self.message_entry.delete(0, 'end')
   
    def receive_message(self):
        buffer = ''
        while True:
            try:
                message = self.socket.recv(16384)
                buffer += message.decode('utf-8', errors='ignore')
                while '\n' in buffer:
                    line, buffer = buffer.split('\n', 1)
                    self.handle_line(line.strip())
            except:
                break
        self.socket.close()
   
    def handle_line(self, line):
        if not line:
            return
        parts = line.split('@',3)
        message_type = parts[0]
        if message_type == 'TEXT':
            if len(parts) >= 3:
                self.add_message(f'{parts[1]}: {parts[2]}')
        elif message_type == 'IMAGE':
            if len(parts) >= 4:
                try:
                    image_data = base64.b64decode(parts[3])
                    img = Image.open(io.BytesIO(image_data))
                    img = self.resize_image(img)
                    self.add_message(f'{parts[1]}: {parts[2]}', img=img)
                except Exception as e:
                    self.add_message(f"Error: {e}")
        elif message_type == 'ONLINE':
            print(message_type, parts[1])
            pass
win = MainWindow()
win.mainloop()




