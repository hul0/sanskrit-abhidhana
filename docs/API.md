# Sanskrit Abhidhana REST API Reference

Sanskrit Abhidhana provides a high-throughput, low-latency (<5ms) REST API for searching Monier-Williams Sanskrit dictionary entries (286,525 headwords), performing full-text English definition searches, and transliterating across 15+ Indic and Roman schemes.

---

## Base URL

```
http://127.0.0.1:8000
```

---

## 1. Headword Definition Endpoint

### `GET /api/v1/define/{word}`

Retrieves Monier-Williams dictionary definitions for a Sanskrit headword. Accepts headwords in Devanagari, IAST, SLP1, Harvard-Kyoto (HK), ITRANS, or loose ASCII.

#### Path Parameters
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `word` | `string` | **Yes** | Headword string (e.g. `krishna`, `kṛṣṇa`, `कृष्ण`, `dharma`, `darma`) |

#### Query Parameters
| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `script` | `string` | `"auto"` | Input scheme: `auto`, `devanagari`, `iast`, `slp1`, `hk`, `itrans`, `velthuis`, `telugu`, `bengali`, `kannada`, `malayalam`, `tamil`, `ascii` |
| `limit` | `integer` | `50` | Maximum entries to return (1 - 200) |
| `raw_xml` | `boolean` | `false` | Include raw Monier-Williams XML markup in response |

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/define/krishna?script=auto&limit=5"
```

#### Example Response (`200 OK`)
```json
{
  "query": "krishna",
  "detected_script": "ascii",
  "search_type": "headword",
  "count": 1,
  "results": [
    {
      "key_slp1": "kfzRa",
      "headword_iast": "kṛṣṇa",
      "headword_devanagari": "कृष्ण",
      "headword_ascii": "krishna",
      "homonym": 1,
      "grammatical_code": "f.",
      "grammatical_info": "feminine",
      "definition": "black, dark, dark-blue; (with or without pakṣa) the dark half of a lunar month from full to new moon...",
      "abbreviations": [
        {
          "code": "N.",
          "expansion": "Name"
        },
        {
          "code": "L.",
          "expansion": "Lexicographers (ancient native Sanskrit dictionaries)"
        }
      ],
      "line_number": 55142.0,
      "page_column": "306,3"
    }
  ]
}
```

---

## 2. Flexible Dictionary Search

### `GET /api/v1/search`

Provides unified search supporting headword lookups, English full-text searches (FTS5), and prefix autocompletion.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `q` | `string` | **Yes** | — | Search query string |
| `type` | `string` | No | `"headword"` | Search mode: `headword`, `english`, or `autocomplete` |
| `script` | `string` | No | `"auto"` | Input scheme override |
| `limit` | `integer` | No | `50` | Max entries (1 - 200) |
| `raw_xml` | `boolean` | No | `false` | Include raw XML |

#### Example Request (English Full-Text Search)
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/search?q=liberation&type=english&limit=3"
```

#### Example Response (`200 OK`)
```json
{
  "query": "liberation",
  "search_type": "english_fts",
  "count": 3,
  "results": [
    {
      "key_slp1": "atimukti",
      "headword_iast": "atimukti",
      "headword_devanagari": "अतिमुक्ति",
      "headword_ascii": "atimukti",
      "definition": "final liberation (from death)...",
      "fts_snippet": "...final <b>liberation</b> (from death), TS. ; ŚBr. xiv...",
      "line_number": 2738.0,
      "page_column": "12,3"
    }
  ]
}
```

---

## 3. Transliteration Utility Endpoint

### `GET /api/v1/transliterate`

Transliterates text across 15+ Indic and Roman schemes.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `string` | **Yes** | — | Input text to transliterate |
| `from_scheme` | `string` | No | `"auto"` | Source scheme (`auto`, `devanagari`, `iast`, `slp1`, `hk`, `itrans`, `velthuis`, `telugu`, etc.) |
| `to_scheme` | `string` | No | `"iast"` | Target scheme (`devanagari`, `iast`, `slp1`, `telugu`, `bengali`, `kannada`, `malayalam`, `tamil`, `ascii`) |

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/transliterate?text=कृष्ण&from_scheme=devanagari&to_scheme=iast"
```

#### Example Response (`200 OK`)
```json
{
  "original_text": "कृष्ण",
  "from_scheme": "devanagari",
  "to_scheme": "iast",
  "transliterated_text": "kṛṣṇa"
}
```

---

## 4. Headword Autocomplete Endpoint

### `GET /api/v1/autocomplete`

Fast prefix autocompletion for Sanskrit headwords.

#### Query Parameters
| Parameter | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `prefix` | `string` | **Yes** | — | Headword prefix string |
| `limit` | `integer` | No | `20` | Max suggestions (1 - 50) |

#### Example Request
```bash
curl -X GET "http://127.0.0.1:8000/api/v1/autocomplete?prefix=krish&limit=3"
```

#### Example Response (`200 OK`)
```json
{
  "prefix": "krish",
  "count": 3,
  "suggestions": [
    {
      "slp1": "kfzRa",
      "iast": "kṛṣṇa",
      "devanagari": "कृष्ण",
      "ascii": "krishna"
    },
    {
      "slp1": "kfzRABA",
      "iast": "kṛṣṇābhā",
      "devanagari": "कृष्णाभा",
      "ascii": "krishnabha"
    }
  ]
}
```

---

## 5. Health Check Endpoint

### `GET /health`

Verifies server health and database readiness.

#### Example Response (`200 OK`)
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": 1753552000.0
}
```

---

## 6. System Telemetry & Metrics Endpoint

### `GET /metrics`

Reports live process RSS memory usage (MB), request counter, and average latency.

#### Example Response (`200 OK`)
```json
{
  "memory_rss_mb": 42.15,
  "memory_limit_mb": 300.0,
  "memory_status": "optimal (<300MB target)",
  "total_requests": 1420,
  "average_latency_ms": 0.48
}
```

---

## Response Header Telemetry

All API HTTP responses include execution latency in milliseconds:

```http
HTTP/1.1 200 OK
Content-Type: application/json
X-Process-Time-Ms: 0.45
```
