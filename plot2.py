import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# โหลดไฟล์ Excel
file_path = r"D:\Users\admin\Desktop\final project\New folder\Book1.xlsx"  # เปลี่ยนเป็น path ของคุณ
df = pd.read_excel(file_path, header=None)

# ลบแถวที่มีค่า NaN
df_cleaned = df.dropna()

# ใช้ข้อมูลจาก 2 คอลัมน์แรก
data1 = pd.to_numeric(df_cleaned.iloc[:, 0], errors='coerce').dropna()  # คอลัมน์แรก
data2 = pd.to_numeric(df_cleaned.iloc[:, 1], errors='coerce').dropna()  # คอลัมน์ที่สอง

# คำนวณค่าเฉลี่ยและส่วนเบี่ยงเบนมาตรฐาน
mean1, std_dev1 = np.mean(data1), np.std(data1)
mean2, std_dev2 = np.mean(data2), np.std(data2)

# กำหนดช่วงของ x รอบ mean
x1 = np.linspace(mean1 - 3*std_dev1, mean1 + 3*std_dev1, 100)
x2 = np.linspace(mean2 - 3*std_dev2, mean2 + 3*std_dev2, 100)

# คำนวณ Gaussian distribution (Bell Curve ปกติ)
bell_curve1 = np.exp(-((x1 - mean1) ** 2) / (2 * std_dev1 ** 2))  # Bell Curve ปกติ
bell_curve2 = np.exp(-((x2 - mean2) ** 2) / (2 * std_dev2 ** 2))  # Bell Curve ปกติ

# สร้างกราฟ
plt.figure(figsize=(10, 5))
plt.plot(x1, bell_curve1, marker='o', linestyle='-', color='blue', label="Column 1 (Bell Curve)")
plt.plot(x2, bell_curve2, marker='o', linestyle='-', color='red', label="Column 2 (Bell Curve)")
plt.axvline(mean1, color='blue', linestyle='--', label="Mean 1")
plt.axvline(mean2, color='red', linestyle='--', label="Mean 2")

# ตั้งค่ากราฟ
plt.xlabel("X-axis")
plt.ylabel("Density")
plt.title("Comparison of Bell Curves from Two Columns")
plt.legend()
plt.grid()

# แสดงผล
plt.show()