function [Y] = fn_CPM_3p_h(x,Tout)

b0=x(1);
b1=x(2);
b2=x(3);
% b3=x(4);
% b4=x(5);

[nrow, ncol]=size(Tout);
% AA = ones(nrow, ncol);

Y1=zeros(nrow, ncol);
Y2=zeros(nrow, ncol);

% Y=AA*b0;

idx1=find(b2 >= Tout);
idx2=find(b2 < Tout);

Y1(idx1) = b0 + b1*(b2-Tout(idx1));
Y2(idx2) = b0 + zeros(size(idx2)); 

Y=Y1+Y2;  

end

