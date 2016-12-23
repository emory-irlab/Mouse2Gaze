% m2g_huang_baseline:  Evaluates J. Huang et.al baseline on our data
% EXAMPLE:  

% DESCRIPTION : 
% % 

% Author: Dmitry Lagun
% Date: 26-Apr-2012 13:19:56

clc;
clear;
load '../../Data/m2g_data'


%% mouse only baseline 
USE_SERPs_ONLY = 1;
[X, Y, mouse_rmse] = m2g_mouse_baseline(data, USE_SERPs_ONLY);
rmse_mouse = zeros(21, 3);

% k = 3;
% sorted_rmse =  sortrows(rmse(:,k));
% bar (1000 * sorted_rmse(:,k))

%% J. Huang baseline 
X(:,5) = X(:,5) + 1e-3 *ones(size(X,1),1);  % to avoid Inf's
rmse_huang = zeros(21, 3);
for i = 1:21   
    idx_train = X(:,1) ~= i; n_train = sum(idx_train);
    idx_test = X(:,1) == i; n_test = sum(idx_test);

    % training data
    train_x = [X(idx_train,2) log(X(idx_train,4)) log( ones()+ X(idx_train,5)) X(idx_train,2).*log(X(idx_train,4)) X(idx_train,2).*log(X(idx_train,5))];
    train_y = [X(idx_train,3) log(X(idx_train,4)) log(X(idx_train,5)) X(idx_train,3).*log(X(idx_train,4)) X(idx_train,3).*log(X(idx_train,5))];
    
    train_gaze_x = Y(idx_train,2);
    train_gaze_y = Y(idx_train,3);

    % test data
    test_x = [ X(idx_test,2) log(X(idx_test,4)) log(X(idx_test,5)) X(idx_test,2).*log(X(idx_test,4)) X(idx_test,2).*log(X(idx_test,5))];
    test_y = [ X(idx_test,3) log(X(idx_test,4)) log(X(idx_test,5)) X(idx_test,3).*log(X(idx_test,4)) X(idx_test,3).*log(X(idx_test,5))];
    test_gaze_x = Y(idx_test,2);
    test_gaze_y = Y(idx_test,3);

    % train
    beta_x = pinv(train_x) * train_gaze_x;
    beta_y = pinv(train_y) * train_gaze_y;

    % test / eval
    predicted_x = test_x*beta_x;
    predicted_y = test_y*beta_y;
    
    mse_x = mean((test_gaze_x - predicted_x).^2);
    mse_y = mean((test_gaze_y - predicted_y).^2);

    rmse_huang(i,:) = sqrt([mse_x mse_y (mse_x + mse_y)]);
    
    tmp = mean([(test_gaze_x - test_x(:,1)) (test_gaze_y - test_y(:,1))].^2);    
    
    rmse_mouse(i,:) = sqrt([tmp sum(tmp)]);
end 
rmse_huang
%{   
     idx = 2000 : 3000;
     gaze_mouse_plot([test_gaze_x(idx,:) test_gaze_y(idx,:)], [test_x(idx,1) test_y(idx,1)], [predicted_x(idx) predicted_y(idx)]);
     gaze_mouse_compare_plot([test_gaze_x(idx,:) test_gaze_y(idx,:)], [test_x(idx,1) test_y(idx,1)], [predicted_x(idx) predicted_y(idx)]);

%}
ret_huang = 1000*mean(rmse_huang);
ret_mouse = 1000*mean(rmse_mouse);
sprintf('huang:\t%2.2f\t%2.2f\t%2.2f',ret_huang (1),ret_huang (2),ret_huang (3))
sprintf('mouse:\t%2.2f\t%2.2f\t%2.2f',ret_mouse(1),ret_mouse(2),ret_mouse(3))