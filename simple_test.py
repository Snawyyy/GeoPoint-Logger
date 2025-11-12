import sys
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout

app = QApplication(sys.argv)

window = QWidget()
window.setWindowTitle('Simple Test')
window.setGeometry(100, 100, 300, 200)

layout = QVBoxLayout()
label = QLabel('PyQt5 is working!')
layout.addWidget(label)
window.setLayout(layout)

window.show()
sys.exit(app.exec_())