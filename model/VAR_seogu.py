# Vector Auto Regression
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from statsmodels.tsa.api import VAR
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

# 한글 폰트 설정
fe = fm.FontEntry(fname=r"font/NanumGothic.ttf", name="NanumGothic")
fm.fontManager.ttflist.insert(0, fe)  # Matplotlib에 폰트 추가
plt.rcParams.update({"font.size": 10, "font.family": "NanumGothic"})

# 데이터 불러오기
file_path = "data/data.xlsx"
sheets = ["동구", "중구", "서구", "유성구", "대덕구"]
data = {}

for sheet in sheets:
    data[sheet] = pd.read_excel(file_path, sheet_name=sheet)

seogu_data: pd.DataFrame = data["서구"]

# '시점' 열을 datetime 형식으로 변환
seogu_data["시점"] = pd.to_datetime(seogu_data["시점"], format="%Y.%m.%d")
seogu_data.set_index("시점", inplace=True)
seogu_data.index.freq = "MS"  # 명시적으로 빈도 설정

# 필요한 열만 선택
variables = ["인구수", "세대수", "사업체수", "주택거래량", "아파트거래량", "토지거래량"]
seogu_data = seogu_data[variables]

# 데이터 전처리: 결측치 제거 및 차분
seogu_data = seogu_data.dropna()
seogu_data_diff = seogu_data.diff().dropna()

# VAR 모델 학습
model = VAR(seogu_data_diff)
model_fit = model.fit(maxlags=15, ic="aic")

# 예측
forecast_steps = 36  # 예측할 기간 설정 (예: 3년)
lag_order = model_fit.k_ar
forecast_input = seogu_data_diff.values[-lag_order:]

forecast_diff = model_fit.forecast(y=forecast_input, steps=forecast_steps)
forecast_diff_df = pd.DataFrame(
    forecast_diff,
    index=pd.date_range(
        start=seogu_data.index[-1], periods=forecast_steps + 1, freq="MS"
    )[1:],
    columns=variables,
)

# 차분 역변환
last_observation = seogu_data.iloc[-1]
forecast = last_observation + forecast_diff_df.cumsum()

# 예측 결과 출력
print(forecast)

# 예측 데이터 엑셀 추가
forecast_copy = forecast.copy()
forecast_copy.reset_index(inplace=True)
forecast_copy.rename(columns={"index": "시점"}, inplace=True)
forecast_copy["시점"] = forecast_copy["시점"].dt.strftime("%Y-%m-%d")
file_path = "data/seogu_predict.xlsx"
with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
    forecast_copy.to_excel(writer, sheet_name="서구", index=False)


# 결과 시각화
plt.figure(figsize=(12, 6))
plt.title("예측:서구")
plt.plot(seogu_data["인구수"], label="실제 인구수:서구", color="blue")
plt.plot(forecast["인구수"], label="예측 인구수:서구", color="red")
plt.plot(seogu_data["세대수"], label="실제 세대수:서구", color="green")
plt.plot(forecast["세대수"], label="예측 세대수:서구", color="red")
plt.legend()
plt.show()


"""
데이터 성능 테스트
"""

# 데이터를 학습용과 테스트용으로 나누기
split_date = "2019-03-01"  # 70% 데이터에 해당하는 날짜
train_data = seogu_data[:split_date]
test_data = seogu_data[split_date:]

# 학습 데이터의 차분 계산
train_data_diff = train_data.diff().dropna()

# 데이터 포인트 수에 따른 maxlags 설정
n_obs = train_data_diff.shape[0]
maxlags = min(15, n_obs // 10)  # maxlags를 데이터 포인트 수의 10% 이하로 설정

# VAR 모델 학습
model = VAR(train_data_diff)
model_fit = model.fit(maxlags=maxlags, ic="aic")

# 테스트 데이터를 사용하여 예측
forecast_steps = len(test_data)
lag_order = model_fit.k_ar
forecast_input = train_data_diff.values[-lag_order:]

forecast_diff = model_fit.forecast(y=forecast_input, steps=forecast_steps)
forecast_diff_df = pd.DataFrame(
    forecast_diff,
    index=test_data.index,
    columns=variables,
)

# 차분 역변환
last_observation = train_data.iloc[-1]
forecast = last_observation + forecast_diff_df.cumsum()

# '인구수'와 '세대수'만 비교
actual_population = test_data["인구수"]
predicted_population = forecast["인구수"]
actual_households = test_data["세대수"]
predicted_households = forecast["세대수"]

# 평가 지표 계산
mae_population = mean_absolute_error(actual_population, predicted_population)
mse_population = mean_squared_error(actual_population, predicted_population)
rmse_population = np.sqrt(mse_population)
mape_population = (
    np.mean(np.abs((actual_population - predicted_population) / actual_population))
    * 100
)

mae_households = mean_absolute_error(actual_households, predicted_households)
mse_households = mean_squared_error(actual_households, predicted_households)
rmse_households = np.sqrt(mse_households)
mape_households = (
    np.mean(np.abs((actual_households - predicted_households) / actual_households))
    * 100
)

# 평가 결과 출력
print(f"인구수 예측 성능:")
print(f"MAE: {mae_population}")
print(f"MSE: {mse_population}")
print(f"RMSE: {rmse_population}")
print(f"MAPE: {mape_population}%")

print(f"\n세대수 예측 성능:")
print(f"MAE: {mae_households}")
print(f"MSE: {mse_households}")
print(f"RMSE: {rmse_households}")
print(f"MAPE: {mape_households}%")
