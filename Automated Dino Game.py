import cv2
import cvzone
import numpy as np
import pyautogui
from cvzone.FPS import FPS
from mss import mss
import time

fpsReader = FPS()


def capture_screen_region_opencv(x, y, desired_width, desired_height):
    screenshot = pyautogui.screenshot(region=(x, y, desired_width, desired_height))
    screenshot = np.array(screenshot)
    screenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
    return screenshot


def capture_screen_region_opencv_mss(x, y, width, height):
    with mss() as sct:
        monitor = {"top": y, "left": x, "width": width, "height": height}
        screenshot = sct.grab(monitor)
        # تحويل الصورة إلى صيغة OpenCV
        img = np.array(screenshot)
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)  # تحويل من BGRA إلى BGR
        return img


def pre_process(_imgCrop):
    # تحويل الصورة إلى تدرج رمادي لتسهيل العتبة
    gray_frame = cv2.cvtColor(_imgCrop, cv2.COLOR_BGR2GRAY)
    # تطبيق عتبة ثنائية مع عكس الألوان
    _, binary_frame = cv2.threshold(gray_frame, 127, 255, cv2.THRESH_BINARY_INV)
    # استخراج الحواف باستخدام Canny
    canny_frame = cv2.Canny(binary_frame, 50, 50)
    # توسيع الحواف باستخدام dilation
    kernel = np.ones((5, 5))
    dilated_frame = cv2.dilate(canny_frame, kernel, iterations=2)
    return dilated_frame


def find_obstacles(_imgCrop, _imgPre):
    imgContours, conFound = cvzone.findContours(_imgCrop, _imgPre, minArea=100, filter=None)
    return imgContours, conFound


def game_logic(conFound, _imgContours, jump_distance=65):
    if conFound:
        # فرز الكونتورات للحصول على الكونتور الأيسر
        left_most_contour = sorted(conFound, key=lambda x: x["bbox"][0])
        cv2.line(_imgContours, (0, left_most_contour[0]["bbox"][1] + 10),
                 (left_most_contour[0]["bbox"][0], left_most_contour[0]["bbox"][1] + 10),
                 (0, 200, 0), 10)
        # إذا كانت المسافة الأفقية أقل من jump_distance
        if left_most_contour[0]["bbox"][0] < jump_distance:
            pyautogui.press("space")
            print("Jump pressed")

            # الانتظار لمدة 0.5 ثانية بعد القفزة
            time.sleep(0.5)

            # التأكد من تنفيذ ضغط السهم للأسفل
            print("Pressing Down Key Now...")
            pyautogui.press("down")
            print("Down key pressed successfully!")


while True:
    # الخطوة 1 - التقاط جزء من شاشة اللعبة
    imgGame = capture_screen_region_opencv_mss(450, 300, 650, 200)

    # الخطوة 2 - اقتصاص المنطقة المطلوبة من الصورة
    cp = (100, 140, 110)
    imgCrop = imgGame[cp[0]:cp[1], cp[2]:]

    # الخطوة 3 - معالجة الصورة لاستخراج الحواف
    imgPre = pre_process(imgCrop)

    # الخطوة 4 - إيجاد العقبات باستخدام الكونتورات
    imgContours, conFound = find_obstacles(imgCrop, imgPre)

    # الخطوة 5 - تطبيق منطق اللعبة (قفزة، ثم ضغط سهم الأسفل بعد 0.5 ثانية)
    game_logic(conFound, imgContours)

    # دمج الصورة المعدلة مع لقطة شاشة اللعبة
    imgGame[cp[0]:cp[1], cp[2]:] = imgContours

    # تحديث وإظهار عدد الإطارات في الثانية
    fps, imgGame = fpsReader.update(imgGame)
    cv2.imshow("Game", imgGame)
    cv2.waitKey(1)
