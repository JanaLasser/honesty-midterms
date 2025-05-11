from sentence_transformers import SentenceTransformer, util, models
import torch
import pickle
import argparse
import numpy as np
import pandas as pd
from pandarallel import pandarallel
pandarallel.initialize(nb_workers=15)

def config(parser):
    parser.add_argument('--model_name_or_path')
    parser.add_argument('--input_file')
    parser.add_argument('--output_file')
    parser.add_argument('--fact_lexicon')
    parser.add_argument('--belief_lexicon')
    parser.add_argument('--avg_dict', action="store_true")
    parser.add_argument('--verbalize_label', action="store_true")
    parser.add_argument('--save_embeddings', action="store_true")
    parser.add_argument('--use_word_definition', action="store_true")
    parser.add_argument('--use_definition', action="store_true")
    parser.add_argument('--use_example', action="store_true")
    parser.add_argument('--average_of_similarity', action="store_true")
    parser.add_argument('--maximum_of_similarity', action="store_true")
    parser.add_argument('--smoke_test', action="store_true")
    parser.add_argument('--text_column', type=str, default='text')
    parser.add_argument('--corpus', type=str)
    parser.add_argument('--compression_type', type=str, default='infer')
    parser.add_argument('--length_threshold', type=int, default=10)
    parser.add_argument('--tab_delimiter', action="store_true")
    return parser 

def preprocess(df, args):
    df["text"].replace(
        to_replace=[r"(?:https?:\/\/(?:www\.|(?!www))[^\s\.]+\.[^\s]{2,}|www\.[^\s]+\.[^\s]{2,})"],
        value=[""], 
        regex=True,
        inplace=True
    )
    df["text"].replace(to_replace=r"&.*;", value="", regex=True, inplace=True)
    df["text"].replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=["",""], regex=True, inplace=True) 
    df["text"].replace(to_replace=r"\s+", value=" ", regex=True, inplace=True)
    df["text"].replace(to_replace=r"\@\w+", value="@user", regex=True, inplace=True)

    #if 'text' in df.columns:
    #    df = df.drop_duplicates(subset='text', keep='first')
    if 'id' in df.columns:
        df = df.drop_duplicates(subset='id', keep='first')
    if args.corpus == 'Twitter':
        df['id'] = df['id'].str.replace('"', '')
        if 'retweeted' in df.columns:
            df = df[~df.retweeted]
        def tw_len(x):
            x = str(x).split()
            x_filter = filter(lambda x: x != '@user', x)
            x_filter = list(x_filter)
            return len(x_filter)
        df['length'] = df.text.parallel_apply(tw_len)
    else:
        def text_len(x):
            x = str(x).split()
            return len(x)
        df['length'] = df.text.parallel_apply(text_len)
    if args.length_threshold:
        df = df[df.length > args.length_threshold]
    return df

def get_embeddings(text, model_name_or_path):
    model = SentenceTransformer(model_name_or_path)
    #encode text in batches perhaps save this to disk
    corpus_embeddings = model.encode(
        text, batch_size=1024,
        show_progress_bar=True, 
        convert_to_tensor=True
    ) 
    assert len(corpus_embeddings) == len(text)
    return corpus_embeddings

def compute_similarity(text_embeddings, label_embeddings):
    cos_sim = util.cos_sim(text_embeddings, label_embeddings)
    return cos_sim

