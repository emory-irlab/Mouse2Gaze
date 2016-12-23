function label = get_result(results, x, y, offsetY)

% get_result:  returns result label at given poisition (x,y)
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 08-May-2012 16:15:21
label = -1;
err = 10; % px
inner_height = 844 + offsetY; % px 
for i = 1 : size(results,1)
    if (y >= inner_height || y <= offsetY)
        label = -1;
        break;
    end
    if ( x > results(i,1) - err && x < results(i,1) + results(i,2) + err ...
                    && y >= results(i,3) - err && y <= results(i,3) + results(i,4) + err )
        label = i; 
        break;
    end
end

end