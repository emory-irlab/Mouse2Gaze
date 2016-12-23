clc;
load gd_int
interp_dt = 20;
% fixation algorithm parmeters 
start_bin = 3                    % min_fix_dur
D = 0.01                                % 100 px

[pX,pY,pI,pL] = fixDispersion(gd_int(:,2), gd_int(:,3), start_bin, D);
gaze_fix_plot(gd_int(:,[2 3]), pX, pY)
mean(pL*20)