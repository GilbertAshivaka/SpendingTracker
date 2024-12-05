import sys
from PyQt6.QtWidgets import (QMainWindow, QApplication, QLabel, QPushButton, QVBoxLayout, 
                             QHBoxLayout, QTextEdit, QTableWidget, QTableWidgetItem, QDialog, 
                             QLineEdit, QComboBox, QFormLayout, QDateEdit, QMessageBox, QWidget)

from PyQt6.QtCore import Qt, QDate
import sqlite3

def initializeDatabase():
    conn = sqlite3.connect("finance_tracker.db")
    cursor = conn.cursor()
    cursor.execute("""
                   CREATE TABLE IF NOT EXISTS transactions(
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT,
                   category TEXT,
                   amount REAL,
                   description TEXT
                   )
                   """)
    conn.commit()
    conn.close()


class AddTransactionDialog(QDialog):
    def __init__(self, parent =None):
        super().__init__(parent)

        self.setWindowTitle("Add Transaction")
        self.setModal(True)
        self.setFixedSize(300, 200)

        #FormLayout
        formLayout = QFormLayout()
        self.dateInput = QDateEdit()
        self.dateInput.setDate(QDate.currentDate())
        self.dateInput.setCalendarPopup(True)

        self.categoryInput = QComboBox()
        self.categoryInput.addItems(["Food", "Utilities", "Transport", "Entertainment", "Others"])
        
        self.amountInput = QLineEdit()
        self.amountInput.setPlaceholderText("Amount")

        self.description = QLineEdit()
        self.description.setPlaceholderText("Description(optional)")

        #adding the items to the layout
        formLayout.addRow("Date:", self.dateInput)
        formLayout.addRow("Category: ", self.categoryInput)
        formLayout.addRow("Amount:", self.amountInput)
        formLayout.addRow("Description:", self.description)

        #buttons 
        buttonLayout = QHBoxLayout()
        self.addButton = QPushButton("Add")
        self.addButton.clicked.connect(self.addTransaction)
        self.cancelButton = QPushButton("Cancel")
        self.cancelButton.clicked.connect(self.reject)
        #adding to the layout 
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.cancelButton)

        #mainLayout
        mainLayout = QVBoxLayout()
        mainLayout.addLayout(formLayout)
        mainLayout.addLayout(buttonLayout)
        self.setLayout(mainLayout)

    def addTransaction(self):
        date = self.dateInput.text()
        category = self.categoryInput.currentText()
        
        try:
            amount = float(self.amountInput.text())
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid amount.")
            return
        
        description = self.description.text()

        conn = None
        try:
            conn = sqlite3.connect("finance_tracker.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO transactions(date, category, amount, description) VALUES(?,?,?,?)", 
                        (date, category, amount, description))
            conn.commit()
            self.accept()
        
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"Failed to add transaction: {str(e)}")
        
        finally:
            if conn:
                conn.close()
                
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Tracker")
        self.setGeometry(100, 100, 600, 400)

        mainLayout = QVBoxLayout()

        self.dashBoardLabel = QLabel("Welcome, track your spending habits")
        self.dashBoardLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mainLayout.addWidget(self.dashBoardLabel)

        #table for bdisplaying transactions 
        self.transactionTable = QTableWidget()
        self.transactionTable.setHorizontalHeaderLabels(["Date", "Category", "Amount", "Description"])
        self.transactionTable.horizontalHeader().setStretchLastSection(True)

        mainLayout.addWidget(self.transactionTable)

        #the buttons 
        buttonLayout = QHBoxLayout()
        self.addButton = QPushButton("Add Transaction")
        self.addButton.clicked.connect(self.openAddTransactionDialog)
        self.refreshButton = QPushButton("Refresh")
        self.refreshButton.clicked.connect(self.loadTransactions)
        buttonLayout.addWidget(self.addButton)
        buttonLayout.addWidget(self.refreshButton)

        mainLayout.addLayout(buttonLayout)

        #central Widget
        centralWidget = QLabel()
        centralWidget.setLayout(mainLayout)
        self.setCentralWidget(centralWidget)

        #initialize the data 
        self.loadTransactions()

    def openAddTransactionDialog(self):
        dialog = AddTransactionDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.loadTransactions()
    
    def loadTransactions(self):
        conn = None
        try:
            conn = sqlite3.connect("finance_tracker.db")
            cursor = conn.cursor()
            cursor.execute("SELECT date, category, amount, description FROM transactions")
            rows = cursor.fetchall()
            
            self.transactionTable.setRowCount(len(rows))

            for rowIndex, rowData in enumerate(rows):
                for columnIndex, data in enumerate(rowData):
                    self.transactionTable.setItem(rowIndex, columnIndex, QTableWidgetItem(str(data)))
        
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Database Error", f"An error occurred: {str(e)}")
        
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    initializeDatabase()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
        
