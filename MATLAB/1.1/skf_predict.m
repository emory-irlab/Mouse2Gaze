function [X_p, V] = skf_predict(A, C, Q, R, H, Y, X_init, V_init, varargin)

% skf_predict:  Performs forward pass of linear dynamical system
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 23-Apr-2012 15:43:44

ss = size(A ,1);
T = size(Y, 2);
X_p = zeros(ss, T);
V = zeros(ss, ss, T);

s = 1*ones(1, T); % A matrix state vector

%Ap = H(1) * A(:,:,1) + H(2) * A(:,:,2);
Ap = A(:,:,1);
Qp = Q(:,:,1);

v_t_1 = Ap * V_init * Ap' + Qp;
x_t_1 = Ap * X_init;
K = v_t_1 * C' * pinv(R + C * v_t_1 * C');
V(:,:,1) = v_t_1 - K * C * v_t_1;
X_p(:,1) = x_t_1 + K*(Y(:,1) - C * x_t_1 ) ;

for t = 2 : T
    v_t_1 = Ap * V(:,:,t-1) * Ap' + Qp;
    x_t_1 = Ap * X_p(:,t-1);
    K = v_t_1 * C' * pinv((R + C * v_t_1 * C'));
    V(:,:,t) = v_t_1 - K * C * v_t_1;
    X_p(:,t) = x_t_1 + K*(Y(:,t) - C * x_t_1 );        
end

end