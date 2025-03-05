import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# โหลดไฟล์ Excel
file_path = r"D:\projects\Book1.xlsx"  # เปลี่ยนเป็น path ของคุณ
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

# คำนวณค่าทางสถิติ
stats = {
    "Metric": ["Max", "Min", "Mean", "S.D."],
    "Column A": [data_A.max(), data_A.min(), np.mean(data_A), np.std(data_A)],
    "Column B": [data_B.max(), data_B.min(), np.mean(data_B), np.std(data_B)]
}

# แปลงเป็น DataFrame
df_stats = pd.DataFrame(stats)

# สร้างกราฟ Density Plot
plt.figure(figsize=(10, 6))
sns.kdeplot(data_A.dropna(), color='blue', fill=True, alpha=0.3, label="Column A")
sns.kdeplot(data_B.dropna(), color='red', fill=True, alpha=0.3, label="Column B")

# แสดงค่า Max, Min, Mean, S.D. บนกราฟ
text_x = min(data_A.min(), data_B.min())  # ตำแหน่งข้อความบนแกน X
plt.text(text_x, 0.06, 
         f"Column A:\nMax: {data_A.max():.2f}\nMin: {data_A.min():.2f}\nMean: {np.mean(data_A):.2f}\nS.D.: {np.std(data_A):.2f}", 
         fontsize=10, color='blue', bbox=dict(facecolor='white', alpha=0.6))

plt.text(text_x, 0.045, 
         f"Column B:\nMax: {data_B.max():.2f}\nMin: {data_B.min():.2f}\nMean: {np.mean(data_B):.2f}\nS.D.: {np.std(data_B):.2f}", 
         fontsize=10, color='red', bbox=dict(facecolor='white', alpha=0.6))

# ตั้งค่ากราฟ
plt.title("Density Plot of Column A and Column B")
plt.xlabel("Values")
plt.ylabel("Density")
plt.legend()
plt.grid()

# แสดงกราฟ
plt.show()

# แสดงค่าสถิติในรูปแบบตาราง
print(df_stats)
