import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# โหลดไฟล์ Excel
file_path = r"D:\Users\admin\Desktop\final project\New folder\Book1.xlsx"  # เปลี่ยนเป็น path ของคุณ
df = pd.read_excel(file_path, header=None)

# ลบแถวที่มีค่า NaN
df_cleaned = df.dropna()

# แปลงข้อมูลคอลัมน์ 0 และ 1 ให้เป็นตัวเลข (ถ้ามีค่าไม่ใช่ตัวเลขจะกลายเป็น NaN)
df_cleaned.iloc[:, 0] = pd.to_numeric(df_cleaned.iloc[:, 0], errors='coerce')
df_cleaned.iloc[:, 1] = pd.to_numeric(df_cleaned.iloc[:, 1], errors='coerce')

# ลบค่า NaN ที่อาจเกิดขึ้นหลังจากแปลงข้อมูล
df_cleaned = df_cleaned.dropna()

# ใช้ข้อมูลจากคอลัมน์แรก (A) และคอลัมน์ที่สอง (B)
data_A = df_cleaned.iloc[:, 0]
data_B = df_cleaned.iloc[:, 1]

# สร้างกราฟ Density Plot
plt.figure(figsize=(8, 5))
sns.kdeplot(data_A, color='blue', fill=True, alpha=0.3, label="Column A")
sns.kdeplot(data_B, color='red', fill=True, alpha=0.3, label="Column B")

# ตั้งค่ากราฟ
plt.title("Density Plot of Column A and Column B")
plt.xlabel("Values")
plt.ylabel("Density")
plt.legend()
plt.grid()

# แสดงกราฟ
plt.show()