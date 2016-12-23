function H = hankel_matrix(X, T, varargin)

% hankel_matrix:  Forms T - observation Hankel matrix
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 23-Apr-2012 16:52:06

[n, m] = size(X);
H = zeros(n - T, T * m);
for i = 1 : n - T
    for j = 1:T
        H(i, 1 + (j - 1) * m : j*m) = X(i + j - 1,:);
    end
end
end