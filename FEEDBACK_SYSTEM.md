# Feedback Mechanism - Continuous Improvement System

## Overview
The feedback mechanism allows users to provide feedback on chatbot responses through thumbs up/down buttons. This data is stored for continuous improvement of the RAG system.

---

## Architecture

### 1. Database Layer
**Table: `feedback`**
```sql
- id: Primary key
- session_id: Link to chat session
- message_id: Link to specific message
- question: User's original question
- response: Bot's response
- retrieved_chunks: JSON - The chunks used to generate response
- sources: JSON - Source documents referenced
- rating: Integer (1 = thumbs up, -1 = thumbs down)
- comment: Optional user comment
- is_reviewed: Boolean - Has admin reviewed this?
- is_used_for_training: Boolean - Used for fine-tuning?
- created_at: Timestamp
- reviewed_at: Timestamp when reviewed
```

### 2. Backend API
**Endpoints:**

```python
POST /feedback/
# Submit user feedback
{
  "session_id": "uuid",
  "message_id": 123,
  "question": "What is the dress code?",
  "response": "The dress code...",
  "rating": 1,  # 1 or -1
  "comment": "Very helpful!",
  "retrieved_chunks": [...],
  "sources": ["document.pdf"]
}

GET /feedback/negative?skip=0&limit=100
# Get all thumbs down feedback for review

GET /feedback/unreviewed?skip=0&limit=100
# Get unreviewed feedback

PATCH /feedback/{id}/review
# Mark feedback as reviewed

GET /feedback/stats
# Get feedback statistics
{
  "total_feedback": 150,
  "positive": 120,
  "negative": 30,
  "unreviewed": 10,
  "satisfaction_rate": 80.0
}
```

### 3. Frontend UI
- **Thumbs up/down buttons** appear below each assistant message
- **Visual feedback** when clicked (green/red highlight)
- **"Thank you"** message after submission
- **Disabled** after feedback given (one vote per message)

---

## Usage Flow

```
User asks question
    ↓
Bot responds with answer + metadata
    ↓
User clicks 👍 or 👎
    ↓
Feedback stored in database with:
  - Original question
  - Bot's response
  - Retrieved chunks
  - Source documents
    ↓
Admin reviews negative feedback
    ↓
Improvements made to:
  - Document chunking
  - Prompt engineering
  - Query expansion
  - Golden dataset (Q&A pairs)
```

---

## Continuous Improvement Workflow

### Level 1: Immediate Insights (No Action Required)
**What to monitor:**
- Satisfaction rate (should be > 70%)
- Common negative feedback topics
- Questions that consistently get thumbs down

**Access:**
```bash
GET /feedback/stats
# Check overall satisfaction

GET /feedback/negative
# Review problem areas
```

### Level 2: Prompt Tuning (Weekly)
**When:** Satisfaction rate < 70% or patterns in negative feedback

**Actions:**
1. Review negative feedback
2. Identify common issues:
   - Too verbose?
   - Missing information?
   - Wrong document retrieved?
3. Update system prompt in `chat_service.py`

**Example fix:**
```python
# If users say "too wordy"
prompt = f"""Answer concisely in 2-3 sentences...

# If users say "not specific enough"
prompt = f"""Use exact quotes from documents...

# If users say "misunderstands questions"
prompt = f"""First, understand what the user is really asking...
```

### Level 3: Query Expansion (Monthly)
**When:** Same question gets different results

**Actions:**
1. Find questions with negative feedback
2. Check retrieved chunks - were they relevant?
3. Add query variations in `generate_response()`:

```python
if "duty hours" in question.lower():
    query_variations.extend([
        "working hours",
        "shift timings",
        "roster schedule",
        "duty shift"
    ])
```

### Level 4: Golden Dataset (Quarterly)
**When:** > 50 pieces of feedback collected

**Actions:**
1. Export negative feedback:
   ```sql
   SELECT question, response, retrieved_chunks 
   FROM feedback 
   WHERE rating = -1 AND is_reviewed = TRUE
   ```

2. Create golden Q&A pairs:
   ```json
   {
     "question": "What is the dress code?",
     "correct_chunks": [22, 77],
     "correct_answer": "The dress code shall be specified by..."
   }
   ```

3. Use for:
   - Testing retrieval quality
   - Fine-tuning embedding layer
   - Evaluating new models

### Level 5: Fine-Tuning (Annually)
**When:** > 500 feedback entries collected

