import os
import json
import time
import random
from pathlib import Path
from groq import Groq

try:
    from memory_store import get_memory_summary, add_topic
    MEMORY_ENABLED = True
except Exception as e:
    print(f"[Memory] Unavailable: {e}")
    MEMORY_ENABLED = False
    def get_memory_summary(): return ""
    def add_topic(t, s): pass

DATASET_PATH = Path("datasets/training_data.jsonl")
DAILY_TARGET = 200

groq_keys = []
for key_name in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
    key = os.environ.get(key_name)
    if key:
        groq_keys.append(key)

print(f"[AAES] Loaded {len(groq_keys)} Groq keys (rotating)")

LEVELS = {
    1:  "basic Python functions, variables, loops, and conditionals",
    2:  "Python classes, objects, inheritance, and encapsulation",
    3:  "error handling, file operations, and input validation",
    4:  "REST APIs with FastAPI, routing, and request handling",
    5:  "database operations with SQLAlchemy and data modeling",
    6:  "async programming, concurrency, and background tasks",
    7:  "testing with pytest, mocking, and test coverage",
    8:  "design patterns: factory, singleton, observer, decorator",
    9:  "data structures and algorithms: trees, graphs, dynamic programming",
    10: "system design: caching, queuing, load balancing concepts",
    11: "complete backend systems with authentication and authorization",
    12: "microservices architecture and inter-service communication",
    13: "message queues with RabbitMQ and Kafka patterns",
    14: "API security: OAuth2, JWT, rate limiting, input sanitization",
    15: "performance optimization: profiling, caching, database indexing",
    16: "Docker containerization and Docker Compose orchestration",
    17: "CI/CD pipelines with GitHub Actions and automated testing",
    18: "machine learning pipelines with scikit-learn and data preprocessing",
    19: "cloud infrastructure: AWS/GCP services, serverless functions",
    20: "full production systems: monitoring, logging, scaling, disaster recovery",
}

