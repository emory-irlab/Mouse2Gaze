function prec = precision(ratings,k)
ii = ratings(1:k) > 0;
prec = sum(ii) / k;