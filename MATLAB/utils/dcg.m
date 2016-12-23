function dcg = dcg(ratings)
i = 1 : length(ratings);
dcg = sum( (2.^ratings - 1) ./ log2(1 + i));