
function [X_array, idx] = fn_nan2zero(X_array)

% [row, col]= find( isnan(X_array) == 1);
% X_array(row, col) = 0;
idx = find( isnan(X_array) == 1);
X_array(idx) = 0;


end