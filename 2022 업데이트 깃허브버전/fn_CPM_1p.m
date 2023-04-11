function [Y] = fn_CPM_1p(x,Tout)
b0=x(1);
[nrow, ncol]=size(Tout);
AA = ones(nrow, ncol);

Y=b0*AA;

end

