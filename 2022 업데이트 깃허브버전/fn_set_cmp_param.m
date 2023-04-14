function [x0,A,b,Aeq,beq,lb,ub,nonlcon] = fn_set_cmp_param(CPM_type, y_mea)
% 셋팅
To_lb= 0;
To_ub= 30;

% 회귀 파라메터 제약
Y_min=min(y_mea);
Y_max=max(y_mea);

% 1차셋팅
% b0_0 = median(y_mea, 'omitnan');
% b1_0 = (Y_max-Y_min)/100; % 
% b2_0 = b1_0;

% 2차셋팅
b0_0 = 0;  
b1_0 = 0; 
b2_0 = 0;


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
        A  = []; 
        b  = [];
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
end

