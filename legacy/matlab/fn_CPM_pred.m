function [y_pred, p, p_L, p_R, idx_L, idx_R, yint_L, yslp_L, yint_R, yslp_R] = fn_CPM_pred (CPM_type, x_opt, Tout)

%   자세한 설명 위치
switch CPM_type
    case '1p'
        p = 1;
        p_L=1;
        p_R=1;
        [y_pred] = fn_CPM_1p(x_opt,Tout);
        idx_L=find( 50 >= Tout);
        idx_R=find( -50 < Tout);
        
        yint_L = x_opt(1);
        yslp_L = 0;
        
        yint_R = x_opt(1);
        yslp_R = 0;
  
    case '3p_h'
        p = 3;
        p_L=2;
        p_R=1;
        [y_pred] = fn_CPM_3p_h(x_opt,Tout);
        idx_L=find(x_opt(3) >= Tout);
        idx_R=find(x_opt(3) < Tout);
        
        
        yint_L = x_opt(1) + x_opt(2)*x_opt(3);
        yslp_L = - x_opt(2);
        
        yint_R = x_opt(1);
        yslp_R = 0;
        
    case '3p_c'
        p = 3;
        p_L=1;
        p_R=2;
        [y_pred] = fn_CPM_3p_c(x_opt,Tout);
        idx_L=find(x_opt(3) >= Tout);
        idx_R=find(x_opt(3) < Tout);
        
        yint_L = x_opt(1) - x_opt(2)*x_opt(3);
        yslp_L = x_opt(2);
        
        yint_R = x_opt(1);
        yslp_R = 0;
    
    case '5p'
        p = 5;
        p_L=2;
        p_R=2;
        [y_pred] = fn_CPM_5p(x_opt,Tout);
        idx_L=find(x_opt(4) >= Tout);
        idx_R=find(x_opt(5) < Tout);
        
        yint_L = x_opt(1) + x_opt(2)*x_opt(4);
        yslp_L = - x_opt(2);
        
        yint_R = x_opt(1) - x_opt(3)*x_opt(5);
        yslp_R = x_opt(3);

    otherwise
end
end

