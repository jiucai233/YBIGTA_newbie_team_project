import pandas as pd
from fastapi import APIRouter, HTTPException
from database.mongodb_connection import get_reviews, save_preprocessed_reviews
from review_analysis.preprocessing.google_processor import GoogleProcessor
from review_analysis.preprocessing.kakao_processor import KakaoProcessor
from review_analysis.preprocessing.tripdotcom_processor import TripdotcomProcessor

router = APIRouter(prefix="/review")

@router.post("/preprocess/{site_name}")
def preprocess_reviews(site_name: str):
    print(f"✅ 들어온 요청 site_name: {site_name}")

    # 1. MongoDB에서 데이터 가져오기 (List[Dict] 형태)
    reviews = get_reviews(site_name)

    if not reviews:
        raise HTTPException(
            status_code=404, 
            detail=f"No data found for site: {site_name}"
        )

    # 2. 프로세서 맵 (클래스가 인자를 요구하므로 가짜 경로 ""를 넣어줍니다)
    processor_map = {
        "google": GoogleProcessor("", ""),
        "kakao": KakaoProcessor("", ""),
        "tripdotcom": TripdotcomProcessor("", "")
    }

    if site_name not in processor_map:
        raise HTTPException(
            status_code=400, 
            detail=f"Unsupported site: {site_name}"
        )

    processor = processor_map[site_name]
    processor.df = pd.DataFrame(reviews)
    processor.preprocess()
    
    processor.feature_engineering()

    processed_reviews = processor.df.to_dict("records")

    preprocessed_collection_name = save_preprocessed_reviews(
        site_name, processed_reviews
    )

    return {
        "message": "Preprocessing completed",
        "site": site_name,
        "processed_count": len(processed_reviews),
        "saved_to_collection": preprocessed_collection_name
    }