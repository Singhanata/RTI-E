import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# โหลดไฟล์ Excel (เปลี่ยนเป็น path ของคุณ)
file_path = r"D:\projects\Book1.xlsx"  # เปลี่ยนเป็น path ของคุณ
df = pd.read_excel(file_path, header=None)  # โหลดไฟล์โดยไม่มี header

# ลบแถวที่มีค่า NaN
df_cleaned = df.dropna()

# ใช้ข้อมูลจาก 2 คอลัมน์แรก
data1 = pd.to_numeric(df_cleaned.iloc[:, 0], errors='coerce').dropna()  # คอลัมน์แรก
data2 = pd.to_numeric(df_cleaned.iloc[:, 1], errors='coerce').dropna()  # คอลัมน์ที่สอง

# คำนวณค่าทางสถิติ
stats = {
    "Metric": ["Max", "Min", "Mean", "S.D."],
    "Column 1": [data1.max(), data1.min(), np.mean(data1), np.std(data1)],
    "Column 2": [data2.max(), data2.min(), np.mean(data2), np.std(data2)]
}

# แปลงเป็น DataFrame
df_stats = pd.DataFrame(stats)

# กำหนดช่วงของ x รอบค่าเฉลี่ย (Mean)
x1 = np.linspace(np.mean(data1) - 3*np.std(data1), np.mean(data1) + 3*np.std(data1), 100)
x2 = np.linspace(np.mean(data2) - 3*np.std(data2), np.mean(data2) + 3*np.std(data2), 100)

# คำนวณ Gaussian Distribution (Bell Curve)
bell_curve1 = np.exp(-((x1 - np.mean(data1)) ** 2) / (2 * np.std(data1) ** 2))  
bell_curve2 = np.exp(-((x2 - np.mean(data2)) ** 2) / (2 * np.std(data2) ** 2))  

# สร้างกราฟ
plt.figure(figsize=(12, 6))
plt.plot(x1, bell_curve1, marker='o', linestyle='-', color='blue', label="Column 1 (Bell Curve)")
plt.plot(x2, bell_curve2, marker='o', linestyle='-', color='red', label="Column 2 (Bell Curve)")
plt.axvline(np.mean(data1), color='blue', linestyle='--', label="Mean 1")
plt.axvline(np.mean(data2), color='red', linestyle='--', label="Mean 2")

# แสดงค่า Max, Min, Mean, และ S.D. บนกราฟ
text_x = min(x1[0], x2[0])  # ตำแหน่งของข้อความบนแกน X
plt.text(text_x, max(bell_curve1) * 0.8, 
         f"Column 1:\nMax: {data1.max():.2f}\nMin: {data1.min():.2f}\nMean: {np.mean(data1):.2f}\nS.D.: {np.std(data1):.2f}", 
         fontsize=10, color='blue', bbox=dict(facecolor='white', alpha=0.6))

plt.text(text_x, max(bell_curve2) * 0.6, 
         f"Column 2:\nMax: {data2.max():.2f}\nMin: {data2.min():.2f}\nMean: {np.mean(data2):.2f}\nS.D.: {np.std(data2):.2f}", 
         fontsize=10, color='red', bbox=dict(facecolor='white', alpha=0.6))

# ตั้งค่ากราฟ
plt.xlabel("X-axis")
plt.ylabel("Density")
plt.title("Comparison of Bell Curves from Two Columns")
plt.legend()
plt.grid()

# แสดงผล
plt.show()

# แสดงค่าสถิติในรูปแบบตาราง
print(df_stats)
