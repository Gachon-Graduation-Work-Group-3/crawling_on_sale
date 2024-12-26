import time
import crawling_parrel
import preprocessing
import classify
import utils

if __name__ == "__main__":
    start_time = time.time()

    # 크롤링하고 파일 저장
    df = crawling_parrel.crawl_bobaedream()
    path = "./results/on_sale_cars.csv"
    utils.save_to_csv(df, path)

    # 파일 불러와서 전처리하고 저장
    df_to_prep = utils.load_to_csv(path)
    df_prep = preprocessing.prep(df_to_prep)
    path = "./results/on_sale_cars_prep.csv"
    utils.save_to_csv(df_prep, path)

    # 파일 불러와서 분류하고 저장
    df_to_classify = utils.load_to_csv(path)
    df_classify = classify.classify(df_to_classify)
    path = "./results/on_sale_cars_classify.csv"
    utils.save_to_csv(df_classify, path)

    end_time = time.time()

    print(end_time-start_time)
