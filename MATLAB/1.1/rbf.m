function v = rbf(x1, x2, lambda)
% v = exp (- lambda * norm(x1 - x2));
v = exp (- lambda * norm(x1 - x2,2));