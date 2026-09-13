function [idx] = fn_CPM_cookd_plot(y, D, p)

% figure;
%subplot(1,2,2);

plot(y, D,'x','MarkerFaceColor','Red',...
    'MarkerEdgeColor','Red');
% xlabel('row number');


% 이상치
t_cookd  = 3 * mean(D,'omitnan');
hold on
plot(y, ones(size(y)) * t_cookd,'k:')
idx = find(D > t_cookd);

% if ~isempty(idx)
% for m=1: numel(idx) 
%     text(y(idx(m)),D(idx(m)),['O',num2str(idx(m))],'HorizontalAlignment','right', 'VerticalAlignment','bottom')            
% end
% else
% end
% legend('D','OL한계','Location','best')

% 영향점
n = numel(y);
inf_y  = 4  / (n-p-1);
hold on
plot(y, ones(size(y)) * inf_y,'c--')
idx = find(D > inf_y);
if ~isempty(idx)
for m=1: numel(idx) 
    text(y(idx(m)),D(idx(m)),['F',num2str(idx(m))],'HorizontalAlignment','right', 'VerticalAlignment','bottom','color','k')            
end
else
end
% 
% 높은 영향력
high_inf_y  = 1;
hold on
plot(y, ones(size(y)) * high_inf_y,'b--')
idx = find(D > high_inf_y);
if ~isempty(idx)
for m=1: numel(idx) 
    text(y(idx(m)),D(idx(m)),['H',num2str(idx(m))],'HorizontalAlignment','left', 'VerticalAlignment','top','color','k')
end
else
end

 legend('Cook d','d=3*avg(d)','d=4/(n-p-1)','d=1','Location','best')
%  legend('Cook d','3*AVG(d)','d>1','Location','best')

end
