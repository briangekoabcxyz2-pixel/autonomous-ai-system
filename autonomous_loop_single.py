import os
import json
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

# Load all available Groq keys for rotation
groq_keys = []
for key_name in ["GROQ_API_KEY", "GROQ_API_KEY_2", "GROQ_API_KEY_3"]:
    key = os.environ.get(key_name)
    if key:
        groq_keys.append(key)

groq_key_index = [0]
print(f"[AI] Groq loaded with {len(groq_keys)} API keys for rotation")

def get_groq_client():
    return Groq(api_key=groq_keys[groq_key_index[0] % len(groq_keys)])

def rotate_groq_key():
    groq_key_index[0] += 1
    if groq_key_index[0] >= len(groq_keys):
        print("[Rate Limit] All Groq keys exhausted. Exiting gracefully.")
        exit(0)
    print(f"[Rotation] Switching to Groq key {groq_key_index[0] + 1} of {len(groq_keys)}")

LEVELS = {
    # Tier 1: Python Fundamentals
    1: "basic Python functions, variables, loops, and conditionals",
    2: "Python classes, objects, inheritance, and encapsulation",
    3: "error handling, file operations, and input validation",
    # Tier 2: Web Development
    4: "REST APIs with FastAPI, routing, and request handling",
    5: "database operations with SQLAlchemy and data modeling",
    6: "async programming, concurrency, and background tasks",
    # Tier 3: Software Engineering
    7: "testing with pytest, mocking, and test coverage",
    8: "design patterns: factory, singleton, observer, decorator",
    9: "data structures and algorithms: trees, graphs, dynamic programming",
    10: "system design: caching, queuing, load balancing concepts",
    # Tier 4: Backend & Security
    11: "complete backend systems with authentication and authorization",
    12: "microservices architecture and inter-service communication",
    13: "message queues with RabbitMQ and Kafka patterns",
    14: "API security: OAuth2, JWT, rate limiting, input sanitization",
    15: "performance optimization: profiling, caching, database indexing",
    # Tier 5: DevOps & ML
    16: "Docker containerization and Docker Compose orchestration",
    17: "CI/CD pipelines with GitHub Actions and automated testing",
    18: "machine learning pipelines with scikit-learn and data preprocessing",
    19: "cloud infrastructure: AWS/GCP services, serverless functions",
    20: "full production systems: monitoring, logging, scaling, disaster recovery",
}

