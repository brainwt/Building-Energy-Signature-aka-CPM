function [save_T_stat, C_cookd, C_ZRE] = fn_CPM_run_z(Tout, y_mea, pathnm_csv, pathnm_pics, Case_str, date_fr, date_to)

%% 문서 정보
% 작성자: 김덕우
% 작성일: 191206

%% nan 값의 처리
if sum(isnan(Tout)) > 1
    disp(['[fn_CPM_run] Tout 에 Nan 값이 있습니다. CASE:',Case_str])
elseif  sum(isnan(y_mea)) > 1
    disp(['[fn_CPM_run] y_mea 에 Nan 값이 있습니다. CASE:',Case_str])
else
   
end
    
Tout = fn_nan2zero(Tout);
y_mea = fn_nan2zero(y_mea);

% 주의 Tout과 y_mea는 1x12n 배열이어야함. 
% pathnm_pics
fnExistFolder(pathnm_pics);

%% CPM type 선택
CPM_type_list={'1p','2p_h','2p_c','3p_h','3p_c','4p_h','4p_c','5p'};
%  CPM_type_list={'2p_c'};
%   CPM_type_list={'2p_h'};
%   CPM_type_list={'5p'};
% CPM_type='1p';
% CPM_type={'2p'};
% CPM_type='3p_h';
% CPM_type='3p_c';
% CPM_type='4p_h';
% CPM_type='4p_c';
% CPM_type='5p';

%% 솔버기반 최적화
% 초기값 설정 - 매우 중요. 수렴값이 급격히 달라짐
Y_min=min(y_mea);
Y_max=max(y_mea);

To_lb= 5;
To_ub= 20;
    
% 상수초기값
b0_0 = 0;

% 좌측기울기초기값
% b1_0 = (Y_max-Y_min)/10;
b1_0 = 0;

% 우측기울기초기값
b2_0 = b1_0;

save_T_stat = [];

for m=1:length(CPM_type_list)
% for m=1:3
    CPM_type=CPM_type_list{m};
    f = @(x)fn_CPM_obj(x,Tout,y_mea,CPM_type);

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
%             lb=[0];
            lb=[-inf]; % 정규화 값이라서 음수가 나올수 있다.
            ub=[inf];
            nonlcon=[];

        case '2p_h'
            x0 = [b0_0  b1_0];  % b0, b1
            A = []; 
            b = [];
            Aeq=[];
            beq=[];
            lb=[-inf    0]; % 기울기는 음수 또는 양수 % https://www.sciencedirect.com/science/article/pii/S0378778814009645
            ub=[inf inf ];
            nonlcon=[];

        case '2p_c'
            x0 = [b0_0  b1_0];  % b0, b1
            A = []; 
            b = [];
            Aeq=[];
            beq=[];
            lb=[-inf     0]; % 기울기는 음수 또는 양수 % https://www.sciencedirect.com/science/article/pii/S0378778814009645
            ub=[inf inf ];
            nonlcon=[];
            
        case '3p_h'
            x0 = [b0_0  b1_0  (To_lb+To_ub)/2];  % b0, b1, b2
            A = [];   
            b = [];
            Aeq=[];
            beq=[];
%             lb=[0     0    To_lb];
            lb=[-inf     0    To_lb]; % 정규화 값이라서, 상수가 음수를 갖을 수 있다.
            ub=[inf inf   To_ub];
            nonlcon=[];

        case '3p_c'
            x0 = [b0_0  b1_0  (To_lb+To_ub)/2];  % b0, b1, b2
            A = [];  
            b = [];
            Aeq=[];
            beq=[];
%             lb=[0     0    To_lb]; 
            lb=[-inf     0    To_lb]; % 정규화 값이라서, 상수가 음수를 갖을 수 있다.
            ub=[inf inf   To_ub];
            nonlcon=[];
            
        case '4p_h'
            x0 = [b0_0  b1_0  b2_0  (To_lb+To_ub)/2];  % b0, b1, b2, b3
            %  A*x <= b              
            A = [0 -1 1 0];  % -b1+b2 <= 0
            b = [0];
            Aeq=[];
            beq=[];
%             lb=[0     0     0    To_lb];
            lb=[-inf    0     0    To_lb]; % 정규화 값이라서, 상수가 음수를 갖을 수 있다.
            ub=[inf inf   inf   To_ub];
            nonlcon=[];

        case '4p_c'
            x0 = [b0_0  b1_0  b2_0  (To_lb+To_ub)/2];  % b0, b1, b2, b3
            %  A*x <= b   
            A = [0 1 -1 0];  % -b1+b2 <= 0
            b = [0];
            Aeq=[];
            beq=[];
%             lb=[0     0     0    To_lb];
            lb=[-inf     0     0    To_lb]; % 정규화 값이라서, 상수가 음수를 갖을 수 있다.
            ub=[inf inf   inf   To_ub];
            nonlcon=[];        

        case '5p'
            x0 = [b0_0  b1_0  b2_0  To_lb+4  To_ub-4];  % b0, b1, b2, b3 15도, b4 15도
            A = [0      0  0  1  -1];  % b3 <= b4
            b = [0];
            Aeq=[];
            beq=[];
%             lb=[0     0     0    To_lb     To_lb]; % To_lb = 10
            lb=[-inf     0     0    To_lb     To_lb]; % 정규화 값이라서, 상수가 음수를 갖을 수 있다.
            ub=[inf inf   inf   To_ub    To_ub]; % To_lb = 20
            nonlcon=[];

        otherwise
    end

    %% 최적화
%     options = optimoptions('fmincon','Display','iter');
    options = optimoptions('fmincon');
    [x_opt,~,~,~]  = fmincon(f,x0,A,b,Aeq,beq,lb,ub,nonlcon,options);
    % RMSE_hat =fval;

    % 통계 추출
    [T_stat, ~, D, ~, ZRE, ~] = fn_CPM_stat(Case_str, CPM_type, x_opt, Tout, y_mea, date_fr,date_to );
    
    C_cookd(m,1) = {D};
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


