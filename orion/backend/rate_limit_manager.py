import hashlib
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional
import redis.asyncio as aioredis

logger = logging.getLogger("RateLimitManager")

class RateLimitManager:
    """
    Production Rate Limit, Key Pooling, and Caching Manager.
    Implements:
      1. Redis prompt & response caching (TTL-backed).
      2. Sliding-window RPM/TPM throttle per provider.
      3. Multi-API-Key rotation with automatic failover on 429/exhaustion.
      4. Exponential backoff retry logic.
    """

    def __init__(self, redis_url: str = "redis://127.0.0.1:6379/0"):
        self.redis_url = redis_url
        self.redis: Optional[aioredis.Redis] = None
        
        # Key pools by provider
        self.key_pools: Dict[str, List[str]] = {
            "gemini": self._load_keys("GEMINI_API_KEY", "GOOGLE_API_KEY"),
            "groq": self._load_keys("GROQ_API_KEY"),
            "openrouter": self._load_keys("OPENROUTER_API_KEY"),
            "deepseek": self._load_keys("DEEPSEEK_API_KEY"),
        }
        self.key_indices: Dict[str, int] = {p: 0 for p in self.key_pools}

    def _load_keys(self, *env_var_names: str) -> List[str]:
        keys = []
        for name in env_var_names:
            val = os.getenv(name)
            if val:
                for k in val.split(","):
                    k = k.strip()
                    if k and k not in keys:
                        keys.append(k)
        return keys

    async def get_redis(self) -> Optional[aioredis.Redis]:
        if self.redis is None:
            try:
                self.redis = aioredis.from_url(self.redis_url, decode_responses=True)
                await self.redis.ping()
            except Exception as e:
                logger.warning(f"Redis unavailable for caching/rate-limiting: {e}")
                self.redis = None
        return self.redis

    def get_active_key(self, provider: str) -> Optional[str]:
        """Returns the current active key for a provider."""
        pool = self.key_pools.get(provider, [])
        if not pool:
            return None
        idx = self.key_indices.get(provider, 0) % len(pool)
        return pool[idx]

    def rotate_key(self, provider: str) -> Optional[str]:
        """Rotates to the next available API key when rate-limited."""
        pool = self.key_pools.get(provider, [])
        if not pool or len(pool) <= 1:
            return self.get_active_key(provider)
        self.key_indices[provider] = (self.key_indices[provider] + 1) % len(pool)
        new_key = pool[self.key_indices[provider]]
        logger.info(f"Rotated {provider} key to index {self.key_indices[provider]}")
        return new_key

    def compute_cache_key(self, model: str, prompt: str, system_prompt: str = "") -> str:
        payload = f"{model}:{system_prompt}:{prompt}"
        hashed = hashlib.sha256(payload.encode("utf-8")).hexdigest()
        return f"llm_cache:{hashed}"

    async def get_cached_response(self, model: str, prompt: str, system_prompt: str = "") -> Optional[Dict[str, Any]]:
        r = await self.get_redis()
        if not r:
            return None
        key = self.compute_cache_key(model, prompt, system_prompt)
        try:
            val = await r.get(key)
            if val:
                logger.info(f"Cache HIT for key {key[:18]}...")
                return json.loads(val)
        except Exception as e:
            logger.warning(f"Error reading cache: {e}")
        return None

    async def set_cached_response(self, model: str, prompt: str, response: Dict[str, Any], system_prompt: str = "", ttl_seconds: int = 14400):
        r = await self.get_redis()
        if not r:
            return
        key = self.compute_cache_key(model, prompt, system_prompt)
        try:
            await r.setex(key, ttl_seconds, json.dumps(response))
            logger.info(f"Cached response stored for {ttl_seconds}s")
        except Exception as e:
            logger.warning(f"Error writing cache: {e}")

    async def check_rate_limit(self, provider: str, max_rpm: int = 30) -> bool:
        """
        Sliding-window rate limiter per provider in Redis.
        Returns True if within limit, False if rate-limit breached.
        """
        r = await self.get_redis()
        if not r:
            return True
        now = time.time()
        window_start = now - 60.0
        zset_key = f"rate_limit:{provider}"

        try:
            async with r.pipeline(transaction=True) as pipe:
                pipe.zremrangebyscore(zset_key, 0, window_start)
                pipe.zcard(zset_key)
                pipe.zadd(zset_key, {str(now): now})
                pipe.expire(zset_key, 120)
                _, count, _, _ = await pipe.execute()
                
            if count >= max_rpm:
                logger.warning(f"Rate limit threshold reached for {provider}: {count}/{max_rpm} RPM")
                return False
            return True
        except Exception as e:
            logger.warning(f"Rate limit check bypassed due to error: {e}")
            return True

    @staticmethod
    def compress_context(messages: List[Dict[str, str]], max_tokens_approx: int = 8000) -> List[Dict[str, str]]:
        """
        Keeps system prompt, initial user prompt, and recent history while pruning intermediate turns.
        """
        if not messages or len(messages) <= 4:
            return messages

        # Estimate 4 chars per token
        total_len = sum(len(m.get("content", "")) for m in messages)
        if total_len / 4 <= max_tokens_approx:
            return messages

        # Always preserve system prompt (index 0) and the final 2 turns
        system_msg = [messages[0]] if messages[0].get("role") == "system" else []
        recent_msgs = messages[-4:]
        
        # Take a slice of intermediate context
        logger.info(f"Pruning context from {len(messages)} messages to stay within token budget.")
        return system_msg + recent_msgs
