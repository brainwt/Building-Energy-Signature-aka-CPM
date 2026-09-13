function [Y] = fn_CPM_5p(x,Tout)

b0=x(1);
b1=x(2);
b2=x(3);
b3=x(4);
b4=x(5);

% Tout
[nrow, ncol]=size(Tout);
% AA = ones(nrow, ncol);

Y1=zeros(nrow, ncol);
Y2=zeros(nrow, ncol);
Y3=zeros(nrow, ncol);

idx1=find(b3 >= Tout);
idx2=find(b4 < Tout);
idx3=find( (b3 < Tout & b4 >= Tout) );

Y1(idx1) = b0 + b1*(b3-Tout(idx1));
Y2(idx2) = b0 + b2*(Tout(idx2)-b4);
Y3(idx3) = b0 + zeros(size(idx3));

Y=Y1+Y2+Y3;  

end

