% m2g_lds:  Evaluates LDS approach 
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 26-Apr-2012 14:18:04

clc;
clear;
load '../../Data/m2g_data'

%% Linear Dynamical System
USE_SERPs_ONLY = 1;
tau = 1;
rmse_lds = zeros(21, 3);
interp_dt = 100;
DEBUG_LEVEL = 0;
%% IMPORT DATA
%{
data = m2g_interp('C:\\lagoon\\Data\\User-Study-m2g\\Processed\\gaze_out',...
                'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\mouse_out',... 
                'C:\\lagoon\\Data\\User-Study-m2g\\Processed\\content_out',...
                '../../Data/m2g_data', ...
                  interp_dt, DEBUG_LEVEL);
%}
load '../../Data/m2g_data'


%% LDS settings 
%{
% features 
f_idx_x = [13 14 4 5 6 7 8];
f_idx_y = [11 12 4:10];     

% initial state
X_init = [0.1 0.1 zeros(1,5)]';
V_init = [0.5 0.1 zeros(1,5) ;
          0.1 0.5 zeros(1,5);
          zeros(5,2) 1e-3*eye(5,5)];
%}

% features: ax, ay
%  f_idx_x = [13 14];
%  f_idx_y = [11 12 9 10];     

 f_idx_x = [2 3];
% f_idx_x = [2 3 4 5 6];
f_idx_y = [2 3 4 5 6 19:24];     
% initial state
%  X_init = [0.1 0.1 zeros(1,3)]';
%  V_init = [0.5 0.1 zeros(1,3) ;          
%           zeros(4,2) 1e-3*eye(4,3)];

 X_init = [0.1 0.1]';

 V_init = [0.5 0.5; 0.5 0.5];

      
%% PRECOMPUTE MATRICES 

xs = length(f_idx_x);
ys = length(f_idx_y);

% form X and Y matrices 
NLARGE = 1000*1000; % big number 

% indices: [uid pid]
idx_cnt = zeros(2 * NLARGE, 2); 
idx_tau = zeros(2 * NLARGE, 2);

Xt_1 = zeros(2 * NLARGE, xs); 
Xt = zeros(2 * NLARGE, xs);

% has 1 one more observation that thrown away for Xt
Xy_t = zeros(2 * NLARGE, xs); % stat

%
Y = zeros(2 * NLARGE, ys);

% Block Hankel matrix
D = zeros(NLARGE, tau * ys + 1);

% counts 
cnt = 1;
cnt_tau = 1;

for i = 1 : length(data)
    for p = 1 : length(data{i})
        page = data{i}{p};                
        if (page.T > 50 && ((USE_SERPs_ONLY & page.is_serp) || ~USE_SERPs_ONLY))
            % to esttimate A and Q
            Xt_1(cnt : cnt + page.T - 2, : ) = page.gaze(1:end-1, f_idx_x);
            Xt(cnt : cnt + page.T - 2, : ) = page.gaze(2:end, f_idx_x);             
            % to esttimate C and R
            Xy_t(cnt_tau : cnt_tau + page.T - tau, : ) = page.gaze(tau : end, f_idx_x);                  
            Y(cnt_tau : cnt_tau + page.T - tau, : ) = page.mouse(tau : end, f_idx_y);                  
            for t = 1 : page.T - tau + 1
                D(cnt_tau + t - 1, 1:end - 1) = reshape(page.mouse(t : t + tau - 1, f_idx_y), [1 tau * ys]);
            end
            
            idx_cnt(cnt : cnt + page.T - 2, :) = [i * ones(page.T - 1,1) page.pid * ones(page.T - 1,1)];
            idx_tau(cnt_tau : cnt_tau + page.T - tau, :) = [i * ones(page.T - tau + 1,1) page.pid * ones(page.T - tau + 1,1)];
            
            cnt = cnt + page.T - 1 - 1;
            cnt_tau = cnt_tau + page.T - tau + 1;
            % cnt_pages = cnt_pages + 1;
        end
    end
end

% clean excess
idx_cnt(cnt : end,:) = [];
idx_tau(cnt_tau : end,:) = [];

Xt(cnt : end,:) = [];
Xt_1(cnt : end,:) = [];

Xy_t(cnt_tau : end,:) = [];
%Yt(cnt + 1:end,:) = [];
D(cnt_tau : end,:) = [];
% bias term 
D(:,end) = ones(size(D,1),1);
Y(cnt_tau : end,:) = [];

%% EVALUATE LEAVE-ONE-OUT

for uid = 1 : 21
    train_idx = idx_cnt(:,1) ~= uid;
    test_idx = idx_cnt(:,1) == uid;
    
    train_idx_tau = idx_tau(:,1) ~= uid;
    test_idx_tau = idx_tau(:,1) == uid;
                                     
    % learn LDS parameters  
    [A, C, Q, R, H] = skf_learn(Xt_1(train_idx,:), Xt(train_idx,:), Xy_t(train_idx_tau,:), D(train_idx_tau,:));
                
    % evaluate     
    cnt = 1;
    len = 1;
    
    p_rmse = zeros(sum(test_idx_tau),2);
    
    test_Xt_1 = Xt_1(test_idx,:);
    test_Xt = Xt(test_idx,:);
    test_Y = Y(test_idx_tau,:);
    test_Xy_t = Xy_t(test_idx_tau,:);
    test_D = D(test_idx_tau,:);
        
    pages = unique(idx_cnt(test_idx,2));
    for p = 1 : length(pages)        
        page_idx = idx_cnt(test_idx,2) == pages(p);
        page_idx_tau = idx_tau(test_idx_tau,2) == pages(p);
        page_X = test_Xt(page_idx,:);        
        page_Y = test_Y(page_idx_tau,:);
        page_D = test_D(page_idx_tau,:);
        [X_p, V] = skf_predict(A, C, Q, R, H, page_D',  X_init, V_init);
        len = sum(page_idx_tau);
        predicted_reg = page_D * pinv(C)';
%         p_rmse(cnt : cnt + len - 1,:) =  ((Xy_t(page_idx_tau,[1 2]) - X_p([1 2],:)'));        
        p_rmse(cnt : cnt + len - 1,:) =  ((Xy_t(page_idx_tau,[1 2]) - predicted_reg));        
        cnt = cnt + len;            
        % gaze_mouse_plot(page_X, page_Y, X_p');
        % gaze_mouse_plot(page_X, X_p');
        % gaze_mouse_compare_plot(page_X, page_Y, X_p');
        
    end
        
    p_rmse(cnt:end,:) = [];    
    tmp = mean(p_rmse.^2);
    rmse_lds(uid,:) = sqrt([tmp sum(tmp)]);        
end

rmse_lds
ret_lds = 1000*mean(rmse_lds)
sprintf('lds-filtering:\t%2.2f\t%2.2f\t%2.2f',ret_lds (1),ret_lds(2),ret_lds(3))