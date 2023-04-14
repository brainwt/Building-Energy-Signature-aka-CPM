function [Y] = fn_CPM_2p(x,Tout)

b0=x(1);
b1=x(2);
% b2=x(3);
% b3=x(4);
% b4=x(5);

[nrow, ncol]=size(Tout);
AA = ones(nrow, ncol);

Y=b0*AA + b1*Tout;

end

