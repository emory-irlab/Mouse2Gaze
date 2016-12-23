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

lambda = 1E-3;
l2 = 1e-4;
max_rank = 30;
tol = 1e-4;
rng(100)

N = size(X,1);

X(:,5) = X(:,5) + 1e-3 *ones(size(X,1),1);  % to avoid Inf's and NaNs

data_matrix = [X(:,2) X(:,3) ones(N,1) log(X(:,4)) log(X(:,5)) X(:,2).*log(X(:,4)) X(:,2).*log(X(:,5)) X(:,3).*log(X(:,4)) X(:,3).*log(X(:,5))];
% normalize features 
for i = 4 : size(data_matrix,2)
    data_matrix(:,i) = data_matrix(:,i) - mean(data_matrix(:,i)) * ones(N,1);
    data_matrix(:,i) = data_matrix(:,i) ./ std(data_matrix(:,i));
end

[R, res] = incomplete_chol(data_matrix, @rbf, lambda, tol, max_rank );
res 
%% J. Huang baseline 
l2_accuracy = [];
for l2 = 10.^(-1:0.5:2)    
rmse_huang = zeros(21, 3);
rmse_our = zeros(21, 3);

for i = 1:21   
    idx_train = X(:,1) ~= i; n_train = sum(idx_train);
    idx_test = X(:,1) == i; n_test = sum(idx_test);

    % training data
    train_x = [X(idx_train,2) log(X(idx_train,4)) log(X(idx_train,5)) X(idx_train,2).*log(X(idx_train,4)) X(idx_train,2).*log(X(idx_train,5))];        
    train_y = [X(idx_train,3) log(X(idx_train,4)) log(X(idx_train,5)) X(idx_train,3).*log(X(idx_train,4)) X(idx_train,3).*log(X(idx_train,5))];
    
    train_gaze_x = Y(idx_train,2);
    train_gaze_y = Y(idx_train,3);

    % kernel ridge 
%     ds_perc = 0.05;
%     ds_idx = rand(n_train,1) < ds_perc;
    
    m = size(R,1);
    w_kr = pinv(R * R' + l2 * eye(m,m)) * R(:,idx_train) * [train_gaze_x train_gaze_y];
    % w_y = pinv(R * R' + l2 * eye(m,m)) * R(:,idx_train) * ;
    tmp1 = R(:,idx_test)' * w_kr;
    kr_x = tmp1(:,1);
    kr_y = tmp1(:,2);
    %kr_y = R(:,idx_test)' * w_y;    
    
    
    % test data
    test_x = [ X(idx_test,2) log(X(idx_test,4)) log(X(idx_test,5)) X(idx_test,2).*log(X(idx_test,4)) X(idx_test,2).*log(X(idx_test,5))];
    test_y = [ X(idx_test,3) log(X(idx_test,4)) log(X(idx_test,5)) X(idx_test,3).*log(X(idx_test,4)) X(idx_test,3).*log(X(idx_test,5))];
    test_gaze_x = Y(idx_test,2);
    test_gaze_y = Y(idx_test,3);

    % train
    beta_x = pinv(train_x) * train_gaze_x;
    beta_y = pinv(train_y) * train_gaze_y;

    % test / eval    
    % tmp1 = mean((train_x*beta_x - train_gaze_x).^2);
    % tmp2 = mean((fv - train_gaze_x(ds_idx,:)).^2);    
        
    predicted_x = test_x*beta_x;
    predicted_y = test_y*beta_y;
    
    mse_x = mean((test_gaze_x - predicted_x).^2);
    mse_y = mean((test_gaze_y - predicted_y).^2);
    
    mse_x_kr = mean((test_gaze_x - kr_x).^2);
    mse_y_kr = mean((test_gaze_y - kr_y).^2);

    rmse_huang(i,:) = sqrt([mse_x mse_y (mse_x + mse_y)]);    
    rmse_our(i,:) = sqrt([mse_x_kr mse_y_kr (mse_x_kr + mse_y_kr)]);
    tmp = mean([(test_gaze_x - test_x(:,1)) (test_gaze_y - test_y(:,1))].^2);        
    rmse_mouse(i,:) = sqrt([tmp sum(tmp)]);
 end 
rmse_huang
rmse_our
%{   
     idx = 10000 : 11000;
     gaze_mouse_plot([test_gaze_x(idx,:) test_gaze_y(idx,:)], [test_x(idx,1) test_y(idx,1)], [kr_x(idx) kr_y(idx)])
     gaze_mouse_plot([test_gaze_x(idx,:) test_gaze_y(idx,:)], [test_x(idx,1) test_y(idx,1)], [predicted_x(idx) predicted_y(idx)])

     gaze_mouse_plot([test_gaze_x(idx,:) test_gaze_y(idx,:)], [test_x(idx,1) test_y(idx,1)], [predicted_x(idx) predicted_y(idx)]);
     gaze_mouse_compare_plot([test_gaze_x(idx,:) test_gaze_y(idx,:)], [test_x(idx,1) test_y(idx,1)], [kr_x(idx) kr_y(idx)]);

%}
ret_huang = 1000*mean(rmse_huang);
ret_mouse = 1000*mean(rmse_mouse);
ret_our = 1000*mean(rmse_our);
sprintf('huang:\t%2.2f\t%2.2f\t%2.2f',ret_huang (1),ret_huang (2),ret_huang (3))
sprintf('rmse_our:\t%2.2f\t%2.2f\t%2.2f',ret_our(1),ret_our(2),ret_our(3))
sprintf('mouse:\t%2.2f\t%2.2f\t%2.2f',ret_mouse(1),ret_mouse(2),ret_mouse(3))
l2_accuracy = [l2_accuracy; l2 ret_our(3)]
end
l2_accuracy