TOPIC_POOL = {
    1:  ["temperature unit converter","simple calculator","FizzBuzz with custom rules","number guessing game","list sorting without built-ins","string manipulation utilities","basic banking account","simple todo list","prime number checker","fibonacci sequence","password strength checker","word counter","simple ATM machine","grade calculator","Roman numeral converter","palindrome checker","anagram detector","leap year checker","currency converter","BMI calculator"],
    2:  ["inventory management system","library book tracker","employee payroll system","vehicle rental system","university course enrollment","bank account with inheritance","shape hierarchy with area calculation","animal shelter management","hotel room booking","e-commerce product catalog","social media user profiles","chess piece movement","restaurant order system","hospital patient records","flight booking system","parking lot system","vending machine","subscription service manager","school timetable builder","sports team roster manager"],
    3:  ["CSV file parser with validation","JSON config file loader","log file analyzer","file backup utility","data migration script","input sanitizer for web forms","retry mechanism for API calls","custom exception hierarchy","file encryption utility","directory tree walker","database connection handler","email validator","XML parser with error recovery","bulk file renamer","disk usage analyzer","config file hot reloader","zip archive manager","file deduplicator","log rotation utility","file checksum verifier"],
    4:  ["URL shortener API","weather data API","user authentication endpoints","product search API with filters","rate limiting middleware","file upload endpoint","webhook handler","pagination system","API versioning","health check endpoint","CORS configuration","request validation with Pydantic","background task queue","API key management","GraphQL-style query endpoint","geolocation API","currency exchange API","notification API","image resize API","PDF generation API"],
    5:  ["user activity tracking","multi-tenant database schema","soft delete pattern","database migrations with Alembic","full-text search implementation","many-to-many relationships","database connection pooling","audit trail system","data archiving strategy","query optimization patterns","database seeding script","repository pattern implementation","caching layer with Redis","bulk insert optimization","database health monitoring","time-series data storage","geospatial queries","database sharding strategy","event store implementation","data versioning system"],
    6:  ["async web scraper","concurrent API fetcher","async message queue consumer","WebSocket chat server","async file processor","parallel data pipeline","async rate limiter","background job scheduler","async database queries","event-driven notification system","async cache warmer","concurrent image processor","async email sender","real-time data streaming","async retry with backoff","async task orchestrator","concurrent file downloader","async health checker","real-time leaderboard","async batch processor"],
    7:  ["unit tests for payment processing","mock external API calls","test fixtures for database","parametrized test cases","integration tests for REST API","test coverage reporting","property-based testing","snapshot testing","performance benchmarking tests","test doubles and stubs","BDD with pytest-bdd","mutation testing","end-to-end API testing","load testing with locust","contract testing","fuzz testing","regression test suite","test data factory","API mocking server","database test isolation"],
    8:  ["factory pattern for payment gateways","observer pattern for event system","decorator pattern for logging","singleton database connection","strategy pattern for sorting algorithms","command pattern for undo/redo","repository pattern with unit of work","adapter pattern for third-party APIs","chain of responsibility for request handling","template method for report generation","proxy pattern for caching","facade pattern for complex subsystems","state machine implementation","iterator pattern for data processing","composite pattern for file system"],
    9:  ["binary search tree implementation","graph shortest path algorithm","dynamic programming knapsack","LRU cache implementation","trie for autocomplete","heap-based priority queue","merge sort implementation","hash table from scratch","balanced BST AVL tree","Dijkstra's algorithm","topological sort","sliding window algorithm","two-pointer technique problems","segment tree implementation","union-find data structure"],
    10: ["distributed cache design","message broker architecture","load balancer algorithm","consistent hashing implementation","rate limiter design patterns","circuit breaker pattern","saga pattern for distributed transactions","event sourcing architecture","CQRS implementation","service mesh concepts","API gateway design","distributed lock manager","leader election algorithm","gossip protocol simulation","distributed tracing system"],
    11: ["JWT authentication system","OAuth2 with Google login","role-based access control","API gateway with rate limiting","two-factor authentication","password reset flow","refresh token rotation","session management system","API security headers","encrypted data storage","audit logging system","IP whitelisting middleware","brute force protection","CORS policy manager","secure file upload system"],
    12: ["user service with gRPC","order service with REST","payment service integration","service discovery with Consul","inter-service authentication","distributed configuration management","service health aggregator","API composition pattern","backend for frontend pattern","strangler fig migration pattern","bulkhead pattern implementation","sidecar pattern for logging","ambassador pattern for proxying","microservice chassis framework","distributed tracing with OpenTelemetry"],
    13: ["RabbitMQ producer and consumer","Kafka event streaming pipeline","dead letter queue handler","message retry with backoff","competing consumers pattern","publish-subscribe system","message deduplication","ordered message processing","fan-out message pattern","priority queue with RabbitMQ","event-driven order processing","async notification pipeline","message schema validation","message broker failover","transactional outbox pattern"],
    14: ["SQL injection prevention","XSS protection middleware","CSRF token implementation","API input sanitization","secure password hashing","certificate pinning","dependency vulnerability scanner","security headers middleware","secrets rotation system","API abuse detection","honeypot implementation","secure session cookies","content security policy","OAuth2 PKCE flow","zero-trust API authentication"],
    15: ["database query profiler","Redis caching layer","N+1 query detector","connection pool optimizer","async task queue with priorities","CDN cache invalidation","database index optimizer","memory leak detector","CPU profiling with cProfile","lazy loading implementation","response compression middleware","database query cache","batch processing optimizer","memory-efficient data streaming","application performance monitor"],
    16: ["multi-stage Docker build","Docker Compose for microservices","Docker network configuration","container health checks","Docker volume management","Docker secrets management","container resource limits","Docker image optimization","multi-container application stack","Docker registry setup","container logging configuration","Docker Swarm deployment","Docker build cache optimization","container security scanning","development vs production Docker config"],
    17: ["GitHub Actions test pipeline","automated deployment workflow","Docker build and push action","automated code quality checks","semantic versioning automation","dependency update automation","automated security scanning","multi-environment deployment","rollback automation","automated changelog generation","integration test pipeline","performance regression testing","automated API documentation","infrastructure as code pipeline","blue-green deployment automation"],
    18: ["data preprocessing pipeline","feature engineering system","model training pipeline","cross-validation framework","hyperparameter tuning system","model evaluation metrics","data augmentation pipeline","feature selection system","model serialization and loading","prediction API with FastAPI","A/B testing framework for models","data drift detection","model versioning system","automated retraining pipeline","ML experiment tracking"],
    19: ["AWS Lambda function with API Gateway","S3 file storage integration","DynamoDB data modeling","SQS message queue consumer","CloudWatch logging setup","serverless image processing","AWS Cognito authentication","GCP Cloud Functions deployment","Firebase real-time database","cloud storage file manager","serverless scheduled jobs","cloud CDN configuration","multi-region deployment","cloud cost optimization","infrastructure as code with Terraform"],
    20: ["Prometheus metrics collection","Grafana dashboard setup","ELK stack log aggregation","distributed tracing with Jaeger","chaos engineering with Chaos Monkey","auto-scaling configuration","disaster recovery system","zero-downtime deployment","SLA monitoring system","incident response automation","capacity planning system","performance baseline monitoring","multi-region failover","database backup automation","production readiness checklist"],
}

