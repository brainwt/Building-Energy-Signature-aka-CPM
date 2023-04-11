function [save_T_Ehc, y_pred, save_T_Ehc_mm] = fn_CPM_HC(save_T_stat,Tout)

% idx_md = save_T_stat.MD_RANK == 1;
% dataset = save_T_stat(idx_md,:);

save_T_Ehc = [];
save_T_Ehc_mm = [];

for m=1:size(save_T_stat,1)

    dataset = save_T_stat(m,:);

    CPM_type = dataset.CPM_TY{:};

    xset = [dataset.b0,dataset.b1, dataset.b2, dataset.b3, dataset.b4];

    switch CPM_type
        case '1p'
            p = 1;
            [y_pred] = fn_CPM_1p(xset,Tout);

            Eb = sum(y_pred);
            Eh = 0;
            Ec = 0;

            Eb_mm = y_pred;
            Eh_mm = ones(1,length(y_pred))*0;
            Ec_mm = ones(1,length(y_pred))*0;
    
        case '2p_h'
                % b0_0 : 좌측 기울기
                % b1_0 : 우측 상수항
    
            p = 2;
            [y_pred] = fn_CPM_2p_h(xset,Tout);

            Eb = 0;
            Eh = sum(y_pred);
            Ec = 0;

            Eb_mm = ones(1,length(y_pred))*0;
            Eh_mm = y_pred;
            Ec_mm = ones(1,length(y_pred))*0;
    
        case '2p_c'
                % b0_0 : 좌측 상수항
                % b1_0 : 우측 기울기
    
            p = 2;
            [y_pred] = fn_CPM_2p_c(xset,Tout);

            Eb = 0;
            Eh = 0;
            Ec = sum(y_pred);

            Eb_mm = ones(1,length(y_pred))*0;
            Eh_mm = ones(1,length(y_pred))*0;
            Ec_mm = y_pred;
    
        case '3p_h'
                % b0_0 : 상수항
                % b1_0 : 기울기
                % b2_0 : 변곡점
    
            p = 3;
    
            [y_pred] = fn_CPM_3p_h(xset,Tout);
    
%             Eb = sum( y_pred( Tout > xset(1,3) ) );
            Eb = sum(ones(1,length(y_pred))*xset(1));
            Eh = sum( y_pred( Tout <= xset(1,3)) - xset(1) ); % b2_0 = xset(1,3);
            Ec = 0;


            Eb_mm = ones(1,length(y_pred))*xset(1);
            Eh_mm = zeros(1,length(y_pred));
            Eh_mm(Tout <= xset(1,3)) = y_pred( Tout <= xset(1,3)) - xset(1) ;
            Ec_mm = ones(1,length(y_pred))*0;
    
        case '3p_c'
                % b0_0 : 상수항
                % b1_0 : 기울기
                % b2_0 : 변곡점
    
            p = 3;
            [y_pred] = fn_CPM_3p_c(xset,Tout);
    
            
%             Eb = sum( y_pred( Tout < xset(1,3) ) );
            Eb = sum(ones(1,length(y_pred))*xset(1));
            Eh = 0;
            Ec = sum( y_pred( Tout >= xset(1,3)) - xset(1) ); % b2_0 = xset(1,3);


            Eb_mm = ones(1,length(y_pred))*xset(1);
            Eh_mm = ones(1,length(y_pred))*0;
            
            Ec_mm = zeros(1,length(y_pred));
            Ec_mm(Tout >= xset(1,3)) = y_pred( Tout >= xset(1,3)) - xset(1);
    
        case '4p_h'
                % b0_0 : 상수항
                % b1_0 : 기울기 소
                % b2_0 : 기울기 대
                % b3_0 : 변곡점
    
            p = 4;
            [y_pred] = fn_CPM_4p_h(xset,Tout);
    
            Eh = 0;
            Ec = 0;
            Eb = 0;
    
        case '4p_c'
                % b0_0 : 상수항
                % b1_0 : 기울기 대
                % b2_0 : 기울기 소
                % b3_0 : 변곡점
    
            p = 4;
            [y_pred] = fn_CPM_4p_c(xset,Tout);
            
            Eh = 0;
            Ec = 0;
            Eb = 0;
    
        case '5p'
                % b0_0 : 상수항
                % b1_0 : 좌측 기울기
                % b2_0 : 우측 기울기
                % b3_0 : 좌측 변곡점
                % b4_0 : 우측 변곡점
            p = 5;
            [y_pred] = fn_CPM_5p(xset,Tout);

%             Eb = sum( y_pred( Tout >  xset(1,4) & Tout <= xset(1,5) ) );
            Eb = sum( ones(1,length(y_pred))*xset(1) ) ;
            Eh = sum( y_pred( Tout <= xset(1,4)) - xset(1) ) ; % b3_0 = xset(1,4);
            Ec = sum( y_pred( Tout >  xset(1,5)) - xset(1)  ) ; % b4_0 = xset(1,5);


            Eb_mm = ones(1,length(y_pred))*xset(1) ;

            Eh_mm = zeros(1,length(y_pred));
            Eh_mm(Tout <= xset(1,4)) = y_pred( Tout <= xset(1,4)) - xset(1) ; 

            Ec_mm = zeros(1,length(y_pred));
            Ec_mm(Tout >  xset(1,5)) = y_pred( Tout >  xset(1,5)) - xset(1) ; 
    
        otherwise
    end

    T_Ehc = table(Eh,Ec,Eb);
    save_T_Ehc = [save_T_Ehc ;T_Ehc];

    T_Ehc_mm = table((1:12)',Eb_mm',Eh_mm',Ec_mm');
    T_Ehc_mm.Properties.VariableNames = {'month','Eb','Eh','Ec'};
    save_T_Ehc_mm = [save_T_Ehc_mm ;T_Ehc_mm];


end


end



