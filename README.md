# ***BE-sig*** : ***B***uilding ***E***nergy ***sig***nature Toolkit

```
(230411) 드래프트입니다. 최종본이 아닙니다. 저에겐 아무런 책임이 없을 것... 입니다.

```


## 사용법

### 1 에너지 데이터 준비
- 파일 양식 (일별) : `.\data input\Y_daily.csv` 
- 파일 양식 (월별) : `.\data input\Y_monthly.csv`
> 2015 ~ 2021 년만 입력 가능합니다. 다른 연-월-일 로 하는 경우 기상 파일을 먼저 수정하셈요.   

### 2 기상 파일 준비
- 기상 파일 (일별): ".\data input\weather and holidays\" 폴더의 ` T_weather_all_daily_2015 ~ 2021.csv `
- 기상 파일 (월별): ".\data input\weather and holidays\" 폴더의 ` T_weather_all_monthly_2015 ~ 2021.csv `
- 기상 연도 설정 : 에너지 데이터 파일에 기입된 연월일 값을 토대로 자동으로 불러옵니다. 
  > 현재 2015 ~ 2021 년만 가능합니다. 다른 연-월-일 로 하는 경우 기상파일을 수정해서 쓰세욤.
- 지역 : `Run_CPM_onebyone_f.m` 파일의 **환경설정** 섹션에서, **% 3. 기상대 위치 설정** 을 잘하세욤.   

### 3 매트랩 실행 
- `Run_CPM_onebyone_f.m` 파일을 실행하셈요.

### 4 실행 결과 
- CPM 결과 (모델 정보) : ".\data input\csv_CPM\" 폴더의 ` CPM_Result_pk(건물명)(년도).txt ` 파일 입니다.
- CPM 결과 (산점도) : ".\data input\pics_CPM\" 폴더의 ` CPM_bestfit0_Tot_(daily 또는 monthly)_dayType_pk(건물명)(년도).png ` 파일 입니다.

### 5 CPM 결과 (모델 정보)
- ID    : 건물명 
- DATE_S: 에너지 사용 시작년도
- DATE_E: 에너지 사용 종료년도
- CPM_TY: CPM 모델 타입 
- MD_RANK	: 최저 모델 순위
- b0    	: 모델 계수 ([6 알고리즘 설명 참고](#6-알고리즘-설명-및-출처))
- b1    	: 모델 계수 ([6 알고리즘 설명 참고](#6-알고리즘-설명-및-출처))
- b2    	: 모델 계수 ([6 알고리즘 설명 참고](#6-알고리즘-설명-및-출처))
- b3    	: 모델 계수 ([6 알고리즘 설명 참고](#6-알고리즘-설명-및-출처))
- b4    	: 모델 계수 ([6 알고리즘 설명 참고](#6-알고리즘-설명-및-출처))
- ns    	: 샘플수
- RMSE    : RMSE
- NMBE    : NMBE
- CVRMSE  : CVRMSE
- R2_adj  : 조정된 R2
- pval_b_L: 기울기 계수의 p-value (왼쪽)
- pval_b_R: 기울기 계수의 p-value (오른쪽)
- pval_c_C: 상수항 계수의 p-value (별 의미없음)
- Ckd_out_idx: 이상치로 의심되는 샘플 번호 (쿡의 거리 기준) (예: 2 = 2번째 값)
- ZRE_out_idx: 이상치로 의심되는 샘플 번호 (잔차 거리 기준) (예: 2 = 2번째 값, zeros(1/0) = 해당사항 없음)
- P_M1    : 변곡점 인덱스 (봄철 월 또는 월일)
- P_M2    : 변곡점 인덱스 (가을철 월 또는 월일)
- R2      : R2
- Es      : 에너지원 명

### 6 알고리즘 설명 및 출처
- 알고리즘 설명 : https://www.mdpi.com/1890298
- Kim D-W, Ahn K-U, Shin H, Lee S-E. Simplified Weather-Related Building Energy Disaggregation and Change-Point Regression: Heating and Cooling Energy Use Perspective. Buildings. 2022; 12(10):1717


---
## 알고리즘 검증 (월별 데이터만 검증됨)
- LBNL의 BETTER 툴킷과 비교. (https://github.com/LBNL-JCI-ICF/better.git)
- 잠정 결론 : 둘 다 비슷하다. 다만, BETTER 툴은 4p 모델이 가끔 선택됨. 
- 결과 비교 : ".\BETTER 검증결과\" 폴더의 `결과비교_20230411.xlsx` 파일 참고 
```
  + 엑셀시트 summary (MATLAB vs BETTER) : 상세한 결과 비교표
  + 엑셀시트 R2 (MATLAB vs BETTER)      : R2만 따로 비교
  + 엑셀시트 app1 Y_data                : 입력된 에너지 사용량 값
  + 엑셀시트 app2 X_data                : 입력된 외기온 정보
  + 엑셀시트 app3 MATLAB cpm results only: BE-sig 상세 결과
  + 엑셀시트 app4 MATLAB cpm parameters : BE-sig 모델 설명
  + 엑셀시트 별도 체크 사항              : 그냥 주저리주저리
```


# Copyright
***BE-sig*** : ***B***uilding ***E***nergy ***sig***nature Toolkit Copyright (c) 2023
KICT (subject to receipt of any required approvals from South Korea MOLIT) All rights reserved.

If you have questions about your rights to use or distribute this code, please contact KICT at deukwookim@kict.re.kr.

NOTICE. This source code was developed under funding from the MOLIT South Korean Government consequently retains certain rights. As such, the South Korean Government has been granted for itself and others acting on its behalf a paid-up, nonexclusive, irrevocable, worldwide license in the code to reproduce, distribute copies to the public, prepare derivative works, and perform publicly and display publicly, and to permit other to do so.

끝.

