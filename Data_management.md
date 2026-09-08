# Data Management and Database Design

**AI-Powered Business Risk Analysis and Recommendation System**

---

> **Author:** Shakir | **Project:** Backend AI Business Risk Analysis System  
> **Document Type:** Technical Design Document  
> **Section:** Data Management — Database Architecture, Constraints, Security, and Operations  
> **Version:** 1.0 | **Date:** September 2026

---

## Abstract

This document describes the complete data management architecture of the AI-Powered Business Risk Analysis and Recommendation System. The system persists all business intelligence artifacts — user accounts, analyzed products, AI-generated risk analyses, and processed customer reviews — in a **PostgreSQL 15** relational database. The persistence layer is implemented using **SQLAlchemy 2.x** ORM with a declarative model hierarchy, **Alembic** for schema versioning, and a custom **Repository Pattern** for tenant-isolated data access. Security is enforced through bcrypt password hashing, JWT-based stateless authentication, account lockout policies, and row-level user scoping across all data operations. This document covers the database overview, schema design, constraints, physical layout, security model, retrieval and manipulation operations, and backup and recovery strategies.

---

## Table of Contents

1. [3.1 Database Overview](#31-database-overview)
2. [3.2 Constraints](#32-constraints)
3. [3.3 Physical Database Design](#33-physical-database-design)
4. [3.4 Security Design](#34-security-design)
5. [3.5 Data Retrieval](#35-data-retrieval)
6. [3.6 Data Manipulation](#36-data-manipulation)
7. [3.7 Backup and Recovery](#37-backup-and-recovery)

---

## 3.1 Database Overview

### 3.1.1 Technology Selection

The system uses **PostgreSQL 15** as the primary relational database management system (RDBMS). The selection is driven by the following requirements:

| Requirement | PostgreSQL Feature |
|------------|-------------------|
| Native UUID primary keys | `UUID` type with zero storage overhead |
| Semi-structured JSON columns | `JSONB` / `JSON` with GIN indexing support |
| ACID transactional guarantees | Full MVCC (Multi-Version Concurrency Control) |
| Scalable connection pooling | `psycopg2` + SQLAlchemy pool management |
| Schema migration tooling | Alembic integration via `postgresql+psycopg2` dialect |
| Tenant data isolation | Row-level `user_id` scoping enforced at query level |

A **SQLite fallback** is also supported via the `is_sqlite` flag in `session.py`, enabling local development and testing without a PostgreSQL server dependency.

### 3.1.2 ORM and Connection Architecture

```
Application Layer (FastAPI)
        |
        | SQLAlchemy Session (via get_db_session())
        v
+---------------------------+
|   SQLAlchemy Engine       |
|   pool_size = 5           |
|   max_overflow = 10       |
|   pool_pre_ping = True    |
+---------------------------+
        |
        | postgresql+psycopg2
        v
+---------------------------+
|   PostgreSQL 15           |
|   Host: localhost:5432    |
|   Database: business_risk_db |
+---------------------------+
```

**Connection Configuration** (from `app/config/settings.py`):

```
DATABASE_URL  = "postgresql+psycopg2://postgres:postgres@localhost:5432/business_risk_db"
DB_POOL_SIZE      = 5       # Persistent connections in pool
DB_MAX_OVERFLOW   = 10      # Burst connections above pool_size
pool_pre_ping     = True    # Validate connections before use
```

`pool_pre_ping = True` ensures stale connections are detected and recycled before being handed to the application, preventing "server closed the connection unexpectedly" errors in long-idle deployments.

### 3.1.3 Entity Overview

The database schema comprises **four primary entities** with a strict hierarchical ownership structure:

```
users
  |
  +-- products (owned by user, many per user)
  |       |
  |       +-- analyses (many per product, per user)
  |               |
  |               +-- reviews (many per analysis, per user)
  |
  +-- analyses (direct reference for faster tenant-level history queries)
  |
  +-- reviews (direct reference for fastest per-user review lookup)
```

**Entity Relationship Diagram:**

```
+------------------+          +-------------------+
|     users        |          |     products      |
+------------------+          +-------------------+
| PK id (UUID)     |1       N | PK id (UUID)      |
| email (UNIQUE)   +----------+ FK user_id (UUID) |
| username (UNIQUE)|          | product_url       |
| hashed_password  |          | product_title     |
| full_name        |          | platform          |
| role             |          | category          |
| is_active        |          | overall_rating    |
| failed_login_att.|          | total_reviews     |
| locked_until     |          | seller_name       |
| reset_otp_code   |          | image_url         |
| reset_otp_exp_at |          | external_product_id|
| created_at       |          | current_price     |
| updated_at       |          | created_at        |
+------------------+          | updated_at        |
         |                    +--------+----------+
         |                             |
         |  1                          | 1
         |                             |
         v  N                          v  N
+------------------+          +-------------------+
|    analyses      |          |    reviews        |
+------------------+          +-------------------+
| PK id (UUID)     |          | PK id (UUID)      |
| public_id (STR)  |          | FK user_id (UUID) |
| FK user_id (UUID)|1       N | FK analysis_id    |
| FK product_id    +----------+ review_text (TEXT)|
| status           |          | sentiment         |
| execution_dur_ms |          | confidence_score  |
| quality_risk_scr |          | aspects (JSON)    |
| delivery_risk_scr|          | language          |
| trust_risk_score |          | preprocessing_meta|
| business_risk_idx|          | created_at        |
| business_risk_lvl|          | updated_at        |
| total_reviews    |          +-------------------+
| total_positive   |
| total_negative   |
| total_neutral    |
| average_confidence|
| aspect_statistics (JSON)|
| confidence_statistics (JSON)|
| risk_breakdown (JSON)|
| business_risk_snapshot (JSON)|
| recommendation_snapshot (JSON)|
| created_at       |
| updated_at       |
+------------------+
```

**Figure 1.** Entity Relationship Diagram (ERD) of the database schema.

### 3.1.4 Base Entity Design

All four entities inherit from the abstract `BaseEntity` class defined in `app/database/base.py`, which provides three universal fields:

```python
class BaseEntity(Base):
    __abstract__ = True

    id         = Column(UUIDType, primary_key=True, default=uuid.uuid4, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=..., onupdate=...)
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | `UUID` (PK) | Universally unique surrogate key, generated via `uuid.uuid4()` at insertion time |
| `created_at` | `TIMESTAMPTZ` | UTC timestamp of record creation, immutable after insert |
| `updated_at` | `TIMESTAMPTZ` | UTC timestamp of last modification, auto-updated on every `UPDATE` via `onupdate` hook |

**UUID Primary Key Rationale:**  
UUID primary keys (v4, random) are selected over sequential integer IDs for the following reasons:
- **Distributed safety**: IDs can be generated client-side or across microservices without coordination.
- **Opacity**: Sequential IDs expose record counts and insertion order to API consumers; UUIDs do not.
- **Merge-safe**: UUID PKs permit safe database merges without collision risk.

The `UUIDType` custom `TypeDecorator` transparently maps to PostgreSQL's native `UUID` type when connected to PostgreSQL, or to `CHAR(36)` for SQLite compatibility.

---

## 3.2 Constraints

### 3.2.1 Primary Key Constraints

Every table enforces a single-column UUID primary key:

| Table | PK Column | Type |
|-------|-----------|------|
| `users` | `id` | UUID (NOT NULL, UNIQUE) |
| `products` | `id` | UUID (NOT NULL, UNIQUE) |
| `analyses` | `id` | UUID (NOT NULL, UNIQUE) |
| `reviews` | `id` | UUID (NOT NULL, UNIQUE) |

### 3.2.2 Unique Constraints

| Table | Column(s) | Constraint Type | Business Rule |
|-------|-----------|----------------|---------------|
| `users` | `email` | UNIQUE | One account per email address |
| `users` | `username` | UNIQUE | One account per username handle |
| `analyses` | `public_id` | UNIQUE | Human-readable analysis identifier (`anl_...`) is globally unique |

### 3.2.3 Not-Null Constraints

The following columns are declared `nullable=False`, enforcing mandatory data presence at the database level:

**`users` table:**

| Column | Reason |
|--------|--------|
| `email` | Required for authentication and OTP dispatch |
| `username` | Required for login and display |
| `hashed_password` | Required for credential verification |
| `role` | Required for RBAC; defaults to `"seller"` |
| `is_active` | Required for account status checks |
| `failed_login_attempts` | Required for lockout tracking; defaults to `0` |

**`products` table:**

| Column | Reason |
|--------|--------|
| `user_id` | Tenant ownership — every product must belong to a user |
| `product_url` | Core scrape target — cannot be null |
| `product_title` | Required for display and search |
| `platform` | Required for scraper routing; defaults to `"Daraz"` |
| `overall_rating` | Required metric; defaults to `0.0` |
| `total_reviews` | Required metric; defaults to `0` |

**`analyses` table:**

| Column | Reason |
|--------|--------|
| `public_id` | Public business identifier for API access |
| `user_id` | Tenant ownership |
| `product_id` | Analysis must reference a product |
| `status` | Pipeline state machine; defaults to `"completed"` |
| `business_risk_level` | Core output — every completed analysis must have a risk classification |

**`reviews` table:**

| Column | Reason |
|--------|--------|
| `user_id` | Tenant ownership |
| `analysis_id` | Reviews must belong to an analysis |
| `review_text` | Core input — cannot be empty |

### 3.2.4 Foreign Key Constraints with Cascaded Deletion

All foreign key relationships implement `ON DELETE CASCADE`, ensuring referential integrity is maintained automatically without orphaned records:

```
users.id  (1)
    |
    +--cascade--> products.user_id     (N)  [all user products deleted with user]
    |
    +--cascade--> analyses.user_id     (N)  [all user analyses deleted with user]
    |
    +--cascade--> reviews.user_id      (N)  [all user reviews deleted with user]

products.id  (1)
    |
    +--cascade--> analyses.product_id  (N)  [all analyses deleted with product]

analyses.id  (1)
    |
    +--cascade--> reviews.analysis_id  (N)  [all reviews deleted with analysis]
```

This cascade strategy ensures that:
- Deleting a user account removes ALL associated products, analyses, and reviews.
- Deleting a product cascades to all of its analyses and their reviews.
- Deleting an analysis removes all its stored review records.

This is implemented in SQLAlchemy `relationship()` declarations with `cascade="all, delete-orphan"`.

### 3.2.5 Default Value Constraints

| Table | Column | Default Value | Rationale |
|-------|--------|---------------|-----------|
| `users` | `role` | `"seller"` | Standard tenant role on self-registration |
| `users` | `is_active` | `True` | New accounts are immediately active |
| `users` | `failed_login_attempts` | `0` | No failed attempts on creation |
| `products` | `platform` | `"Daraz"` | Primary supported e-commerce platform |
| `products` | `overall_rating` | `0.0` | Populated after scraping |
| `products` | `total_reviews` | `0` | Populated after scraping |
| `analyses` | `status` | `"completed"` | Default for synchronously completed runs |
| `analyses` | `execution_duration_ms` | `0.0` | Timed externally and persisted post-run |

### 3.2.6 Domain / Enum Constraints

The following string columns store enumerated values. Domain constraints are enforced at the application layer (via Pydantic schemas and service-layer validation) rather than `CHECK` constraints, providing flexibility for future enum extension:

| Table | Column | Allowed Values |
|-------|--------|----------------|
| `users` | `role` | `"seller"`, `"admin"` |
| `analyses` | `status` | `"pending"`, `"processing"`, `"scraped"`, `"completed"`, `"failed"` |
| `analyses` | `business_risk_level` | `"VERY_LOW"`, `"LOW"`, `"MEDIUM"`, `"HIGH"`, `"CRITICAL"` |
| `reviews` | `sentiment` | `"positive"`, `"negative"`, `"neutral"` |

---

## 3.3 Physical Database Design

### 3.3.1 Table Definitions

**Table: `users`**

```sql
CREATE TABLE users (
    id                    UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    email                 VARCHAR(255) NOT NULL UNIQUE,
    username              VARCHAR(64)  NOT NULL UNIQUE,
    hashed_password       VARCHAR(255) NOT NULL,
    full_name             VARCHAR(128),
    role                  VARCHAR(32)  NOT NULL DEFAULT 'seller',
    is_active             BOOLEAN      NOT NULL DEFAULT TRUE,
    failed_login_attempts INTEGER      NOT NULL DEFAULT 0,
    locked_until          TIMESTAMP WITH TIME ZONE,
    reset_otp_code        VARCHAR(16),
    reset_otp_expires_at  TIMESTAMP WITH TIME ZONE,
    created_at            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at            TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `products`**

```sql
CREATE TABLE products (
    id                   UUID          PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID          NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_url          VARCHAR(2048) NOT NULL,
    product_title        VARCHAR(512)  NOT NULL,
    platform             VARCHAR(64)   NOT NULL DEFAULT 'Daraz',
    category             VARCHAR(512),
    overall_rating       FLOAT         NOT NULL DEFAULT 0.0,
    total_reviews        INTEGER       NOT NULL DEFAULT 0,
    seller_name          VARCHAR(256),
    image_url            VARCHAR(2048),
    external_product_id  VARCHAR(128),
    current_price        VARCHAR(64),
    created_at           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at           TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `analyses`**

```sql
CREATE TABLE analyses (
    id                       UUID         PRIMARY KEY DEFAULT gen_random_uuid(),
    public_id                VARCHAR(64)  NOT NULL UNIQUE,
    user_id                  UUID         NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    product_id               UUID         NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    status                   VARCHAR(32)  NOT NULL DEFAULT 'completed',
    execution_duration_ms    FLOAT        NOT NULL DEFAULT 0.0,
    quality_risk_score       FLOAT        NOT NULL DEFAULT 0.0,
    delivery_risk_score      FLOAT        NOT NULL DEFAULT 0.0,
    trust_risk_score         FLOAT        NOT NULL DEFAULT 0.0,
    business_risk_index      FLOAT        NOT NULL DEFAULT 0.0,
    business_risk_level      VARCHAR(32)  NOT NULL,
    total_reviews            INTEGER      NOT NULL DEFAULT 0,
    total_positive_reviews   INTEGER      NOT NULL DEFAULT 0,
    total_negative_reviews   INTEGER      NOT NULL DEFAULT 0,
    total_neutral_reviews    INTEGER      NOT NULL DEFAULT 0,
    average_confidence       FLOAT        NOT NULL DEFAULT 0.0,
    aspect_statistics        JSON,
    confidence_statistics    JSON,
    risk_breakdown           JSON,
    business_risk_snapshot   JSON,
    recommendation_snapshot  JSON,
    created_at               TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at               TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

**Table: `reviews`**

```sql
CREATE TABLE reviews (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    analysis_id             UUID        NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    review_text             TEXT        NOT NULL,
    sentiment               VARCHAR(32),
    confidence_score        FLOAT       NOT NULL DEFAULT 0.0,
    aspects                 JSON,
    language                VARCHAR(32),
    preprocessing_metadata  JSON,
    created_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    updated_at              TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now()
);
```

### 3.3.2 Indexing Strategy

The system defines a comprehensive set of indexes to support the primary query patterns identified in the data access layer:

**Single-Column Indexes (Auto-created by SQLAlchemy `index=True`):**

| Table | Column | Purpose |
|-------|--------|---------|
| `users` | `email` | Fast login lookup by email |
| `users` | `username` | Fast login lookup by username |
| `users` | `reset_otp_code` | OTP verification lookup |
| `products` | `user_id` | All products owned by a user |
| `products` | `product_url` | Deduplication check on re-analysis |
| `analyses` | `public_id` | Direct API access by public identifier |
| `analyses` | `user_id` | All analyses for a user |
| `analyses` | `product_id` | All analyses for a product |
| `analyses` | `business_risk_index` | Sort and filter by continuous risk score |
| `analyses` | `business_risk_level` | Filter analyses by categorical risk level |
| `reviews` | `user_id` | All reviews per user |
| `reviews` | `analysis_id` | All reviews for an analysis |
| `reviews` | `sentiment` | Sentiment distribution queries |

**Composite Indexes (Explicitly Declared via `__table_args__`):**

```python
# products
Index("idx_products_user_created",     "user_id", "created_at")

# analyses
Index("idx_analyses_user_created",     "user_id", "created_at")
Index("idx_analyses_user_risk_level",  "user_id", "business_risk_level")

# reviews
Index("idx_reviews_user_analysis",     "user_id", "analysis_id")
```

| Index Name | Columns | Supports Query Pattern |
|------------|---------|----------------------|
| `idx_products_user_created` | `(user_id, created_at)` | Tenant-scoped paginated product history ordered by most recent |
| `idx_analyses_user_created` | `(user_id, created_at)` | Tenant-scoped paginated analysis history ordered by most recent |
| `idx_analyses_user_risk_level` | `(user_id, business_risk_level)` | Tenant-scoped risk level dashboard filtering |
| `idx_reviews_user_analysis` | `(user_id, analysis_id)` | Tenant-scoped review retrieval for a specific analysis |

**Composite index design rationale:** All composite indexes place `user_id` as the leading column. Since virtually all production queries include a `WHERE user_id = ?` clause (tenant isolation), leading with `user_id` allows PostgreSQL's query planner to eliminate all rows belonging to other tenants via index scan before evaluating secondary predicates.

### 3.3.3 Column Storage Strategy: First-Class vs. JSON

The `analyses` table implements a deliberate **hybrid storage model** that separates scalar metrics from complex nested data:

**First-Class SQL Scalar Columns:**

```sql
quality_risk_score      FLOAT   -- Indexed, sortable, aggregatable
delivery_risk_score     FLOAT
trust_risk_score        FLOAT
business_risk_index     FLOAT   -- Indexed for dashboard sorts
business_risk_level     VARCHAR -- Indexed for categorical filter
total_reviews           INTEGER
total_positive_reviews  INTEGER
total_negative_reviews  INTEGER
total_neutral_reviews   INTEGER
average_confidence      FLOAT
```

These fields are stored as typed SQL columns because they are used in `WHERE`, `ORDER BY`, and `GROUP BY` clauses for filtering, sorting, and dashboard aggregations. SQL indexes can be applied, and PostgreSQL's query planner can optimize range scans and equality checks efficiently.

**JSON Document Columns:**

```sql
aspect_statistics        JSON  -- {quality: {mentions, ratio, strength...}, delivery: ..., trust: ...}
confidence_statistics    JSON  -- {average_confidence, low_confidence_ratio}
risk_breakdown           JSON  -- Full fuzzy risk breakdown snapshot
business_risk_snapshot   JSON  -- Complete BusinessRiskResult object snapshot
recommendation_snapshot  JSON  -- Generated recommendations list
```

These fields store complex nested objects that are returned as-is to API consumers. They do not require filtering or aggregation at the SQL level, making JSON document storage appropriate. This avoids premature normalization of deeply nested structures into separate tables, reducing join complexity.

### 3.3.4 System Admin Seed Record

A bootstrap system user is automatically inserted during schema initialization:

```sql
INSERT INTO users (id, email, username, hashed_password, full_name, role, is_active, ...)
VALUES ('00000000-0000-0000-0000-000000000000',
        'system@local', 'system_admin', 'hashed_system',
        'System Admin', 'admin', TRUE, ...)
ON CONFLICT (id) DO NOTHING;
```

This `DEFAULT_SYSTEM_USER_ID` (`00000000-0000-0000-0000-000000000000`) serves as a sentinel ownership value for legacy records migrated before multi-tenant user isolation was introduced, preventing foreign key violations during schema upgrades.

---

## 3.4 Security Design

### 3.4.1 Password Security

User passwords are never stored in plaintext. The system uses **bcrypt** with automatic salting for one-way password hashing:

```python
# app/security/password.py
def hash_password(password: str) -> str:
    pwd_bytes = password.encode('utf-8')[:72]  # bcrypt 72-byte limit
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)
```

**Security properties of the implementation:**
- **Per-password unique salts:** `bcrypt.gensalt()` generates a cryptographically random 128-bit salt for every password, ensuring identical passwords produce different hashes.
- **Adaptive work factor:** bcrypt's work factor is configurable and can be increased as hardware improves without invalidating existing hashes.
- **72-byte truncation:** Enforces bcrypt's documented maximum input length, preventing hash collisions on very long passwords.
- **Timing-safe comparison:** `bcrypt.checkpw()` uses constant-time comparison, preventing timing oracle attacks.

The `hashed_password` column stores the complete bcrypt output string in `VARCHAR(255)`, which includes the algorithm identifier (`$2b$`), work factor, salt, and hash — all encoded in a single 60-character string.

### 3.4.2 Authentication and JWT Token Management

Authentication uses **stateless JWT (JSON Web Tokens)** with HMAC-SHA256 signing (`HS256`):

```python
# app/security/jwt.py
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24   # 24-hour token lifespan

def create_access_token(data: Dict[str, Any], expires_delta=None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)
```

**JWT Payload Structure:**

```json
{
  "sub": "<user_uuid>",
  "username": "<username>",
  "exp": <unix_timestamp>,
  "iat": <unix_timestamp>
}
```

| Claim | Value | Purpose |
|-------|-------|---------|
| `sub` | User UUID string | Identifies the authenticated user for tenant scoping |
| `username` | Username string | Conveniently cached in token for display |
| `exp` | UTC + 24h | Token expiry, validated server-side on every request |
| `iat` | Issue time | Auditing — when the token was issued |

**Security properties:**
- Tokens are signed with a server-side `JWT_SECRET_KEY`. Any modification to the payload invalidates the signature.
- `ExpiredSignatureError` is caught and returned as `HTTP 401` with a clear message.
- Stateless design means no session table is needed in the database, eliminating session fixation risks.

### 3.4.3 Account Lockout Policy

To prevent brute-force attacks against user credentials, the system implements a **progressive lockout mechanism** stored in the `users` table:

```python
# app/services/auth_service.py
MAX_FAILED_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES  = 15
```

**Lockout Flow:**

```
Login attempt
    |
    v
[Fetch user by email/username]
    |
    v
[Check locked_until > now_utc?]
    |--- YES --> raise AccountLockedError (HTTP 401)
    |
    v
[Verify password]
    |--- FAIL --> increment failed_login_attempts
    |             if >= 5: set locked_until = now + 15 min
    |             commit --> raise InvalidCredentialsError
    |
    +--- SUCCESS --> reset failed_login_attempts = 0
                    reset locked_until = NULL
                    commit --> issue JWT
```

The `locked_until` and `failed_login_attempts` fields in the `users` table persist lockout state across server restarts and across distributed instances, as the state is database-resident rather than in-memory.

### 3.4.4 OTP-Based Password Reset

The system provides a secure, time-limited OTP flow for password recovery using two dedicated columns on the `users` table:

| Column | Type | Purpose |
|--------|------|---------|
| `reset_otp_code` | `VARCHAR(16)` | Temporary one-time password code |
| `reset_otp_expires_at` | `TIMESTAMPTZ` | Expiry timestamp for OTP validity window |

The OTP is dispatched via the `EmailService` over SMTP (Gmail, configurable via `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` in settings). After successful verification, both fields are cleared to prevent OTP reuse.

### 3.4.5 Tenant Data Isolation

Every data access operation enforces tenant isolation by scoping all queries to the authenticated user's `user_id`. This is implemented consistently at the **Repository layer** rather than relying on application service logic:

```python
# AnalysisRepository - Tenant-scoped retrieval
stmt = select(Analysis).where(
    Analysis.public_id == public_id,
    Analysis.user_id == user_id       # <-- Tenant filter
)

# ProductRepository - Tenant-scoped listing
stmt = select(Product).where(
    Product.user_id == user_id        # <-- Tenant filter
).order_by(Product.created_at.desc())
```

**Isolation guarantees:**
- A user cannot retrieve, modify, or delete another user's products, analyses, or reviews.
- All paginated list queries include `WHERE user_id = ?` as a mandatory predicate.
- Cascade deletion on `users.id` ensures all tenant data is atomically removed when an account is deleted.

### 3.4.6 Environment Variable Security

Sensitive configuration values are never hardcoded in source files. They are loaded from environment variables using **Pydantic Settings**:

```python
# app/config/settings.py
class Settings(BaseSettings):
    DATABASE_URL: str  # Loaded from .env -- never committed to VCS
    SMTP_USER:    str
    SMTP_PASSWORD: str
    model_config = SettingsConfigDict(env_file=".env")
```

The `.env` file is explicitly listed in `.gitignore`, preventing accidental credential exposure in version control.

---

## 3.5 Data Retrieval

### 3.5.1 Session Management

All database operations are conducted within a SQLAlchemy `Session`, provisioned via the FastAPI dependency injection pattern:

```python
# app/database/session.py
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        db_logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()
```

Key session properties:
- `autocommit=False`: All writes require explicit `db.commit()`, enabling multi-step transactional writes.
- `autoflush=False`: Prevents implicit SQL flushes before every query, giving the service layer control over flush timing.
- Session lifetime is scoped to a single HTTP request via FastAPI's dependency injection generator (`yield`).
- The `finally` block ensures `db.close()` always executes, returning the connection to the pool even on exceptions.

### 3.5.2 User Retrieval Queries

The `UserRepository` (`app/repositories/user_repository.py`) provides the following retrieval operations:

| Method | SQL Equivalent | Use Case |
|--------|---------------|----------|
| `get_by_id(user_id)` | `SELECT * FROM users WHERE id = ?` | Token validation — user identity resolution |
| `get_by_email(email)` | `SELECT * FROM users WHERE email = ?` | Registration duplicate check |
| `get_by_username(username)` | `SELECT * FROM users WHERE username = ?` | Registration duplicate check |
| `get_by_email_or_username(identifier)` | `SELECT * FROM users WHERE email = ? OR username = ?` | Flexible login — accepts either identifier |

All lookups use SQLAlchemy Core `select()` expressions rather than ORM shorthand, providing explicit SQL control and avoiding N+1 query patterns.

### 3.5.3 Analysis Retrieval Queries

The `AnalysisRepository` (`app/repositories/analysis_repository.py`) supports the following retrieval operations:

**Single Record Retrieval:**

```python
def get_by_public_id(self, public_id: str, user_id: UUID = None) -> Optional[Analysis]:
    stmt = (
        select(Analysis)
        .options(joinedload(Analysis.product), joinedload(Analysis.reviews))
        .where(Analysis.public_id == public_id)
    )
    if user_id is not None:
        stmt = stmt.where(Analysis.user_id == user_id)
    return self.db.scalars(stmt).first()
```

`joinedload()` is used to eagerly fetch the related `product` and `reviews` collections in a single SQL `JOIN` query, preventing N+1 SELECT problems when the API response requires nested product and review data.

**Paginated History Retrieval:**

```python
def list_paginated(self, user_id, page, limit, risk_level, search, sort_by, order):
    stmt = (
        select(Analysis)
        .join(Analysis.product)
        .options(joinedload(Analysis.product))
        .where(Analysis.user_id == user_id)
    )
    # Optional: filter by risk_level
    if risk_level:
        stmt = stmt.where(Analysis.business_risk_level == risk_level.upper())
    # Optional: full-text search on product title or public_id
    if search:
        stmt = stmt.where(or_(
            Product.product_title.ilike(f"%{search}%"),
            Analysis.public_id.ilike(f"%{search}%")
        ))
    # Dynamic sort column and direction
    sort_col = getattr(Analysis, sort_by, Analysis.created_at)
    stmt = stmt.order_by(sort_col.desc() if order == "desc" else sort_col.asc())
    # Pagination
    stmt = stmt.offset((page - 1) * limit).limit(limit)
```

**Supported Query Parameters:**

| Parameter | SQL Operation | Example |
|-----------|--------------|---------|
| `user_id` | `WHERE user_id = ?` | Tenant isolation |
| `risk_level` | `WHERE business_risk_level = ?` | Filter by risk category |
| `search` | `WHERE product_title ILIKE ? OR public_id ILIKE ?` | Case-insensitive substring search |
| `sort_by` | `ORDER BY <column>` | `created_at`, `business_risk_index` |
| `order` | `ASC` / `DESC` | Sort direction |
| `page`, `limit` | `OFFSET`, `LIMIT` | Server-side pagination |

**Total Count Query:**

```python
count_stmt = select(func.count()).select_from(stmt.subquery())
total = self.db.scalar(count_stmt)
```

Using a subquery count prevents double-fetching and ensures the count reflects the same filter predicates as the data query, enabling accurate pagination metadata.

### 3.5.4 Product Retrieval Queries

The `ProductRepository` provides:

**URL-based Lookup with User-Priority Fallback:**

```python
def get_by_url(self, product_url: str, user_id: UUID = None) -> Optional[Product]:
    # Check user-owned product first
    if user_id is not None:
        user_prod = db.scalars(select(Product).where(
            Product.product_url == product_url,
            Product.user_id == user_id
        )).first()
        if user_prod:
            return user_prod
    # Fall back to global URL match (deduplication across tenants)
    return db.scalars(select(Product).where(Product.product_url == product_url)).first()
```

This two-phase lookup prevents duplicate product records when multiple tenants analyze the same product URL, while still preferring the user's own record when it exists.

### 3.5.5 Review Retrieval Queries

```python
def get_by_analysis_id(self, analysis_id: UUID) -> List[Review]:
    stmt = select(Review).where(Review.analysis_id == analysis_id)
    return list(self.db.scalars(stmt).all())
```

Reviews are retrieved in bulk by `analysis_id` for use in detailed analysis response payloads.

---

## 3.6 Data Manipulation

### 3.6.1 Transactional Write Pattern

All write operations follow a consistent **Unit of Work** pattern:

```
1. Begin transaction (implicit with autocommit=False)
2. Repository.add() / Repository.bulk_add()
    --> db.add(entity)   or   db.add_all(entities)
    --> db.flush()        (write to DB but don't commit)
3. Service layer validates flushed state
4. db.commit()           (make changes permanent)
5. db.refresh(entity)    (reload auto-generated fields: id, timestamps)
```

`db.flush()` is used between repository operations within the same request to make changes visible within the current transaction (e.g., to obtain the auto-generated `id` of a newly inserted product before inserting a dependent analysis), without committing to the database prematurely.

### 3.6.2 User Creation

```python
# AuthService.register_user()
new_user = User(
    email=schema.email.lower().strip(),
    username=schema.username.lower().strip(),
    hashed_password=hash_password(schema.password),
    role="seller",
    is_active=True,
    failed_login_attempts=0
)
created_user = user_repo.create(new_user)  # db.add() + db.flush()
db.commit()
db.refresh(created_user)
```

Email and username are normalized to lowercase before storage, ensuring case-insensitive uniqueness (`john@example.com` == `John@Example.COM`).

### 3.6.3 Analysis and Review Persistence

The `AnalysisService.run_analysis()` method executes a multi-entity transactional write:

```
1. Upsert Product:
   - Check product existence by URL (user-scoped, then global)
   - If not found: ProductRepository.add(new_product) + flush()
   - If found: reuse existing product record (update metadata)

2. Create Analysis:
   - Instantiate Analysis with all fuzzy risk scores, JSON snapshots
   - AnalysisRepository.add(analysis) + flush() -> assigns id

3. Bulk-Insert Reviews:
   - For each AI-predicted review: create Review entity
   - ReviewRepository.bulk_add(reviews) + flush()

4. Commit all three operations atomically:
   - db.commit() -- atomically persists product + analysis + reviews
```

If any step raises an exception, the `get_db_session()` dependency catches it, calls `db.rollback()`, and re-raises — ensuring no partial state is committed to the database.

### 3.6.4 Analysis Deletion

```python
def delete_by_public_id(self, public_id: str, user_id: UUID) -> bool:
    analysis = self.get_by_public_id(public_id, user_id=user_id)
    if not analysis:
        return False
    self.db.delete(analysis)
    self.db.flush()
    return True
```

The deletion cascade defined on the `analyses → reviews` relationship automatically removes all associated review records when `db.delete(analysis)` is executed. No explicit `DELETE FROM reviews` statement is needed.

### 3.6.5 Account Lockout Updates

```python
# On failed login attempt:
user.failed_login_attempts += 1
if user.failed_login_attempts >= MAX_FAILED_LOGIN_ATTEMPTS:
    user.locked_until = datetime.now(timezone.utc) + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
db.commit()

# On successful login:
user.failed_login_attempts = 0
user.locked_until = None
db.commit()
```

These lightweight `UPDATE` operations are committed immediately after authentication outcomes to ensure lockout state is always current, even in the event of server restarts or load-balanced requests.

### 3.6.6 Schema Auto-Migration

On application startup, `ensure_schema_migrations()` performs **additive, idempotent column migrations** using `ALTER TABLE ... ADD COLUMN` statements:

```python
# session.py
inspector = inspect(engine)
existing_cols = [c["name"].lower() for c in inspector.get_columns("users")]
if "role" not in existing_cols:
    conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(32) DEFAULT 'seller'"))
```

This mechanism handles schema evolution for deployments upgrading from older versions without running explicit Alembic migration scripts. All migration statements are:
- **Additive only** (never drop or rename columns without explicit Alembic scripts)
- **Guarded by column existence checks** (idempotent — safe to run multiple times)
- **Executed within a single transaction** (`engine.begin()`)

---

## 3.7 Backup and Recovery

### 3.7.1 Schema Version Control with Alembic

Database schema changes are version-controlled using **Alembic** (`alembic.ini`):

```ini
[alembic]
script_location = database/migrations
prepend_sys_path = .
```

**Migration Workflow:**

```
# Generate a new migration script after model changes
alembic revision --autogenerate -m "add_otp_columns_to_users"

# Apply pending migrations to production database
alembic upgrade head

# Inspect current revision
alembic current

# Roll back one revision
alembic downgrade -1

# Roll back to a specific revision
alembic downgrade <revision_id>
```

Alembic's `autogenerate` compares the current `Base.metadata` (all ORM model definitions) against the live database schema and generates `upgrade()` and `downgrade()` functions, supporting both forward migration and rollback.

The Alembic `env.py` dynamically reads `DATABASE_URL` from the application settings object, ensuring migration scripts always target the correct database environment.

### 3.7.2 PostgreSQL Backup Strategy

**Full Database Backup (pg_dump):**

```bash
# Logical dump -- portable, cross-version
pg_dump \
    --host=localhost \
    --port=5432 \
    --username=postgres \
    --dbname=business_risk_db \
    --format=custom \            # Compressed binary format
    --file=backup_$(date +%Y%m%d_%H%M%S).dump

# Restore from dump
pg_restore \
    --host=localhost \
    --dbname=business_risk_db \
    --format=custom \
    backup_20260908_150000.dump
```

**Recommended Backup Schedule:**

| Frequency | Type | Retention |
|-----------|------|-----------|
| Daily | Full `pg_dump` | 30 days |
| Weekly | Full `pg_dump` | 90 days |
| Monthly | Full `pg_dump` | 1 year |
| Continuous | WAL archiving (Point-In-Time Recovery) | 7 days of WAL segments |

### 3.7.3 Point-In-Time Recovery (PITR)

For production deployments, **WAL (Write-Ahead Log) archiving** enables Point-In-Time Recovery — the ability to restore the database to any second in time within the retention window:

**PostgreSQL `postgresql.conf` settings for PITR:**

```ini
wal_level = replica
archive_mode = on
archive_command = 'cp %p /var/lib/postgresql/wal_archive/%f'
```

**Recovery from a specific time:**

```bash
# Restore base backup
pg_basebackup -D /var/lib/postgresql/data_restore -Fp -Xs -P

# Create recovery.conf (PostgreSQL < 12) or postgresql.conf addition (>= 12)
restore_command = 'cp /var/lib/postgresql/wal_archive/%f %p'
recovery_target_time = '2026-09-08 12:00:00 UTC'
```

### 3.7.4 Disaster Recovery Plan

| Scenario | Recovery Action | RTO | RPO |
|----------|----------------|-----|-----|
| Accidental row deletion | Restore from daily backup or PITR | 1–4 hours | Up to 24 hours (or seconds with PITR) |
| Table corruption | `pg_restore` from latest `pg_dump` | 30 min | Last backup timestamp |
| Full database loss | Restore base backup + replay WAL | 2–6 hours | Seconds (with PITR) |
| Schema migration failure | `alembic downgrade -1` + revert model code | 15 min | Zero (no data loss) |
| Server hardware failure | Provision new PostgreSQL instance, restore dump | 2–4 hours | Last backup timestamp |

### 3.7.5 Development Environment Reset

For development and testing, the `Base.metadata.create_all(bind=engine)` call in `session.py` auto-creates all tables if they do not exist:

```python
# session.py -- executed on module import
try:
    Base.metadata.create_all(bind=engine)
    ensure_schema_migrations()
except Exception as err:
    db_logger.warning(f"Could not auto-create tables: {err}")
```

This means a fresh development environment requires only:
1. A running PostgreSQL instance
2. A valid `DATABASE_URL` in `.env`
3. Application startup — tables are created automatically

For a clean reset in development:

```bash
# Drop and recreate database
psql -U postgres -c "DROP DATABASE IF EXISTS business_risk_db;"
psql -U postgres -c "CREATE DATABASE business_risk_db;"

# Start application -- tables re-created automatically
uvicorn app.main:app --reload
```

### 3.7.6 Database Monitoring and Health Check

The system exposes a `/health` endpoint via `HealthService` (`app/services/health_service.py`) that verifies database connectivity as part of system health reporting. The health check executes a lightweight probe query against the database, returning `"healthy"` or `"unhealthy"` status, enabling integration with infrastructure monitoring tools (e.g., Kubernetes liveness probes, AWS RDS health checks).

---

## Summary

This document has described the complete data management architecture of the AI-Powered Business Risk Analysis and Recommendation System. The key design decisions are summarized below:

| Design Area | Decision | Rationale |
|-------------|----------|-----------|
| RDBMS | PostgreSQL 15 | Native UUID, JSON, full ACID, scalable pooling |
| ORM | SQLAlchemy 2.x Declarative | Pythonic models, type safety, Alembic compatibility |
| PK Strategy | UUID v4 | Opacity, distribution safety, merge-safe |
| Tenant Isolation | `user_id` row-level scoping in Repository layer | Defense-in-depth, auditable, testable |
| Password Security | bcrypt with per-password salt | Adaptive hashing, collision-free, timing-safe |
| Authentication | Stateless JWT (HS256, 24h expiry) | Scalable, no session table needed |
| Brute-Force Protection | 5-attempt lockout, 15-minute cooldown | Stored in DB — distributed-safe |
| Schema Evolution | Alembic migrations + runtime auto-migration | Version-controlled, idempotent, rollback-capable |
| JSON vs. SQL | Scalar risk metrics in SQL; nested snapshots in JSON | SQL enables filtering/sorting; JSON avoids over-normalization |
| Indexing | Composite indexes with `user_id` as leading column | Optimized for tenant-scoped paginated queries |
| Backup | Daily `pg_dump` + WAL PITR | Full + granular recovery coverage |

---

*End of Data Management Document*

---

> **Document Status:** Complete  
> **Reviewed By:** Author  
> **Related Documents:** research_component-2.md — Business Risk Calculation and Fuzzy Inference
