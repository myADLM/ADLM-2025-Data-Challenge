import json
import queue
import random
import threading
import time
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass
from typing import Optional

from botocore.exceptions import (ClientError, ConnectionClosedError,
                                 EndpointConnectionError, ReadTimeoutError)

from app.src.util.aws import get_bedrock_client

# ---- Rate limiter configuration
REQUESTS_PER_MINUTE = 50
MIN_INTERVAL = 60.0 / REQUESTS_PER_MINUTE
MAX_CONCURRENT_REQUESTS = 30


# ---- Global state
@dataclass
class QueuedRequest:
    payload: dict
    model_id: str
    future: Future
    max_attempts: int
    timeout: Optional[float] = None  # seconds for caller wait


@dataclass
class BedrockState:
    q: queue.Queue[QueuedRequest]
    shutdown: threading.Event
    lock: threading.Lock
    next_allowed: float
    active_requests: int
    dispatcher: threading.Thread | None = None
    executor: ThreadPoolExecutor | None = None


_state = BedrockState(
    q=queue.Queue(),
    shutdown=threading.Event(),
    lock=threading.Lock(),
    next_allowed=time.monotonic(),
    active_requests=0,
)


def _start_services_if_needed():
    with _state.lock:
        if _state.executor is None:
            _state.executor = ThreadPoolExecutor(
                max_workers=MAX_CONCURRENT_REQUESTS, thread_name_prefix="bedrock-worker"
            )

        if _state.dispatcher is None or not _state.dispatcher.is_alive():
            t = threading.Thread(
                target=_dispatcher, name="bedrock-dispatcher", daemon=True
            )
            _state.dispatcher = t
            t.start()


def _dispatcher():
    """Dispatch requests to worker pool at controlled rate."""
    while not _state.shutdown.is_set():
        try:
            req: QueuedRequest = _state.q.get(timeout=1.0)
        except queue.Empty:
            continue

        # Skip cancelled futures
        if req.future.cancelled():
            continue

        # Wait for rate limiting and concurrent request limit
        while True:
            with _state.lock:
                now = time.monotonic()
                rate_ok = now >= _state.next_allowed
                concurrency_ok = _state.active_requests < MAX_CONCURRENT_REQUESTS

                if rate_ok and concurrency_ok:
                    # Reserve the next slot and increment active count
                    _state.next_allowed = max(now, _state.next_allowed) + MIN_INTERVAL
                    _state.active_requests += 1
                    break

                # Calculate how long to wait
                wait_time = 0.1  # default short wait for concurrency
                if not rate_ok:
                    wait_time = max(wait_time, _state.next_allowed - now)

            # Allow early exit on shutdown
            if _state.shutdown.wait(timeout=wait_time):
                return

        # Submit to thread pool for concurrent execution
        _state.executor.submit(_process_request_wrapper, req)


def _process_request_wrapper(req: QueuedRequest):
    """Wrapper to handle active request counting."""
    try:
        _process_request(req)
    finally:
        with _state.lock:
            _state.active_requests -= 1


def _process_request(req: QueuedRequest):
    """Invoke with backoff on throttling/transient errors."""
    bedrock = get_bedrock_client()  # Each thread gets its own client
    base = 0.2  # initial backoff (s)

    for attempt in range(1, req.max_attempts + 1):
        if req.future.cancelled():
            return

        try:
            resp = bedrock.invoke_model(
                modelId=req.model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(req.payload),
            )
            data = json.loads(resp["body"].read())
            text = _extract_text(data)
            req.future.set_result(text)
            return

        except ClientError as e:
            code = (e.response.get("Error") or {}).get("Code", "")
            if code in {
                "Throttling",
                "ThrottlingException",
                "TooManyRequestsException",
                "ProvisionedThroughputExceededException",
            }:
                # For throttling, add extra backoff and retry
                if attempt == req.max_attempts:
                    req.future.set_exception(e)
                    return

                # Exponential backoff with jitter
                sleep = base * (2 ** (attempt - 1))
                jitter = random.random() * 0.25 * sleep
                time.sleep(sleep + jitter)
                continue
            else:
                req.future.set_exception(e)
                return

        except (EndpointConnectionError, ConnectionClosedError, ReadTimeoutError) as e:
            # transient network—retry with backoff
            if attempt == req.max_attempts:
                req.future.set_exception(e)
                return
            sleep = base * (2 ** (attempt - 1))
            jitter = random.random() * 0.25 * sleep
            time.sleep(sleep + jitter)

        except Exception as e:
            req.future.set_exception(e)
            return

    # Should not reach here, but just in case:
    req.future.set_exception(RuntimeError("exhausted retries"))


def _extract_text(data: dict) -> str:
    """Safely extract the first text chunk; fall back to raw JSON."""
    try:
        parts = data["output"]["message"]["content"]
        for p in parts:
            if "text" in p and isinstance(p["text"], str):
                return p["text"].strip()
    except Exception:
        pass
    return json.dumps(data)


def shutdown_rate_worker():
    """Optional: call at program end for a clean exit."""
    _state.shutdown.set()

    # Shutdown dispatcher
    dispatcher = _state.dispatcher
    if dispatcher and dispatcher.is_alive():
        dispatcher.join(timeout=2.0)

    # Shutdown executor
    executor = _state.executor
    if executor:
        executor.shutdown(wait=True)


def query_model(
    system: str,
    message: str,
    *,
    max_attempts: int = 10,
    model_id: str = "amazon.nova-lite-v1:0",
    timeout: Optional[float] = None,
) -> str:
    """
    Queue a request and block until the result (or timeout).
    """
    _start_services_if_needed()

    payload = {
        "schemaVersion": "messages-v1",
        "system": [{"text": system}],
        "messages": [
            {
                "role": "user",
                "content": [{"text": message, "cachePoint": {"type": "default"}}],
            }
        ],
        "inferenceConfig": {"temperature": 0.7, "maxTokens": 10000},
    }

    fut = Future()
    req = QueuedRequest(
        payload=payload,
        model_id=model_id,
        future=fut,
        max_attempts=max_attempts,
        timeout=timeout,
    )

    _state.q.put(req)

    # Allow caller to bound their wait
    return fut.result(timeout=timeout)
