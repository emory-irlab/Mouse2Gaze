function [X, Y, rmse] = m2g_mouse_baseline(train_data, USE_SERPs_ONLY, varargin)

% m2g_mouse_baseline: Evalutes mouse-gaze simple baseline
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 20-Apr-2012 13:34:41



% form X and Y matrices 
NLARGE = 5*1000*1000;
X = zeros(NLARGE, 5);
Y = zeros(NLARGE, 3);
cnt = 1;
for i = 1 : length(train_data)
    for p = 1 : length(train_data{i})
        page = train_data{i}{p};        
        if (page.T > 50 && ((USE_SERPs_ONLY & page.is_serp) || ~USE_SERPs_ONLY))
            % X(cnt : cnt + page.T - 1, : ) = [i * ones(page.T,1) page.mouse(:,[11 12 7 8]) ];
            % Y(cnt : cnt + page.T - 1, : ) = [i * ones(page.T,1) page.gaze(:,[13 14]) ];      
             X(cnt : cnt + page.T - 1, : ) = [i * ones(page.T,1) page.mouse(:,[2 3 7 8]) ];
             Y(cnt : cnt + page.T - 1, : ) = [i * ones(page.T,1) page.gaze(:,[2 3]) ];      
            cnt = cnt + page.T;
        end
    end
end

% clean the excess
X(cnt:end,:) = [];
Y(cnt:end,:) = [];

% for bias term in regression
rmse = sqrt(mean((Y(:,[2 3]) - X(:,[2 3])).^2));
end