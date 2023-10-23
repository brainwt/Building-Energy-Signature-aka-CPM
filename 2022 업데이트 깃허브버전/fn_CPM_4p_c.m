function [Y] = fn_CPM_4p_c(x,Tout)

b0=x(1);
b1=x(2);
b2=x(3);
b3=x(4);
% b4=x(5);

[nrow, ncol]=size(Tout);
% AA = ones(nrow, ncol);

Y1=zeros(nrow, ncol);
Y2=zeros(nrow, ncol);

idx1=find(b3 >= Tout); % 왼쪽
idx2=find(b3 < Tout); % 오른쪽

% Y1(idx1) = b0 - b1*(b3-Tout(idx1));
Y1(idx1) = b0 + b1*(Tout(idx1)-b3);
Y2(idx2) = b0 + b2*(Tout(idx2)-b3);
    
Y=Y1+Y2;  

end

