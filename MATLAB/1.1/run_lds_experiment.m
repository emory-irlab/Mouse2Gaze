clc;
clear;

mouse_data = importdata('C:\\lagoon\\workspace\\Data\\mouse2gaze\\Processed\\mouse_out','\t');
gaze_data = importdata('C:\\lagoon\\workspace\\Data\\mouse2gaze\\Processed\\gaze_out','\t');

%% sequence indices  
t = 1;
u = 0;


% interpolation settings 
interp_dt = 20; % ms
interp_method = 'nearest';


dx = [];
dy = [];

xt = [];
xt_1 =[];

for pid = 1 : max(mouse_data(:,3))        
    md = mouse_data((mouse_data(:,3) == pid),:);
    gd = gaze_data((gaze_data(:,3) == pid),:);
    start_t = gd(1,4);
    if size(md, 1) < 2
        continue;
    end
    
    md(:,4) = md(:,4) - start_t;
    gd(:,4) = gd(:,4) - start_t;
    
    % clean duplicate samples    
    idx_del = find(diff(md(:,4)) == 0);
    md(idx_del,:) = [];
    
    time = 0 : interp_dt : gd(end, 4);
    T = length(time);
    
    md_int = zeros(length(time), 3);
    gd_int = zeros(length(time), 3);
    
    md_int(:,1) = time;
    gd_int(:,1) = time;
             
    md_int(:,2) = interp1(md(:,4), md(:,6) ./ 1000, time, interp_method,'extrap');
    md_int(:,3) = interp1(md(:,4), md(:,7) ./ 1000, time, interp_method,'extrap');
        
    gd_int(:,2) = interp1(gd(:,4), gd(:,6) ./ 1000, time, interp_method,'extrap');
    gd_int(:,3) = interp1(gd(:,4), gd(:,7) ./ 1000, time, interp_method,'extrap');
    
    % form xt and xt_1
    for i = 1 : T - 2        
        xt = [xt; gd_int(i+1,[2 3]) (gd_int(i+2,[2 3]) - gd_int(i+1,[2 3]))./interp_dt];
        xt_1 = [xt_1; gd_int(i,[2 3]) (gd_int(i+1,[2 3]) - gd_int(i,[2 3]))./interp_dt];
    end
    % diffs
    dx = [dx; gd_int(:,2) - md_int(:,2)];
    dy = [dy; gd_int(:,3) - md_int(:,3)];    
    %[dx dy] = (gd_int(:, [2 3]) - md_int(:, [2 3])).^2;
end

%% check for goodness of interpolation 

%gaze_mouse_plot(gd(:,[6 7]),md(:,[6 7]));
%gaze_mouse_plot(gd_int(:,[2 3]),md_int(:,[2 3]));

%% plot distribution of differences 
%{
xi = -1e3:50:1e3;

dx_h = hist(dx, xi) ./ size(dx,1);
dy_h = hist(dy, xi) ./ size(dx,1);
deuclid_h = hist(sqrt(dx.^2 + dy.^2), xi) ./ size(dx,1);
hold on

plot(xi, dx_h, '--rx', 'LineWidth', 2)
plot(xi, dy_h, '--bo', 'LineWidth', 2)
plot(xi, deuclid_h, '--go', 'LineWidth', 2)
legend('\Deltax', '\Deltay' , '\DeltaEuclid');
grid on
hold off
%}

%% learn system matrix 
sprintf('learning A matrix ...  ')
A1 = xt \ xt_1; 
A2 = pinv(xt_1) * xt;

n1 = norm(xt - xt_1 * A1)
n2 = norm(xt - xt_1 * A2)

%% plot x_t sort 
hold on
[B,IX] = sort(xt_1(:,1));
plot(xt_1(:,2),xt(:,3),'bo')
hold off
sprintf('done')