# BE-sig :Building Energy signature Toolkit

### 사용법

#### 1 에너지 데이터 준비
- 파일 양식 (일별) : ```.\data input\Y_daily.csv``` 
- 파일 양식 (월별) : ```.\data input\Y_monthly.csv```
> 2015 ~ 2021 년만 입력 가능합니다. 다른 연-월-일 로 하는 경우 기상 파일을 먼저 수정하셈요.   

#### 2 기상 파일 준비
- 기상 파일 (일별): ".\data input\weather and holidays\" 폴더의 ``` T_weather_all_daily_2015 ~ 2021.csv ```
- 기상 파일 (월별): ".\data input\weather and holidays\" 폴더의 ``` T_weather_all_monthly_2015 ~ 2021.csv ```
- 기상 연도 설정 : 에너지 데이터 파일에 기입된 연월일 값을 토대로 자동으로 불러옵니다. 
  > 현재 2015 ~ 2021 년만 가능합니다. 다른 연-월-일 로 하는 경우 기상파일을 수정해서 쓰세욤.
- 지역 : ```Run_CPM_onebyone_f.m``` 파일의 **환경설정** 섹션에서, **% 3. 기상대 위치 설정** 을 잘하세욤.   

#### 3 매트랩 실행 
- ```Run_CPM_onebyone_f.m``` 파일을 실행하셈요.

