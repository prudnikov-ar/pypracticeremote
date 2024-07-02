import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout, QPushButton, QFileDialog,
                             QHBoxLayout, QDialog, QInputDialog, QScrollArea, QWidget)
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt
import cv2
import numpy as np

class ImageProcessingApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.image = None
        self.original_image = None

    def initUI(self):
        self.setWindowTitle('Image Processing App 1000x600')
        self.resize(1000, 600)

        self.imageLabel = QLabel(self)
        self.imageLabel.setAlignment(Qt.AlignCenter)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.imageLabel)
        self.scrollArea.setWidgetResizable(True)

        loadButton = QPushButton('Load Image', self)
        loadButton.clicked.connect(self.loadImage)
        
        webcamButton = QPushButton('Capture from Webcam', self)
        webcamButton.clicked.connect(self.captureFromWebcam)
        
        channelButton = QPushButton('Show Color Channel', self)
        channelButton.clicked.connect(self.showColorChannel)
        
        resizeButton = QPushButton('Resize Image', self)
        resizeButton.clicked.connect(self.resizeImage)
        
        borderButton = QPushButton('Add Border', self)
        borderButton.clicked.connect(self.addBorder)
        
        rectangleButton = QPushButton('Draw Recretangle', self)
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
        fileName, _ = QFileDialog.getOpenFileName(self, "Load Image", "", "Images (*.png *.jpg)", options=options)
        if fileName:
            self.image = cv2.imread(fileName)
            self.original_image = self.image.copy()
            self.displayImage(self.image)
        else:
            self.showErrorMessage("Failed to load image.")
    
    def captureFromWebcam(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.showErrorMessage("Failed to connect to webcam.")
            return
        
        cv2.namedWindow("Press Space to Capture", cv2.WINDOW_NORMAL)

        while True:
            ret, frame = cap.read()
            if not ret:
                self.showErrorMessage("Failed to capture image from webcam.")
                break

            cv2.imshow("Press Space to Capture", frame)

            key = cv2.waitKey(1)
            if key == 32:  # Space key
                self.image = frame
                self.original_image = self.image.copy()
                self.displayImage(self.image)
                break
            elif key == 27:  # Escape key
                break

        cap.release()
        cv2.destroyWindow("Press Space to Capture")

    def showColorChannel(self):
        if self.image is None:
            self.showErrorMessage("No image loaded.")
            return

        items = ("Red", "Green", "Blue")
        item, ok = QInputDialog.getItem(self, "Select Color Channel", "Channel:", items, 0, False)
        
        if ok and item:
            channel = {"Red": 2, "Green": 1, "Blue": 0}[item]
            channel_image = np.zeros_like(self.image)
            channel_image[:, :, channel] = self.image[:, :, channel]
            self.displayImage(channel_image)

    def fitToWindow(self):
        if self.image is None:
            self.showErrorMessage("No image loaded.")
            return

        # Get the size of the scroll area
        scroll_width = self.scrollArea.width()
        scroll_height = self.scrollArea.height()

        # Calculate the aspect ratio of the image
        image_width = self.image.shape[1]
        image_height = self.image.shape[0]
        aspect_ratio = image_width / image_height

        # Calculate new dimensions to fit within the scroll area
        new_width = scroll_width
        new_height = int(new_width / aspect_ratio)

        if new_height > scroll_height:
            new_height = scroll_height
            new_width = int(new_height * aspect_ratio)

        # Resize the image
        resized_image = cv2.resize(self.image, (new_width, new_height))
        self.image = resized_image
        self.displayImage(self.image)

    def resizeImage(self):
        if self.image is None:
            self.showErrorMessage("No image loaded.")
            return

        width, ok1 = QInputDialog.getInt(self, "Resize Image", "Enter width:", value=self.image.shape[1], min=1)
        height, ok2 = QInputDialog.getInt(self, "Resize Image", "Enter height:", value=self.image.shape[0], min=1)
        
        if ok1 and ok2:
            resized_image = cv2.resize(self.image, (width, height))
            self.image = resized_image
            self.displayImage(self.image)
        
    def addBorder(self):
        if self.image is None:
            self.showErrorMessage("No image loaded.")
            return

        border_size, ok = QInputDialog.getInt(self, "Add Border", "Enter border size:", min=0)
        if ok:
            bordered_image = cv2.copyMakeBorder(self.image, border_size, border_size, border_size, border_size, cv2.BORDER_CONSTANT, value=[0, 0, 0])
            self.image = bordered_image
            self.displayImage(self.image)

    def drawRectangle(self):
        if self.image is None:
            self.showErrorMessage("No image loaded.")
            return

        x, ok1 = QInputDialog.getInt(self, "Draw Rectangle", "Enter x coordinate:", min=0, max=self.image.shape[1])
        y, ok2 = QInputDialog.getInt(self, "Draw Rectangle", "Enter y coordinate:", min=0, max=self.image.shape[0])
        width, ok3 = QInputDialog.getInt(self, "Draw Rectangle", "Enter width:", min=0, max=self.image.shape[1] - x)
        height, ok4 = QInputDialog.getInt(self, "Draw Rectangle", "Enter height:", min=0, max=self.image.shape[0] - y)

        if ok1 and ok2 and ok3 and ok4:
            cv2.rectangle(self.image, (x, y), (x + width, y + height), (255, 0, 0), 2)
            self.displayImage(self.image)

    def resetImage(self):
        if self.original_image is not None:
            self.image = self.original_image.copy()
            self.displayImage(self.image)

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
        error_dialog.setWindowTitle("Error")
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

# import cv2

# def blure_face(img):
#     (h, w) = img.shape[:2]
#     dW = int(w/3.0)
#     dH = int(h/3.0)
#     if dW % 2 == 0:
#         dW -= 1
#     if dH % 2 == 0:
#         dH -= 1
#     return cv2.GaussianBlur(img, (dW, dH), 0)

# capture = cv2.VideoCapture(0)
# face = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")

# while True:
#     ret, img = capture.read()

#     faces = face.detectMultiScale(img, scaleFactor=1.5, minNeighbors=5, minSize=(20, 20))


#     for (x, y, w, h) in faces:
#         # cv2.rectangle(img, (x, y), (x+w, y+h), (255, 0, 0), 2)
#         img[y:y+h, x:x+w] = blure_face(img[y:y+h, x:x+w])

#     cv2.imshow("Andrew", img)

#     k = cv2.waitKey(30) & 0xFF
#     if k == 27:
#         break
# capture.release()
# cv2.destroyAllWindows()
