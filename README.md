# Data processing and analysis code for publication "Belief-speaking in political races"
This repository contains the data processing and analysis scripts for the publication "Belief-speaking in political races". Note that the full reproduction materials include the folders `data/` and `utilities/` which are not located in this GitHub repository because they are too large. Instead, they have been uploaded to an accompanying OSF repository ([DOI: 10.17605/OSF.IO/4RG7P](https://doi.org/10.17605/OSF.IO/4RG7P)). To reproduce the work presented in the paper, download these two folders from the OSF repository and copy them into the main directory of this repository (at the same level as the folders `code/`, `results/`, and `plots/`).

Note also that the reproduction materials do not contain raw tweet texts. Instead, all derived statistics necessary to run the statistical modelling are provided, alongside all IDs of tweets used to derive the statistics. Given access to the Twitter API rehydration feature, tweets can be downloaded again as long as they haven't been deleted by the users. We are also willing to share tweet texts with other researchers for research purposes upon reasonable request. Furthermore, we do not publish the NewsGuard website ratings used for the exploratory analysis because they are proprietary. For researchers that do not have access to the NewsGuard ratings, we advise to use the alternative non-proproetary ratings published by Lin et al. (2023, DOI: [10.1093/pnasnexus/pgad286](https://doi.org/10.1093/pnasnexus/pgad286)).

## Workflow data preparation
* **clean_KnowWho_data.ipynb**: Loads and cleans the raw midterm candidate lists from KnowWho.
    * in:
      * `data/raw/candidates_exp09142022.csv` (from [KnowWho](https://kw1.knowwho.com/candidate-data/candidate-lists/))
    * out:
      * `data/tmp/KnowWho_profiles_clean.csv`
* **get_twitter_profiles.ipynb**: Retrieves the profile information of the midterm candidates from the Twitter API.
    * in:
      * `data/tmp/KnowWho_profiles_clean.csv` (from `clean_KnowWho_data.ipynb`)
    * out:
      * `data/tmp/candidate_twitter_profiles.csv`
* **get_twitter_timelines.ipynb**: Retrieves the timelines of candidates from the Twitter API, cleans and combines all timelines. Also extracts URLs for unravelling and organises URL unravelling (not relevant for this publication).
    * in:
      * `data/tmp/candidate_twitter_profiles.csv` (from `get_twitter_profiles.ipynb`)
      * `utilities/url_shorteners.txt` (list of common URL shortening services)
    * out:
      * `data/raw/combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip`
      * `data/raw/combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean_tweetIDs.txt`
      * `data/tmp/midterm_candidates_unraveled_urls.csv.xz` (relevant only for exploratory analysis)
* **merge_profile_data.ipynb**: Merges KnowWho candidate profiles with Twitter profile information, exports data for manual research on election margins.
    * in:
      * `data/tmp/candidate_twitter_profiles.csv` (from `get_twitter_profiles.ipynb`)
      * `data/tmp/KnowWho_profiles_clean.csv` (from `clean_KnowWho_data.ipynb`)
    * out:
      * `data/tmp/KnowWho_profiles_merged_twitter.csv`
      * `data/tmp/primaries_for_margin_research.csv`
      * `data/raw/primaries_for_margin_research_RW_JL.csv` (after manually adding the election margins and correcting errors)
* **split_data.ipynb**: Splits the full candidate timelines into three data sets: (i) the study data set encompassing four weeks worth of tweets before and after each election, (ii) the first pilot data set encompassing all tweets from 2022-01-01 up to 16 weeks before each election, and (iii) the second pilot data set encompassing all tweets starting 16 weeks after each election and up to 2023-05-01. Creates the temporary files pilot_data1_text.csv.gzip, pilot_data2_text.csv.gzip and study_data_text.csv.gzip containing the tweet texts and IDs and calls the script **label_glove840B_DDR.sh** to calculate the honesty components from the tweet texts (see below).
    * in:
      * `data/raw/combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip` (from `get_twitter_timelines.ipynb`)
      * `data/tmp/KnowWho_profiles_merged_twitter.csv` (from `merge_profile_data.ipynb`)
      * `data/raw/primaries_for_margin_research_RW_JL.csv` (from `merge_profile_data.ipynb` after manually adding the election margins and correcting errors)
      * `data/tmp/pilot_data1_honesty_component_scores.csv.gzip` (from `label_glove840B_DDR.sh`, called internally, see below)
      * `data/tmp/pilot_data2_honesty_component_scores.csv.gzip` (from `label_glove840B_DDR.sh`, called internally, see below)
    * out:
      * `data/processed/study_data.csv.gzip` (study data minus tweet texts for power analysis)
      * `data/processed/pilot_data1.csv.gzip` (pilot data set 1 minus tweet texts for variance component estimation)
      * `data/processed/pilot_data2.csv.gzip` (pilot data set 2 minus tweet texts for variance component estimation)
* **label_glove840B_DDR.sh** (calls compute_sbert_avg_lexicon.py internally): Computes belief-speaking and fact-speaking scores of tweets in the first pilot data set and second pilot data set.
    * in:
      * `data/tmp/pilot_data1_text.csv.gzip` (from `split_data.ipynb`)
      * `data/tmp/pilot_data2_text.csv.gzip` (from `split_data.ipynb`)
      * `utilities/belief_speaking_p=0.05_swapped_wn_def_example.csv` (belief-speaking dictionary)
      * `utilities/fact_speaking_p=0.05_swapped_wn_def_example.csv` (fact-speaking dictionary)
      * `utilities/sentence-transformers` (sentence embedding model)
    * out:
      * `data/tmp/pilot_data1_honesty_component_scores.csv.gzip`
      * `data/tmp/pilot_data2_honesty_compone nt_scores.csv.gzip`
     
## Workflow analysis
* **estimate_variance_factors_pilot_data.ipynb**: Estimates the different variance factors from the pilot data for the power analysis.
    * in:
        * `data/processed/pilot_data1.csv.gzip`
        * `data/processed/pilot_data2.csv.gzip`
    * out:
        * `results/variance_components/variance_components_election_analysis_belief_speaking.txt`
        * `results/variance_components/variance_components_election_analysis_fact_speaking.txt`
        * `results/variance_components/variance_components_incumbent_analysis_belief_speaking.txt`
        * `results/variance_components/variance_components_vote_percent_analysis_belief_speaking.txt`
* **analyse_elections.ipynb**: Conducts the power analysis for hypotheses 1 and 2 – the effect of before and after an election on the prevalence of belief-speaking and fact-speaking.
    * in:
        * `results/variance_components/variance_components_election_analysis_belief_speaking.txt`
        * `results/variance_components/variance_components_election_analysis_fact_speaking.txt`
        * `data/study_data.csv.gzip`
    * out:
        * `results/elections_belief-speaking_power_analysis.csv`
        * `results/elections_fact-speaking_power_analysis.csv`
        * `plots/power_analysis_elections.pdf`
* **analyse_incumbents.ipynb**: Conducts the power analysis for hypothesis 3 – the effect of being an incumbent in an election on the prevalence of belief-speaking.
    * in:
        * `results/variance_components/variance_components_incumbent_analysis_belief_speaking.txt`
        * `data/study_data.csv.gzip`
    * out:
        * `results/incumbent_power_analysis.csv`
        * `plots/power_analysis_incumbent.pdf`
* **analyse_vote_percent.ipynb**: Conducts the power analysis for hypothesis 4 – the effect of being a favourite (operationalised via the percent of the vote gained) on the prevalence of belief-speaking.
    * in:
        * `results/variance_components/variance_components_vote_percent_analysis_belief_speaking.txt`
        * `data/study_data.csv.gzip`
    * out:
        * `results/vote_share_power_analysis.csv`
        * `plots/power_analysis_vote_share.pdf`
* **data_distribution_plots.ipynb**: creates figure 1 - the distribution of tweets in the study and pilot data sets over time.
  * in:
    * `data/study_data.csv.gzip`
    * `data/pilot_data1.csv.gzip`
    * `data/pilot_data2.csv.gzip`
  * out:
    * `plots/data_distribution.pdf`

## Exploratory: trustworthiness analysis
* **exploratory_create_url_data.ipynb**: Creates an URL data frame and aggregates the Twitter information with NewsGuard scores.
    * in:
      * `data/raw/combined_midterm_candidate_timelines_2022-01-01_to_2023-05-01_clean.csv.gzip` (from `get_twitter_timelines.ipynb`)
      * `data/raw/metadata-2022110801.csv` (NewsGuard scores, not included in repo)
    * out:
      * `data/tmp/midterm_URLs_2022-01-01_to_2023-05-01.csv.gzip`