function [A, C, Q, R, S] = skf_learn(Xt_1, Xt, Xy_t, D, varargin)
 
% skf_learn:  Estimates switching LDS parameters
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 23-Apr-2012 15:44:17

% xs = length(f_idx_x);
% ys = length(f_idx_y);
xs = size(Xt,2);
ys = size(D,2);
A = zeros(xs, xs, 2);
Q = zeros(xs, xs, 2);


%{
% form X and Y matrices 
NLARGE = 1000*1000; % big number 

Xt_1 = zeros(2 * NLARGE, xs); 
Xt = zeros(2 * NLARGE, xs);

% has 1 one more observation that thrown away for Xt
% Yt = zeros(2 * NLARGE, ys); % state 
Xy_t = zeros(2 * NLARGE, xs); % state 


% Extended observability matrix / Hankel matrix
D = zeros(NLARGE, tau * ys + 1);

cnt = 1;
cnt_tau = 1;
% cnt_pages = 0;

% collect the date into matrix form
for i = 1 : length(train_data)
    for p = 1 : length(train_data{i})
        page = train_data{i}{p};                
        if (page.T > 10 && ((USE_SERPs_ONLY & page.is_serp) || ~USE_SERPs_ONLY))
            % to esttimate A and Q
            Xt_1(cnt : cnt + page.T - 2, : ) = page.gaze(1:end-1, f_idx_x);
            Xt(cnt : cnt + page.T - 2, : ) = page.gaze(2:end, f_idx_x); 
            
            % to esttimate C and R
            Xy_t(cnt_tau : cnt_tau + page.T - tau, : ) = page.gaze(tau : end, f_idx_x);                  
            
            for t = 1 : page.T - tau + 1
                D(cnt_tau + t - 1, 1:end - 1) = reshape(page.mouse(t : t + tau - 1, f_idx_y), [1 tau * ys]);
            end
            
            cnt = cnt + page.T - 1 - 1;
            cnt_tau = cnt_tau + page.T - tau + 1;
            % cnt_pages = cnt_pages + 1;
        end
    end
end
%}
% clean the excess
% Xt(cnt : end,:) = [];
% Xt_1(cnt : end,:) = [];

% Xy_t(cnt_tau : end,:) = [];
%Yt(cnt + 1:end,:) = [];
% D(cnt_tau : end,:) = [];
% bias term 
% D(:,end) = ones(size(D,1),1);
% Xt = A * Xt_1
A(:,:,1) =  Xt' * pinv(Xt_1');
% residual covatiance 
Q(:,:,1) = cov(Xt - (A(:,:,1)*Xt_1')');

% swithcing is not used 
A(:,:,2) = zeros(xs,xs);
Q(:,:,2) = zeros(xs,xs);
S = [1 0]; 

% Yt = C * Xt
% C = D' * pinv(Xy_t');
% try trick
 C = pinv(Xy_t' * pinv(D')); 

R = cov((D - (C * Xy_t')'));


%{ 
 beta =  Xy_t' * pinv(D');
 tmp = (mean(((Xy_t' -  beta * D')').^2));
 rmse = [tmp sum(tmp)].^0.5
  
 tmp1 = mean((Xy_t - D * pinv(C)').^2);
 rmse_1 = [tmp1 sum(tmp1)].^0.5
%}
% residual covariance 


% C = C';
% A(:,:,1) = A(:,:,1)';
% Q(:,:,1) = Q(:,:,1)';
% R = R';

X = [];
Y = [];
end