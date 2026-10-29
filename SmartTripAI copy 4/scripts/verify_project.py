import os
import pickle
import numpy as np
import pandas as pd

def run_checks():
    print("==============================================")
    print("         SMARTTRIP AI - VERIFICATION          ")
    print("==============================================")
    
    passed = True
    
    # 1. Check folder and files existence
    files_to_check = {
        "tourism_dataset": "data/tourism_dataset.csv",
        "hotel_dataset": "data/hotel_dataset.csv",
        "nearby_attractions": "data/nearby_attractions.csv",
        "embeddings": "data/tourism_embeddings.npy",
        "metadata": "data/tourism_metadata.pkl"
    }
    
    print("\n🔍 Step 1: Checking files existence...")
    for key, filepath in files_to_check.items():
        if os.path.exists(filepath):
            print(f"  [PASS] Found file: {filepath}")
        else:
            print(f"  [FAIL] Missing file: {filepath}")
            passed = False
            
    if not passed:
        print("\n❌ Verification failed due to missing files.")
        return False
        
    # 2. Check row counts for datasets
    print("\n🔍 Step 2: Validating row counts...")
    
    # Tourism dataset
    tourism_df = pd.read_csv("data/tourism_dataset.csv")
    tourism_rows = len(tourism_df)
    if tourism_rows >= 2000:
        print(f"  [PASS] tourism_dataset.csv has {tourism_rows} rows (minimum 2,000 required).")
    else:
        print(f"  [FAIL] tourism_dataset.csv has only {tourism_rows} rows (minimum 2,000 required).")
        passed = False
        
    # Hotel dataset
    hotel_df = pd.read_csv("data/hotel_dataset.csv")
    hotel_rows = len(hotel_df)
    if hotel_rows >= 3000:
        print(f"  [PASS] hotel_dataset.csv has {hotel_rows} rows (minimum 3,000 required).")
    else:
        print(f"  [FAIL] hotel_dataset.csv has only {hotel_rows} rows (minimum 3,000 required).")
        passed = False
        
    # Nearby attractions dataset
    attractions_df = pd.read_csv("data/nearby_attractions.csv")
    attractions_rows = len(attractions_df)
    if attractions_rows >= 5000:
        print(f"  [PASS] nearby_attractions.csv has {attractions_rows} rows (minimum 5,000 required).")
    else:
        print(f"  [FAIL] nearby_attractions.csv has only {attractions_rows} rows (minimum 5,000 required).")
        passed = False
        
    # 3. Check embedding dimensions & index matching
    print("\n🔍 Step 3: Validating embeddings & metadata...")
    embeddings = np.load("data/tourism_embeddings.npy")
    emb_shape = embeddings.shape
    
    with open("data/tourism_metadata.pkl", "rb") as f:
        meta_df = pickle.load(f)
    meta_rows = len(meta_df)
    
    print(f"  - Embeddings matrix shape: {emb_shape}")
    print(f"  - Metadata rows load: {meta_rows}")
    
    if emb_shape[0] == tourism_rows:
        print("  [PASS] Embedding vectors count matches tourism dataset rows.")
    else:
        print(f"  [FAIL] Embedding count ({emb_shape[0]}) does not match dataset rows ({tourism_rows}).")
        passed = False
        
    if emb_shape[1] == 384:
        print("  [PASS] Embedding dimensionality matches SentenceTransformer all-MiniLM-L6-v2 (384 dimensions).")
    else:
        print(f"  [FAIL] Expected 384 dimensions, found {emb_shape[1]}.")
        passed = False
        
    if meta_rows == tourism_rows:
        print("  [PASS] Metadata pickle rows match tourism dataset rows.")
    else:
        print(f"  [FAIL] Metadata pickle rows ({meta_rows}) does not match tourism dataset rows ({tourism_rows}).")
        passed = False
        
    # 4. Check data columns schema
    print("\n🔍 Step 4: Validating dataset schemas...")
    
    expected_tourism_cols = {
        "Place", "City", "State", "Category", "Description", "Rating", 
        "Latitude", "Longitude", "Best_Time", "Entrance_Fee", 
        "Average_Visit_Hours", "Popularity_Score", "Tourist_Type", "Price_Fare", "Image_URL"
    }
    actual_tourism_cols = set(tourism_df.columns)
    missing_tourism_cols = expected_tourism_cols - actual_tourism_cols
    if not missing_tourism_cols:
        print("  [PASS] Tourism dataset schema is correct.")
    else:
        print(f"  [FAIL] Tourism dataset is missing columns: {missing_tourism_cols}")
        passed = False
        
    expected_hotel_cols = {
        "Hotel_Name", "City", "Hotel_Rating", "Hotel_Price", 
        "Description", "Amenities", "Distance_From_Attraction", "Review_Count"
    }
    actual_hotel_cols = set(hotel_df.columns)
    missing_hotel_cols = expected_hotel_cols - actual_hotel_cols
    if not missing_hotel_cols:
        print("  [PASS] Hotel dataset schema is correct.")
    else:
        print(f"  [FAIL] Hotel dataset is missing columns: {missing_hotel_cols}")
        passed = False
        
    expected_attraction_cols = {
        "Attraction_Name", "Nearby_Place", "Distance_KM", "Category", "Rating"
    }
    actual_attraction_cols = set(attractions_df.columns)
    missing_attraction_cols = expected_attraction_cols - actual_attraction_cols
    if not missing_attraction_cols:
        print("  [PASS] Nearby attractions dataset schema is correct.")
    else:
        print(f"  [FAIL] Nearby attractions dataset is missing columns: {missing_attraction_cols}")
        passed = False
        
    # 5. Check image URLs formatting
    print("\n🔍 Step 5: Validating image URLs schema...")
    empty_urls = tourism_df["Image_URL"].isna().sum()
    if empty_urls == 0:
        print("  [PASS] All rows contain non-empty Image URLs.")
    else:
        print(f"  [FAIL] Found {empty_urls} rows with empty Image URLs.")
        passed = False
        
    invalid_urls = (~tourism_df["Image_URL"].str.startswith("http")).sum()
    if invalid_urls == 0:
        print("  [PASS] All Image URLs are formatted correctly (starting with http/https).")
    else:
        print(f"  [FAIL] Found {invalid_urls} rows with malformed Image URLs.")
        passed = False
        
    # Print summary
    print("\n==============================================")
    if passed:
        print(" 🎉 VERIFICATION SUCCESSFUL: ALL CHECKS PASSED!")
        print(" SmartTrip AI project is fully configured and ready.")
        print("==============================================")
        return True
    else:
        print(" ❌ VERIFICATION FAILED: PLEASE CORRECT ERRORS LISTED ABOVE.")
        print("==============================================")
        return False

if __name__ == "__main__":
    run_checks()
