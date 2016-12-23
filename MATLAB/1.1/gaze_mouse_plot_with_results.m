function f = gaze_mouse_plot_with_results(gaze, mouse, results)
f = figure();
hold on 
 plot(gaze(:,1),gaze(:,2),'-bo','Markersize',10, 'MarkerFaceColor',[0.6 0.6 1.0])
 plot(mouse(:,1),mouse(:,2),'-ro','Markersize',10,'MarkerFaceColor',[1.0 0.6 0.6])
 set(gca,'YDir','Reverse')
 legend('gaze', 'mouse')
 
 for i = 1 : size(results,1)
     rectangle('Position',results(i,[1 3 2 4]),'LineWidth',1)     
 end
 
 rectangle('Position',[0 0 1280 844],'LineWidth',2, 'EdgeColor',[0.7 0.9 0.7])     
 
hold off