def get_client(key_index):
    return Groq(api_key=groq_keys[key_index % len(groq_keys)])

def ask_ai(prompt, key_index, max_tokens=1024):
    """Call Teacher AI. Returns None if rate limited — caller must handle."""
    for attempt in range(2):
        try:
            client = get_client(key_index)
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            time.sleep(6)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"[Key {key_index+1}] Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                print(f"[Key {key_index+1}] Error: {e}")
                return None
    return None  # rate limited after retries — do NOT fallback, just return None

def ask_student(prompt, key_index):
    """Call Student AI with quality-encouraging wrapper."""
    wrapped = f"""You are a Python developer completing a coding task.
Write clean, working Python code for the following task.
Include docstrings, type hints, and handle edge cases where appropriate.
Show your implementation with brief inline comments.

TASK:
{prompt}"""
    for attempt in range(2):
        try:
            client = get_client(key_index)
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": wrapped}],
                temperature=0.7,
                max_tokens=1500
            )
            time.sleep(6)
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"[Student Key {key_index+1}] Rate limited, waiting 30s...")
                time.sleep(30)
            else:
                return None
    return None

def get_total():
    if not DATASET_PATH.exists():
        return 0
    with open(DATASET_PATH) as f:
        return sum(1 for line in f if line.strip())

def get_stats():
    if not DATASET_PATH.exists():
        DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
        return 0, 0, 1
    records = []
    with open(DATASET_PATH) as f:
        for line in f:
            try:
                records.append(json.loads(line))
            except:
                pass
    if not records:
        return 0, 0, 1
    total = len(records)
    recent = records[-20:]
    avg_score = sum(r.get("evaluation_score", 0) for r in recent) / len(recent)
    current_level = min(15, max(1, (total // 100) + 1))
    return total, avg_score, current_level

def pick_topic(level, memory_summary):
    pool = TOPIC_POOL.get(level, [])
    available = [t for t in pool if t.lower() not in memory_summary.lower()]
    if not available:
        available = pool  # all used, reset
    return random.choice(available)

def store_record(prompt, output, correction, score, level, topic):
    record = {
        "prompt": prompt,
        "student_output": output,
        "teacher_correction": correction,
        "evaluation_score": score,
        "level": level,
        "topic": topic
    }
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def run_one(run_id, key_index):
    total, avg_score, level = get_stats()
    level_desc = LEVELS[level]
    memory_summary = get_memory_summary() if MEMORY_ENABLED else ""
    difficulty = "straightforward" if avg_score < 0.5 else "moderately challenging" if avg_score < 0.8 else "advanced"

    # Step 1: Pick topic from pool (no AI needed)
    topic = pick_topic(level, memory_summary)

    # Step 2: Generate task
    task_prompt = f"""You are a senior software engineer creating a coding challenge.
Topic: {topic}
Difficulty: {difficulty} (Level {level}/20)
Focus: {level_desc}

Write a detailed, realistic coding task that:
1. Reflects real production code scenarios
2. Has clear requirements and constraints
3. Includes example inputs and expected outputs
4. Specifies edge cases to handle
5. Mentions any libraries or patterns to use

Return ONLY the task description. Be specific and practical."""

    task = ask_ai(task_prompt, key_index, max_tokens=600)
    if not task:
        print(f"[Run {run_id}] Task generation failed — rate limited. Stopping cleanly.")
        return "STOP"

    # Step 3: Get student response
    output = ask_student(task, key_index)
    if not output:
        print(f"[Run {run_id}] Student failed — rate limited. Stopping cleanly.")
        return "STOP"

    # Step 4: Evaluate with rich prompt — retry up to 3 times, never fallback
    eval_prompt = f"""You are a senior software engineer and Python expert conducting a thorough code review.

TASK GIVEN TO STUDENT:
{task}

STUDENT SUBMISSION:
{output}

Conduct a professional code review covering ALL sections:

## 1. CORRECTNESS
- Does the code solve the task correctly?
- Are there bugs or logical errors?
- Does it handle edge cases?

## 2. CODE QUALITY
- Is the code readable and well-structured?
- Are names descriptive? Is it DRY?

## 3. BEST PRACTICES
- PEP 8 compliance, docstrings, type hints, error handling?

## 4. COMPLETENESS
- Are all requirements fulfilled?
- Is it production-ready?

## 5. IMPROVED SOLUTION
Provide a complete corrected version with inline comments.

## 6. KEY LEARNING POINTS
List 3-5 specific things the student should learn from this review.

End your response with exactly:
SCORE: X (where X is 0-10)"""

    correction = None
    score = None
    for attempt in range(3):
        result = ask_ai(eval_prompt, key_index, max_tokens=2048)
        if not result:
            print(f"[Run {run_id}] Evaluation rate limited on attempt {attempt+1}. Stopping cleanly.")
            return "STOP"
        if "unavailable" in result.lower() or "SCORE:" not in result:
            print(f"[Run {run_id}] Bad evaluation on attempt {attempt+1}, retrying...")
            time.sleep(15)
            continue
        try:
            score_line = [l for l in result.split("\n") if "SCORE:" in l][-1]
            score = int(score_line.split("SCORE:")[-1].strip().split()[0]) / 10
            correction = result
            break
        except:
            print(f"[Run {run_id}] Could not parse score on attempt {attempt+1}, retrying...")
            time.sleep(15)

    # If evaluation completely failed after 3 attempts — skip, do NOT store
    if correction is None or score is None:
        print(f"[Run {run_id}] Evaluation failed after 3 attempts — skipping record, not storing.")
        return False

    # Step 5: Store only complete, quality records
    store_record(task, output, correction, score, level, topic)
    add_topic(topic, score)

    current_total = get_total()
    print(f"[Run {run_id}] Complete | Score: {round(score*10)}/10 | Level: {level}/20 | Total: {current_total} | Key: {key_index+1}")
    return True

if __name__ == "__main__":
    start_time = time.time()
    initial_total = get_total()
    target = initial_total + DAILY_TARGET
    print(f"[AAES] Starting | Current: {initial_total} | Target: {target} | Keys: {len(groq_keys)}")

    run_id = 0
    key_index = 0
    succeeded = 0
    failed = 0

    while get_total() < target:
        elapsed = time.time() - start_time
        if elapsed > 20000:
            print("[AAES] Max runtime reached, stopping.")
            break

        run_id += 1
        result = run_one(run_id, key_index)

        if result == "STOP":
            print("[AAES] Rate limits exhausted — stopping cleanly. No incomplete records saved.")
            break
        elif result:
            succeeded += 1
        else:
            failed += 1

        key_index = (key_index + 1) % len(groq_keys)

    final_total = get_total()
    print(f"[AAES] Done | Final: {final_total} | Added: {final_total - initial_total} | Succeeded: {succeeded} | Failed: {failed}")
