import pandas as pd
import numpy as np
import csv
import fasttext
from scipy.spatial.distance import cosine
from scipy.stats import ttest_rel
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
import subprocess
import scipy
from scipy.stats import ttest_1samp



# load data
df = pd.read_csv("comp_extraction_for_transparency_gerALL_cleaned.csv", sep=";")
print(df)

# load fastText model
ft = fasttext.load_model("cc.de.300.bin")

#----------------
## functions
def get_vec(word):
    return ft.get_word_vector(word)

def cosine_sim(v1, v2):
    return 1 - cosine(v1, v2)

# compositional veczors
def compose(v1, v2):
    return v1 + v2

# make surface vectors for queried consts
def make_AB_surface(row):
    return row["const_1_text"] + row["const_2_text"]

def make_BC_surface(row):
    return row["const_2_text"] + row["const_3_text"]

#----------------------
## prep data
# exztract all the different vectors
rows = []

for _, row in df.iterrows():
    # single constituent lemmas
    vA = get_vec(row["const_1_lemma"])
    vB = get_vec(row["const_2_lemma"])
    vC = get_vec(row["const_3_lemma"])

    # composed embedded comps
    vAB_comp = compose(vA, vB)
    vBC_comp = compose(vB, vC)

    # queried embedded comps / surface form extracted via text
    AB_surface = make_AB_surface(row)
    BC_surface = make_BC_surface(row)

    vAB_query = get_vec(AB_surface)
    vBC_query = get_vec(BC_surface)

    # whole comps
    vABC = get_vec(row["compound"])

    rows.append({"compound": row["compound"],"gold": row["gold_branching"],"vA": vA, "vB": vB, "vC": vC, "vAB_comp": vAB_comp, "vBC_comp": vBC_comp, "vAB_query": vAB_query,"vBC_query": vBC_query, "vABC": vABC})

vec_df = pd.DataFrame(rows)

#------------------
# calc all metrics
# semantic coherence of the competing branching structures
# via sim of structure to sim of whole comp
for rep in ["comp", "query"]:
    vec_df[f"sim_AB_ABC_{rep}"] = vec_df.apply(lambda r: cosine_sim(r[f"vAB_{rep}"], r["vABC"]), axis=1)
    vec_df[f"sim_BC_ABC_{rep}"] = vec_df.apply(lambda r: cosine_sim(r[f"vBC_{rep}"], r["vABC"]), axis=1)

# head-structure coherence by branching structure (more similar: A to BC or Ab to C)

for rep in ["comp", "query"]:
    vec_df[f"sim_AB_C_{rep}"] = vec_df.apply(lambda r: cosine_sim(r[f"vAB_{rep}"], r["vC"]), axis=1)
    vec_df[f"sim_A_BC_{rep}"] = vec_df.apply(lambda r: cosine_sim(r["vA"], r[f"vBC_{rep}"]), axis=1)

# delta coherence measure / get coherence deltas between internal and whole-word
# if delta > 0 = AB predicted, else BC

for rep in ["comp", "query"]:
    vec_df[f"delta_{rep}"] = (vec_df[f"sim_AB_ABC_{rep}"] - vec_df[f"sim_BC_ABC_{rep}"])

# transparency asymmetry
#

for rep in ["comp", "query"]:
    vec_df[f"TA_AB_{rep}"] = (vec_df[f"sim_AB_ABC_{rep}"] / (cosine_sim(vec_df.loc[0, "vA"], vec_df.loc[0, "vABC"]) + cosine_sim(vec_df.loc[0, "vB"], vec_df.loc[0, "vABC"])))

    vec_df[f"TA_BC_{rep}"] = (vec_df[f"sim_BC_ABC_{rep}"] / (cosine_sim(vec_df.loc[0, "vB"], vec_df.loc[0, "vABC"]) +cosine_sim(vec_df.loc[0, "vC"], vec_df.loc[0, "vABC"])))
#-----------------------------

