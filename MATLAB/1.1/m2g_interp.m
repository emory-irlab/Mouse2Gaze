function [data] = m2g_interp(gaze_path, mouse_path, content_out, out_path, interp_dt, DEBUG_LEVEL, varargin)
% m2g_interp  This function interpolates gaze and mouse measurements and
% saves the result at given path in .mat binary.

% EXAMPLE:  

% Author: Dmitry Lagun
% Date: 20-Apr-2012 12:34:41
sprintf('reading mouse data ... ')
mouse_data = importdata(mouse_path, '\t');
sprintf('reading gaze data ... ')
gaze_data = importdata(gaze_path, '\t');
sprintf('reading page content data ... ')
content_data = importdata(content_out, '\t');

% interpolation settings 
interp_method = 'nearest';

% fixation algorithm parmeters 
start_bin = round(60 / interp_dt);     % min_fix_dur
D = 0.01;                                % 100 px

uids = unique(mouse_data(:,1))
sprintf('# of users : %s', length(uids))
data = cell(1, length(uids));
fix = [];
sprintf('processing ...  ')
for i  = 1 : length(uids)
    uid = uids(i)
    mdu = mouse_data(mouse_data(:,1) == uid,:);
    gdu = gaze_data(gaze_data(:,1) == uid,:);    
    pp = unique(mdu(:,3));
    num_pages = length(pp);
    pages = cell(num_pages,1);
    for p = 1 : num_pages
        pid = pp(p);
        md = mdu((mdu(:,3) == pid),:);
        gd = gdu((gdu(:,3) == pid),:);
        start_t = gd(1,5);
        if size(md, 1) < 2 || size(gd, 1) < 2
            pages{p} = struct('mouse', [], 'gaze', [], 'pid', pid, 'T', 0);
            continue;
        end

        md(:,5) = md(:,5) - start_t;
        gd(:,5) = gd(:,5) - start_t;
        
        % result layout  
        ii = content_data(:,1) == uid & content_data(:,2) == pid;
        pd = content_data(ii, 3:end);                
        % clean duplicate samples  
        idx = diff(md(:,5)) == 0;
        md(idx,:) = [];
        
        time = 0 : interp_dt : gd(end, 5);                
        
        md_int = zeros(length(time), 5);
        gd_int = zeros(length(time), 5);

        md_int(:,1) = time;
        gd_int(:,1) = time;
        T = length(time);
        
        % -------------------- GAZE FEATURES ------------------------------
        % Gaze:  gx, gy
        gd_int(:,2) = interp1(gd(:,5), gd(:,7) ./ 1000, time, interp_method, 'extrap');        
        gd_int(:,3) = interp1(gd(:,5), gd(:,8) ./ 1000, time, interp_method, 'extrap');                       
        
        % Gaze: speed 
        gd_int(2:end,4) = diff(gd_int(:,2)); gd_int(1,4) = 0;
        gd_int(2:end,5) = diff(gd_int(:,3)); gd_int(1,5) = 0;
        gd_int(:,6) = sqrt(gd_int(:,4).^2 + gd_int(:,5).^2);
        
        % Gaze: speed - direction
        gd_int(:,7) = sign(gd_int(:,4));
        gd_int(:,8) = sign(gd_int(:,5));
        
        % Gaze: scroll
        gd_int(:,9) = interp1(gd(:,5), gd(:,9) ./ 1000, time, interp_method, 'extrap');        
        gd_int(:,10) = interp1(gd(:,5), gd(:,10) ./ 1000, time, interp_method, 'extrap');        
        
        % Gaze: scroll speed
        gd_int(:,11) = [0; diff(gd_int(:,9))];
        gd_int(:,12) = [0; diff(gd_int(:,10))];
        
        % Gaze: ax, ay
        gd_int(:,13) = gd_int(:,2) + gd_int(:,9);
        gd_int(:,14) = gd_int(:,3) + gd_int(:,10);
        
        % Gaze pupil: px, py
        gd_int(:,15) = interp1(gd(:,5), gd(:,11) , time, interp_method, 'extrap');   
        gd_int(:,16) = interp1(gd(:,5), gd(:,12) , time, interp_method, 'extrap');
        %{
        % 17 - 36
        for j = 1 : 10
            gd_int(:,16 + 1 + (j-1)*2) = pd(3 + (j-1)*4) * ones(T,1);
            gd_int(:,16 + 2 + (j-1)*2) = pd(4 + (j-1)*4) * ones(T,1);
        end
        
        % 37 - 56
        for j = 1 : 10
            gd_int(:,37 + 1 + (j-1)*2) = pd(1 + (j-1)*4) * ones(T,1) - gd_int(:,11);
            gd_int(:,37 + 2 + (j-1)*2) = pd(3 + (j-1)*4) * ones(T,1) - gd_int(:,12);
        end
        %}              
        % -------------------- MOUSE FEATURES ------------------------------
        % Mouse:  cx, cy
        md_int(:,2) = interp1(md(:,5), md(:,9) ./ 1000, time, interp_method, 'extrap');
        md_int(:,3) = interp1(md(:,5), md(:,10) ./ 1000, time, interp_method, 'extrap');
        
        % Mouse: speed (x,y,abs)
        md_int(:,4) = [0; diff(md_int(:,2))]; 
        md_int(:,5) = [0; diff(md_int(:,3))]; 
        md_int(:,6) = sqrt(md_int(:,4).^2 + md_int(:,5).^2);
                                
        % Mouse: last-move and time since page load
        md_int(:,7) = interp1(md(:,5), md(:,7) , time, 'linear', 'extrap');
        md_int(:,8) = interp1(md(:,5), md(:,8) , time, 'linear', 'extrap');                        
        
        % Mouse: scroll X and Y
        md_int(:,9) = gd_int(:,9);
        md_int(:,10) = gd_int(:,10);
        
        % Mouse: ax, ay
        md_int(:,11) = md_int(:,2) + md_int(:,9);
        md_int(:,12) = md_int(:,3) + md_int(:,10);
        
        % Mouse: scroll speed
        md_int(:,13) = [0; diff(md_int(:,9))];
        md_int(:,14) = [0; diff(md_int(:,10))];
                
        % Mouse: speed direction 
        md_int(:,15) = sign(md_int(:,4));
        md_int(:,16) = sign(md_int(:,5));
        
        % Mouse: acceleration 
        md_int(:,17) = [0; diff(md_int(:,4))];
        md_int(:,18) = [0; diff(md_int(:,5))];                
        
        % Features for Huang et.al baseline 
        md_int(:,19) = log(1e-3 * ones(T,1) + md_int(:,7));  
        md_int(:,20) = log(1e-3 * ones(T,1) + md_int(:,8));
        
        % cx * log(tm), cx * log(td)
        md_int(:,21) = md_int(:,11) .* md_int(:,19);  
        md_int(:,22) = md_int(:,11) .* md_int(:,20);
        
        % cy * log(tm), cy * log(td)
        md_int(:,23) = md_int(:,12) .* md_int(:,19);  
        md_int(:,24) = md_int(:,12) .* md_int(:,20);               
        %{        
        % 25 - 44
        for j = 1 : 10
            md_int(:,24 + 1 + (j-1)*2) = pd(3 + (j-1)*4) * ones(T,1);
            md_int(:,24 + 2 + (j-1)*2) = pd(4 + (j-1)*4) * ones(T,1);
        end
        
        % 45 - 64
        for j = 1 : 10
            md_int(:,45 + 1 + (j-1)*2) = pd(1 + (j-1)*4) * ones(T,1) - md_int(:,11);
            md_int(:,45 + 2 + (j-1)*2) = pd(3 + (j-1)*4) * ones(T,1) - md_int(:,12);
        end
        %}
        %  gaze_mouse_plot(gd_int(:,[2 3]), md_int(:, [2 3]));
        
        [pX,pY,pI,pL] = fixDispersion(gd_int(:,2), gd_int(:,3), start_bin, D);
        
        f_idx = zeros(1, length(time));             % index of measurements within fixation. otherwise saccade
        for k = 1 : length(pL)
            f_idx(pI(k) : pI(k) + pL(k) - 1) = 1;
        end
        
        
        pages{p} = struct('pid', pid, 'T', T,...
                            'mouse', md_int, 'gaze', gd_int,...
                            'pX', pX, 'pY', pY, 'pI', pI, 'pL', pL, 'f_idx', f_idx,...
                            'uid', md(1,1), 'is_serp', md(1,4),...
                            'pVx', [0 diff(pX)]', 'pVy', [0 diff(pY)]',...
                             'resultLayout', pd);                                                        
       % debug
       if (DEBUG_LEVEL > 0)            
           %gaze_fix_plot(gd_int(:,[2 3]), pX, pY)
           fix = [fix pL*interp_dt];
       end
    end
    data{i} = pages;
end

if (DEBUG_LEVEL > 0)            
    hist(fix, 100)
    mean(fix)
end

save(out_path, 'data');
sprintf('m2g_interp: done')
end