
% m2g_debug:  Debuggin code for mouse - gaze data
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 26-Apr-2012 11:31:18


load m2g_data

uid = 1;
for pid = 1 : min([length(data{uid}) 10])
    page = data{uid}{pid};    
    %gaze_mouse_plot(page.mouse(:,[2 3]), page.gaze(:,[2 3]));
    gaze_mouse_plot(page.mouse(:,[11 12]), page.gaze(:,[13 14]));
end