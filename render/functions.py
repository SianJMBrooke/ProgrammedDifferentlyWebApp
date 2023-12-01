import re
import random
import numpy as np
import pandas as pd
import pickle5 as pickle

from pylint.lint import Run

model_path = "render/static/render/gender_guess_model_mk4-down.pkl"
txt_path = "render/static/render/pylint_error_names.txt"


def process_py(py_file):
    """
    Processes uploaded python file and produces a guess and score.
    :param py_file: python file to guess
    :return:
    """
    gender_guesser = pickle.load(open(model_path, "rb"))
    random.seed(42)

    # Run pylint on the uploaded file
    results = Run([py_file, "--reports=y", "--enable=all"], exit=False)

    pylint_score = results.linter.stats.global_note
    mod_comp_dict = results.linter.stats.code_type_count
    mod_const_dict = results.linter.stats.node_count

    features_dict = {  # Module Constituents
        "Str_Function": mod_const_dict["function"],
        "Str_Method": mod_const_dict["method"],
        "Str_Klass": mod_const_dict["klass"],
        # Module Components
        "Str_Total_Lines": mod_comp_dict["total"],
        "Str_Code_Lines": mod_comp_dict["code"],
        "Str_Empty_Lines": mod_comp_dict["empty"],
        "Str_Docstring_Lines": mod_comp_dict["docstring"],
        "Str_Comment_Lines": mod_comp_dict["comment"],
        # Style Checker Messages (below)
        "Component Checker": [],
        "Frequency": []}

    for m, f in results.linter.stats.by_msg.items():
        features_dict["Component Checker"].append(m)
        features_dict["Frequency"].append(f)

    component_df = pd.DataFrame(features_dict)
    component_df["Component Checker"] = [[i] for i in component_df["Component Checker"]]
    component_df["Component Checker"] = component_df["Component Checker"] \
        .multiply(component_df["Frequency"], axis="index")
    component_df = component_df.explode("Component Checker")

    # Group the Checkers
    with open(txt_path, "r") as file:
        pylint_sum = file.read()

    cat_py = re.findall(r"(?<=   )(.+)(?=\/)", pylint_sum)
    mssg_py = re.findall(r"(?<=\/)(.+)", pylint_sum)

    checker_dict = dict(zip(mssg_py, cat_py))
    component_df["Checker Group"] = component_df["Component Checker"].map(checker_dict)
    component_df.drop(["Component Checker", "Frequency"], axis=1, inplace=True)

    check_cols = ["Checker Group_convention", "Checker Group_error", "Checker Group_information",
                  "Checker Group_refactor", "Checker Group_warning"]

    features = pd.get_dummies(component_df)
    feature_list = list(features.columns)

    extra_cols = list(set(check_cols).difference(feature_list))
    feature_list.extend(extra_cols)
    features[extra_cols] = 0

    features = features[list(set(feature_list + extra_cols))]
    features = np.array(features)

    output_gender_guess = gender_guesser.predict(features)[0]
    output_gender_proba = gender_guesser.predict_proba(features)[0]

    if output_gender_guess == 0:
        output_gender_guess = "Feminine"
    else:
        output_gender_guess = "Masculine"

    feature_list = ['Str_Function', 'Str_Method', 'Str_Klass', 'Str_Total_Lines',
                    'Str_Code_Lines', 'Str_Empty_Lines', 'Str_Docstring_Lines',
                    'Str_Comment_Lines', 'Checker_Group_convention', 'Checker_Group_error',
                    'Checker_Group_information', 'Checker_Group_refactor', 'Checker_Group_warning']

    feature_importance_raw = pd.Series(gender_guesser.feature_importances_, index=feature_list).to_dict()
    feature_importance = {key: round(feature_importance_raw[key], 2) for key in feature_importance_raw}

    feature_importance["organisation"] = round(
        feature_importance["Str_Total_Lines"] + feature_importance["Str_Code_Lines"] \
        + feature_importance["Str_Empty_Lines"] + feature_importance["Str_Docstring_Lines"] \
        + feature_importance["Str_Comment_Lines"], 2) * 100

    feature_importance["constituents"] = round(feature_importance["Str_Function"] + feature_importance["Str_Method"] \
                                               + feature_importance["Str_Klass"], 2) * 100

    feature_importance["checkers"] = round(
        feature_importance["Checker_Group_convention"] + feature_importance["Checker_Group_error"] + \
        feature_importance["Checker_Group_information"] + feature_importance["Checker_Group_refactor"] + \
        feature_importance["Checker_Group_warning"], 2) * 100

    return {'pylint_score': round(pylint_score, 2),
            'output_gender_guess': output_gender_guess,
            'output_gender_proba': round(max(output_gender_proba), 2),
            'feature_importance': feature_importance}


