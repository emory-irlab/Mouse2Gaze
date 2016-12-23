function [R, res] = incomplete_chol(data, fun, lambda, eta, max_rank)

j = 0;
N = size(data,1);
R = zeros(max_rank, N);
d = zeros(N,1);
I = zeros(max_rank,1);
for i = 1 : N
    d(i) = fun(data(i,:), data(i,:), lambda);
end

[a, I(j+1)] = max(d);
nu = zeros(max_rank);

while (a > eta && j <= max_rank)
    j = j + 1;
    nu(j) = sqrt(a);
    for i = 1:N
        R(j,i) = (fun(data(I(j),:), data(i,:), lambda) - R(:,i)' * R(:,I(j))) / nu(j);
        d(i) = d(i) - R(j,i)^2;
    end
    [a, I(j+1)] = max(d);
    sprintf('iteration %d: res = %2.4f', j, a)
end
T = j;
R = R(1:T,:);
res = a;