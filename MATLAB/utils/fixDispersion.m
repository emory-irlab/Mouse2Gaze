% Dmitry Lagun 2009

% Revised 2010, 2012

function [pX,pY,pI,pL] = fixDispersion(x_cord, y_cord, start_bin, D)

%Default setting 

%start_bin = 10;
bin = start_bin;;
i = 1;

pX = [];
pY = [];
pI = [];
pL = [];
flag = 0;

while (length(x_cord) >= i + bin)
    skip = i : i + bin;
    %dx = (max (x_cord(skip)) - min (x_cord(skip)));
    %dy = (max (y_cord(skip)) - min (y_cord(skip)));
    
    dx = var(x_cord(skip));
    dy = var(y_cord(skip));
    
    if ( sqrt(dx + dy) < D )
    %if (sum (Centroid (x_cord(skip),y_cord(skip))) < D )
        flag = 1;
        bin = bin + 1;
    elseif (flag == 1)
        pX = [pX median(x_cord(skip))];
        pY = [pY median(y_cord(skip))];
        pI = [pI i];
        pL = [pL bin];
        flag = 0;
        i = i + bin -1;
        bin = start_bin;
    elseif flag == 0
        i = i + 1;
    end
end

if (flag == 1)
    pX = [pX mean(x_cord(skip))];
    pY = [pY mean(y_cord(skip))];
    pI = [pI i];
    pL = [pL bin];
end

