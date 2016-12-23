function mean_ap = mean_ap(ratings)
mean_ap = 0;
for k = 1 : length(ratings)
    mean_ap = mean_ap + (ratings(k) > 0) * precision(ratings,k);
end
mean_ap = mean_ap  / sum(ratings > 0);