TOPIC_POOL = {
    1: [
        "temperature unit converter", "simple calculator", "FizzBuzz with custom rules",
        "number guessing game", "list sorting without built-ins", "string manipulation utilities",
        "basic banking account", "simple todo list", "prime number checker", "fibonacci sequence",
        "password strength checker", "word counter", "simple ATM machine", "grade calculator",
        "Roman numeral converter", "palindrome checker", "anagram detector", "leap year checker",
        "currency converter", "BMI calculator",
    ],
    2: [
        "inventory management system", "library book tracker", "employee payroll system",
        "vehicle rental system", "university course enrollment", "bank account with inheritance",
        "shape hierarchy with area calculation", "animal shelter management", "hotel room booking",
        "e-commerce product catalog", "social media user profiles", "chess piece movement",
        "restaurant order system", "hospital patient records", "flight booking system",
        "parking lot system", "vending machine", "subscription service manager",
        "school timetable builder", "sports team roster manager",
    ],
    3: [
        "CSV file parser with validation", "JSON config file loader", "log file analyzer",
        "file backup utility", "data migration script", "input sanitizer for web forms",
        "retry mechanism for API calls", "custom exception hierarchy", "file encryption utility",
        "directory tree walker", "database connection handler", "email validator",
        "XML parser with error recovery", "bulk file renamer", "disk usage analyzer",
        "config file hot reloader", "zip archive manager", "file deduplicator",
        "log rotation utility", "file checksum verifier",
    ],
    4: [
        "URL shortener API", "weather data API", "user authentication endpoints",
        "product search API with filters", "rate limiting middleware", "file upload endpoint",
        "webhook handler", "pagination system", "API versioning", "health check endpoint",
        "CORS configuration", "request validation with Pydantic", "background task queue",
        "API key management", "GraphQL-style query endpoint", "geolocation API",
        "currency exchange API", "notification API", "image resize API", "PDF generation API",
    ],
    5: [
        "user activity tracking", "multi-tenant database schema", "soft delete pattern",
        "database migrations with Alembic", "full-text search implementation",
        "many-to-many relationships", "database connection pooling", "audit trail system",
        "data archiving strategy", "query optimization patterns", "database seeding script",
        "repository pattern implementation", "caching layer with Redis", "bulk insert optimization",
        "database health monitoring", "time-series data storage", "geospatial queries",
        "database sharding strategy", "event store implementation", "data versioning system",
    ],
    6: [
        "async web scraper", "concurrent API fetcher", "async message queue consumer",
        "WebSocket chat server", "async file processor", "parallel data pipeline",
        "async rate limiter", "background job scheduler", "async database queries",
        "event-driven notification system", "async cache warmer", "concurrent image processor",
        "async email sender", "real-time data streaming", "async retry with backoff",
        "async task orchestrator", "concurrent file downloader", "async health checker",
        "real-time leaderboard", "async batch processor",
    ],
    7: [
        "unit tests for payment processing", "mock external API calls", "test fixtures for database",
        "parametrized test cases", "integration tests for REST API", "test coverage reporting",
        "property-based testing", "snapshot testing", "performance benchmarking tests",
        "test doubles and stubs", "BDD with pytest-bdd", "mutation testing",
        "end-to-end API testing", "load testing with locust", "contract testing",
        "fuzz testing", "regression test suite", "test data factory",
        "API mocking server", "database test isolation",
    ],
    8: [
        "factory pattern for payment gateways", "observer pattern for event system",
        "decorator pattern for logging", "singleton database connection",
        "strategy pattern for sorting algorithms", "command pattern for undo/redo",
        "repository pattern with unit of work", "adapter pattern for third-party APIs",
        "chain of responsibility for request handling", "template method for report generation",
        "proxy pattern for caching", "facade pattern for complex subsystems",
        "state machine implementation", "iterator pattern for data processing",
        "composite pattern for file system",
    ],
    9: [
        "binary search tree implementation", "graph shortest path algorithm",
        "dynamic programming knapsack", "LRU cache implementation",
        "trie for autocomplete", "heap-based priority queue", "merge sort implementation",
        "hash table from scratch", "balanced BST (AVL tree)", "Dijkstra's algorithm",
        "topological sort", "sliding window algorithm", "two-pointer technique problems",
        "segment tree implementation", "union-find data structure",
    ],
    10: [
        "distributed cache design", "message broker architecture", "load balancer algorithm",
        "consistent hashing implementation", "rate limiter design patterns",
        "circuit breaker pattern", "saga pattern for distributed transactions",
        "event sourcing architecture", "CQRS implementation", "service mesh concepts",
        "API gateway design", "distributed lock manager", "leader election algorithm",
        "gossip protocol simulation", "distributed tracing system",
    ],
    11: [
        "JWT authentication system", "OAuth2 with Google login", "role-based access control",
        "API gateway with rate limiting", "two-factor authentication",
        "password reset flow", "refresh token rotation", "session management system",
        "API security headers", "encrypted data storage", "audit logging system",
        "IP whitelisting middleware", "brute force protection", "CORS policy manager",
        "secure file upload system",
    ],
    12: [
        "user service with gRPC", "order service with REST", "payment service integration",
        "service discovery with Consul", "inter-service authentication",
        "distributed configuration management", "service health aggregator",
        "API composition pattern", "backend for frontend pattern",
        "strangler fig migration pattern", "bulkhead pattern implementation",
        "sidecar pattern for logging", "ambassador pattern for proxying",
        "microservice chassis framework", "distributed tracing with OpenTelemetry",
    ],
    13: [
        "RabbitMQ producer and consumer", "Kafka event streaming pipeline",
        "dead letter queue handler", "message retry with backoff",
        "competing consumers pattern", "publish-subscribe system",
        "message deduplication", "ordered message processing",
        "fan-out message pattern", "priority queue with RabbitMQ",
        "event-driven order processing", "async notification pipeline",
        "message schema validation", "message broker failover",
        "transactional outbox pattern",
    ],
    14: [
        "SQL injection prevention", "XSS protection middleware",
        "CSRF token implementation", "API input sanitization",
        "secure password hashing", "certificate pinning",
        "dependency vulnerability scanner", "security headers middleware",
        "secrets rotation system", "API abuse detection",
        "honeypot implementation", "secure session cookies",
        "content security policy", "OAuth2 PKCE flow",
        "zero-trust API authentication",
    ],
    15: [
        "database query profiler", "Redis caching layer",
        "N+1 query detector", "connection pool optimizer",
        "async task queue with priorities", "CDN cache invalidation",
        "database index optimizer", "memory leak detector",
        "CPU profiling with cProfile", "lazy loading implementation",
        "response compression middleware", "database query cache",
        "batch processing optimizer", "memory-efficient data streaming",
        "application performance monitor",
    ],
    16: [
        "multi-stage Docker build", "Docker Compose for microservices",
        "Docker network configuration", "container health checks",
        "Docker volume management", "Docker secrets management",
        "container resource limits", "Docker image optimization",
        "multi-container application stack", "Docker registry setup",
        "container logging configuration", "Docker Swarm deployment",
        "Docker build cache optimization", "container security scanning",
        "development vs production Docker config",
    ],
    17: [
        "GitHub Actions test pipeline", "automated deployment workflow",
        "Docker build and push action", "automated code quality checks",
        "semantic versioning automation", "dependency update automation",
        "automated security scanning", "multi-environment deployment",
        "rollback automation", "automated changelog generation",
        "integration test pipeline", "performance regression testing",
        "automated API documentation", "infrastructure as code pipeline",
        "blue-green deployment automation",
    ],
    18: [
        "data preprocessing pipeline", "feature engineering system",
        "model training pipeline", "cross-validation framework",
        "hyperparameter tuning system", "model evaluation metrics",
        "data augmentation pipeline", "feature selection system",
        "model serialization and loading", "prediction API with FastAPI",
        "A/B testing framework for models", "data drift detection",
        "model versioning system", "automated retraining pipeline",
        "ML experiment tracking",
    ],
    19: [
        "AWS Lambda function with API Gateway", "S3 file storage integration",
        "DynamoDB data modeling", "SQS message queue consumer",
        "CloudWatch logging setup", "serverless image processing",
        "AWS Cognito authentication", "GCP Cloud Functions deployment",
        "Firebase real-time database", "cloud storage file manager",
        "serverless scheduled jobs", "cloud CDN configuration",
        "multi-region deployment", "cloud cost optimization",
        "infrastructure as code with Terraform",
    ],
    20: [
        "Prometheus metrics collection", "Grafana dashboard setup",
        "ELK stack log aggregation", "distributed tracing with Jaeger",
        "chaos engineering with Chaos Monkey", "auto-scaling configuration",
        "disaster recovery system", "zero-downtime deployment",
        "SLA monitoring system", "incident response automation",
        "capacity planning system", "performance baseline monitoring",
        "multi-region failover", "database backup automation",
        "production readiness checklist",
    ],
}

