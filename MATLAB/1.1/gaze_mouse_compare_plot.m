function f = gaze_mouse_compare_plot(gaze, mouse, varargin)

% gaze_mouse_compare_plot:  One-line description here, please.
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 26-Apr-2012 12:41:53

f = figure();

 subplot(2,1,1)
 hold on 
 plot(gaze(:,1),'-bx','Markersize',10, 'MarkerFaceColor',[0.6 0.6 1.0])
 plot(mouse(:,1),'-rx','Markersize',10,'MarkerFaceColor',[1.0 0.6 0.6])
 grid on
 if (length(varargin)> 0) 
     X_p = varargin{1};
     plot(X_p (:,1),'-gx','Markersize',10,'MarkerFaceColor',[0.6 1.0 0.6])           
     legend('gaze','mouse','LDS-predicted')
 else
     
     legend('gaze','mouse')
 end
 hold off
 subplot(2,1,2)
 hold on 
 plot(gaze(:,2),'-bx','Markersize',10, 'MarkerFaceColor',[0.6 0.6 1.0])
 plot(mouse(:,2),'-rx','Markersize',10,'MarkerFaceColor',[1.0 0.6 0.6])
 grid on
 if (length(varargin)> 0) 
     X_p = varargin{1};
     plot(X_p (:,2),'-gx','Markersize',10,'MarkerFaceColor',[0.6 1.0 0.6])           
     legend('gaze','mouse','LDS-predicted')
 else
     grid on
     legend('gaze','mouse')
 end
 hold off
end
 
