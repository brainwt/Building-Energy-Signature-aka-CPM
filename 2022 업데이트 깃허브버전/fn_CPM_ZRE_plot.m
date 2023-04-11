function [idx] = fn_CPM_ZRE_plot(x, ZRE)

% figure;
%subplot(1,2,2);

plot(x, ZRE,'x','MarkerFaceColor','Red',...
    'MarkerEdgeColor','Red');


% ±âÁØ¼± 
% REF = 3;
REF = 2.5;

hold on
plot(x, ones(size(x)) * REF,'k:')
plot(x, ones(size(x)) * -REF,'k:')
idx = find(ZRE > REF | ZRE < -REF);
legend('ZRE','ZRE=2.5','Location','best')
% plot(x, zeros(size(x))   ,'k:')

if ~isempty(idx)
for m=1: numel(idx) 
    text(x(idx(m)),ZRE(idx(m)),['O',num2str(idx(m))],'HorizontalAlignment','left', 'VerticalAlignment','bottom')            
end
else
end


end
