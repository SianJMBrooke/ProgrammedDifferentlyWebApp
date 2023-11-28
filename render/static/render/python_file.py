# Import Libraries
import matplotlib.pyplot as plt
import pandas as pd
import scipy
import seaborn as sns
import numpy as np
import statsmodels.formula.api as smf
from scipy.stats import pearsonr
import matplotlib.patches as mpatches

import os

sns.set_theme(style="whitegrid")

# -------------------------------------------------------- #
# Clean the Data
# -------------------------------------------------------- #

# Read in OLMs Data
# os.chdir("~/PycharmProject/DisOLMs")

# Keys
survey_key = pd.read_csv('Rename_Columns.csv').T.to_dict()[0]

survey_raw = pd.read_csv("InDis-OLMS_March+10%2C+2022_01.01.csv").rename(columns=survey_key)
survey_df = survey_raw.drop(survey_raw.index[[0, 1]])

# Drop rows with duplicated emails
survey_df = survey_df.drop_duplicates(subset=["Email", ])
survey_df.drop(["Start Date", "End Date", "Response Type", "Progress", "Duration (in seconds)",
                "Recipient Last Name", "Recipient First Name", "Recipient Email", "External Data Reference",
                "Distribution Channel", "Location Latitude", "Location Longitude", "User Language"],
               axis=1, inplace=True)

# Check for people trying to game the survey
IP_dupes = survey_df.groupby("IP Address").filter(lambda x: len(x) > 1).sort_values("IP Address")
IP_dupes.to_csv("Suspect_Responses.csv")

# Datatypes
for i in survey_df.columns:
    try:
        survey_df[i] = pd.to_numeric(survey_df[i])
    except:
        survey_df[i] = survey_df[i].astype("string")

# Formatting
survey_df["OLI"] = survey_df["OLI"].str.replace(r"\W\(.*\)", "", regex=True)
survey_df["Education"] = survey_df["Education"].str.replace(r"\W\(.*\)", "", regex=True)

survey_df = survey_df[survey_df["Elig_BA"] != "<NA>"]

# Income Column
survey_df["Assume_Day_Income"] = survey_df.apply(lambda x:
                                                 x["Day_Rate"] if x["Day_Rate"] > 0 else x["Hourly_Rate"] * 8,
                                                 axis=1)

# -------------------------------------------------------- #
# Remove Suspects
# -------------------------------------------------------- #
sus_df = pd.read_csv("Suspect_Emails_Removed.csv")
sus_emails = list(sus_df[sus_df["Removed"] == 1]["Email"])
# 166 Data points to remove, suspcious IP addresses.

clean_survey = survey_df[~survey_df["Email"].isin(sus_emails)]

# -------------------------------------------------------- #
# Discrimination Sources
# -------------------------------------------------------- #

recode_freq = {"Never": "0",
               "Yes, but not in the past year": "1",
               "Yes, once or twice in the past year": "2",
               "Yes, many times in the past year": "3"}

clean_survey = clean_survey.replace(recode_freq)

# Overall Metrics of Discrimination Forms (Note this should not be re-run)
clean_survey["Clients_Discrim_Scale"] = clean_survey.filter(regex='^Clients_Discrim_',
                                                      axis=1).astype(int).sum(axis=1) / (3*9)
clean_survey["Freel_Discrim_Scale"] = clean_survey.filter(regex='^Freel_Discrim_',
                                                    axis=1).astype(int).sum(axis=1) / (3*9)
clean_survey["Platform_Discrim_Scale"] = clean_survey.filter(regex='^Platform_Discrim_',
                                                       axis=1).astype(int).sum(axis=1) / (3*8)

# Plot Discrimination Scales
    fig = sns.kdeplot(clean_survey['Clients_Discrim_Scale'], color="r", label="By Clients")
    fig = sns.kdeplot(clean_survey['Freel_Discrim_Scale'], color="b", label="By Other Freelancers")
    fig = sns.kdeplot(clean_survey['Platform_Discrim_Scale'], color="g", label="By Platforms")
    fig.set(xlabel="Standardised Discrimination Scale")
    plt.legend()
    plt.show()

# -------------------------------------------------------- #
# Reformatting and Simplifying
# -------------------------------------------------------- #

skills_dict = {"Expert": 5,
               "Proficient": 4,
               "Competent": 3,
               "Advanced Beginner": 2,
               "Novice": 1}

clean_survey = clean_survey.applymap(lambda x: skills_dict[x] if x in skills_dict else x)

length_dict = {"< 3 months ": 1,
                   "3-6 months": 2,
                   "6-12 months": 3,
                   "1-3 years": 4,
                   "3-5 years": 5,
                   "5-10 yeats": 6,
                   "> 10 years": 7}

clean_survey = clean_survey.applymap(lambda x: length_dict[x] if x in length_dict else x)

# Days to Numbers
clean_survey["Days_Freelance"] = clean_survey["Days_Freelance"].replace(r"\D*", "", regex=True).astype(int)

