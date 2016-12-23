function new(filename, code)

if ~strcmpi(filename((end-1):end), '.m')
    filename = [filename '.m'];
end
if exist(filename, 'file')
    display('File Already Exists');
else
    f = fopen(filename, 'w');
    try
        fprintf(f, ['function [varargout] = ' filename(1:(end-2)) '(varargin)\n']);
        fprintf(f, ['\n%% ' filename(1:(end-2)) ':  One-line description here, please.\n']);
        
        fprintf(f, ['%% EXAMPLE:  \n\n']);
        fprintf(f, ['%% DESCRIPTION : \n%% \n%% \n\n']);
        fprintf(f, ['%% Author: Dmitry Lagun\n']);        
        fprintf(f, ['%% Date: ' datestr(now) '\n\n\n']);			
        
        %fprintf(f, ['function [varargout] = ' filename(1:(end-2)) '(varargin)\n']);
        %fprintf(f, '%% PURPOSE: function purpose\n');
        %fprintf(f, '%%---------------------------------------------------\n');
        %fprintf(f, ['%% USAGE: varargout = ' filename(1:(end-2)) '(varargin)\n']);
        %fprintf(f, '%% where: varargin = vector of input variables\n');
        %fprintf(f, '%%---------------------------------------------------\n');
        %fprintf(f, '%% RETURNS: a vector of output arguments composed of:\n');
        %fprintf(f, '%% x = 1.2\n');
        %fprintf(f, '%% --------------------------------------------------\n');
        %fprintf(f, '%% SEE ALSO: f(results)\n');
        %fprintf(f, '%%---------------------------------------------------\n');
        %fprintf(f, '%% REFERENCES: \n');
        %fprintf(f, '%%---------------------------------------------------\n');
        %fprintf(f, '%% REMARKS: \n');
        %fprintf(f, '%%---------------------------------------------------\n\n');
        %fprintf(f, '%% Written by:\n');
        
        %[s, r] = system('net user %username% /domain');
        %fprintf(f, ['%% Username: ' 'Dmitry Lagun \n']);
        %fprintf(f, ['%% Display Name: ' strtrim(r(findstr(r, 'Full Name')+length('Full Name'):findstr(r, 'Comment')-1)) '\n']);
        %fprintf(f, ['%% Computer Name: ' getenv('computername') '\n']);
        %fprintf(f, ['%% Windows: ' char(System.Environment.OSVersion.ToString()) '\n']);
        %fprintf(f, ['%% Date: ' datestr(now) '\n\n\n']);
        % append code if given
        if nargin == 2
            if iscell(code)
                for i = 1:length(code)
                    if ischar(code{i})
                        fprintf(f, code{i});
                        fprintf(f, '\n');
                    end
                end
            elseif ischar(code)
                fprintf(f, code);
                fprintf(f, '\n\n');
            end
        end
        fprintf(f, 'end');
    catch
        fclose(f);
    end
end
try
    open(filename);
catch
    display('Could not open created file!');
end
end