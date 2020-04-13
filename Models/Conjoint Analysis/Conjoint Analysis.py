import pandas as pd
import itertools

def expand_grid(options):
    '''Given a dictionary, return a dataframe with all possible options'''
    rows = itertools.product(*options.values())
    df = pd.DataFrame.from_records(rows, columns=options.keys())
    size = df.shape[0] + 1
    df["Option"] = pd.Series([("Option " + str(i)) for i in range(1, size)])
    df.set_index("Option", inplace=True)
    return df

def score(preference_series, product_offering_series):
    '''Returns the score given depending on the preferences and what the product offers'''
    score = 0
    for feature in product_offering_series:
        score += preference_series[str(feature)]
    return score

def score_all(df_score, df_preference_data, df_offers):
    '''Given a blank df_score with indicies that represent the user
       Fill the df_score with scores depending on preference and offering data'''
    offerings = df_offers.index
    users = df_score.index
    for offering in offerings:
        df_score[offering] = ""
        for user in users:
            df_score.at[user, offering] = score(df_preference_data.loc[user], df_offers.loc[offering])
        df_score[offering] = df_score[offering].astype(int)
    return df_score

def market_share(df_score):
    '''Given a df containing scores and columns being the offerings,
       return a df that has the market share for each customer'''
    offerings = df_score.columns
    df_market_share = pd.DataFrame(index = df_score.index)
    for offering in offerings:
        df_market_share["% "+ str(offering)] = df_score[offering]/df_score.sum(axis=1)
    return df_market_share

# Get Data
df_new_offers_options = pd.read_csv(r"Conjoint Analysis\New Product Offering Data.csv", header = 0, index_col = 0)
df_current_offers = pd.read_csv(r"Conjoint Analysis\Existing Product Offerings Data.csv", header = 0, index_col = 0)
df_preference_data = pd.read_csv(r"Conjoint Analysis\Preference Data.csv", header = 0, index_col = 0)

# Create all possible combinations
df_new_possible_offerings = expand_grid(df_new_offers_options.to_dict(orient="list")).dropna()

# Create score template
df_score = pd.DataFrame()
df_score["Users"] = df_preference_data.index
df_score.set_index("Users", inplace=True)

# Get original score
df_og_score = score_all(df_score.copy(deep=True), df_preference_data, df_current_offers)
# Get new scores
df_new_scores = score_all(df_score.copy(deep=True), df_preference_data, df_new_possible_offerings)

# Calculate the % brand that is earned orignal
number_of_users = len(df_score.index)
print("% Market Share Analysis by Share of Preference:")
df_og_market_share = market_share(df_og_score)
offerings = df_og_market_share.columns
for offering in offerings:
    print("Market share " + offering + ": {} %".format(round(100*df_og_market_share[offering].sum()/number_of_users, 2)))

offering_market_share = pd.Series()
# Calculate the % of each new offering
for new_offering in df_new_scores.columns:
    df_current_with_new = df_og_score.copy(deep=True)
    df_current_with_new[new_offering] = df_new_scores[new_offering]
    df_market_share_with_new = market_share(df_current_with_new)
    offering_market_share[new_offering] = round(100*df_market_share_with_new["% " + new_offering].sum()/number_of_users, 2)
print("\n")

# Once the three scenarios are complete, gather and calculate
print("Top 3 Generated Scenarios: \n")
offering_market_share = offering_market_share.sort_values(ascending=False).head(3)
for new_offering in offering_market_share.index:
    df_current_with_new = df_og_score.copy(deep=True)
    df_current_with_new[new_offering] = df_new_scores[new_offering]
    df_market_share_with_new = market_share(df_current_with_new)
    offerings = df_market_share_with_new.columns
    print("Scenario: " + new_offering)
    print(df_new_possible_offerings.loc[new_offering].to_list())
    print("")
    for offering in offerings:
        print("Market share " + offering + ": {} %".format(round(100*df_market_share_with_new[offering].sum()/number_of_users, 2)))
    print("\n")

# First Choice Only
df_og_score["Preferred Brand"] = df_og_score.idxmax(axis=1)

print("\nPreferred Brand Count:")
print(df_og_score["Preferred Brand"].value_counts())