# Categorical
clean_survey["OLI"] = clean_survey["OLI"].astype("category")
clean_survey["Education"] = clean_survey["Education"].astype("category")
clean_survey["Income_Freelance_Percent"] = clean_survey["Income_Freelance_Percent"].astype("category")

# Remap Values
reformat_general = {"Unsure": np.nan, "Unsure / Don't know ": np.nan, "<NA>": np.nan,
                    "No": "1", "Yes": "2"}
reformat_likert = {"Strongly agree": "5", "Somewhat agree": "4", "Neither agree nor disagree": "3",
                   "Somewhat disagree": "2", "Strongly disagree": "1"}
reformat_situ = {"It's comfortable": "5", "It's sufficient": "4", "It's tight but okay, we need to be careful": "3",
                 "We have a hard time making ends meet": "2", "We can't manage without getting into debt": "1",
                 "I don't know / I don't want to answer": np.nan}

clean_survey["Disability_Num"] = pd.to_numeric(clean_survey["Disability"].str.replace(r"(I\s.*)", "1", regex=True)\
    .replace("No disability", "2"))

clean_survey = clean_survey.replace(reformat_general)
clean_survey = clean_survey.replace(reformat_likert)
clean_survey = clean_survey.replace(reformat_situ)

# Simplify Ethnicity
reformat_ethno = {"English / Welsh / Scottish / Northern Irish / British": "White",
                  "Irish": "White",
                  "Gypsy or Irish Traveller": "White",
                  "Any other White background, please describe": "White",
                  "White and Black Caribbean": "Multiple",
                  "White and Black African": "Multiple",
                  "White and Asian": "Multiple",
                  "Any other Mixed / Multiple ethnic backgrounds, please describe": "Multiple",
                  "Indian": "Asian",
                  "Pakistani": "Asian",
                  "Bangladeshi": "Asian",
                  "Any other Asian background, please describe": "Asian",
                  "African": "Black",
                  "Caribbean": "Black",
                  "Any other Black/African/Caribbean background, please describe": "Black",
                  "Any other ethnic group, please describe": "Other" }

clean_survey["Ethnicity_Simple"] = clean_survey["Ethnicity"].replace(reformat_ethno)

clean_survey["Intersectionality"] = clean_survey["Gender"] + "_" + clean_survey["Ethnicity_Simple"]


fig = sns.kdeplot(clean_survey['Days_Freelance'], hue=clean_survey["Ethnicity_Simple"])
plt.show()

# Rating own skills as freelancer
fig = sns.kdeplot(clean_survey['Freelance_Skills'], hue=clean_survey["Education"])
plt.show()

# -------------------------------------------------------- #
# Descriptive Statistics
# -------------------------------------------------------- #

# Describe
clean_survey.describe()
clean_survey.dtypes

# Demographics
def describe_olm(col, df=clean_survey):
    """
    Returns description of column in OLM survey.
    """
    type_col = df[col].dtype
    if type_col == int:
        return df[col].describe()
    else:
        return df[col].value_counts(normalize=True, dropna=False,
                                    ascending=True)


Gender = describe_olm("Gender")
Ethnicity = describe_olm("Ethnicity_Simple")
Age = describe_olm("Age")
Disability = describe_olm("Disability")
Edu = describe_olm("Education")
OLI = describe_olm("OLI")

# Cross Tabulate
table = pd.crosstab(survey_df["Gender"], survey_df["OLI"])


# Cross Tab Visual
def crossplot_olm(var, group, df=clean_survey, thres=5):
    """
    Implementation of seaborn catplot. Plots % of var by group.
    """
    x, y = var, group

    df = df.groupby(y).filter(lambda x: len(x) > thres)
    df = df.groupby(x).filter(lambda x: len(x) > thres)

    df1 = df.groupby(x)[y].value_counts(normalize=True)
    df1 = df1.mul(100)
    df1 = df1.rename('Percent').reset_index()

    g = sns.catplot(x=x, y='Percent', hue=y, kind='bar', data=df1,
                    palette='Set2', alpha=.4)
    g.ax.set_ylim(0, 100)
    g.ax.set_xticklabels(g.ax.get_xticklabels(), rotation=90)

    for p in g.ax.patches:
        txt = str(p.get_height().round(0)) + '%'
        txt_x = p.get_x()
        txt_y = p.get_height()
        g.ax.text(txt_x, txt_y, txt)
    plt.subplots_adjust(bottom=0.35)
    plt.show()


crossplot_olm("OLI", "Gender")

order_percent = ["0-20%", "20-40%", "40-60%", "60-80%", "80-100%"]

sns.violinplot(x="Income_Freelance_Percent", y="Assume_Day_Income",
               hue="Gender", data=clean_survey, order=order_percent,
               palette="muted")
plt.subplots_adjust(bottom=0.35)
plt.show()

# -------------------------------------------------------- #
# Exploratory for Paper
# -------------------------------------------------------- #

