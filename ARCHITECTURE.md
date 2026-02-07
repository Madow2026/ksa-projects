# Architecture & AI Implementation Guide

## 🏗️ System Architecture Overview

The Saudi Projects Intelligence Platform is built on a modular, production-ready architecture designed for scalability, maintainability, and extensibility.

## 📊 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER                           │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              Streamlit Web Dashboard                   │   │
│  │  • Interactive UI  • Real-time updates  • Charts       │   │
│  │  • Filters  • Search  • Export  • Admin controls       │   │
│  └────────────────────────────────────────────────────────┘   │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                   APPLICATION LAYER                             │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │           Data Processing Pipeline                       │  │
│  │  Orchestrates: Scraping → AI → Validation → Storage     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────────────┐  │
│  │  Scraper    │  │  AI Engine  │  │  Data Processor      │  │
│  │ Orchestrator│  │             │  │  • Deduplication     │  │
│  │             │  │ • NLP       │  │  • Scoring           │  │
│  │ • News      │  │ • GPT-4     │  │  • Validation        │  │
│  │ • Websites  │  │ • Classify  │  │  • Merge             │  │
│  │ • LinkedIn  │  │ • Extract   │  │                      │  │
│  │ • Maps      │  │ • Similarity│  │                      │  │
│  └─────────────┘  └─────────────┘  └──────────────────────┘  │
└───────────────────────────┬─────────────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────────────┐
│                    DATA LAYER                                   │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Database Manager (SQLAlchemy ORM)           │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                 SQLite Database (MVP)                    │  │
│  │  • projects  • sources  • regions  • logs  • updates     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │  External APIs  │
                    │  • OpenAI GPT   │
                    │  • News APIs    │
                    └─────────────────┘
```

## 🧠 AI Engine Implementation

### 1. **Entity Extraction Pipeline**

```python
Text Input → Preprocessing → AI Model → Structured Output → Validation
```

#### Process Flow:

1. **Text Preprocessing**
   - Clean HTML/special characters
   - Normalize whitespace
   - Handle Arabic/English mixed text

2. **AI Extraction** (GPT-4)
   ```json
   Prompt: "Extract structured project info from this text..."
   
   Response: {
       "project_name": "King Salman Park",
       "status": "Under Construction",
       "region": "Riyadh",
       "category": "Mega Project",
       "owner": "Royal Commission for Riyadh City",
       "contractor": "Saudi Binladin Group",
       "confidence": 0.92
   }
   ```

3. **Fallback** (Rule-based NLP)
   - If GPT-4 unavailable
   - Uses regex + keyword matching
   - Entity recognition with patterns

4. **Validation**
   - Check required fields
   - Validate region/category values
   - Reject if completed/cancelled

### 2. **Classification System**

#### Project Status Classification

```python
def classify_status(text):
    """
    Active keywords: "under construction", "ongoing", "in progress"
    Completed keywords: "completed", "inaugurated", "delivered"
    Cancelled keywords: "suspended", "cancelled", "halted"
    """
    
    if contains(COMPLETED_KEYWORDS):
        return REJECT  # Don't store completed projects
    
    if contains(ACTIVE_KEYWORDS):
        return CLASSIFY_AS_ACTIVE
    
    return "Announced"  # Default for new projects
```

#### Category Classification

Uses keyword matching + AI:

| Category | Keywords | Examples |
|----------|----------|----------|
| Residential | housing, villa, apartment | Residential developments |
| Commercial | retail, mall, office | Shopping centers, offices |
| Infrastructure | road, bridge, metro | Transportation projects |
| Mega Project | mega, neom, giga | Large-scale developments |
| Healthcare | hospital, medical | Medical facilities |
| Energy | power, solar, oil | Energy projects |

### 3. **Semantic Deduplication**

#### Algorithm:

```python
def is_duplicate(project1, project2):
    """
    Uses semantic similarity to detect duplicates
    """
    
    # Step 1: Encode project names using transformer
    embedding1 = model.encode(project1.name)
    embedding2 = model.encode(project2.name)
    
    # Step 2: Calculate cosine similarity
    similarity = cosine_similarity(embedding1, embedding2)
    
    # Step 3: Check additional factors
    same_region = (project1.region == project2.region)
    same_category = (project1.category == project2.category)
    
    # Step 4: Decision
    if similarity > 0.85 and same_region:
        return True  # Duplicate
    
    return False
