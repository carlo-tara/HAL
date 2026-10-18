from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from threading import Lock
from typing import Any

SUPPORTED_TASKS = {"choice", "routing", "score", "noul"}


def _string_tuple(value: Any, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, (list, tuple)) or any(
        not isinstance(item, str) for item in value
    ):
        raise TypeError(f"{field} must be a list or tuple of strings")
    return tuple(value)


@dataclass(frozen=True)
class TaskContract:
    task_type: str
    instruction: str
    source: str = ""
    output_format: str = ""
    constraints: tuple[str, ...] = ()
    risk_level: str = "unknown"
    complexity: str = "unknown"
    candidates: tuple[str, ...] = ()
    criteria: str = ""
    is_intermediate: bool = False
    changes_flow: bool = False

    @classmethod
    def from_request(
        cls, task_type: str, args: tuple[Any, ...], metadata: Any
    ) -> TaskContract:
        if task_type not in SUPPORTED_TASKS:
            raise ValueError(f"Unsupported System 1 task: {task_type}")
        if isinstance(metadata, cls):
            if metadata.task_type != task_type:
                raise ValueError(
                    "Task contract family does not match the requested task"
                )
            return metadata
        if not isinstance(metadata, Mapping):
            raise TypeError("task_contract must be a mapping or TaskContract")

        instruction = metadata.get("instruction", args[0] if args else "")
        if not isinstance(instruction, str) or not instruction.strip():
            raise ValueError("task_contract requires a non-empty instruction")
        if task_type in {"choice", "routing"}:
            default_candidates = args[1] if len(args) > 1 else ()
            candidates = _string_tuple(
                metadata.get("candidates", default_candidates), "candidates"
            )
        else:
            candidates = _string_tuple(metadata.get("candidates", ()), "candidates")

        source = metadata.get("source", "")
        output_format = metadata.get("output_format", "")
        risk_level = metadata.get("risk_level", "unknown")
        complexity = metadata.get("complexity", "unknown")
        criteria = metadata.get(
            "criteria", args[1] if task_type == "score" and len(args) > 1 else ""
        )
        constraints = _string_tuple(metadata.get("constraints", ()), "constraints")
        is_intermediate = metadata.get("is_intermediate", False)
        changes_flow = metadata.get("changes_flow", False)
        for name, value in (
            ("is_intermediate", is_intermediate),
            ("changes_flow", changes_flow),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{name} must be a boolean")
        for name, value in (
            ("source", source),
            ("output_format", output_format),
            ("risk_level", risk_level),
            ("complexity", complexity),
            ("criteria", criteria),
        ):
            if not isinstance(value, str):
                raise TypeError(f"{name} must be a string")

        return cls(
            task_type=task_type,
            instruction=instruction,
            source=source,
            output_format=output_format,
            constraints=constraints,
            risk_level=risk_level,
            complexity=complexity,
            candidates=candidates,
            criteria=criteria,
            is_intermediate=is_intermediate,
            changes_flow=changes_flow,
        )


@dataclass
class LayaCallBudget:
    """Share one instance across a run; count HTTP attempts, not local/cache hits."""

    max_calls: int = 1
    max_retries: int = 0
    retry_reason: str = ""
    _calls: int = field(default=0, init=False, repr=False)
    _retries: int = field(default=0, init=False, repr=False)
    _lock: Any = field(default_factory=Lock, init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        for name, value in (
            ("max_calls", self.max_calls),
            ("max_retries", self.max_retries),
        ):
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{name} must be a non-negative integer")
        if self.max_retries > 1:
            raise ValueError("At most one transient retry is allowed per run")
        if not isinstance(self.retry_reason, str):
            raise TypeError("retry_reason must be a string")
        if self.max_retries and not self.retry_reason.strip():
            raise ValueError("Retries require an explicit reason")

    @property
    def calls(self) -> int:
        with self._lock:
            return self._calls

    @property
    def retries(self) -> int:
        with self._lock:
            return self._retries

    def try_consume(self, *, ceiling: int | None = None) -> bool:
        with self._lock:
            limit = self.max_calls if ceiling is None else min(self.max_calls, ceiling)
            if self._calls >= limit:
                return False
            self._calls += 1
            return True

    def try_retry(self, *, ceiling: int | None = None) -> bool:
        with self._lock:
            limit = self.max_calls if ceiling is None else min(self.max_calls, ceiling)
            if self._retries >= self.max_retries or self._calls >= limit:
                return False
            self._retries += 1
            return True


@dataclass(frozen=True)
class PreflightDecision:
    payload: dict[str, Any] | None
    local_result: str | None = None


def prepare_laya_request(contract: TaskContract) -> PreflightDecision:
    if (
        contract.task_type in {"choice", "routing"}
        and contract.risk_level == "low"
        and contract.complexity == "atomic"
        and len(contract.candidates) == 1
    ):
        return PreflightDecision(payload=None, local_result=contract.candidates[0])

    instruction = " ".join(contract.instruction.split())[:160]
    metadata = [
        f"task_family={contract.task_type}",
        f"complexity={contract.complexity}",
        f"risk={contract.risk_level}",
        f"source_chars={len(contract.source)}",
    ]
    if contract.output_format:
        metadata.append(f"format={contract.output_format[:48]}")
    if contract.constraints:
        compact_constraints = "; ".join(
            " ".join(item.split())[:64] for item in contract.constraints[:4]
        )
        metadata.append(f"constraints={compact_constraints}")
    text = "; ".join(metadata + [f"instruction={instruction}"])

    payload: dict[str, Any] = {"task": contract.task_type, "text": text}
    if contract.task_type == "choice":
        payload["options"] = list(contract.candidates)
    elif contract.task_type == "routing":
        payload["routes"] = list(contract.candidates)
    elif contract.task_type == "score" and contract.criteria:
        payload["criteria"] = " ".join(contract.criteria.split())[:120]
    return PreflightDecision(payload=payload)
