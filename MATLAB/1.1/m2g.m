% 

% m2g: Runs experiment pipeline and compares several methods 
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 20-Apr-2012 13:09:53


clc;
%clear;
DEBUG_LEVEL = 0;
USE_SERPs_ONLY = 0;
%% iterpolate data
interp_dt = 100; % ms 

%{
base_dir = 'C:\\lagoon\\Data\\mouse2gaze\\Processed\\';
base_dir = 'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\';

data = m2g_interp([base_dir 'gaze_out'],...
                [base_dir 'mouse_out'],... 
                [base_dir 'content_out'],...
                '../../Data/m2g_data', ...
                  interp_dt, DEBUG_LEVEL);
%}
load '../../Data/m2g_data'
 
%% generate features for CRF
base_dir = 'C:\\lagoon\\Data\\mouse2gaze\\';
% base_dir = 'C:\\lagoon\\Data\\User-Study-m2g\\';
h = m2g_crf_gen_features(data, [base_dir '\\CRF\\train_feats'], ...
                        [base_dir '\\CRF\\train_labels']);
bar(h)
%% mouse baseline  
%{ 
[X, Y, mouse_rmse] = m2g_mouse_baseline(data, USE_SERPs_ONLY);
rmse = zeros(21, 3);
edist = zeros(21, 1);
for i = 1 : 21
    idx = X(:,1) == i;    
    r = sqrt(mean(((Y(idx,[2 3]) - X(idx,[2 3])).^2)));
    edist(i) = mean(sum(((Y(idx,[2 3]) - X(idx,[2 3])).^2),2));    
    rmse (i,:) = [r sqrt(sum(r.^2))];    
    % bar(1000 * sort(rmse(:,1)))
end
%}