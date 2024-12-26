import pandas as pd
import numpy as np
import ast

# pd.set_option("display.max_columns", None)
# pd.set_option("display.max_colwidth", 90)


# 중복값 제외
def duplicates_prep(df):
    df_copy = df.copy()
    df_copy = df_copy.drop_duplicates()
    return df_copy


# 최초등록일 전처리
def first_reg_prep(df):
    df_copy = df.copy()
    df_copy["first_reg"] = df_copy["first_reg"].astype(str)
    df_copy["first_reg"] = (
        df_copy["first_reg"]
        .str.strip("최초등록")
        .str.strip("[")
        .str.strip("]")
        .str.strip("'")
        .str.replace(".", "/")
    )
    df_copy["first_reg"] = df_copy["first_reg"].str.replace("/", "-").str.strip()

    # "24-01-01" 형식을 "2024-01-01"로 바꾸기
    df_copy["first_reg"] = df_copy["first_reg"].apply(lambda x: "20" + x)

    # datetime으로 변환
    # df_copy['first_reg'] = pd.to_datetime(df_copy['first_reg'], format="%Y-%m-%d")

    return df_copy


# 연식 전처리
def age_prep(df):
    df_copy = df.copy()
    df_copy["age"] = (
        df_copy["age"]
        .str.extract(r"(\d{4}.\d{2})")[0]
        .str.replace("/", ".")
        .str.strip()
        .str.replace(".", "-")
    )

    # datetime으로 변환
    # df_copy['first_reg'] = pd.to_datetime(df_copy['first_reg'], format="%Y-%m-%d")

    return df_copy


# 배기량 전처리
def cc_prep(df):
    df_copy = df.copy()
    df_copy["cc"] = (
        df_copy["cc"]
        .str.replace(r"\s*\(.*\)", "", regex=True)
        .str.replace(" ", "")
        .str.strip()
    )
    df_copy["cc"] = (
        df_copy["cc"].str.replace("cc", "").str.replace(",", "").replace("", "0").astype(float)
    )
    df_copy["cc"] = df_copy["cc"].fillna(0)
    return df_copy


# 보증정보 전처리
def guarn_prep(df):
    df_copy = df.copy()
    df_copy["guarn"] = df_copy["guarn"].replace(
        ["정보없음", "불가", "만료", "가능"], None
    )
    df_copy["guarn"] = df_copy["guarn"].replace({np.nan: None}).str.replace(" ", "")
    df_copy["guarn"] = df_copy["guarn"].str.replace(",", "")
    return df_copy


# 이름 전처리
def name_prep(df):
    df_copy = df.copy()

    # 이름이 결측값인 애들 제거    
    df_copy = df_copy[~df_copy['name'].apply(lambda x: isinstance(x, float))]
    df_copy = df_copy[~df_copy['name'].isnull()]

    df_copy["name"] = df_copy["name"].str.replace("^\\d*\\s?", "", regex=True)
    df_copy["name"] = df_copy["name"].replace({np.nan: None})
    df_copy["name"] = df_copy["name"].astype(str)

    return df_copy


# 엔진형식 전처리
def engine_prep(df):
    df_copy = df.copy()
    df_copy["engine"] = df_copy["engine"].str.replace(" ", "")
    return df_copy


# 신차대비가격 전처리
def new_percent_prep(df):
    df_copy = df.copy()
    df_copy.loc[df_copy["new_percent"] == "809498.0", "new_percent"] = None
    df_copy.loc[
        df_copy["new_percent"].isin(["소유", "반납", "운용", "렌터카"]), "new_percent"
    ] = 0
    df_copy["new_percent"] = df_copy["new_percent"].fillna(0).astype(float)
    return df_copy


# 가격 전처리 float으로 형변환(만원단위임)
def price_prep(df):
    df_copy = df.copy()
    df_copy["price"] = (
        df_copy["price"]
        .str.replace("만원", "")
        .str.replace(",", "")
        .str.extract("(\\d+)")[0]
        .astype(float)
    )
    df_copy["price"] = df_copy["price"].fillna(0)
    return df_copy


# 주행거리 전처리
def mileage_prep(df):
    df_copy = df.copy()
    df_copy["mileage"] = (
        df_copy["mileage"]
        .str.replace("km", "")
        .str.replace(",", "")
        .str.replace("mi", "")
        .str.strip()
        .astype(float)
    )
    df_copy["mileage"] = df_copy["mileage"].fillna(0)
    return df_copy


# 신차가격 전처리
def new_price_prep(df):
    df_copy = df.copy()
    df_copy["new_price"] = (
        df_copy["new_price"]
        .str.replace("만원", "")
        .str.replace(",", "")
        .str.extract(r"(\d+)")[0]
    )
    df_copy["new_price"] = df_copy["new_price"].astype(float)
    df_copy["new_price"] = df_copy["new_price"].fillna(0)
    return df_copy


# 조회수 전처리 float으로 형변환
def view_prep(df):
    df_copy = df.copy()
    df_copy["view"] = (
        df_copy["view"]
        .str.replace("조회", "")
        .str.strip()
        .str.replace(",", "")
        .astype(float)
    )
    df_copy["view"] = df_copy["view"].fillna(0)
    return df_copy


# 브랜드 컬럼 추가
def create_brand(row):
    """df_copy['brand'] = df_copy.apply(create_brand, axis=1)"""
    # 개별 행(row)에 대해 브랜드 이름 설정
    if "현대" in row["name"]:
        return "현대"
    elif "제네시스" in row["name"]:
        return "제네시스"
    elif "기아" in row["name"]:
        return "기아"
    elif "쉐보레" in row["name"] or "대우" in row["name"]:
        return "쉐보레/대우"
    else:
        return "기타"