# Rich topic pool to force diversity
TOPIC_POOL = {
    1: [
        "temperature unit converter", "simple calculator", "FizzBuzz with custom rules",
        "number guessing game", "list sorting without built-ins", "string manipulation utilities",
        "basic banking account", "simple todo list", "prime number checker", "fibonacci sequence",
        "password strength checker", "word counter", "simple ATM machine", "grade calculator",
        "Roman numeral converter",
    ],
    2: [
        "inventory management system", "library book tracker", "employee payroll system",
        "vehicle rental system", "university course enrollment", "bank account with inheritance",
        "shape hierarchy with area calculation", "animal shelter management", "hotel room booking",
        "e-commerce product catalog", "social media user profiles", "chess piece movement",
        "restaurant order system", "hospital patient records", "flight booking system",
    ],
    3: [
        "CSV file parser with validation", "JSON config file loader", "log file analyzer",
        "file backup utility", "data migration script", "input sanitizer for web forms",
        "retry mechanism for API calls", "custom exception hierarchy", "file encryption utility",
        "directory tree walker", "database connection handler", "email validator",
        "XML parser with error recovery", "bulk file renamer", "disk usage analyzer",
    ],
    4: [
        "URL shortener API", "weather data API", "user authentication endpoints",
        "product search API with filters", "rate limiting middleware", "file upload endpoint",
        "webhook handler", "pagination system", "API versioning", "health check endpoint",
        "CORS configuration", "request validation with Pydantic", "background task queue",
        "API key management", "GraphQL-style query endpoint",
    ],
    5: [
        "user activity tracking", "multi-tenant database schema", "soft delete pattern",
        "database migrations with Alembic", "full-text search implementation",
        "many-to-many relationships", "database connection pooling", "audit trail system",
        "data archiving strategy", "query optimization patterns", "database seeding script",
        "repository pattern implementation", "caching layer with Redis", "bulk insert optimization",
        "database health monitoring",
    ],
    6: [
        "async web scraper", "concurrent API fetcher", "async message queue consumer",
        "WebSocket chat server", "async file processor", "parallel data pipeline",
        "async rate limiter", "background job scheduler", "async database queries",
        "event-driven notification system", "async cache warmer", "concurrent image processor",
        "async email sender", "real-time data streaming", "async retry with backoff",
    ],
    7: [
        "unit tests for payment processing", "mock external API calls", "test fixtures for database",
        "parametrized test cases", "integration tests for REST API", "test coverage reporting",
        "property-based testing", "snapshot testing", "performance benchmarking tests",
        "test doubles and stubs", "BDD with pytest-bdd", "mutation testing",
        "end-to-end API testing", "load testing with locust", "contract testing",
    ],
    8: [
        "JWT authentication system", "OAuth2 with Google login", "role-based access control",
        "API gateway with rate limiting", "microservices communication", "event sourcing pattern",
        "CQRS implementation", "distributed session management", "two-factor authentication",
        "API security headers", "password reset flow", "refresh token rotation",
        "audit logging system", "IP whitelisting", "encrypted data storage",
    ],
    9: [
        "React dashboard with FastAPI backend", "real-time charts with WebSockets",
        "form validation frontend and backend", "file upload with progress bar",
        "infinite scroll pagination", "dark mode toggle", "responsive navigation menu",
        "search with autocomplete", "drag and drop interface", "image gallery with lazy loading",
        "multi-step form wizard", "data table with sorting and filtering",
        "toast notification system", "modal dialog component", "offline-first PWA",
    ],
    10: [
        "CI/CD pipeline with GitHub Actions", "Docker containerization", "Kubernetes deployment",
        "monitoring with Prometheus and Grafana", "logging with ELK stack",
        "blue-green deployment strategy", "auto-scaling configuration", "secrets management",
        "database backup automation", "SSL certificate management", "CDN configuration",
        "load balancer setup", "disaster recovery plan", "performance profiling",
        "zero-downtime deployment",
    ],
}

