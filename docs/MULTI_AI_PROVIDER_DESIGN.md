# Multi-AI Provider Architecture Design

**Status:** 📋 Planned (Future Enhancement)  
**Branch:** Will be implemented on `feature/multi-ai-providers`  
**Priority:** Medium (after infrastructure-setup merge)

---

## 🎯 Goal

Enable seamless switching between AI providers (OpenAI, Claude, etc.) for cover letter generation with:
- Unified interface
- Easy provider switching via config
- Cost tracking
- Quality comparison tools

---

## 🏗️ Architecture Design

### **Directory Structure**

```
src/
  ai_providers/
    __init__.py              # Export get_provider() factory
    base_provider.py         # Abstract base class
    openai_provider.py       # OpenAI (GPT-4o-mini, GPT-4o)
    claude_provider.py       # Anthropic (Claude 3.5 Sonnet, Haiku)
    provider_factory.py      # Auto-select provider
    cost_tracker.py          # Track API costs
  
  cover_letter.py            # Refactored to use ai_providers
  
config/
  .env                       # AI_PROVIDER config
```

### **Base Provider Interface**

```python
# src/ai_providers/base_provider.py
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class GenerationResult:
    """Result from AI generation"""
    text: str
    input_tokens: int
    output_tokens: int
    cost: float
    model: str
    provider: str

class AIProvider(ABC):
    """Abstract base class for AI cover letter providers"""
    
    @abstractmethod
    def __init__(self, api_key: str, model: str):
        """Initialize provider with credentials"""
        pass
    
    @abstractmethod
    def generate_cover_letter(
        self, 
        job_data: Dict[str, Any],
        cv_text: str,
        language: str,
        max_tokens: int = 300
    ) -> GenerationResult:
        """
        Generate cover letter body text
        
        Args:
            job_data: Job posting data (company, title, description)
            cv_text: CV/resume text for context
            language: Target language ('german' or 'english')
            max_tokens: Maximum output tokens
            
        Returns:
            GenerationResult with text, tokens, cost
        """
        pass
    
    @abstractmethod
    def get_pricing(self) -> Dict[str, float]:
        """
        Get pricing information
        
        Returns:
            {
                'input_per_million': float,
                'output_per_million': float
            }
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name (e.g., 'OpenAI', 'Claude')"""
        pass
    
    @property
    @abstractmethod
    def model_name(self) -> str:
        """Model name (e.g., 'gpt-4o-mini', 'claude-3-5-sonnet')"""
        pass
```

### **Provider Factory**

```python
# src/ai_providers/provider_factory.py
from typing import Optional
from .base_provider import AIProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from utils.env import get_str
from utils.log_config import get_logger

logger = get_logger(__name__)

def get_provider(provider_name: Optional[str] = None) -> AIProvider:
    """
    Get AI provider instance based on config
    
    Args:
        provider_name: Override provider ('openai', 'claude', None=auto)
        
    Returns:
        AIProvider instance
        
    Raises:
        ValueError: If provider not available or configured
    """
    
    if not provider_name:
        provider_name = get_str('AI_PROVIDER', 'openai').lower()
    
    if provider_name == 'openai':
        api_key = get_str('OPENAI_API_KEY', default=None)
        model = get_str('OPENAI_MODEL', 'gpt-4o-mini')
        
        if not api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        logger.info(f"Using OpenAI provider: {model}")
        return OpenAIProvider(api_key=api_key, model=model)
    
    elif provider_name == 'claude':
        api_key = get_str('ANTHROPIC_API_KEY', default=None)
        model = get_str('ANTHROPIC_MODEL', 'claude-3-5-sonnet-20241022')
        
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY not configured")
        
        logger.info(f"Using Claude provider: {model}")
        return ClaudeProvider(api_key=api_key, model=model)
    
    else:
        raise ValueError(f"Unknown AI provider: {provider_name}")
```

---

## 💰 **Cost Tracking**