# BA Break down
# 1. Identity: Gender, Age, Ethnicity, Education, Employment Status
# 2. Life Context: Dependents, Financial Situation
# 3. Freelancing: OLI, Length Freelancing (Years), Days Freelancing,
# Income from freelancing (%), Projects at Once, Assumed Income, Platforms
# 4. Profile Attributes: Real Name, Profile Picture, Ranking
# 5. Attracting Work: Platforms, Advertise
# 6. Skills: Soft Skills, Freelancing Skills
# 7. Positive about Freelancing
# 8. Negative Experiences (Not being paid etc.), Behaviour
# 9. Discrimination: Platforms, Clients, Other Freelancers
# (Any significant diff between gender, ethnicity, intersectionality)
# 10. Responses to Discrimination

foo = pd.Categorical(clean_survey["Gender"])
bar = pd.Categorical(clean_survey["Ethnicity_Simple"])
print(pd.crosstab(foo, bar).to_latex())

# -------------------------------------------------------- #
# Differences in Experiences
# -------------------------------------------------------- #
# Gender Tests
gender_diff = ["Age", "Freelance_Skills", "Clients_Discrim_Scale", "Freel_Discrim_Scale",
               "Platform_Discrim_Scale"]

# Drop gender-queer to t-test
clean_survey = clean_survey.groupby("Gender").filter(lambda x: len(x) > 5)

clean_survey["Gender_Num"] = clean_survey["Gender"].map({"Woman": 1, "Man": 2})

for i in gender_diff:
    df = clean_survey
    result = scipy.stats.ttest_ind(df["Gender_Num"], df[i], equal_var=False)
    if result[1] > .05:
        print("SIGNIFICANT:\n", i, result, "\n")
    else:
        print("NOT SIGNIFICANT:\n", i, "\n")

cols = ["Clients_Discrim_Scale", "Freel_Discrim_Scale", "Platform_Discrim_Scale"]

# Heatmap
def input_heat(input, output=cols, df=clean_survey):
    """
    Plots heat map of independent to dependent variables.
    """
    plt.figure(figsize=(8, 12))
    output.append(input)

    corr_df = df[output].corr()[[input]].sort_values(by=input, ascending=False)
    pvals = df[output].corr(method=lambda x, y: pearsonr(x, y)[1])  - np.eye(*df[output].corr().shape)

    heatmap = sns.heatmap(corr_df[pvals <0.05], vmin=-1, vmax=1, annot=True,
                          cmap='RdBu_r')
    heatmap.set_title('Features Correlating with {}'.format(input.replace("_", " ")),
                      fontdict={'fontsize': 18}, pad=16)
    colors = [sns.color_palette("Greys", n_colors=1, desat=1)[0]]

    texts = [f"Not Significant (at {0.05})"]
    patches = [mpatches.Patch(color=colors[i], label="{:s}".format(texts[i])) for i in range(len(texts))]
    plt.legend(handles=patches, loc='best')
    plt.show()

# -------------------------------------------------------- #
# Clustering
# -------------------------------------------------------- #

# Variables to cluster on:
#      Discrimination Typology, Soft and Freelancing Skills,
#      Length Freelance, Days Freelance, Assumed Income,
#      Positives.


# -------------------------------------------------------- #
# EXTRA
# -------------------------------------------------------- #

# Analysis
# Self judgement (by identity groups) of skill and rates (controlling for OLI)

# Fit regression model (using the natural log of one of the regressors)
results = smf.ols('Assume_Day_Income ~ Age + Education', data=clean_survey).fit()

# What is most important in day rate? (OLI or Confidence or Experience)
# Do higher skills lead to higher pay? (Across Identity Groups)
# Do different intersectional identities experience different discrimination

# -------------------------------------------------------- #
# Interview Selection
# -------------------------------------------------------- #

# Want to be interviewed
interview_df = clean_survey[clean_survey["Interview"] == "Yes, I would like to be contacted."]

# Harassment frequency
interview_df["Interview_discrim"] = interview_df[["Clients_Discrim_Scale",
                                                  "Freel_Discrim_Scale"]].sum(axis=1)

interview_col = ["Pronouns", "Intersectionality", "Age", "Education", "OLI",
                 "Length_Frelance", "Pos_Enjoy_Freelance", "Clients_Discrim", "Freel_Discrim",
                 "Platform_Discrim", "Email", "Assume_Day_Income", "Interview_discrim",
                 "Clients_Discrim_Scale", "Freel_Discrim_Scale", "Platform_Discrim_Scale"]

interview_df = interview_df[interview_col]

discrim_col = ["Clients_Discrim", "Freel_Discrim", "Platform_Discrim"]

interview_df[discrim_col] = interview_df[discrim_col].replace({"Unsure / Don't know ": np.nan,
                                                               "No": np.nan, "<NA>": np.nan})

shortlist_df = interview_df.dropna(subset=discrim_col, thresh=1).reset_index()
shortlist_df[["OLI", "Intersectionality", "Interview_discrim", "Email"]].to_csv("InterviewCandidates.csv")

# Interview
#    What are the hypothesis from the data?
#    Who has experienced higher frequency?

# Fabian: What can help freelancers get over the inital difficulty when they start?

