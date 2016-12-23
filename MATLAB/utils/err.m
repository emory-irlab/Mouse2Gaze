function err = err(ratings)
p = 1;
err = 0;

for k = 1 : length(ratings)
    R = gain(ratings(k),2);
    err = err + p * R / k;
    p = p * (1 - R);
end

function gain = gain(x,max_val)
gain = (2^x - 1) / (2 ^ max_val);