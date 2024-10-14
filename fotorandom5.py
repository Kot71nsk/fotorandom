import os
import tkinter as tk
from tkinter import filedialog, StringVar
from PIL import Image, ImageTk
import random

class ImageApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Viewer v0.3 by Kot71")
        
        self.directory = StringVar()
        self.slideshow_interval = StringVar(value='15000')  # Интервал между сменой изображений (в миллисекундах)
        self.images = []
        self.current_image_index = 0
        self.is_paused = False
        self.pause_id = None

        # Основной интерфейс
        self.label = tk.Label(root, text="Выбери директорию с картинками:")
        self.label.pack(pady=10)

        self.entry = tk.Entry(root, textvariable=self.directory, width=50)
        self.entry.pack(pady=10)

        self.browse_button = tk.Button(root, text="Browse", command=self.browse_directory)
        self.browse_button.pack(pady=5)

        self.interval_label = tk.Label(root, text="Интервал (мс):")
        self.interval_label.pack(pady=5)

        self.interval_entry = tk.Entry(root, textvariable=self.slideshow_interval, width=10)
        self.interval_entry.pack(pady=5)

        self.start_button = tk.Button(root, text="Погнали!", command=self.start_slideshow)
        self.start_button.pack(pady=20)

        #self.del_button = tk.Button(root, text="Del", command=self.delete_image)
        #self.del_button.pack(pady=5)

        # Обработчики нажатия клавиш
        self.root.bind('<Escape>', self.close_image_window)  # Закрыть программу на Escape
        self.root.bind('<Left>', self.show_previous_image)  # Переключение на предыдущее изображение
        self.root.bind('<space>', self.toggle_pause)  # Пауза/возобновление на пробел

    def browse_directory(self):
        directory = filedialog.askdirectory()
        self.directory.set(directory)

    def start_slideshow(self):
        try:
            self.images = self.get_images(self.directory.get())
            if not self.images:
                raise FileNotFoundError("Картинки не найдены.")
            
            # Перемешиваем изображения
            random.shuffle(self.images)

            self.current_image_index = 0
            self.is_paused = False
            self.open_image_window()
        except FileNotFoundError as e:
            print(e)
        except Exception as e:
            print(f"An error occurred: {e}")

    def get_images(self, directory):
        images = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    images.append(os.path.join(root, file))
        return images

    def open_image_window(self):
        self.image_window = tk.Toplevel(self.root)
        self.image_window.attributes('-fullscreen', True)
        self.image_window.configure(bg='black')  # Устанавливаем черный фон
        self.image_window.bind('<Escape>', self.close_image_window)  # Закрытие окна на Escape
        self.image_window.bind('<Left>', self.show_previous_image)  # Переключение на предыдущее изображение
        self.image_window.bind('<space>', self.toggle_pause)  # Пауза/возобновление на пробел
        self.image_window.bind('<Delete>', self.delete_image)  # Удаление текущего изображения

        self.image_label = tk.Label(self.image_window, bg='black')  # Фон метки черный
        self.image_label.pack(fill=tk.BOTH, expand=tk.YES)

        self.display_image()

        # Устанавливаем фокус на окно с изображением
        self.image_window.focus_set()

    def display_image(self):
        """Отображает текущее изображение."""
        if self.image_label:
            self.image_label.destroy()

        image_path = self.images[self.current_image_index]
        image = Image.open(image_path)
        screen_width = self.image_window.winfo_screenwidth()
        screen_height = self.image_window.winfo_screenheight()

        # Вычисляем новый размер изображения с сохранением пропорций
        image.thumbnail((screen_width, screen_height), Image.LANCZOS)

        photo = ImageTk.PhotoImage(image)

        self.image_label = tk.Label(self.image_window, image=photo, bg='black')
        self.image_label.image = photo
        self.image_label.pack(fill=tk.BOTH, expand=tk.YES)

        if not self.is_paused:
            try:
                interval = int(self.slideshow_interval.get().strip())  # Удаляем лишние пробелы
                self.pause_id = self.image_window.after(interval, self.show_next_image)
            except ValueError:
                print("Неверный формат интервала. Используется интервал по умолчанию.")
                self.pause_id = self.image_window.after(3000, self.show_next_image)

    def show_next_image(self):
        """Показывает следующее изображение в списке."""
        self.current_image_index = (self.current_image_index + 1) % len(self.images)
        self.display_image()

    def show_previous_image(self, event=None):
        """Показывает предыдущее изображение в списке."""
        self.current_image_index = (self.current_image_index - 1) % len(self.images)
        self.display_image()

    def toggle_pause(self, event=None):
        if self.is_paused:
            # Возобновляем показ изображений
            self.is_paused = False
            if self.pause_id:
                self.image_window.after_cancel(self.pause_id)
            self.show_next_image()
        else:
            # Ставим на паузу
            self.is_paused = True
            if self.pause_id:
                self.image_window.after_cancel(self.pause_id)

    def delete_image(self, event=None):
        """Удаляет текущее изображение."""
        if self.images:
            try:
                os.remove(self.images[self.current_image_index])
                del self.images[self.current_image_index]
                if self.current_image_index >= len(self.images):
                    self.current_image_index = 0
                self.display_image()
            except Exception as e:
                print(f"Ошибка при удалении изображения: {e}")

    def close_image_window(self, event=None):
        # Закрываем окно показа изображений
        if self.image_window:
            self.image_window.destroy()
            self.image_window = None

def main():
    root = tk.Tk()
    app = ImageApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()