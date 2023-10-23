function [save_T_stat, C_cookd, C_ZRE] = fn_CPM_run_MS(Tout, y_mea, pathnm_csv, pathnm_pics, Case_str, date_fr, date_to)
% https://www.sciencedirect.com/science/article/pii/S0378778814009645

%% 문서 정보
% 작성자: 김덕우
% 작성일: 191206
    
% 주의사항
% Tout과 y_mea는 1x12n 배열이어야함. 

% 수정사항
% (220608) 기울기 제약을 해제. 이상치 탐색시 활용.
% (210302) 방학등 1% 이하의 사용량은 nan 으로 처리한다.
% (210302) 4parameter 모델은 고려하지 않음

%--------------------------------------------------
% (230417) GlobalSearch 별로 성능이 안좋음
% gs = GlobalSearch;
% [x_opt,fval] = run(gs,problem);    
%--------------------------------------------------

%% 폴더 체크
fnExistFolder(pathnm_pics);

%% 극소값 처리
% 220608 NaN 오류 로 인해서 미처리 : 하한 lb와 상한 ub는 NaN이 아니어야 합니다.
% y_mea( y_mea <= prctile(y_mea,1) ) = nan;
% idx= y_mea <= prctile(y_mea,1) & y_mea <= median(y_mea)/10;
% y_mea( idx ) = nan;


%% CPM type 선택
% CPM_type_list={'1p','2p_h','2p_c','3p_h','3p_c','4p_h','4p_c','5p'};
CPM_type_list={'1p','2p_h','2p_c','3p_h','3p_c','5p'};

%% 솔버기반 최적화
% 초기값 설정 - 매우 중요. 수렴값이 급격히 달라짐


% 외기 온도 탐색 범위 제약
% 1차 셋팅
% To_lb= 5;
% To_ub= 20;

% 2차 셋팅
% To_lb= 0;
% To_ub= 30;

% 3차 셋팅 (221212)
To_lb= 0;
To_ub= 25;

% 회귀 파라메터 제약

Y_min = min(y_mea);
Y_max = max(y_mea);

% 1차셋팅
% b0_0 = median(y_mea, 'omitnan');
% b1_0 = (Y_max-Y_min)/100; % 
% b2_0 = b1_0;

% 2차셋팅
b0_0 = 0;  
b1_0 = 0; 
b2_0 = 0;

save_T_stat = [];

for m=1:length(CPM_type_list)
% for m=1:3
    CPM_type=CPM_type_list{m};
%     CPM_type
    f = @(x)fn_CPM_obj(x, Tout, y_mea, CPM_type);

        %% 초기값 제약조건 설정
        % A = [1,2] 및 b = 1을 사용하여 A*x <= b 형식으로 선형 부등식 제약 조건을 나타냅니다.
        % Aeq = [2,1] 및 beq = 1을 사용하여 Aeq*x = beq 형식으로 선형 등식 제약 조건을 나타냅니다

    switch CPM_type
        case '1p'
            x0 = [b0_0 ];  % b0, b1
            A = []; 
            b = [];
            Aeq=[];
            beq=[];
            lb=[Y_min];
            ub=[Y_max];
            nonlcon=[];

        case '2p_h'
            % b0_0 : 좌측 기울기
            % b1_0 : 우측 상수항

            x0 = [b0_0  b1_0];             

            A = []; 
            b = [];
            Aeq=[];
            beq=[];
            
            lb=[0       Y_min]; % 기울기는 음수 또는 양수 % https://www.sciencedirect.com/science/article/pii/S0378778814009645
            ub=[inf     Y_max];
            nonlcon=[];

        case '2p_c'
            % b0_0 : 좌측 상수항
            % b1_0 : 우측 기울기

            x0 = [b0_0  b1_0];  % b0, b1
            A = []; 
            b = [];
            Aeq=[];
            beq=[];

            lb=[Y_min     0]; % 기울기는 음수 또는 양수 % https://www.sciencedirect.com/science/article/pii/S0378778814009645
            ub=[Y_max   inf];
            nonlcon=[];
            
        case '3p_h'
            % b0_0 : 상수항
            % b1_0 : 기울기
            % b2_0 : 변곡점

            x0 = [b0_0  b1_0  (To_lb+To_ub)/2];  % b0, b1, b2
            A = [];   
            b = [];
            Aeq=[];
            beq=[];
            lb=[Y_min     0      To_lb];
            ub=[Y_max    inf     To_ub];
            nonlcon=[];

        case '3p_c'
            % b0_0 : 상수항
            % b1_0 : 기울기
            % b2_0 : 변곡점

            x0 = [b0_0  b1_0  (To_lb+To_ub)/2];  % b0, b1, b2
            A  = [];  
            b  = [];
            Aeq= [];
            beq= [];
            lb = [Y_min     0   To_lb];
            ub = [Y_max   inf   To_ub];
            nonlcon=[];

        case '5p'
            % b0_0 : 상수항
            % b1_0 : 좌측 기울기
            % b2_0 : 우측 기울기
            % b3_0 : 좌측 변곡점
            % b4_0 : 우측 변곡점

            x0 = [b0_0  b1_0  b2_0  (To_lb+To_ub)/2  (To_lb+To_ub)/2]; 