def ask_ai(prompt, max_tokens=1024):
    for attempt in range(len(groq_keys)):
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                rotate_groq_key()
            else:
                raise
    print("[Rate Limit] All Groq keys exhausted. Exiting gracefully.")
    exit(0)

def ask_student(prompt):
    # Wrap prompt to encourage quality student output
    wrapped = f"""You are a Python developer completing a coding task.
Write clean, working Python code for the following task.
Include docstrings, type hints, and handle edge cases where appropriate.
Show your implementation with brief inline comments.

TASK:
{prompt}"""
    for attempt in range(len(groq_keys)):
        try:
            client = get_groq_client()
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": wrapped}],
                temperature=0.7,
                max_tokens=1500
            )
            return response.choices[0].message.content
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                rotate_groq_key()
            else:
                raise
    print("[Rate Limit] All Groq keys exhausted. Exiting gracefully.")
    exit(0)

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
    current_level = min(20, max(1, (total // 100) + 1))
    return total, avg_score, current_level

def generate_topic(level, avg_score, total):
    import random
    # Use topic pool for diversity, fallback to AI if needed
    pool = TOPIC_POOL.get(level, [])
    memory_summary = get_memory_summary() if MEMORY_ENABLED else ""
    # Filter out recently used topics from memory
    available = [t for t in pool if t.lower() not in memory_summary.lower()]
    if not available:
        available = pool  # reset if all used
    if available:
        return random.choice(available)
    # Fallback to AI generation
    level_desc = LEVELS[level]
    prompt = f"""You are an expert Python teacher designing a curriculum.
Student level: {level}/10. Average score: {round(avg_score*100)}%. Tasks completed: {total}.
Level focus: {level_desc}.
Memory of past lessons: {memory_summary}
Generate ONE specific, real-world coding topic not in this list: {memory_summary}
Return ONLY the topic name, no explanation."""
    return ask_ai(prompt, max_tokens=50)

def generate_task(topic, level, avg_score):
    level_desc = LEVELS[level]
    difficulty = "straightforward" if avg_score < 0.5 else "moderately challenging" if avg_score < 0.8 else "advanced"
    prompt = f"""You are a senior software engineer creating a coding challenge.
Topic: {topic}
Difficulty: {difficulty} (Level {level}/10)
Focus: {level_desc}

Write a detailed, realistic coding task that:
1. Reflects real production code scenarios
2. Has clear requirements and constraints
3. Includes example inputs and expected outputs
4. Specifies edge cases to handle
5. Mentions any libraries or patterns to use

Return ONLY the task description. Be specific and practical."""
    return ask_ai(prompt, max_tokens=600)

def evaluate(prompt, output, level):
    eval_prompt = f"""You are a senior software engineer and Python expert conducting a thorough code review.

TASK GIVEN TO STUDENT:
{prompt}

STUDENT SUBMISSION:
{output}

Conduct a professional code review covering ALL of the following sections:

## 1. CORRECTNESS
- Does the code solve the task correctly?
- Are there any bugs or logical errors?
- Does it handle the specified edge cases?

## 2. CODE QUALITY
- Is the code readable and well-structured?
- Are variable and function names descriptive?
- Is the code DRY (Don't Repeat Yourself)?
- Is the complexity appropriate for the task?

## 3. BEST PRACTICES
- Does it follow PEP 8 style guidelines?
- Are there proper docstrings and comments?
- Is error handling implemented correctly?
- Are type hints used where appropriate?

## 4. COMPLETENESS
- Are all requirements from the task fulfilled?
- Are edge cases handled?
- Is the solution production-ready?

## 5. IMPROVED SOLUTION
Provide a complete, corrected version of the code that demonstrates best practices.
Include inline comments explaining key decisions.

## 6. KEY LEARNING POINTS
List 3-5 specific things the student should learn from this review.

Be thorough, educational, and constructive. This review will be used to train an AI model.

End your response with exactly this line:
SCORE: X (where X is a number from 0 to 10 based on overall quality)"""
    for attempt in range(3):
        correction = ask_ai(eval_prompt, max_tokens=2048)
        if "unavailable" in correction.lower() or "SCORE:" not in correction:
            print(f"[Evaluate] Attempt {attempt+1} failed, retrying...")
            import time
            time.sleep(30)
            continue
        try:
            score_line = [l for l in correction.split("\n") if "SCORE:" in l][-1]
            score = int(score_line.split("SCORE:")[-1].strip().split()[0]) / 10
            return correction, score
        except:
            print(f"[Evaluate] Could not parse score on attempt {attempt+1}, retrying...")
            time.sleep(30)
    print("[Evaluate] All retries failed, skipping record.")
    return None, None

def store(prompt, output, correction, score, level, topic):
    DATASET_PATH.parent.mkdir(parents=True, exist_ok=True)
    record = {"prompt": prompt, "student_output": output, "teacher_correction": correction, "evaluation_score": score, "level": level, "topic": topic}
    with open(DATASET_PATH, "a") as f:
        f.write(json.dumps(record) + "\n")

def run():
    print("[AAES] Intelligent run started - 3 Groq keys rotating!")
    total, avg_score, level = get_stats()
    print(f"[Stats] Total: {total} | Avg Score: {round(avg_score*100)}% | Level: {level}/10")
    try:
        print(f"[Teacher] Generating topic for level {level}...")
        topic = generate_topic(level, avg_score, total)
        print(f"[Teacher] Topic: {topic}")
        task = generate_task(topic, level, avg_score)
        print(f"[Teacher] Task generated.")
        output = ask_student(task)
        print(f"[Student] Response received.")
        correction, score = evaluate(task, output, level)
        if correction is None or score is None:
            print("[AAES] Evaluation failed after retries, skipping this record.")
            return
        store(task, output, correction, score, level, topic)
        add_topic(topic, score)
        total_new = total + 1
        print(f"[Dataset] Total: {total_new} | Score: {round(score*10)}/10 | Level: {level}/10")
        print(f"[Memory] Topic saved: {topic}")
        if score >= 0.8:
            print(f"[Progress] Student performing well at level {level}!")
        else:
            print(f"[Progress] Student needs more practice at level {level}.")
        print("[AAES] Run complete!")
    except Exception as e:
        if "429" in str(e) or "rate_limit" in str(e).lower():
            print("[Rate Limit] Exiting gracefully.")
            exit(0)
        print(f"[ERROR] {e}")
        raise

if __name__ == "__main__":
    for i in range(10):
        print(f"\n[AAES] Starting run {i+1} of 10...")
        run()
