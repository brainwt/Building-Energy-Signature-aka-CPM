# Legacy — 기존 MATLAB 구현

Python 패키지(`src/besig/`)로 리팩토링되기 전의 MATLAB 원본입니다.
**참고용으로 보존**하며, 새 기능은 Python 쪽에만 추가됩니다.

## 구성

```
matlab/
├── Run_CPM_onebyone_f.mlx            # 메인 라이브스크립트 (원본, 바이너리)
├── Run_CPM_onebyone_f_extracted.m    # 위 .mlx에서 추출한 평문 코드 (읽기용)
├── fn_CPM_{1p,2p*,3p*,4p*,5p}.m      # 모델식 8종
├── fn_CPM_obj.m / fn_CPM_run*.m      # 목적함수 / 최적화 루프 3종
├── fn_CPM_run_MS.m                   # 멀티스타트 최적화 (아래 설명 참고)
├── fn_CPM_stat.m                     # 통계 지표
├── fn_CPM_plot*.m                    # 시각화
├── fn_CPM_HC.m                       # 난방/냉방 분해
└── fn_*.m                            # 보조 함수
BETTER 검증결과/                       # BETTER 도구와의 비교 결과
```

`Run_CPM_onebyone_f_extracted.m`은 `.mlx`(zip 컨테이너)의 코드 셀만 뽑아낸
것으로, 원본에 없던 파일입니다. 실행용이 아니라 **diff·코드리뷰용**입니다.
마크다운 셀은 `%%%% [스타일] 내용` 주석으로 표시했습니다.

## `fn_CPM_run_MS.m` — 멀티스타트 최적화

삭제된 `global-optimization` 브랜치(마지막 커밋 `850e31f`)에서 가져온 파일입니다.
`fn_CPM_run.m`을 복사해 최적화 부분만 바꾼 것으로, 단일 시작점 대신
MATLAB `MultiStart`를 씁니다.

```matlab
% --------- legacy 방식 ---------
% options = optimoptions('fmincon','Display','off');
% [x_opt,fval,...] = fmincon(f,x0,A,b,Aeq,beq,lb,ub,nonlcon,options);

% ---------  멀티스타트 방식 (230414) ---------
options = optimoptions('fmincon','Display','off','Algorithm','sqp');
problem = createOptimProblem('fmincon','objective',f,'x0',x0, ...);
rs = RandomStartPointSet('NumStartPoints',20,'ArtificialBound',10000);
ms = MultiStart;
[x_opt,fval] = run(ms,problem, rs);
```

원본의 초기값(기울기 계수 = 0)은 변곡점이 있는 모델에서 국소최적해에 갇힙니다.
이 파일은 그 문제를 다룬 **선행 구현**이며, Python 패키지의 기본 최적화 전략
`--strategy multistart`가 같은 접근을 따릅니다. 효과를 보이려고 함께 추가됐던
예제 자료 두 개는 `data/Y_monthly_41220-52882.csv`,
`data/Y_monthly_41670-100177112.csv`로 옮겨 회귀 테스트
(`tests/test_multistart_benefit.py`)에 쓰고 있습니다.

MATLAB 최적화 도구상자(Global Optimization Toolbox)가 있어야 실행됩니다.

## 실행하려면 경로 수정이 필요합니다

리팩토링 과정에서 자료 폴더가 옮겨졌습니다.

| 이전 | 현재 |
|---|---|
| `.\data input\Y_daily.csv` | `..\..\data\Y_daily.csv` |
| `.\data input\weather and holidays\` | `..\..\data\weather\` |
| `.\data input\csv_CPM\` , `.\data input\pics_CPM\` | (출력 폴더 — 원하는 곳으로) |

`Run_CPM_onebyone_f.mlx`의 **환경설정** 절과 `fn_CPM_date_index.m`
(기상 폴더 경로가 함수 안에 박혀 있습니다)을 위 표대로 고치면 동작합니다.

## 알려진 문제 (Python 버전에서 수정됨)

* `fn_CPM_run.m`, `fn_CPM_run_z.m`, `fn_CPM_run_unc.m`의 주석이 CP949로
  저장되어 UTF-8 환경에서 깨집니다.
* 변곡점 탐색 상한이 `fn_CPM_run.m`은 25, `fn_set_cmp_param.m`은 30으로
  어긋나 있습니다. 실제 실행 경로는 전자입니다.
* `fn_CPM_HC.m`의 `4p_h` / `4p_c` 분기가 시계열 변수
  (`Eb_mm`, `Eh_mm`, `Ec_mm`)를 만들지 않아, 4파라메터 모델로 호출하면
  "정의되지 않은 변수" 오류가 납니다.
* 기상 연도 2015–2021과 Windows 경로 구분자가 코드에 박혀 있습니다.
* 휴일 표 `T_oj_day_holi_2021.csv`가 빠져 있어 2021년 일별 분석이 실패합니다.
  (Python 버전은 요일을 날짜에서 직접 계산해 대체합니다.)