# import tkinter as tk
# from tkinter import filedialog, messagebox
# from PIL import Image, ImageTk, ImageDraw
# import cv2
# import numpy as np
# import pyautogui
# import time  # استيراد مكتبة time
#
# class ImageEditorApp:
#     def __init__(self, master):
#         self.master = master
#         master.title("تطبيق التعامل مع الصور والكاميرا")
#
#         # إعداد Canvas لعرض الصورة
#         self.canvas = tk.Canvas(master, width=600, height=400, bg="gray")
#         self.canvas.pack()
#
#         # إنشاء أزرار للوظائف المطلوبة
#         self.btn_open = tk.Button(master, text="فتح صورة", command=self.open_image)
#         self.btn_open.pack(side=tk.LEFT, padx=5, pady=5)
#
#         self.btn_capture = tk.Button(master, text="التقاط صورة بالكاميرا", command=self.capture_image)
#         self.btn_capture.pack(side=tk.LEFT, padx=5, pady=5)
#
#         self.btn_save = tk.Button(master, text="حفظ الصورة", command=self.save_image)
#         self.btn_save.pack(side=tk.LEFT, padx=5, pady=5)
#
#         self.btn_filter = tk.Button(master, text="تطبيق فلتر الرمادي", command=self.apply_grayscale)
#         self.btn_filter.pack(side=tk.LEFT, padx=5, pady=5)
#
#         self.btn_flip = tk.Button(master, text="صورة مرآة", command=self.apply_flip)
#         self.btn_flip.pack(side=tk.LEFT, padx=5, pady=5)
#
#         self.btn_info = tk.Button(master, text="معلومات الصورة", command=self.show_image_info)
#         self.btn_info.pack(side=tk.LEFT, padx=5, pady=5)
#
#         # المتغيرات الأساسية لتخزين الصورة
#         self.image = None       # الصورة الأصلية (PIL Image)
#         self.draw_image = None  # نسخة من الصورة يمكن الرسم عليها
#         self.photo = None       # الصورة المعروضة في الـ Canvas
#
#         # إعدادات الرسم: حفظ إحداثيات البداية للرسم
#         self.last_x, self.last_y = None, None
#         self.canvas.bind("<ButtonPress-1>", self.on_button_press)
#         self.canvas.bind("<B1-Motion>", self.on_move_press)
#
#     def open_image(self):
#         # فتح صورة من الجهاز باستخدام filedialog
#         file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg *.png *.bmp")])
#         if file_path:
#             self.image = Image.open(file_path)
#             self.draw_image = self.image.copy()
#             self.display_image()
#
#     def capture_image(self):
#         # التقاط صورة من الكاميرا باستخدام OpenCV مع استخدام CAP_DSHOW (مناسب لأنظمة ويندوز)
#         cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
#         if not cap.isOpened():
#             messagebox.showerror("خطأ", "لا يمكن فتح الكاميرا")
#             return
#         # الانتظار قليلاً للسماح للكاميرا بالتشغيل
#         time.sleep(0.5)
#         ret, frame = cap.read()
#         cap.release()
#         if ret and frame is not None:
#             # تحويل الصورة من BGR (المستخدمة في OpenCV) إلى RGB (المستخدمة في PIL)
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#             self.image = Image.fromarray(frame)
#             self.draw_image = self.image.copy()
#             self.display_image()
#         else:
#             messagebox.showerror("خطأ", "لم يتم التقاط الصورة من الكاميرا")
#
#     def save_image(self):
#         # حفظ الصورة المعدلة
#         if self.draw_image:
#             file_path = filedialog.asksaveasfilename(defaultextension=".png")
#             if file_path:
#                 self.draw_image.save(file_path)
#                 messagebox.showinfo("نجاح", "تم حفظ الصورة")
#         else:
#             messagebox.showerror("خطأ", "لا يوجد صورة للحفظ")
#
#     def apply_grayscale(self):
#         # تطبيق فلتر الرمادي باستخدام OpenCV
#         if self.draw_image:
#             open_cv_image = np.array(self.draw_image)
#             gray = cv2.cvtColor(open_cv_image, cv2.COLOR_RGB2GRAY)
#             # تحويل الصورة الرمادية إلى RGB لعرضها بشكل صحيح في Tkinter
#             gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
#             self.draw_image = Image.fromarray(gray)
#             self.display_image()
#         else:
#             messagebox.showerror("خطأ", "لا يوجد صورة لتطبيق الفلتر")
#
#     def apply_flip(self):
#         # تطبيق عملية انعكاس الصورة (صورة مرآة)
#         if self.draw_image:
#             flipped = self.draw_image.transpose(Image.FLIP_LEFT_RIGHT)
#             self.draw_image = flipped
#             self.display_image()
#         else:
#             messagebox.showerror("خطأ", "لا يوجد صورة لتطبيق العملية")
#
#     def show_image_info(self):
#         # إظهار معلومات عن الصورة (الأبعاد وعدد القنوات)
#         if self.draw_image:
#             open_cv_image = np.array(self.draw_image)
#             height, width, channels = open_cv_image.shape
#             info = f"الأبعاد: {width}x{height}\nعدد القنوات: {channels}"
#             messagebox.showinfo("معلومات الصورة", info)
#         else:
#             messagebox.showerror("خطأ", "لا يوجد صورة لعرض المعلومات")
#
#     def display_image(self):
#         # تحديث وعرض الصورة على الـ Canvas
#         self.photo = ImageTk.PhotoImage(self.draw_image)
#         self.canvas.delete("all")
#         self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
#
#     def on_button_press(self, event):
#         # حفظ نقطة البداية عند الضغط على الفأرة
#         self.last_x, self.last_y = event.x, event.y
#
#     def on_move_press(self, event):
#         # أثناء سحب الفأرة، يتم رسم خط بين النقطة السابقة والنقطة الحالية
#         if self.last_x is not None and self.last_y is not None and self.draw_image:
#             draw = ImageDraw.Draw(self.draw_image)
#             draw.line((self.last_x, self.last_y, event.x, event.y), fill="red", width=3)
#             self.last_x, self.last_y = event.x, event.y
#             self.display_image()
#
# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ImageEditorApp(root)
#     root.mainloop()
