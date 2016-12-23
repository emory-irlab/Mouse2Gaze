%
% m2g_data_summary:  Provides descriptive information about the dataset
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 24-Apr-2012 16:47:59


clc;
clear;

DEBUG_LEVEL = 0;
USE_SERPs_ONLY = 1;

%% iterpolate data
interp_dt = 20; % ms 
%{
data = m2g_interp('C:\\lagoon\\Data\\User-Study-m2g\\Processed\\gaze_out',...
                'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\mouse_out',... 
                'm2g_data', ...
                interp_dt, DEBUG_LEVEL);
%}
% load data
load m2g_data
 
%% mouse baseline  

[X, Y, mouse_rmse] = m2g_mouse_baseline(data, USE_SERPs_ONLY);

%% mouse - gaze distance
rmse = zeros(21, 4);
edist = zeros(21, 1);
for i = 1 : 21
    idx = X(:,1) == i;    
    r = sqrt(mean(((Y(idx,[2 3]) - X(idx,[2 3])).^2)));
    edist(i) = mean(sum(((Y(idx,[2 3]) - X(idx,[2 3])).^2),2));    
    uid = data{i}{1}.uid;
    rmse (i,:) = [uid r sqrt(sum(r.^2))];        
end
sprintf('median(x-dist): %2.4f\nmedian(y-dist): %2.4f\nmedian(e-dist): %2.4f', 1000*median(rmse(:,2)), 1000*median(rmse(:,3)), 1000*median(rmse(:,4)) )

%% mouse - gaze lag 

tau = 1;
lag_distance = [];
for tau = 1 : 100
    tmp = zeros(21, 1);
    for i = 1 : 21
        idx = X(:,1) == i;    
        Y_1 = X(idx,[2 3]);
        X_1 = Y(idx,[2 3]);
        X_1(1:tau,:) = [];
        Y_1(end - tau + 1: end, :) = []; 
        r = sqrt(mean(((Y_1 - X_1).^2)));
        %edist(i) = mean(sum(((Y(idx,[2 3]) - X(idx,[2 3])).^2),2));    
        %uid = data{i}{1}.uid;
        %rmse (i,:) = [uid r sqrt(sum(r.^2))];                
        tmp (i) = sqrt(sum(r.^2));
    end
    lag_distance = [lag_distance; mean(tmp)];
end
plot(lag_distance)


