function mi = argmax(x)
[c,i] = max(x);
mi = -1;
if (length(i) > 0)
    mi = i;
end
    