```

#### Model Used:
- **paraphrase-multilingual-mpnet-base-v2**
- Supports Arabic + English
- 768-dimensional embeddings
- ~50MB model size

### 4. **Confidence Scoring Algorithm**

```python
confidence = (
    source_count_score * 0.30 +      # Multiple sources
    completeness_score * 0.30 +       # Data completeness
    reliability_score * 0.20 +        # Source quality
    recency_score * 0.20              # Update freshness
)
```

#### Factors:

1. **Source Count** (30%)
   - 1 source: 0.20
   - 2 sources: 0.40
   - 3 sources: 0.60
   - 5+ sources: 1.00

2. **Data Completeness** (30%)
   - Required fields filled: 70%
   - Optional fields filled: 30%
   - Formula: `(required/4) * 0.7 + (optional/6) * 0.3`

3. **Source Reliability** (20%)
   - Arab News: 0.90
   - MEED Projects: 0.90
   - Construction Week: 0.85
   - LinkedIn: 0.75
   - Google Maps: 0.70
   - Unknown: 0.50

4. **Recency** (20%)
   - < 7 days: 1.00
   - < 30 days: 0.90
   - < 90 days: 0.80
   - Older: 0.70

### 5. **Update & Merge Logic**

When a duplicate is found:

```python
def merge_projects(existing, new_data):
    """
    Merge strategy: Keep most complete information
    """
    
    for field in UPDATEABLE_FIELDS:
        # Update if existing is empty but new has data
        if not existing[field] and new_data[field]:
            existing[field] = new_data[field]
        
        # Or if new data has higher confidence
        elif new_data.confidence > existing.confidence:
            existing[field] = new_data[field]
    
    # Add new source
    existing.sources.append(new_data.source)
    
    # Recalculate confidence with multiple sources
    existing.confidence = calculate_confidence(
        existing, 
        source_count=len(existing.sources)
    )
    
    # Log update
    log_update(existing.id, changes)
```

## 🔄 Data Flow

### Full Pipeline Execution:

```
1. SCRAPING PHASE
   ├── Initialize scrapers
   ├── Fetch pages from sources
   ├── Parse HTML → Extract articles
   └── Filter: Saudi-related + project keywords
       Result: Raw articles/items

2. EXTRACTION PHASE
   ├── For each item:
   ├── Send to AI engine
   ├── Extract structured data
   ├── Classify status/category
   └── Validate required fields
       Result: Structured project objects

3. VALIDATION PHASE
   ├── Check if project is active (not completed)
   ├── Verify region is valid
   ├── Ensure minimum data quality
   └── Calculate confidence score
       Result: Validated projects

4. DEDUPLICATION PHASE
   ├── Search database for similar names
   ├── Calculate semantic similarity
   ├── If duplicate → Merge & update
   └── If new → Prepare for insert
       Result: Deduplicated projects

5. STORAGE PHASE
   ├── Insert new projects
   ├── Add source URLs
   ├── Log changes
   └── Update statistics
       Result: Database updated

6. REPORTING PHASE
   └── Generate summary statistics
       Result: Pipeline summary
```

## 🗄️ Database Schema Details

### Entity Relationship:

```
┌─────────────┐       ┌──────────────┐
│  Projects   │1────n│   Sources    │
│  (Main)     │       │  (URLs)      │
└─────────────┘       └──────────────┘
      │
      │1
      │
      │n
┌─────────────┐
│ Update Logs │
│  (History)  │
└─────────────┘

┌─────────────┐       ┌──────────────┐
│  Regions    │       │Scraping Logs │
│(Reference)  │       │  (Activity)  │
└─────────────┘       └──────────────┘
```

### Indexes:

- `projects.project_name` (B-tree)
- `projects.region` (B-tree)
- `projects.category` (B-tree)
- `projects.confidence_score` (B-tree)
- `sources.project_id` (Foreign key)

## 🚀 Performance Optimizations

### 1. **Caching Strategy**
- Session-based caching in Streamlit
- Database connection pooling
- Query result caching (5 minutes)

### 2. **Scraping Optimizations**
- Concurrent requests (max 5)
- Request timeout (30s)
- Random delays (1-3s) to be polite
- Retry logic with exponential backoff

### 3. **AI Optimizations**
- Batch processing for embeddings
- Model loaded once (singleton)
- Fallback to rule-based if AI fails
- Token limit: 3000 chars per extraction

### 4. **Database Optimizations**
- Bulk inserts where possible
- Indexed frequent query fields
- Connection pooling
- Query optimization with filters

## 🔐 Security Considerations

### API Keys
- Stored in `.env` (not in git)
- Never logged or exposed
- Validated on startup

### Web Scraping Ethics
- Respect robots.txt
- Rate limiting implemented
- User-agent identification
- Delays between requests

### Data Privacy
- No personal information stored
- Public data only
- GDPR considerations (if applicable)

## 📈 Scalability Path

### Current (MVP):
- SQLite database
- Single-threaded scraping
- Local deployment

### Phase 2:
- PostgreSQL database
- Multi-threaded scraping
- Redis caching
- Docker deployment

### Phase 3:
- Microservices architecture
- Message queue (RabbitMQ/Kafka)
- Distributed scraping
- Kubernetes orchestration

## 🧪 Testing Strategy

### Unit Tests
- AI extraction accuracy
- Deduplication logic
- Confidence scoring
- Data validation

### Integration Tests
- Pipeline end-to-end
- Database operations
- Scraper reliability

### Manual Testing
- UI/UX testing
- Edge cases
- Performance testing

---

**Next Steps**: Review [README.md](README.md) for usage instructions.
