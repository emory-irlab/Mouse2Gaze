function ndcg = ndcg(ratings)
[ideal_ranking,idx] = sort(ratings, 'descend');
ndcg =  dcg(ratings) / dcg(ideal_ranking);