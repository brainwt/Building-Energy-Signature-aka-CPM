function [ ] = fn_CPM_plot_z(do_plot, save_T_stat, C_cookd, C_ZRE,  Tout, y_mea, pathnm_csv, pathnm_pics, Case_str, date_fr, date_to)
% [save_T_stat, mdl] = fn_CPM_run(Tout, y_mea, pathnm_csv, pathnm_pics, Case_str, do_plot,  date_fr, date_to)

% 주의 Tout과 y_mea는 1x12n 배열이어야함. 
% pathnm_pics
fnExistFolder(pathnm_pics);

%% CPM 선택
CPM_type_list={'1p','2p_h','2p_c','3p_h','3p_c','4p_h','4p_c','5p'};
%  CPM_type_list={'2p_c'};
%   CPM_type_list={'2p_h'};
%   CPM_type_list={'5p'};
% CPM_type='1p';
% CPM_type={'2p'};
% CPM_type='3p_h';
% CPM_type='3p_c';
% CPM_type='4p_h';
% CPM_type='4p_c';
% CPM_type='5p';
% close all

%%
% do_plot 1 : 그림.
% do_plot = input('시각화 Save? : [0]No, [1]Yes, -> ');

switch do_plot 
    case 0
         disp('No CPM plot')
         
    case 1
if do_plot == 0
    fig_vis = 'off';
    
elseif do_plot == 1
    fig_vis = 'on';  
    
end
%      fig_vis = 'off';   
         
         f1=figure('visible',fig_vis,'units','normalized','outerPosition',[0.05 0.1 0.9 0.8]);

        for m=1:length(CPM_type_list)
            CPM_type=CPM_type_list{m};

                subplot(2,4,m);
                idx= strcmp( save_T_stat.CPM_TY, CPM_type ) == 1;
                T_stat = save_T_stat(idx,:);
                x_opt(1) = T_stat.b0;
                x_opt(2) = T_stat.b1;
                x_opt(3) = T_stat.b2;
                x_opt(4) = T_stat.b3;
                x_opt(5) = T_stat.b4;      

                switch CPM_type
                    case '1p'               
                        [y_pred] = fn_CPM_1p(x_opt,Tout);
                        b0=x_opt(1);
                        scatter(Tout,y_mea,'k') 
                        hold on
                        Xset=[Tout];
                        Yset=[y_pred];
                        plot(Xset,Yset,'g.-', 'LineWidth' , 1.5)
                        text(min(Xset),b0,'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')
                         plot([min(Xset),min(Xset)],[0,0],'k:.') % FALSE LINE

                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end

                    case '2p_h'
                        [y_pred] = fn_CPM_2p_h(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);

                        scatter(Tout,y_mea,'k') 
                        hold on
                        Xset=[Tout];
                        Yset=[y_pred];
                        [B,I] = sort(Xset);

                        % 구역별 플롯
                        plot(B,Yset(I),'r.-', 'LineWidth' , 1.5)
                        text(median(Xset),median(Yset),['b1:',num2str(b1)],'HorizontalAlignment','left', 'VerticalAlignment','bottom')
                        
                        plot(0,b0,'k:.') % b0 라인
                        text(0,b0,'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')
                        
                        % y = b0-b1*Tout
                        plot([min(Xset),min(Xset)],[0,0],'k:.') % FALSE LINE

                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end
                    case '2p_c'
                        [y_pred] = fn_CPM_2p_c(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);

                        scatter(Tout,y_mea,'k') 
                        hold on
                        Xset=[Tout];
                        Yset=[y_pred];
                        [B,I] = sort(Xset);

                        % 구역별 플롯
                        plot(B,Yset(I),'b.-', 'LineWidth' , 1.5)
