function  h = m2g_crf_gen_features(data, feat_path, labels_path)

% m2g_crf_gen_features:  This file generates features for CRF (HCRF format)
% EXAMPLE:  

% DESCRIPTION : 
% 
% 

% Author: Dmitry Lagun
% Date: 08-May-2012 16:08:41
tau = 1;
fData = fopen(feat_path,'w+');
fLabels = fopen(labels_path,'w+');
labels_pool = zeros(1000*1000,1);
cnt = 1;
fx = [11 12 19:24];
 % # of features 
views = [];
th = [];
for i = 1 : length(data)
    for p = 1 : length(data{i})
        page = data{i}{p};     
        if (page.T > 10 && page.is_serp == 1) 
            T = page.T;
            labels = zeros(page.T,1);     
            results = page.resultLayout(:,1:4);            
            % results = reshape(page.resultLayout([1:4:40 2:4:40 3:4:40 4:4:40]), [10 4]);   
            for j = 1 : T                
                tmp = get_result(results ,...                
                1000*page.gaze(j,13), 1000*page.gaze(j,14), page.gaze(j,10) * 1000);
                
                if (tmp > 0)
                    labels(j) = tmp;
%                     labels(j) = 10;
                else 
                    labels(j) = -1;
                end                            
            end
            % debug 
            % hist(labels,11)
            % a = 1;
            % gaze_mouse_plot(page.gaze(:,[13 14]), page.mouse(:,[11 12]))
            % gaze_mouse_plot_with_results(page.gaze(:,[13 14]).*1000, page.mouse(:,[11 12]).*1000, results)
            
            ii = labels > 0;
            nT = sum(ii);
            if (nT < 1)
                continue;
            end
            cnt = cnt + nT;
            labels_pool(cnt : cnt + sum(ii) - 1) = labels(ii);            
            fprintf(fLabels,'1,%d\n', nT);
            tmp = sprintf('%d,', labels(ii)); 
            fprintf(fLabels,'%s\n', tmp(1:end-1));                             
            % size(page.resultLayout)
            
            if (isempty(page.resultLayout))
                features = [page.mouse(ii,fx) repmat(zeros(1, 380), nT, 1)];
            else                
                k = size(page.resultLayout,1);
                if (k < 10)                    
                    page.resultLayout = [page.resultLayout; zeros(10 - k, 38)];
                end
                features = [page.mouse(ii,fx) repmat(reshape(page.resultLayout(1:10,:), [1 380]),nT, 1)];
            end
            nf = size(features,2);
            fprintf(fData, '%d,%d\n',nf,nT);                          
            printf_matrix(fData, features');            
            th = [th labels(ii)'];
        end
    end
    views = [views; hist(th,1:10)];
    th = [];
end
mean(views)
bar(mean(views))
fclose(fData);
fclose(fLabels);
labels_pool(cnt+1:end) = [];
h =  hist(labels_pool,10);
end