# test representations: which of the reps is a stronger rep of the internal structure
# composed or queried?
# paired ttest plus cohens delta

# FIRST per internal structre
# If: Mean(comp − query) > 0 and significant = compsoed representation is more similar to whole word
#If: Mean(comp − query) < 0 and significant =queried representation more smiliar to  whole word
#
# If not significant: no reliable difference in representational strength

for node in ["AB", "BC"]:

    comp_vals = vec_df[f"sim_{node}_ABC_comp"]
    query_vals = vec_df[f"sim_{node}_ABC_query"]

    t, p = ttest_rel(comp_vals, query_vals)

    diff = comp_vals - query_vals
    cohens_d = diff.mean() / diff.std(ddof=1)

    print(f"{node} node:")
    print("Mean comp:", comp_vals.mean())
    print("Mean query:", query_vals.mean())
    print("Mean difference (comp - query):", diff.mean())
    print("Cohen's d =", round(cohens_d, 3))
    print("t =", round(t, 3), ", p =", p)


# SECOND collapsed for glaobally stronger rep

all_comp = np.concatenate([
    vec_df["sim_AB_ABC_comp"].values,
    vec_df["sim_BC_ABC_comp"].values
])

all_query = np.concatenate([
    vec_df["sim_AB_ABC_query"].values,
    vec_df["sim_BC_ABC_query"].values
])

t, p = ttest_rel(all_comp, all_query)

diff_global = all_comp - all_query
cohens_d_global = diff_global.mean() / diff_global.std(ddof=1)

print("Global comparison:")
print("Mean comp:", all_comp.mean())
print("Mean query:", all_query.mean())
print("Mean difference (comp - query):", diff_global.mean())
print("Cohen's d =", round(cohens_d_global, 3))
print("t =", round(t, 3), ", p =", p)



#-----------------------
## statistical eval of coherence metrics (general and HA):
# FIRST
# is the internal node of the gold branching more similar
# to the whole-word than the competing branching structire?

# sim prep
def gold_vs_competing(row, rep):
    if row["gold"] == "AB":
        return row[f"sim_AB_ABC_{rep}"], row[f"sim_BC_ABC_{rep}"]
    else:
        return row[f"sim_BC_ABC_{rep}"], row[f"sim_AB_ABC_{rep}"]

for rep in ["comp", "query"]:
    vec_df[[f"gold_sim_{rep}", f"comp_sim_{rep}"]] = vec_df.apply(lambda r: pd.Series(gold_vs_competing(r, rep)), axis=1)

# paired ttest for corr
# p < 0.05 = hypothesis confirmed

for rep in ["comp", "query"]:
    t, p = ttest_rel(vec_df[f"gold_sim_{rep}"],vec_df[f"comp_sim_{rep}"])
    print(f"ttest (general similarity of internal to whole) {rep.upper()} representation:")
    print(f"t = {t:.3f}, p = {p}\n")

## SECOND
# is the gold branching more head-aligned than the competing/
# gold-head-structure = more coherent than competing structre?

# HA prep
def gold_vs_competing(row, rep):
    if row["gold"] == "AB":
        return row[f"sim_AB_C_{rep}"], row[f"sim_A_BC_{rep}"]
    else:
        return row[f"sim_A_BC_{rep}"], row[f"sim_AB_C_{rep}"]

for rep in ["comp", "query"]:
    vec_df[[f"gold_HA_{rep}", f"comp_HA_{rep}"]] = vec_df.apply(lambda r: pd.Series(gold_vs_competing(r, rep)), axis=1)

# paired ttest for corr
# p < 0.05 = hypothesis confirmed

for rep in ["comp", "query"]:
    t, p = ttest_rel(vec_df[f"gold_HA_{rep}"],vec_df[f"comp_HA_{rep}"])
    print(f"ttest (similarity of modifier to head) {rep.upper()} representation:")
    print(f"t = {t:.3f}, p = {p}\n")

#-----------
## statistical eval of TA:

