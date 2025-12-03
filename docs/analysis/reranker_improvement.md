## Comparison: Before vs After Enabling Reranker

| Metric                 | Without reranker | With reranker | Δ (abs.)     | Comment |
|------------------------|------------------|---------------|-------------|---------|
| Precision@1            | 0.6939           | **0.7143**    | **+0.0204** | Slight improvement in top-1 precision – better first hit. |
| Recall@1               | 0.6939           | **0.7143**    | **+0.0204** | Same positive change for top-1 recall. |
| Precision@3            | 0.3265           | 0.3129        | −0.0136     | Small drop in precision at top-3. |
| Recall@3               | **0.9796**       | 0.9388        | −0.0408     | Target content appears slightly less often in top-3. |
| Precision@5            | 0.2238           | 0.2129        | −0.0109     | Minor decrease in precision at top-5. |
| Recall@5               | **1.0000**       | 0.9592        | −0.0408     | Previously the target was always in top-5, now almost always. |
| Faithfulness           | 8.96             | 8.96          | 0.00        | No change. |
| Relevance              | 9.73             | **9.78**      | **+0.05**   | Answers are slightly more relevant. |
| Completeness           | 8.20             | **8.37**      | **+0.17**   | Answers became more complete. |
| Conciseness            | **8.65**         | 8.51          | −0.14       | Answers became slightly less concise. |
| Overall LLM score      | 8.88             | **8.90**      | **+0.02**   | Small overall gain in answer quality. |
| Retrieve time (ms)     | 53.7             | **31.4**      | **−22.3**   | Base retrieval is faster. |
| Rerank time (ms)       | –                | 984.2         | +984.2      | Extra cost for the reranking step. |
| LLM time (ms)          | 5164.2           | **4586.2**    | **−578.0**  | LLM runs slightly faster (less/noise in context). |
| Total latency (ms)     | **5219.0**       | 5602.9        | +383.9      | Overall latency increased due to reranking. |

### Takeaways

- **Quality vs. Ranking Trade-off**
  - Top-1 metrics improved (Precision@1 and Recall@1 from 0.6939 → 0.7143), which is what the user actually sees most of the time.
  - LLM-based scores slightly improved (overall_score 8.88 → 8.90, relevance and completeness also up), meaning final answers became a bit more useful and well-grounded.
  - At the same time, recall@3/5 and precision@3/5 dropped slightly, indicating that some relevant candidates are now being filtered out or pushed lower by the reranker.

- **Latency & Performance**
  - Base retrieval became faster (53.7 ms → 31.4 ms), but reranking added ~984 ms on top.
  - Total latency increased moderately (≈+384 ms), but LLM time decreased (5164.2 ms → 4586.2 ms), likely due to a cleaner, more focused context being sent to the model.

- **Overall Effect**
  - Enabling the reranker yields **slightly better top-1 quality and answer usefulness**, at the cost of:
    - a **small degradation in recall@k** (k=3,5) and conciseness,
    - and a **moderate increase in end-to-end latency**.
  - Given the current results, the reranker looks like a reasonable trade-off if the main goal is to optimize for **answer quality from the user’s perspective** rather than maximising raw recall@k.