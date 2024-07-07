import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog,
                             QHBoxLayout, QDialog, QInputDialog, QScrollArea, QWidget)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import numpy as np
import os

class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image = None
        self.original_image = None

    def initUI(self):
        self.setWindowTitle('Приложение 1000x600')
        self.resize(1000, 600)

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setWidgetResizable(True)

        loadButton = QPushButton('Загрузить фото', self)
        loadButton.clicked.connect(self.loadImage)
        
        webcamButton = QPushButton('Снять фото', self)
        webcamButton.clicked.connect(self.captureFromWebcam)
        
        channelButton = QPushButton('Канал изображения', self)
        channelButton.clicked.connect(self.showColorChannel)
        
        resizeButton = QPushButton('Изменить размер', self)
        resizeButton.clicked.connect(self.resizeImage)
        
        borderButton = QPushButton('Добавить границы', self)
        borderButton.clicked.connect(self.addBorder)
        
        rectangleButton = QPushButton('Нарисовать прямоугольник', self)
        rectangleButton.clicked.connect(self.drawRectangle)
        
        resetButton = QPushButton('<-', self)
        resetButton.setFixedSize(40, 30)
        resetButton.clicked.connect(self.resetImage)

        resizeButtonToWindow = QPushButton('[ ]', self)
        resizeButtonToWindow.setFixedSize(40, 30)
        resizeButtonToWindow.clicked.connect(self.fitToWindow)
        
        hbox = QHBoxLayout()
        hbox.addWidget(loadButton)
        hbox.addWidget(webcamButton)
        hbox.addWidget(channelButton)
        hbox.addWidget(resizeButton)
        hbox.addWidget(borderButton)
        hbox.addWidget(rectangleButton)
        hbox.addWidget(resetButton)
        hbox.addWidget(resizeButtonToWindow)
        
        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.scrollArea)
        
        container = QWidget()
        container.setLayout(vbox)
        self.setCentralWidget(container)

    def loadImage(self):
        options = QFileDialog.Options()
        fileName, _ = QFileDialog.getOpenFileName(self, "Загрузить фото", "", "Images (*.png *.jpg)", options=options)
        if fileName:
            fileName = os.path.abspath(fileName)
            try:
                # Открываем файл в бинарном режиме и читаем его содержимое
                with open(fileName, 'rb') as f:
                    file_bytes = np.asarray(bytearray(f.read()), dtype=np.uint8)
                    self.image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
                    
                if self.image is not None:
                    self.original_image = self.image.copy()
                    self.displayImage(self.image)
                else:
                    self.showErrorMessage("Ошибка загрузки: не удалось прочитать файл изображения.")
            except Exception as e:
                self.showErrorMessage(f"Ошибка загрузки: {str(e)}")
        else:
            self.showErrorMessage("Ошибка загрузки.")
    
    def captureFromWebcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.showErrorMessage("Не удалось подключиться к камере.")
            return
        
        cv2.namedWindow("press SPACE to capture", cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                self.showErrorMessage("Ошибка загрузки фото с камеры.")
                break

            cv2.imshow("press SPACE to capture", frame)

            key = cv2.waitKey(1)
            if key == 32:  # SPACE
                self.image = frame
                self.original_image = self.image.copy()
                self.displayImage(self.image)
                break
            elif key == 27:  # Escape
                break

        cap.release()
        cv2.destroyWindow("press SPACE to capture")

    def showColorChannel(self):
        if self.image is None:
            self.showErrorMessage("Фото не загружено.")
            return

        items = ("Красный", "Зелёный", "Синий")
        item, ok = QInputDialog.getItem(self, "Выберите канал", "Канал:", items, 0, False)
        
        if ok and item:
            channel = {"Красный": 2, "Зелёный": 1, "Синий": 0}[item]
            channel_image = np.zeros_like(self.image)
            channel_image[:, :, channel] = self.image[:, :, channel]
            self.displayImage(channel_image)

    def fitToWindow(self):
        if self.image is None:
            self.showErrorMessage("Фото не загружено.")
            return

        scroll_width = self.scrollArea.width()
        scroll_height = self.scrollArea.height()

        image_width = self.image.shape[1]
        image_height = self.image.shape[0]
        aspect_ratio = image_width / image_height

        new_width = scroll_width
        new_height = int(new_width / aspect_ratio)

        if new_height > scroll_height:
            new_height = scroll_height
            new_width = int(new_height * aspect_ratio)

        # Изменить размер фото
        resized_image = cv2.resize(self.image, (new_width, new_height))
        self.image = resized_image
        self.displayImage(self.image)

    def resizeImage(self):
        if self.image is None:
            self.showErrorMessage("Фото не загружено.")
            return

        width, ok1 = QInputDialog.getInt(self, "Изменить размер", "Ширина:", value=self.image.shape[1], min=1)
        height, ok2 = QInputDialog.getInt(self, "Изменить размер", "Высота:", value=self.image.shape[0], min=1)
        
        if ok1 and ok2:
            resized_image = cv2.resize(self.image, (width, height))
            self.image = resized_image
            self.displayImage(self.image)
        
    def addBorder(self):
        if self.image is None:
            self.showErrorMessage("Фото не загружено.")
            return

        border_size, ok = QInputDialog.getInt(self, "Добавить границы", "Введите толщину рамок:", min=0)
        if ok:
            bordered_image = cv2.copyMakeBorder(self.image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            self.image = bordered_image
            self.displayImage(self.image)

    def drawRectangle(self):
        if self.image is None:
            self.showErrorMessage("Фото не загружено.")
            return

        x, ok1 = QInputDialog.getInt(self, "Нарисовать прямоугольник", "Координаты по x:", min=0, max=self.image.shape[1])
        y, ok2 = QInputDialog.getInt(self, "Нарисовать прямоугольник", "Координаты по y:", min=0, max=self.image.shape[0])
        width, ok3 = QInputDialog.getInt(self, "Нарисовать прямоугольник", "Ширина:", min=0, max=self.image.shape[1] - x)
        height, ok4 = QInputDialog.getInt(self, "Нарисовать прямоугольник", "Высота:", min=0, max=self.image.shape[0] - y)

        if ok1 and ok2 and ok3 and ok4:
            cv2.rectangle(self.image, (x, y), (x + width, y + height), (255, 0, 0), 2)
            self.displayImage(self.image)

    def resetImage(self):
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.displayImage(self.image)
        else:
            self.showErrorMessage("Фото не загружено.")
            return

    def displayImage(self, img):
        qformat = QImage.Format_RGB888
        if len(img.shape) == 2:
            qformat = QImage.Format_Grayscale8

        img = QImage(img, img.shape[1], img.shape[0], img.strides[0], qformat)
        img = img.rgbSwapped()

        self.imageLabel.setPixmap(QPixmap.fromImage(img))
        self.imageLabel.adjustSize()

    def showErrorMessage(self, message):
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Ошибка")
        vbox = QVBoxLayout()
        label = QLabel(message, self)
        label.setAlignment(Qt.AlignCenter)
        vbox.addWidget(label)
        error_dialog.setLayout(vbox)
        error_dialog.exec_()  

if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = ImageProcessingApp()
    mainWindow.show()
    sys.exit(app.exec_())
