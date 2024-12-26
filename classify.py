import json


def map_car_hierarchy(row, path):

    with open(path) as f:
        data = json.load(f)

    car_name = row['name']
    # print(car_name)

    manufacturer_name = "unknown"
    model_name = "unknown"
    submodel_name = "unknown"
    grade_name = "unknown"

    for brand, models in data.items():
        # print(brand)
        if brand in car_name:
            manufacturer_name = brand
        else:
            continue
        
        sorted_models = sorted(models.keys(), key=len, reverse=True)
        for model in sorted_models:
            if model in car_name:
                model_name = model
            else:
                continue

            sorted_submodels = sorted(models[model].keys(), key=len, reverse=True)
            for submodel in sorted_submodels:
                if submodel in car_name:
                    submodel_name = submodel
                else:
                    continue

                sorted_grades = sorted(models[model][submodel], key=len, reverse=True)
                for grade in sorted_grades:
                    if grade in car_name:
                        grade_name = grade
                        return [manufacturer_name, model_name, submodel_name, grade_name]

    return [manufacturer_name, model_name, submodel_name, grade_name]


def classify(df):
    path = "car_hierarchy.json"
    df_copy = df.copy()
    
    df_copy[["manufacturer", "model", "submodel", "grade"]] = df_copy.apply(lambda row: map_car_hierarchy(row, path=path), axis=1, result_type="expand")
    return df_copy