**Actions:**
1. Prepare training data from feedback
2. Fine-tune:
   - **Embedding model** (for better retrieval)
   - **LLM** (for better responses)
3. A/B test new model vs old model
4. Deploy if satisfaction rate improves by > 5%

---

## Admin UI Features (Future)

### Feedback Dashboard
```
📊 Feedback Statistics
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Feedback: 150
Thumbs Up: 120 (80%)
Thumbs Down: 30 (20%)
Unreviewed: 10

📉 Problem Areas:
1. Dress code questions (15 👎)
2. Leave policy (8 👎)
3. Transfer procedures (7 👎)

🔍 Recent Negative Feedback:
[List of thumbs down with review button]
```

### Review Interface
```
Question: "What is the dress code?"
Response: "I don't have information..."
Retrieved Chunks: [Show first 100 chars of each]
Sources: 22584_HRD-36-2025.pdf

[X] Wrong chunks retrieved
[X] Good chunks but bad answer
[ ] Information not in documents

Action Taken:
[ ] Updated query expansion
[ ] Fixed prompt
[ ] Added to golden dataset

[Mark as Reviewed]
```

---

## Metrics to Track

### 1. Satisfaction Rate
```python
satisfaction_rate = (thumbs_up / total_feedback) * 100
# Target: > 70%
```

### 2. Review Velocity
```python
review_velocity = unreviewed_feedback_count / days_since_last_review
# Target: < 10 unreviewed per week
```

### 3. Improvement Impact
```python
before_improvement = satisfaction_rate(last_month)
after_improvement = satisfaction_rate(this_month)
impact = after_improvement - before_improvement
# Target: > 5% improvement per iteration
```

---

## API Examples

### Submit Positive Feedback
```bash
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "abc-123",
    "message_id": 456,
    "question": "What is the dress code?",
    "response": "The dress code shall be specified by...",
    "rating": 1,
    "sources": ["22584_HRD-36-2025.pdf"]
  }'
```

### Get Negative Feedback for Review
```bash
curl http://localhost:8000/feedback/negative?limit=10
```

### Get Statistics
```bash
curl http://localhost:8000/feedback/stats
```

---

## Database Migration

Run this to create the feedback table:

```sql
CREATE TABLE feedback (
    id SERIAL PRIMARY KEY,
    session_id VARCHAR NOT NULL,
    message_id INTEGER NOT NULL,
    question TEXT NOT NULL,
    response TEXT NOT NULL,
    retrieved_chunks JSON,
    sources JSON,
    rating INTEGER NOT NULL,
    comment TEXT,
    is_reviewed BOOLEAN DEFAULT FALSE,
    is_used_for_training BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

CREATE INDEX idx_feedback_session ON feedback(session_id);
CREATE INDEX idx_feedback_rating ON feedback(rating);
CREATE INDEX idx_feedback_reviewed ON feedback(is_reviewed);
```

Or let SQLAlchemy create it automatically:
```python
# Already done in main.py:
Base.metadata.create_all(bind=engine)
```

---

## Benefits

### For Users
- ✅ Simple one-click feedback
- ✅ Immediate visual confirmation
- ✅ Non-intrusive (optional)

### For Developers
- ✅ Real usage data
- ✅ Identify problem areas quickly
- ✅ Measure improvement over time
- ✅ Build training datasets

### For the System
- ✅ Continuous learning
- ✅ Better retrieval over time
- ✅ Domain-specific optimization
- ✅ Quality assurance

---

## Next Steps

1. ✅ **Implemented**: Basic feedback collection
2. 🔄 **In Progress**: Admin dashboard for review
3. 📅 **Planned**: Golden dataset builder
4. 📅 **Planned**: A/B testing framework
5. 📅 **Planned**: Automated retraining pipeline

---

## Testing

```bash
# Start backend
cd backend
uvicorn app.main:app --reload

# Test feedback submission
curl -X POST http://localhost:8000/feedback/ \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "test-123",
    "message_id": 1,
    "question": "Test question",
    "response": "Test response",
    "rating": 1
  }'

# Check stats
curl http://localhost:8000/feedback/stats
```

---

## Summary

The feedback mechanism creates a **virtuous cycle**:

```
User Feedback → Data Collection → Analysis → Improvements → Better Responses → Happy Users → More Feedback
```

This transforms the chatbot from a static system into a **continuously improving** AI assistant that gets smarter with every interaction! 🚀
