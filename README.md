## Architecture

### Multi-Agent Design
The system uses 4 specialized agents orchestrated by LangGraph:

1. **Research Agent**: Searches web for competitor information (Tavily Search)
2. **Extraction Agent**: Extracts detailed content from pages (Tavily Extract)
3. **Crawl Agent**: Deep crawls websites for hidden info (Tavily Crawl)
4. **Analysis Agent**: Synthesizes insights using GPT-4o-mini

### Workflow Orchestration
Agents execute in a logical sequence, where each agent builds on 
the previous agent's output:
```
Research → Extraction → Crawl → Analysis
```

This sequential flow ensures:
- Clean data dependencies
- Predictable state management
- Easy debugging and maintenance

### Performance Optimization
**Within-agent parallelism** provides significant performance gains:
- All competitors are processed simultaneously within each agent
- Uses `asyncio.gather()` for concurrent API calls
- Result: **1.9x speedup** (22s vs 42s sequential)

Example:
```python
# Research Agent processes all 7 competitors in parallel
tasks = [search(competitor) for competitor in competitors]
results = await asyncio.gather(*tasks)  # 0.27s instead of 2.1s
```