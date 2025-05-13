# Workflow data preparation
* **clean_KnowWho_data.ipynb**: Loads and cleans the raw midterm candidate lists from KnowWho.
    * in:
      * candidates_exp09142022.csv (from [KnowWho](https://kw1.knowwho.com/candidate-data/candidate-lists/))
    * out:
      * KnowWho_profiles_clean.csv
* **get_twitter_profiles.ipynb**: Retrieves the profile information of the midterm candidates from the Twitter API.
    * in:
      * KnowWho_profiles_clean.csv (from clean_KnowWho_data.ipynb)
    * out:
      * candidate_twitter_profiles.csv
* **get_twitter_timelines.ipynb**: Retrieves the timelines of candidates from the Twitter API, cleans and combines all timelines. Also extracts URLs for unravelling and organises URL unravelling (not relevant for this publication).
    * in:
      * candidate_twitter_profiles.csv (from get_twitter_profiles.ipynb)
      * data/utilities/url_shorteners.txt (list of common URL shortening services)
    * out:
      * combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip
      * combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean_tweetIDs.txt
      * midterm_candidates_unraveled_urls.csv.xz (not relevant for this publication)
* **label_glove840B_DDR.sh** (calls compute_sbert_avg_lexicon.py internally): Computes belief-speaking and fact-speaking scores of tweets.
    * in:
      * combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip (from get_twitter_timelines.ipynb)
      * data/utilities/belief_speaking_p=0.05_swapped_wn_def_example.csv (belief-speaking dictionary)
      * data/utilities/fact_speaking_p=0.05_swapped_wn_def_example.csv (fact-speaking dictionary)
      * data/utilities/sentence-transformers (sentence embedding model)
    * out:
      * combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_honesty_component_scores.csv.gzip
* **process_twitter_timelines.ipynb**: Creates an URL and a tweet data frame and aggregates the Twitter information with length-corrected belief-speaking and fact-speaking scores and NewsGuard scores (not relevant for this publication).
    * in:
      * combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip (from get_twitter_timelines.ipynb)
      * combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_honesty_component_scores.csv.gzip (from label_glove840B_DDR.sh)
      * metadata-2022110801.csv (NewsGuard scores, not included in repo)
    * out:
      * midterm_URLs_2022-01-01_to_2023-05-01.csv.gzip
      * midterm_tweets_2022-01-01_to_2023-05-01.csv.gzip
* **merge_profile_data.ipynb**: Merges KnowWho candidate profiles with Twitter profile information, exports data for manual research on election margins.
    * in:
      * candidate_twitter_profiles.csv (from get_twitter_profiles.ipynb)
      * KnowWho_profiles_clean.csv (from clean_KnowWho_data.ipynb)
    * out:
      * KnowWho_profiles_merged_twitter.csv
      * primaries_for_margin_research.csv
      * primaries_for_margin_research_RW_JL.csv (after manually adding the election margins and correcting errors)