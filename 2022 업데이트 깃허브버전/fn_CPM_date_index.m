function [date_index] = fn_CPM_date_index(Y)

%%
    % Duration 
    if numel(Y.USE_DATE{1}) == 6
        [y, ~, ~] = ymd(datetime(Y.USE_DATE,"InputFormat",'yyyyMM'));
    elseif numel(Y.USE_DATE{1}) == 8
        [y, ~, ~] = ymd(datetime(Y.USE_DATE,"InputFormat",'yyyyMMdd'));
    else 
        msg = 'ERROR : Check size of "Y.USE_DATE" '
        assert(false, msg)
    end

    
    date_start = min ( unique(y) );
    date_end   = max ( unique(y) );
    % date_end   = 2019;
    yrs_vec    = date_start : date_end;

%%
    if numel(Y.USE_DATE{1}) == 6
        % 연도별 색상 구분
        date_index = y;
    
    elseif numel(Y.USE_DATE{1}) == 8
        % 요일 데이터
        varNames = {'t',	    'DayNumber','DayName','locdate',    'dateName','isHoliday','Day_index'};
        varTypes = {'datetime',	'double',	'char',	  'datetime',	'char',	'char',	'double'};
        dataStartLine = 2;
        delimiter = ',';
        
        opts = delimitedTextImportOptions('VariableNames', varNames, ...
                                          'VariableTypes', varTypes,...
                                          'VariableNamingRule','preserve',...
                                          'DataLines', dataStartLine,...
                                          'Delimiter',delimiter); 
        
        
        T_days = [];
        for m = 1:numel(yrs_vec)
            fnm = ['T_oj_day_holi_',num2str(yrs_vec(m)),'.csv'];
            T_days0 = readtable(['.\data input\weather and holidays\',fnm],opts);
            T_days = [T_days ;T_days0];
        end
        
        Day_index = T_days.Day_index; % 1 평일, 2 토요일 3 일요일 및 휴일
        
        idx_week    = (Day_index ==1)';
        idx_weekend = (Day_index ~=1)';
        
        date_index = (T_days.DayName)'; % 
      
    end
end