%                         text(median(Xset),median(Yset),'b1','HorizontalAlignment','right', 'VerticalAlignment','bottom')
                        text(median(Xset),median(Yset),['b1:',num2str(b1)],'HorizontalAlignment','right', 'VerticalAlignment','bottom')

                        plot(0,b0,'k:.') % b0 라인
                        text(0,b0,'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')

                        plot([min(Xset),min(Xset)],[0,0],'k:.') % FALSE LINE

                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end
                    case '3p_h'
                        [y_pred] = fn_CPM_3p_h(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);
                        b2=x_opt(3);

                        scatter(Tout ,y_mea,'k')  
                        hold on
                        Xset=[Tout,  b2];
                        Yset=[y_pred,b0]; 
                        [B,I] = sort(Xset);
                        BY=Yset(I);
                        % 구역별 플롯
                        plot(B(B<=b2),BY(B<=b2),'r.-', 'LineWidth' , 1.5)
                        plot(B(B>=b2),BY(B>=b2),'g.-', 'LineWidth' , 1.5)
                        text(median(B(B<b2)), median(BY(BY>b0 )), ['b1:',num2str(b1)],'HorizontalAlignment','left', 'VerticalAlignment','bottom')

                        plot([b2,b2],       [0, b0],'k:.') % b2 라인
                        text(b2,    b0/2                                ,'b2','HorizontalAlignment','left','VerticalAlignment','bottom')            

            %             plot([min(Xset),b2],[b0,b0],'k:.') % b0 라인
                        plot([min(Xset),max(Xset)],[b0,b0],'k:.') % b0 라인
                        text(min(Xset),b0, 'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')

                        % 구분월
                        [val1,idx1]=min( abs (Tout-b2) );
                        NR_M1 = Tout(idx1); % 가장 값이 가까운 월

                        plot(NR_M1,0,'k:v')           
                        text(NR_M1,0,['M',num2str(idx1)],'HorizontalAlignment','right', 'VerticalAlignment','bottom') 
                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end
                    case '3p_c'
                        [y_pred] = fn_CPM_3p_c(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);
                        b2=x_opt(3);

                        scatter(Tout ,y_mea,'k') 
                        hold on
                        Xset=[Tout,  b2];
                        Yset=[y_pred,b0]; 
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b2),BY(B<=b2),'g.-', 'LineWidth' , 1.5)
                        plot(B(B>=b2),BY(B>=b2),'b.-', 'LineWidth' , 1.5)
                        text(median(B(B>b2)), median(BY(BY>b0 )),['b1:',num2str(b1)],'HorizontalAlignment','left', 'VerticalAlignment','top')

                        plot([b2,b2],       [0, b0],'k:.') % b2 라인
                        text(b2,b0/2,'b2','HorizontalAlignment','left','VerticalAlignment','bottom')            

                        plot([min(Xset),max(Xset)],[b0,b0],'k:.') % b0 라인
                        text(min(Xset),b0, 'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')

                        % 구분월
                        [val1,idx1]=min( abs (Tout-b2) );
                        NR_M1 = Tout(idx1); % 가장 값이 가까운 월

                        plot(NR_M1,0,'k:v')           
                        text(NR_M1,0,['M',num2str(idx1)],'HorizontalAlignment','right', 'VerticalAlignment','bottom') 
                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end
                    case '4p_h'
                        [y_pred] = fn_CPM_4p_h(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);
                        b2=x_opt(3);
                        b3=x_opt(4);

                        scatter(Tout,y_mea,'k')
                        hold on
                        Xset=[Tout,b3];
                        Yset=[y_pred,b0];
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b3),BY(B<=b3),'r.-','LineWidth' , 1.5)
                        text(median(B(B<=b3)), median(BY(B<=b3)),['b1:',num2str(b1)],'HorizontalAlignment','left', 'VerticalAlignment','bottom')
                        plot(B(B>=b3),BY(B>=b3),'.-', 'Color',[0.9 0.5 0], 'LineWidth' , 1.5)
                        text(median(B(B>=b3)), median(BY(B>=b3)),'b2','HorizontalAlignment','left', 'VerticalAlignment','bottom')

                        % 보조축
            %             plot([min(Xset),b3],[b0,b0],'k:.')
                        plot([min(Xset),max(Xset)],[b0,b0],'k:.') % b0 라인
                        text(min(Xset),b0,'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')
                        plot([b3,b3],[0,b0],'k:.')
                        text(b3,b0/2,'b3','HorizontalAlignment','right','VerticalAlignment','bottom')            

                        % 구분월
                        [val1,idx1]=min( abs (Tout-b3) );
                        NR_M1 = Tout(idx1); % 가장 값이 가까운 월

                        plot(NR_M1,0,'k:v')           
                        text(NR_M1,0,['M',num2str(idx1)],'HorizontalAlignment','right', 'VerticalAlignment','bottom') 

                        % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end

                    case '4p_c'
                        [y_pred] = fn_CPM_4p_c(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);
                        b2=x_opt(3);
                        b3=x_opt(4);
            %             b4=x_opt(5);

                        scatter(Tout,y_mea,'k')
                        hold on
                        Xset=[Tout,b3];
                        Yset=[y_pred,b0];
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b3),BY(B<=b3),'.-', 'Color',[0,0.7,1],'LineWidth' , 1.5)
                        text(median(B(B<=b3)), median(BY(B<=b3)),['b1:',num2str(b1)],'HorizontalAlignment','left', 'VerticalAlignment','top')
                        plot(B(B>=b3),BY(B>=b3),'b.-', 'LineWidth' , 1.5)
                        text(median(B(B>=b3)), median(BY(B>=b3))    ,'b2','HorizontalAlignment','left', 'VerticalAlignment','top')

                        % 보조축
            %             plot([min(Xset),b3],[b0,b0],'k:.')
                        plot([min(Xset),max(Xset)],[b0,b0],'k:.') % b0 라인
                        text(min(Xset),b0,'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')
                        plot([b3,b3],[0,b0],'k:.')
                        text(b3,b0/2,'b3','HorizontalAlignment','right','VerticalAlignment','bottom')

                        % 구분월
                        [val1,idx1]=min( abs (Tout-b3) );
                        NR_M1 = Tout(idx1); % 가장 값이 가까운 월

                        plot(NR_M1,0,'k:v')           
                        text(NR_M1,0,['M',num2str(idx1)],'HorizontalAlignment','right', 'VerticalAlignment','bottom')            
                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end

                    case '5p'
                        [y_pred] = fn_CPM_5p(x_opt,Tout);

                        b0=x_opt(1);
                        b1=x_opt(2);
                        b2=x_opt(3);
                        b3=x_opt(4);
                        b4=x_opt(5);

                        scatter(Tout,y_mea,'k')
                        hold on
                        Xset=[Tout,b3,b4];
                        Yset=[y_pred,b0,b0];
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b3),BY(B<=b3),'r.-', 'LineWidth' , 1.5)
                        text(median(B(B<=b3)), median(BY(B<=b3)),['b1:',num2str(b1)],'HorizontalAlignment','left', 'VerticalAlignment','bottom')
                        plot(B(B>=b3 & B<=b4), BY(B>=b3 & B<=b4),'g.-', 'LineWidth' , 1.5)

                        plot(B(B>=b4),BY(B>=b4),'b.-', 'LineWidth' , 1.5)
                        text(median(B(B>=b4)), median(BY(B>=b4))    ,'b2','HorizontalAlignment','left', 'VerticalAlignment','top')

                        % 보조축
                        plot([min(Xset),max(Xset)],[b0,b0],'k:.') % b0 라인
                        text(min(Xset),b0,'b0','HorizontalAlignment','right', 'VerticalAlignment','bottom')

                        plot([b3,b3],[0,b0],'k:.')
                        text(b3,b0/2,'b3','HorizontalAlignment','right','VerticalAlignment','bottom')

                        plot([b4,b4],[0,b0],'k:.')           
                        text(b4,b0/2,'b4','HorizontalAlignment','left', 'VerticalAlignment','bottom')            

                        % 구분월
                        [val1,idx1]=min( abs (Tout-b3) );
                        [val2,idx2]=min( abs (Tout-b4) );
                        NR_M1 = Tout(idx1); % 가장 값이 가까운 월
                        NR_M2 = Tout(idx2);

                        plot(NR_M1,0,'k:v')           
                        text(NR_M1,0,['M',num2str(idx1)],'HorizontalAlignment','right', 'VerticalAlignment','bottom')            

                        plot(NR_M2,0,'k:v')           
                        text(NR_M2,0,['M',num2str(idx2)],'HorizontalAlignment','left', 'VerticalAlignment','bottom')            

                         % y 가 0 인 경우
                         ax = gca;
                         y_ax = ax.YLim;
                         if y_ax(2) < 1
                             y_ax(2) = 1;
                             ax.YLim = y_ax;
                         else
                         end
                    otherwise
                end

                    % 그림 최종 설정
                    grid on
                    ax= gca;
                    xticks([min(ax.XTick):5:max(ax.XTick)])
                    xlabel('Temperature [^oC]')
                    ylabel('normalized [-]')
                    title({ ['PK:',Case_str,' /TYPE:',CPM_type];...
                            ['CVRMSE: ', num2str(round(T_stat.CVRMSE,1))] })

        end
            saveas(f1, [pathnm_pics, 'CPM_','pk', Case_str,'_date_', num2str(date_fr), '-', num2str(date_to)], 'png')                


