import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트 설정
fe = fm.FontEntry(fname=r"font/NanumGothic.ttf", name="NanumGothic")
fm.fontManager.ttflist.insert(0, fe)  # Matplotlib에 폰트 추가
plt.rcParams.update({"font.size": 10, "font.family": "NanumGothic"})

# 데이터 불러오기
file_path = "data/data.xlsx"
sheets = ["동구", "중구", "서구", "유성구", "대덕구"]
dfs = {sheet: pd.read_excel(file_path, sheet_name=sheet) for sheet in sheets}

# 데이터 합병
merged_df = pd.concat(dfs.values(), keys=dfs.keys())

# 상관관계 계산
correlation_matrix = merged_df.corr()

# 인구수와 세대수와의 상관관계 출력
population_correlation = correlation_matrix["인구수"]
household_correlation = correlation_matrix["세대수"]

print("인구수와의 상관관계:\n", population_correlation)
print("\n세대수와의 상관관계:\n", household_correlation)

# 히트맵으로 상관관계 시각화
plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap="coolwarm")
plt.title("상관관계 매트릭스")
plt.show()