```python
# src/ai_providers/cost_tracker.py
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dataclasses import dataclass, asdict

@dataclass
class CostEntry:
    timestamp: str
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    cost: float
    company: str
    
class CostTracker:
    """Track AI API costs"""
    
    def __init__(self, log_file: str = "data/ai_costs.json"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
    
    def log_generation(self, result: GenerationResult, company: str):
        """Log a generation event"""
        entry = CostEntry(
            timestamp=datetime.now().isoformat(),
            provider=result.provider,
            model=result.model,
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            cost=result.cost,
            company=company
        )
        
        # Append to log file
        entries = self._load_entries()
        entries.append(asdict(entry))
        
        with open(self.log_file, 'w') as f:
            json.dump(entries, f, indent=2)
    
    def get_total_cost(self, provider: str = None) -> float:
        """Get total cost (optionally filtered by provider)"""
        entries = self._load_entries()
        
        if provider:
            entries = [e for e in entries if e['provider'] == provider]
        
        return sum(e['cost'] for e in entries)
    
    def get_cost_by_provider(self) -> Dict[str, float]:
        """Get cost breakdown by provider"""
        entries = self._load_entries()
        costs = {}
        
        for entry in entries:
            provider = entry['provider']
            costs[provider] = costs.get(provider, 0) + entry['cost']
        
        return costs
    
    def _load_entries(self) -> List[Dict[str, Any]]:
        if not self.log_file.exists():
            return []
        
        with open(self.log_file) as f:
            return json.load(f)
```

---

## 📋 **Implementation Checklist**

### **Phase 1: Refactor Existing Code**
- [ ] Extract current OpenAI logic to `OpenAIProvider` class
- [ ] Implement `AIProvider` interface
- [ ] Update `CoverLetterGenerator` to use provider factory
- [ ] Ensure all tests still pass

### **Phase 2: Add Claude Support**
- [ ] Install `anthropic` library: `pip install anthropic`
- [ ] Create `ClaudeProvider` class
- [ ] Map prompt format to Claude API
- [ ] Test with sample job data

### **Phase 3: Provider Factory & Config**
- [ ] Implement `get_provider()` factory
- [ ] Add env vars: `AI_PROVIDER`, `ANTHROPIC_API_KEY`, `ANTHROPIC_MODEL`
- [ ] Add fallback logic (try primary, fall back to secondary)

### **Phase 4: Cost Tracking**
- [ ] Implement `CostTracker` class
- [ ] Log every generation with tokens and cost
- [ ] Add CLI command to view cost summary: `python src/helper/view_ai_costs.py`

### **Phase 5: Quality Comparison**
- [ ] Create comparison script: generate same letter with both providers
- [ ] Save side-by-side outputs
- [ ] Document quality/cost trade-offs

### **Phase 6: Documentation**
- [ ] Update README with provider switching instructions
- [ ] Add cost estimation guide
- [ ] Document model selection recommendations

---

## 🧪 **Testing Strategy**

### **Test Cases**

1. **Provider switching**
   - Switch between OpenAI and Claude via env var
   - Verify same inputs produce valid outputs from both

2. **Cost accuracy**
   - Mock API responses with known token counts
   - Verify cost calculations match provider pricing

3. **Error handling**
   - Missing API key
   - Invalid model name
   - Rate limit errors
   - Fallback behavior

4. **Quality comparison**
   - Same job data through both providers
   - Human review of outputs
   - Measure word count, tone, format compliance

---

## 📊 **Expected Outcomes**

### **Flexibility**
- Switch providers in seconds (change 1 env var)
- Test different models without code changes
- Compare costs and quality empirically

### **Cost Optimization**
- Use cheap provider (OpenAI gpt-4o-mini) for bulk
- Use premium provider (Claude) for important jobs
- Track spending per provider

### **Resilience**
- Automatic fallback if primary provider fails
- No vendor lock-in
- Easy to add new providers (Gemini, Llama, etc.)

---

## 🚀 **Future Extensions**

### **Advanced Features** (Post-v1)
- [ ] **Ensemble generation**: Generate with multiple providers, pick best
- [ ] **A/B testing**: Randomly assign providers, track application success
- [ ] **Custom prompts per provider**: Optimize prompts for each AI's strengths
- [ ] **Streaming responses**: Real-time generation for UI
- [ ] **Caching**: Cache common job descriptions to reduce API calls

### **Additional Providers**
- [ ] Google Gemini
- [ ] Meta Llama (via Replicate)
- [ ] Local models (Ollama)

---

## 🎯 **Success Criteria**

Multi-provider implementation is successful when:
1. ✅ Can switch providers via single env var change
2. ✅ All tests pass with both providers
3. ✅ Cost tracking accurate to <1% error
4. ✅ Documentation clear enough for non-technical user
5. ✅ No regression in existing OpenAI functionality

---

**Next:** When ready to implement, create branch `feature/multi-ai-providers` from `develop`
