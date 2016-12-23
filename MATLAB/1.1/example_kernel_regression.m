% example of kernel ridge regression
clc;
clear;

x = sort(20*rand(100,1));
y_true = x.*sin(1*x) + 0.1*x.^2; 
y = y_true  + randn(100,1);
x0 = mean(x);
y0 = mean(y);

n = length(x);

%{
hold on 
plot(x,y_true,'-rx')
plot(x,y,'bo')
hold off
%}

X = [ones(100,1) x]';
%% linear regression 
w = inv(X*X')*X*y;

%% kernel regression 
% fill kernel matrix
K = zeros(n,n);
sigma = 1e-1;
lambda = 1e-2;
for i = 1 : n 
    for j = 1 : n
        K(i,j) = exp((-1/(2*sigma))*(x(i) -x(j)).^2);
    end
end

f_k = y'*inv(K + lambda * eye(100))*K;

%% plot results
hold on 
plot(x,y_true,'-rx')
plot(x,y,'bo')
plot(x,w'*X,'-ms')
plot(x,f_k,'-go');
legend('true', 'noisy observation', 'least squares', 'RBF kernel')
grid on
hold off
