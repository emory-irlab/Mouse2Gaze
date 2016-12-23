function [f] = gaze_fix_plot(gaze_data, pX, pY)

% gaze_fix_plot:  One-line description here, please.
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 23-Apr-2012 15:29:23

f = figure();
hold on 
 plot(pX, pY,'ro', 'MarkerSize', 20);
 plot(gaze_data(:,1), gaze_data(:,2),'-bx')
 set(gca,'YDir','Reverse')
hold off

end