# is embedded reliably more than the sum of its parts?
# test whether the internal node of the gold structure is more coherent than the sum of its parts
# If significant and mean > 0: gold internal node is reliably more coherent than the additive baseline
# one-samlpe test

for rep in ["comp", "query"]:

    # get gold TA
    gold_TA = vec_df.apply(
        lambda row:
            row[f"TA_AB_{rep}"] if row["gold"] == "AB"
            else row[f"TA_BC_{rep}"],
        axis=1
    )

    t, p = ttest_1samp(gold_TA, 0)

    print(f"one-sample test (TA){rep.upper()} representation:")
    print("Mean TA_gold:", gold_TA.mean(), ", t =", round(t, 3), ", p =", p)

# test competition: Is TA of gold higher than TA of competing structure?
# paried ttest
# Is TA_gold > TA_comp/ does TA prefer the gold structure over the competitor?
# does transparnecy asymmetry support the gold branching

for rep in ["comp", "query"]:

    TA_gold = vec_df.apply(
        lambda row:
            row[f"TA_AB_{rep}"] if row["gold"] == "AB"
            else row[f"TA_BC_{rep}"],
        axis=1
    )

    TA_comp = vec_df.apply(
        lambda row:
            row[f"TA_BC_{rep}"] if row["gold"] == "AB"
            else row[f"TA_AB_{rep}"],
        axis=1
    )

    t, p = ttest_rel(TA_gold, TA_comp)

    print(f"paired ttest (gold-TA vs. competing TA) {rep.upper()} representation:")
    print("Mean TA_gold:", TA_gold.mean())
    print("Mean TA_comp:", TA_comp.mean())
    print("Mean difference:", (TA_gold - TA_comp).mean())
    print("t =", round(t, 3), ", p =", p)


##----------
# delta pred + get all the other deltas
# does delta coherence predict gold branching?
for rep in ["comp", "query"]:
    accuracy = np.mean(((vec_df[f"delta_{rep}"] > 0) & (vec_df["gold"] == "AB")) | ((vec_df[f"delta_{rep}"] < 0) & (vec_df["gold"] == "BC")))
    print(f"{rep.upper()} delta accuracy: {accuracy:.2f}")

# prediction transparency asymmetry of gold /get TA deltas

for rep in ["comp", "query"]:
    vec_df[f"delta_TA_{rep}"] = (vec_df[f"TA_AB_{rep}"] - vec_df[f"TA_BC_{rep}"])

    vec_df[f"TA_correct_{rep}"] = (((vec_df[f"delta_TA_{rep}"] > 0) & (vec_df["gold"] == "AB")) | ((vec_df[f"delta_TA_{rep}"] < 0) & (vec_df["gold"] == "BC")))

    print(f"{rep.upper()} TA delta accuracy:", vec_df[f"TA_correct_{rep}"].mean())

# pred of head-alignment of gold / get HA deltas

for rep in ["comp", "query"]:
    vec_df[f"delta_HA_{rep}"] = (vec_df[f"sim_AB_C_{rep}"] -vec_df[f"sim_A_BC_{rep}"])

    vec_df[f"HA_correct_{rep}"] = (((vec_df[f"delta_HA_{rep}"] > 0) & (vec_df["gold"] == "AB")) | ((vec_df[f"delta_HA_{rep}"] < 0) & (vec_df["gold"] == "BC")))

    print(f"{rep.upper()} head-alignment delta accuracy:",vec_df[f"HA_correct_{rep}"].mean())

#----------------------
## z-standardization

delta_cols = ["delta_query", "delta_TA_query","delta_HA_query"]

scaler = StandardScaler()
vec_df[[f"z_{c}" for c in delta_cols]] = scaler.fit_transform(vec_df[delta_cols])


##---------------------
# model comparison with aic and likelihood-ratios

# gold to binary for model comparison
model_df = vec_df.copy()
model_df["gold_binary"] = (model_df["gold"] == "AB").astype(int)

# use queried predictors here bc sim to whole-comp higher tahn composed
model_df = model_df[["gold_binary", "z_delta_query", "z_delta_TA_query","z_delta_HA_query", "compound"]].dropna()