% 
%         f2=figure('visible',fig_vis,'units','normalized','outerPosition',[0.05 0.1 0.9 0.8]);
%         for m=1:length(CPM_type_list)
%             CPM_type=CPM_type_list{m};
%             %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%             p = size(x_opt,2);
%             % cook의 거리 계산
%         %     figure(f2);
%             %             if do_plot == 1
%             %             else
%             %                 set(gcf,'Visible','off')
%             %             end
%             subplot(2,4,m);
%             D=C_cookd{m,1};
%             [~] = fn_CPM_cookd_plot(Tout',D, p);
%             grid on
%             xlabel('X variables')
%             ylabel('Cook''s distance');
%             title({ ['PK:',Case_str,' /TYPE:',CPM_type];...
%             ['Cook''s distance plot']})        
%         end
%             saveas(f2, [pathnm_pics, 'CPM_cookd_','pk', Case_str,'_date_', num2str(date_fr), '-', num2str(date_to)], 'png')
% 
%         f3=figure('visible',fig_vis,'units','normalized','outerPosition',[0.05 0.1 0.9 0.8]);
%         for m=1:length(CPM_type_list)
%             CPM_type=CPM_type_list{m};
%         %     figure(f3);
%             subplot(2,4,m);
%             ZRE=C_ZRE{m,1};
%             [~] = fn_CPM_ZRE_plot(Tout',ZRE);            
%             grid on
%             xlabel('X variables')
%             ylabel('Standadized Residual');
%             title({ ['PK:',Case_str,' /TYPE:',CPM_type];...
%             ['Standadized residual plot']})
%         end
%             saveas(f3, [pathnm_pics, 'CPM_ZRE_','pk', Case_str,'_date_', num2str(date_fr), '-', num2str(date_to)], 'png')
%        
%     otherwise
%         disp(['CPM plot commend error, do_plot:', num2str(do_plot)])
% end

% MATLAB 검증용
% for m=1:length(CPM_type_list)
%     CPM_type=CPM_type_list{m};
%             subplot(2,4,m);
%             mdl = fitlm(Tout,y_mea);
%             plotDiagnostics(mdl,'cookd')
%             legend('show') % Show the legend
% end
end  



