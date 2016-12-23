function f = gaze_mouse_plot(gaze, mouse, varargin)
f = figure();
hold on 
 plot(gaze(:,1),gaze(:,2),'-bo','Markersize',10, 'MarkerFaceColor',[0.6 0.6 1.0])
 plot(mouse(:,1),mouse(:,2),'-ro','Markersize',10,'MarkerFaceColor',[1.0 0.6 0.6])
 set(gca,'YDir','Reverse')
 if (length(varargin) > 0)
     X_kf = varargin{1}(:, [1 2]);
     plot(X_kf(:,1), X_kf(:,2) ,'-go','Markersize',10, 'MarkerFaceColor',[0.6 1.0 0.6])     
     legend('gaze', 'mouse', 'LDS-predicted') 
 else
    legend('mouse', 'gaze')
 end
 %% plot variance 
 if (length(varargin) > 1)
     X_kf = varargin{1}(:, [1 2]);
     V = varargin{2};
     T = size(V,3);
     for t = 1 : size(varargin{1},1)         
         ellipse(sqrt(V(1,1,t)), sqrt(V(2,2,t)), 0, X_kf(t,1), X_kf(t,2),'r')
     end
 end
 
hold off
