import json
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.font_manager as fm

# 한글 폰트 설정
fe = fm.FontEntry(fname=r"font/NanumGothic.ttf", name="NanumGothic")
fm.fontManager.ttflist.insert(0, fe)  # Matplotlib에 폰트 추가
plt.rcParams.update({"font.size": 10, "font.family": "NanumGothic"})

# GeoJSON 파일 경로
geojson_file = "data/SIG_WGS84_20220324.json"

# 필요한 SIG_CD 리스트
sig_cd_list = ["30110", "30140", "30170", "30200", "30230"]

# 엑셀 파일 경로
excel_file = "data/data.xlsx"
sheets = ["동구", "중구", "서구", "유성구", "대덕구"]
sig_cd_mapping = {
    "동구": "30110",
    "중구": "30140",
    "서구": "30170",
    "유성구": "30200",
    "대덕구": "30230",
}
dates = ["2011-01-01", "2016-01-01", "2021-01-01"]
predict_date = "2026-01-01"
predict_files = {
    "동구": "data/donggu_predict.xlsx",
    "중구": "data/junggu_predict.xlsx",
    "서구": "data/seogu_predict.xlsx",
    "유성구": "data/yuseonggu_predict.xlsx",
    "대덕구": "data/daedeokgu_predict.xlsx",
}

# GeoJSON 파일을 읽어와서 파싱
with open(geojson_file, "r", encoding="utf-8") as f:
    geojson_dict = json.load(f)

# GeoDataFrame으로 변환
gdf = gpd.GeoDataFrame.from_features(geojson_dict["features"])

# 필요한 SIG_CD에 해당하는 데이터만 선택
selected_gdf = gdf[gdf["SIG_CD"].isin(sig_cd_list)]

# 엑셀 데이터 읽기
data = {}
for sheet in sheets:
    data[sheet] = pd.read_excel(excel_file, sheet_name=sheet)

# '시점'에 따른 '세대수' 데이터를 가져오기
household_data = {date: {} for date in dates}
for sheet in sheets:
    df = data[sheet]
    for date in dates:
        household = df.loc[df["시점"] == date, "세대수"].values[0]
        sig_cd = sig_cd_mapping[sheet]
        household_data[date][sig_cd] = household

# 모든 날짜의 세대수 값을 모아 최소값과 최대값 계산
all_household_values = [pop for date in dates for pop in household_data[date].values()]
vmin = min(all_household_values)
vmax = max(all_household_values)

# 예측 데이터 읽기
predict_household_data = {}
for sheet in sheets:
    df = pd.read_excel(predict_files[sheet])
    household = df.loc[df["시점"] == predict_date, "세대수"].values[0]
    sig_cd = sig_cd_mapping[sheet]
    predict_household_data[sig_cd] = household

# 시각화
fig, axs = plt.subplots(1, 4, figsize=(26, 10))

# 색상 설정
cmap = plt.cm.Blues

for i, (ax, date) in enumerate(zip(axs[:3], dates)):
    selected_gdf["household"] = selected_gdf["SIG_CD"].apply(
        lambda x: household_data[date].get(x, 0)
    )

    # 세대수에 따른 색상 설정
    norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

    # 흰색 배경 설정
    ax.set_facecolor("white")

    # 경계선과 색상으로 채우기
    selected_gdf.boundary.plot(ax=ax, color="black")
    selected_gdf.plot(
        column="household",
        cmap=cmap,
        linewidth=0.8,
        ax=ax,
        edgecolor="black",
        norm=norm,
        legend=True,
    )
    year = date[:7]
    # 제목 설정
    ax.set_title(f"대전시 {year} 세대수")

# 예측 데이터 시각화
ax = axs[3]
selected_gdf["household"] = selected_gdf["SIG_CD"].apply(
    lambda x: predict_household_data.get(x, 0)
)

# 세대수에 따른 색상 설정
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

# 흰색 배경 설정
ax.set_facecolor("white")

# 경계선과 색상으로 채우기
selected_gdf.boundary.plot(ax=ax, color="black")
selected_gdf.plot(
    column="household",
    cmap=cmap,
    linewidth=0.8,
    ax=ax,
    edgecolor="black",
    norm=norm,
    legend=True,
)

predict_year = predict_date[:7]
# 제목 설정
ax.set_title(f"대전시 {predict_date} 예측 세대수")

# 지도 표시
plt.tight_layout()
plt.show()