%             x0 = [b0_0  b1_0  b2_0  To_lb  To_ub]; 
            A  = [0      0  0  1  -1];  % b3 <= b4
            b  = [0];
            Aeq= [];
            beq= [];
            lb = [Y_min      0     0   To_lb    To_lb]; % To_lb = 10
            ub = [Y_max    inf   inf   To_ub    To_ub]; % To_lb = 20
            nonlcon=[];

% ------------------------------------------------- %
        case '4p_h'
            % b0_0 : 상수항
            % b1_0 : 기울기 소
            % b2_0 : 기울기 대
            % b3_0 : 변곡점

            x0 = [b0_0  b1_0  b2_0  (To_lb+To_ub)/2];  % b0, b1, b2, b3
            %  A*x <= b              
            A = [0 -1 1 0];  % -b1+b2 <= 0
            b = [0];
            Aeq=[];
            beq=[];
            lb=[0     0     0   To_lb];
            ub=[inf inf   inf   To_ub];
            nonlcon=[];

        case '4p_c'
            % b0_0 : 상수항
            % b1_0 : 기울기 대
            % b2_0 : 기울기 소
            % b3_0 : 변곡점

            x0 = [b0_0  b1_0  b2_0  (To_lb+To_ub)/2];  % b0, b1, b2, b3
            %  A*x <= b   
            A = [0 1 -1 0];  % -b1+b2 <= 0
            b = [0];
            Aeq=[];
            beq=[];
            lb=[0     0     0   To_lb];
            ub=[inf inf   inf   To_ub];
            nonlcon=[];        
% ------------------------------------------------- %
        otherwise
    end

    %% 최적화

    % --------- legacy 버전 ---------
    % options = optimoptions('fmincon','Display','off');
    % [x_opt,fval,exitflag,output]  = fmincon(f,x0,A,b,Aeq,beq,lb,ub,nonlcon,options);
    
    % ---------  멀티스타트 버전 (230414) ---------
    options = optimoptions('fmincon','Display','off','Algorithm','sqp');
    problem = createOptimProblem('fmincon','objective',...
    f,'x0',x0,'Aineq',A,'bineq',b,'lb',lb,'ub',ub,'nonlcon',nonlcon,'options',options);

    % 잘됨
    rs = RandomStartPointSet('NumStartPoints',20,'ArtificialBound',10000); % ArtificialBound 디폴트 = 1000
    
    % % 시작점 시각화 : 보고싶은 사람만
    % points = list(rs,problem);
    % figure("Visible","off")
    % t=tiledlayout(3,2,'TileSpacing','Compact');
    % for k = 1:numel(x0)
    %     nexttile
    %     plot(points(:,k))
    %     hold on
    %     plot(x0(k),"Marker",'x','Color','r')
    %     title(['b',num2str(k)])
    % end
    % title(t,['CPM type : ', CPM_type])
    % xlabel(t,'samples')
    % 
    % pic_name = ['CPM_RandomStartPointSet_pk',Case_str];
    % saveas(gcf, [pathnm_pics, pic_name, num2str(date_fr), num2str(date_to)], 'png')
    
    ms = MultiStart;
    [x_opt,fval] = run(ms,problem, rs);
    
    %% 통계 추출
    [T_stat, Cook_out_idx, D, ~, ZRE, p ] = fn_CPM_stat(Case_str, CPM_type, x_opt, Tout, y_mea, date_fr,date_to );
    
    C_cookd(m,1) = {D};
%     C_cookd(m,1) = {Cook_out_idx};    
    C_ZRE(m,1) = {ZRE};

    % save opt x
    save_T_stat = [save_T_stat;T_stat];
        
end  
            
    %% 최종 모델 선택

    [~,p1] = sort(save_T_stat.RMSE);
    r1 = transpose( 1:length(save_T_stat.RMSE) );
    r1(p1) = r1;
    rank_md = [r1];

    [~,p2] = sort(rank_md);
    r2 = transpose( 1:length(rank_md) );
    r2(p2) = r2;
    MD_RANK = r2;
    
    % 랭크 저장
    save_T_stat.MD_RANK = MD_RANK;
    save_T_stat = movevars(save_T_stat, 'MD_RANK', 'Before', 'b0');
        
end