# basemodel/ intercept-only baseline
basemodel = smf.glm(
    "gold_binary ~ 1",
    data=model_df,
    family=sm.families.Binomial()
).fit()

# semcorh_model /sem coherence only
semcorh_model = smf.glm(
    "gold_binary ~ z_delta_query",
    data=model_df,
    family=sm.families.Binomial()
).fit()

# SemCoTA_model / SemCo + transparency asymmetrx
SemCoTA_model = smf.glm(
    "gold_binary ~ z_delta_query + z_delta_TA_query",
    data=model_df,
    family=sm.families.Binomial()
).fit()

# SemCoTA_HA_model / SemCo+ta+head-alignment
SemCoTA_HA_model = smf.glm(
    "gold_binary ~ z_delta_query + z_delta_TA_query + z_delta_HA_query",
    data=model_df,
    family=sm.families.Binomial()
).fit()

# allInt_model / all interactions
allInt_model = smf.glm(
    "gold_binary ~ z_delta_query * z_delta_TA_query * z_delta_HA_query",
    data=model_df,
    family=sm.families.Binomial()
).fit()

# model comparsion stats/likelihood-ratio tests of nested models
# p<0.05= added semantic pressure significantly improves model
def likelihoodratio_test(m_small, m_large):
    lr_stats = 2 * (m_large.llf - m_small.llf)
    df = m_large.df_model - m_small.df_model
    p = scipy.stats.chi2.sf(lr_stats, df)
    return lr_stats, df, p

print("likelihoodratio basemodel to semcorh_model:", likelihoodratio_test(basemodel, semcorh_model))
print("likelihoodratio semcorh_model to SemCoTA_model:", likelihoodratio_test(semcorh_model, SemCoTA_model))
print("likelihoodratio SemCoTA_model to SemCoTA_HA_model:", likelihoodratio_test(SemCoTA_model, SemCoTA_HA_model))
print("likelihoodratio SemCoTA_HA_model to allInt_model:", likelihoodratio_test(SemCoTA_HA_model, allInt_model))

# AIC comparison for final model selection
# lower AIC-value= better tradeoff between fit and model complexity
for name, model in zip(["basemodel", "semcorh_model", "SemCoTA_model", "SemCoTA_HA_model", "allInt_model"],[basemodel, semcorh_model, SemCoTA_model, SemCoTA_HA_model, allInt_model]):
    print(name, ' aic value: ', model.aic)

##-----------------------
#gold to binary for lme calc
vec_df["gold_binary"] = (vec_df["gold"] == "AB").astype(int)

# select metrics (all deltas)
model_df_lme = vec_df[["gold_binary", "z_delta_query", "z_delta_TA_query","z_delta_HA_query", "compound"]].dropna()

# pure lme model with random intercept at compound

lme_model = smf.mixedlm(
    "gold_binary ~ z_delta_query + z_delta_TA_query + z_delta_HA_query",
    model_df_lme,
    groups=model_df_lme["compound"]
)

result = lme_model.fit(method=["nm"]) #"lbfgs"
print("Summary mixedlm: ", result.summary())


##--------------
# drop unnecessary vectorcolumns and export csv results
export_vec_df = vec_df.drop(columns=["vA", "vB", "vC","vAB_comp", "vBC_comp", "vAB_query", "vBC_query", "vABC"])

export_vec_df.to_csv("comp_coherence_test_vecdf.csv", index=False)

export_model_df = vec_df.drop(columns=["vA", "vB", "vC","vAB_comp", "vBC_comp", "vAB_query", "vBC_query", "vABC"])

export_model_df.to_csv("comp_coherence_test_modeldf.csv", index=False)
#----------------------
## export data for R analysis

exp_model_df = model_df[["compound","gold_binary", "z_delta_query", "z_delta_TA_query", "z_delta_HA_query"]].copy()

exp_model_df.to_csv("glmm_input.csv", index=False)





