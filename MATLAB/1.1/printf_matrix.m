function printf_matrix(fileID, A)

% printf_matrix:  prints matrix to file handler row-wise
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 08-May-2012 16:26:55
for i = 1 : size(A,1)
    %for j = 1 : size(A,2)
    tmp = sprintf('%d,', A(i,:));
    fprintf(fileID,'%s\n', tmp(1:end-1));    
    %end    
end