#!/bin/bash

source_path="./"
model_name_or_path="../data/utilities/sentence-transformers/glove-model-reduced-stopwords"

# compute belief-speaking and fact-speaking similarities
python ${source_path}/compute_sbert_avg_lexicon.py --model_name_or_path ${model_name_or_path}\
	--input_file "../data/combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip"\
	--output_file "../data/combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_honesty_component_scores.csv.gzip"\
	--fact_lexicon "../data/utilities/fact_speaking_p=0.05_swapped_wn_def_example.csv"\
	--belief_lexicon "../data/utilities/belief_speaking_p=0.05_swapped_wn_def_example.csv"\
	--avg_dict --average_of_similarity\
   --compression_type "gzip"\
	--corpus "Twitter"\
   #--smoke_test