# 이미지 전처리
def image_prep(df):
    df_copy = df.copy()
    # 리스트 타입으로
    # df_copy["image"] = df_copy["image"].apply(
    #     lambda x: (
    #         ast.literal_eval(x) if isinstance(x, str) and x.startswith("[") else None
    #     )
    # )
    # 사고침수유무에 이미지 url이 저장되는 경우가 있어 전처리
    df_copy.loc[
        df_copy["flood_status"].apply(
            lambda x: isinstance(x, str) and x.startswith("[")
        ),
        "image",
    ] = df_copy["flood_status"]
    df_copy.loc[
        df_copy["flood_status"].apply(
            lambda x: isinstance(x, str) and x.startswith("[")
        ),
        "flood_status",
    ] = np.nan
    return df_copy


# 연비 전처리
def fuel_efficient_prep(df):
    df_copy = df.copy()
    df_copy["fuel_efficient"] = (
        df_copy["fuel_efficient"].str.replace("km/ℓ", "").str.replace(" ", "").replace("", "0").astype(float).fillna(0)
    )
    return df_copy


# 최고출력 전처리
def max_out_prep(df):
    df_copy = df.copy()
    df_copy["max_out"] = (
        df_copy["max_out"].str.replace("마력", "").str.replace(" ", "").replace("", "0").astype(float).fillna(0)
    )
    return df_copy


# 최대토크 전처리
def torque_prep(df):
    df_copy = df.copy()
    df_copy["torque"] = (
        df_copy["torque"].str.replace("kg.m", "").str.replace(" ", "").replace("", "0").astype(float).fillna(0)
    )
    return df_copy


# 중량 전처리
def weight_prep(df):
    df_copy = df.copy()
    df_copy["weight"] = (
        df_copy["weight"]
        .str.replace("kg", "")
        .str.replace(",", "")
        .str.replace(" ", "")
        .replace("", "0")
        .astype(float)
        .fillna(0)
    )
    return df_copy


# 유, 무 옵션들 전처리
def bool_options_prep(df):
    df_copy = df.copy()
    option_cols = [
        "sunroof",
        "pano_sunroof",
        "heat_front",
        "heat_back",
        "pass_air",
        "rear_warn",
        "rear_sensor",
        "front_sensor",
        "rear_camera",
        "front_camera",
        "around_view",
        "heat_handle",
        "auto_light",
        "cruise_cont",
        "auto_park",
        "flood_status",
        "illegal_modification",
    ]
    df_copy[option_cols] = df_copy[option_cols].fillna("무")
    return df_copy


# 2, 3 등 여러개를 가지는 옵션들 전처리
def int_options_prep(df):
    df_copy = df.copy()
    option_cols = [
        "navi_gen",
        "navi_non",
        "insur_count",
        "owner_change",
        "total_loss",
        "flood_total_loss",
        "flood_part_loss",
        "my_damage_count",
        "other_damage_count",
        "panel",
        "replace",
        "corrosion",
    ]

    for col in option_cols:
        df_copy[col] = (
            df_copy[col]
            .replace(np.nan, "무")
            .str.replace("무", "0")
            .str.replace("회", "")
            .str.replace(" ", "")
            .replace("", "0")
            .str.replace("유", "1")
            .str.strip()
            .astype(float)
            .fillna(0)
            .astype(int)
        )
    return df_copy


# theft 전처리
def theft_prep(df):
    df_copy = df.copy()
    df_copy["theft"] = 0
    return df_copy


# 내차피해금액, 타차피해금액 전처리
def damage_amount_prep(df):
    df_copy = df.copy()
    df_copy["my_damage_amount"] = (
        df_copy["my_damage_amount"]
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace("원", "")
        .str.replace(",", "")
        .str.replace(" ", "")
        .replace("", "0")
        .astype(float)
        .fillna(0)
    )
    df_copy["other_damage_amount"] = (
        df_copy["other_damage_amount"]
        .str.replace("(", "")
        .str.replace(")", "")
        .str.replace("원", "")
        .str.replace(",", "")
        .str.replace(" ", "")
        .replace("", "0")
        .astype(float)
        .fillna(0)
    )
    return df_copy


def prep(df):
    # df_test = duplicates_prep(df)
    df_prep = first_reg_prep(df)
    df_prep = age_prep(df_prep)
    df_prep = cc_prep(df_prep)
    df_prep = guarn_prep(df_prep)
    df_prep = name_prep(df_prep)
    df_prep = engine_prep(df_prep)
    df_prep = new_percent_prep(df_prep)
    df_prep = price_prep(df_prep)
    df_prep = mileage_prep(df_prep)
    df_prep = new_price_prep(df_prep)
    df_prep = view_prep(df_prep)
    df_prep = image_prep(df_prep)

    df_prep["brand"] = df_prep.apply(create_brand, axis=1)
    df_prep = fuel_efficient_prep(df_prep)
    df_prep = max_out_prep(df_prep)
    df_prep = torque_prep(df_prep)
    df_prep = weight_prep(df_prep)
    df_prep = bool_options_prep(df_prep)
    df_prep = int_options_prep(df_prep)
    df_prep = theft_prep(df_prep)
    df_prep = damage_amount_prep(df_prep)
    print("Preprocessing Complete!")

    return df_prep
