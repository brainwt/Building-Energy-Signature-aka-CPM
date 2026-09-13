function [ ] = fn_CPM_plot(do_plot, save_T_stat, C_cookd, C_ZRE,  Tout, y_mea, pathnm_csv, pathnm_pics, Case_str, date_fr, date_to, y_origin)
%% 주의 Tout과 y_origin는 1x12n 배열이어야함. 


% (210302) 방학등 1% 이하의 사용량은 nan 으로 처리한다.
% y_mea( y_mea <= prctile(y_mea,1) ) = nan;
% idx= y_mea <= prctile(y_mea,1) & y_mea <= median(y_mea)/10;
% y_mea( idx ) = nan;
% (220608) nan 처리시 오류 발생하므로 중지

% idx = save_T_stat.MD_RANK == 1;
% str_CPM_TY = save_T_stat.CPM_TY {idx};


%% y_origin nan 값은 0으로 해서 보여줌
[~, idx_nan] = fn_nan2zero(y_mea);
fnExistFolder(pathnm_pics);

%% CPM 선택
% (210302) 4parameter 모델은 고려하지 않음
% CPM_type_list={'1p','2p_h','2p_c','3p_h','3p_c','4p_h','4p_c','5p'};
% CPM_type_list={'2p_h','2p_c','3p_h','3p_c','5p'};
CPM_type_list={'1p','2p_h','2p_c','3p_h','3p_c','5p'};

%%
% do_plot 1 : 그림.
% do_plot = input('시각화 Save? : [0]No, [1]Yes, -> ');

switch do_plot 
    case 0
         disp('No CPM plot')
         
    case 1
%         fig_vis = 'off';
%         fig_vis = 'on';  
       
%         figure('visible',fig_vis,'units','normalized','outerPosition',[0.05 0.1 0.9 0.8]);
        for m=1:length(CPM_type_list)
            CPM_type=CPM_type_list{m};

        %         figure(f1);
                subplot(2,4,m);
                idx= strcmp( save_T_stat.CPM_TY, CPM_type ) == 1;
                T_stat = save_T_stat(idx,:);
                x_opt(1) = T_stat.b0;
                x_opt(2) = T_stat.b1;
                x_opt(3) = T_stat.b2;
                x_opt(4) = T_stat.b3;
                x_opt(5) = T_stat.b4;      
                
%                 scatter(Tout,y_origin,'k') 
                scatter(Tout, y_origin,'MarkerFaceColor',[0 0.4470 0.7410], 'MarkerEdgeAlpha', 0.5) 
                hold on
                scatter(Tout(idx_nan),y_origin(idx_nan), 'MarkerFaceColor', 'r') 

                switch CPM_type
                    case '1p'               
                        [y_pred] = fn_CPM_1p(x_opt,Tout);
                        b0=x_opt(1);
%                         scatter(Tout,y_origin,'k')                         
                        hold on
                        Xset=[Tout];
                        Yset=[y_pred];
                        plot(Xset, Yset,'g.-', 'LineWidth' , 1.5)
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

%                         scatter(Tout,y_origin,'k') 
                        hold on
                        Xset=[Tout];
                        Yset=[y_pred];
                        [B,I] = sort(Xset);

                        % 구역별 플롯
                        plot(B,Yset(I),'r.-', 'LineWidth' , 1.5)
                        text(median(Xset),median(Yset),'b1','HorizontalAlignment','left', 'VerticalAlignment','bottom')

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

%                         scatter(Tout,y_origin,'k') 
                        hold on
                        Xset=[Tout];
                        Yset=[y_pred];
                        [B,I] = sort(Xset);

                        % 구역별 플롯
                        plot(B,Yset(I),'b.-', 'LineWidth' , 1.5)
                        text(median(Xset),median(Yset),'b1','HorizontalAlignment','right', 'VerticalAlignment','bottom')

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

%                         scatter(Tout ,y_origin,'k')
                        hold on
                        Xset=[Tout,  b2];
                        Yset=[y_pred,b0]; 
                        [B,I] = sort(Xset);
                        BY=Yset(I);
                        % 구역별 플롯
                        plot(B(B<=b2),BY(B<=b2),'r.-', 'LineWidth' , 1.5)
                        plot(B(B>=b2),BY(B>=b2),'g.-', 'LineWidth' , 1.5)
                        text(median(B(B<b2)), median(BY(BY>b0 ))    ,'b1','HorizontalAlignment','left', 'VerticalAlignment','bottom')

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

%                         scatter(Tout ,y_origin,'k') 
                        hold on
                        Xset=[Tout,  b2];
                        Yset=[y_pred,b0]; 
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b2),BY(B<=b2),'g.-', 'LineWidth' , 1.5)
                        plot(B(B>=b2),BY(B>=b2),'b.-', 'LineWidth' , 1.5)
                        text(median(B(B>b2)), median(BY(BY>b0 ))     ,'b1','HorizontalAlignment','left', 'VerticalAlignment','top')

                        plot([b2,b2],       [0, b0],'k:.') % b2 라인
                        text(b2,    b0/2                              ,'b2','HorizontalAlignment','left','VerticalAlignment','bottom')            

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

%                         scatter(Tout,y_origin,'k')
                        hold on
                        Xset=[Tout,b3];
                        Yset=[y_pred,b0];
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b3),BY(B<=b3),'r.-','LineWidth' , 1.5)
                        text(median(B(B<=b3)), median(BY(B<=b3))    ,'b1','HorizontalAlignment','left', 'VerticalAlignment','bottom')
                        plot(B(B>=b3),BY(B>=b3),'.-', 'Color',[0.9 0.5 0], 'LineWidth' , 1.5)
                        text(median(B(B>=b3)), median(BY(B>=b3))    ,'b2','HorizontalAlignment','left', 'VerticalAlignment','bottom')

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

%                         scatter(Tout,y_origin,'k')
                        hold on
                        Xset=[Tout,b3];
                        Yset=[y_pred,b0];
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b3),BY(B<=b3),'.-', 'Color',[0,0.7,1],'LineWidth' , 1.5)
                        text(median(B(B<=b3)), median(BY(B<=b3))    ,'b1','HorizontalAlignment','left', 'VerticalAlignment','top')
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

%                         scatter(Tout,y_origin,'k')
                        hold on
                        Xset=[Tout,b3,b4];
                        Yset=[y_pred,b0,b0];
                        [B,I] = sort(Xset);
                        BY=Yset(I);

                        % 구역별 플롯
                        plot(B(B<=b3),BY(B<=b3),'r.-', 'LineWidth' , 1.5)
                        text(median(B(B<=b3)), median(BY(B<=b3))    ,'b1','HorizontalAlignment','left', 'VerticalAlignment','bottom')
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
%                     ylabel('EUI [kWh/m^2]')
                    ylabel('Energy Use [kWh]')
                    title({ ['PK:',Case_str,' /TYPE:',CPM_type];...
                            ['CVRMSE: ', num2str(round(T_stat.CVRMSE,1))] })

                    hold off
                    
        end
        
end  