def main(args):
    delimiter = '\t' if args.tab_delimiter else None
    if args.smoke_test:
        print("running in test-mode, processing only the first 1000 entries")
        df = pd.read_csv(
            args.input_file, 
            nrows=1000, 
            compression=args.compression_type, 
            delimiter=delimiter,
            dtype={"id":str}
        )
    else:
        df = pd.read_csv(
            args.input_file, 
            compression=args.compression_type, 
            delimiter=delimiter,
            dtype={"id":str}
        )
    
    #rename text column if different from text
    if args.text_column != 'text':
        df = df.rename(columns = {args.text_column:'text'})
    df = preprocess(df, args)
    all_text = df['text']
    all_text = list(all_text)
    text_embeddings = get_embeddings(all_text, args.model_name_or_path)       

    if args.save_embeddings:
        output_fn = args.output_file.replace(".csv", ".pkl")
        with open(output_fn, "wb") as fout:
            pickle.dump(
                {'text': all_text, 'embeddings': text_embeddings},
                fout, 
                protocol=pickle.HIGHEST_PROTOCOL
            )

    fact_keywords = pd.read_csv(args.fact_lexicon) 

    if args.verbalize_label:
        fact_keywords = ["The text expresses "+ l for \
                          l in list(fact_keywords['fact_speaking'])] 
    elif args.use_definition:
        fact_keywords = list(fact_keywords['definition'])
    elif args.use_word_definition:
        fact_keywords = list(fact_keywords['fact_speaking'] + " " \
                              + fact_keywords['definition'])
    elif args.use_example:
        fact_keywords = list(fact_keywords['example'].dropna())
    else:
        fact_keywords = list(fact_keywords['fact_speaking'])  

    fact_embeddings = get_embeddings(fact_keywords, args.model_name_or_path)
    
    if args.avg_dict:
        fact_embeddings = torch.mean(fact_embeddings, dim=0)

    belief_keywords = pd.read_csv(args.belief_lexicon) 
    if args.verbalize_label:
        belief_keywords = ["The text expresses "+ l for l in belief_keywords] 
    elif args.use_definition:
        belief_keywords = list(belief_keywords['definition'])
    elif args.use_word_definition:
        belief_keywords = list(belief_keywords['belief_speaking'] + " " \
                               + belief_keywords['definition'])
    elif args.use_example:
        belief_keywords = list(belief_keywords['example'].dropna())
    else:
        belief_keywords = list(belief_keywords['belief_speaking'])  
    belief_embeddings = get_embeddings(belief_keywords, args.model_name_or_path)
    if args.avg_dict:
        belief_embeddings = torch.mean(belief_embeddings, dim=0)

    fact_sim = util.cos_sim(text_embeddings, fact_embeddings)
    belief_sim = util.cos_sim(text_embeddings, belief_embeddings)

    if args.corpus == "Articles":
        output_cols = ["url"]
    else:
        output_cols = ["id"]
        
    #average of similarity scores
    if args.average_of_similarity:
        avg_fact_score = np.average(fact_sim.cpu().numpy(), axis=1)  
        avg_belief_score = np.average(belief_sim.cpu().numpy(), axis=1)  
        df['avg_fact_score'] = avg_fact_score
        df['avg_belief_score'] = avg_belief_score
        output_cols.extend(["avg_fact_score", "avg_belief_score"])

    elif args.maximum_of_similarity:
        #maximum of similarity scores
        max_fact_scores = np.max(fact_sim.cpu().numpy(), axis=1)  
        max_idxs = np.argmax(fact_sim.cpu().numpy(), axis=1)  
        max_fact_keywords = [fact_keywords[max_idx] for max_idx in max_idxs]

        max_belief_scores = np.max(belief_sim.cpu().numpy(), axis=1)  
        max_idxs = np.argmax(belief_sim.cpu().numpy(), axis=1)  
        max_belief_keywords = [belief_keywords[max_idx] for max_idx in max_idxs]

        df['max_fact_scores'] = max_fact_scores
        df['max_fact_keyword'] = max_fact_keywords

        df['max_belief_score'] = max_belief_scores
        df['max_belief_keyword'] = max_belief_keywords
        output_cols.extend(["max_fact_score", "max_fact_keyword",
                            "max_belief_score", "max_belief_keyword"])
 
    print(df[output_cols].head())
    df[output_cols].to_csv(
        args.output_file, 
        index=False, 
        compression=args.compression_type
    )
        
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = config(parser)
    args = parser.parse_args()
    main(args)

