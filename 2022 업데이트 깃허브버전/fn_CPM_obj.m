function [y_hat] = fn_CPM_obj(x, Tout, y_mea,CPM_type)

switch CPM_type
    case '1p'
        p = 1;
        [y_pred] = fn_CPM_1p(x,Tout);
    case '2p_h'
        p = 2;
        [y_pred] = fn_CPM_2p_h(x,Tout);
        
    case '2p_c'
        p = 2;
        [y_pred] = fn_CPM_2p_c(x,Tout);
        
    case '3p_h'
        p = 3;
        [y_pred] = fn_CPM_3p_h(x,Tout);
    case '3p_c'
        p = 3;
        [y_pred] = fn_CPM_3p_c(x,Tout);
    case '4p_h'
        p = 4;
        [y_pred] = fn_CPM_4p_h(x,Tout);
    case '4p_c'
        p = 4;
        [y_pred] = fn_CPM_4p_c(x,Tout);
    case '5p'
        p = 5;
        [y_pred] = fn_CPM_5p(x,Tout);
    otherwise
end
    n_sample = length(y_pred);    
    
    % 옵션1
    RMSE = sqrt( sum( (y_mea - y_pred).^2 ) / (n_sample - p));
    y_hat = RMSE;
    

%     옵션2
%     ns = length(y_pred);   
%     y_avg = mean(y_mea, 'omitnan');
%     SSerr = sum( ( y_pred - y_mea ).^2 , 'omitnan') ;
%     SStot = sum( ( y_mea - y_avg  ).^2 , 'omitnan') +0.001 ;
%     y_hat =  SSerr/SStot;

      
end

