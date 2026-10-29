# SmartTrip AI: Intelligent Tourism Planning & Recommendation System

SmartTrip AI is a production-ready, university capstone-grade tourism planning and recommendation system. It leverages state-of-the-art Natural Language Processing (SentenceTransformers) for semantic destination matching, combines multiple heuristics (budget, rating, popularity) into a unified match score, schedules nearby spots dynamically, recommends lodging, and provides interactive map visualisations and cost analysis.

---

## 🎯 Core Features
1. **Semantic Destination Discovery**: Free-text natural language interest search powered by the `all-MiniLM-L6-v2` transformer.
2. **Personalized Day-wise Itinerary**: Custom timeline generation mapping morning and afternoon attractions with lunch and dinner spots.
3. **Tourist Match Score**: Dynamic ranking metrics based on semantic similarity, ratings, popularity, and budget compliance.
4. **Surrounding Attractions Explorer**: Proximity discovery showing cafes, markets, and transit options within a 5km radius of each stop.
5. **Interactive Mapping**: WebGL-powered 3D mapping using PyDeck showing planned destinations, hotels, and surrounding points.
6. **Lodging Integration**: Hotel matching filtered by city, price limits, and star rating, allowing real-time selection updates.
7. **Financial Dashboard**: Plotly charts visualizing itemized cost allocations and budget utilization gauges.

---

## ⚙️ System Architecture

```
                       +----------------------------------------+
                       |   User Query & Parameters Input         |
                       |   (Interests, Budget, Style, Duration) |
                       +--------------------+-------------------+
                                            |
                                            v
                       +--------------------+-------------------+
                       |      SentenceTransformers Embedder     |
                       |           (all-MiniLM-L6-v2)           |
                       +--------------------+-------------------+
                                            |
                                            v
                       +--------------------+-------------------+
                       |         Cosine Similarity Matcher      |
                       |       (Semantic Interest Alignment)    |
                       +--------------------+-------------------+
                                            |
                                            v
                       +--------------------+-------------------+
                       |       Tourist Match Score Evaluator    |
                       |   (Similarity, Budget, Star, Pop)      |
                       +--------------------+-------------------+
                                            |
                                            v
                       +--------------------+-------------------+
                       |       Itinerary & Lodging Matcher      |
                       |   (Itinerary Builder + Hotel Search)   |
                       +--------------------+-------------------+
                                            |
                                            v
                       +--------------------+-------------------+
                       |           Financial Calculator         |
                       |     (Subtotal, Transit, Buffer)        |
                       +--------------------+-------------------+
                                            |
                                            v
                       +--------------------+-------------------+
                       |         Streamlit Multi-Page App       |
                       |  (Home, Timeline, Hotels, Maps, Plotly)|
                       +----------------------------------------+
```

---

## 📊 Dataset Specifications
All data is programmatically generated during setup using deterministic random seeding for consistency:
1. **Tourism Dataset (`tourism_dataset.csv`)**: 2,025 unique destinations across 45 major cities in India. Columns include `Place`, `City`, `State`, `Category`, `Description`, `Rating`, `Latitude`, `Longitude`, `Best_Time`, `Entrance_Fee`, `Average_Visit_Hours`, `Popularity_Score`, `Tourist_Type`, and `Price_Fare`.
2. **Hotel Dataset (`hotel_dataset.csv`)**: 3,150 lodging records mapped to the cities, with rating categories (Budget, Mid-range, Luxury) matching their amenity configurations.
3. **Nearby Attractions Dataset (`nearby_attractions.csv`)**: 6,075 local spots categorized into Food & Dining, Shopping, Activity, Viewpoint, Local Market, and Transit, mapped within a 5 KM radius of each tourist place.

---

## 🧠 Neural & Math Engine

### 1. Vector Mapping
Descriptions, categories, and titles are concatenated and tokenized by `all-MiniLM-L6-v2` to output a 384-dimensional dense vector representing the semantics:
$$f(\text{Attraction}) = \mathbf{v} \in \mathbb{R}^{384}$$

### 2. Similarity Metric
Given a query vector $\mathbf{q}$ and destination vector $\mathbf{d}_i$, cosine similarity computes their alignment:
$$\text{Similarity}(\mathbf{q}, \mathbf{d}_i) = \frac{\mathbf{q} \cdot \mathbf{d}_i}{\|\mathbf{q}\| \|\mathbf{d}_i\|}$$

### 3. Tourist Match Score Heuristic
The final match score is a weighted combination of relevance, budget compliance, quality, and popularity:
$$\text{Tourist Match Score} = 0.40 \cdot S_{\text{Similarity}} + 0.20 \cdot B_{\text{Budget}} + 0.20 \cdot R_{\text{Rating}} + 0.20 \cdot P_{\text{Popularity}}$$

---

## 🚀 Installation & Local Deployment

### Prerequisites
- Python 3.9 or higher
- Pip

### Setup Steps
1. **Clone the Repository** and navigate to the project directory:
   ```bash
   cd SmartTripAI
   ```

2. **Configure Virtual Environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Core Libraries**:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Initialize Datasets & Model Embeddings**:
   This step generates the CSV files and precomputes the SentenceTransformer embeddings:
   ```bash
   python scripts/generate_data.py
   ```
   *Note: Downloading the model files on the first startup requires an active internet connection (approx. 90MB).*

5. **Verify Data Integrity**:
   ```bash
   python scripts/verify_project.py
   ```

6. **Start Streamlit Server**:
   ```bash
   streamlit run app.py
   ```
   Open `http://localhost:8501` in your browser to interact with the application.

---

## 🛠️ Folder Structure
```
SmartTripAI/
├── .streamlit/
│   └── config.toml           # Streamlit Slate Dark Theme parameters
├── data/                     # CSV datasets and precomputed vector files
│   ├── tourism_dataset.csv
│   ├── hotel_dataset.csv
│   ├── nearby_attractions.csv
│   ├── tourism_embeddings.npy
│   └── tourism_metadata.pkl
├── scripts/
│   ├── generate_data.py      # Programmatic generator script
│   └── verify_project.py     # Automated validation checks
├── utils/
│   └── helper.py             # Custom glassmorphic CSS styling & loaders
├── app.py                    # Landing welcome page & dataset stats
├── pages/
│   ├── 1_Home.py             # User specification inputs & engine
│   ├── 2_Trip_Results.py     # Day timeline itinerary & PyDeck maps
│   ├── 3_Nearby_Attractions.py # Nearby locations explorer map
│   ├── 4_Hotels.py           # Hotel match listing & interactive switcher
│   ├── 5_Budget.py           # Plotly allocation pie chart & gauge
│   └── 6_About_Project.py    # Math formulations & flowcharts
├── requirements.txt          # Package dependencies listing
└── README.md                 # Detailed documentation
```
