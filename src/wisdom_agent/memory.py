"""
Memory storage for the Wisdom Framework Guide Agent.

Implements explicit, scoped, and reversible memory as per the design:
- Session Memory (default): Lives only during conversation
- Reflective Memory (opt-in): User-authored insights
- Framework Scores (opt-in): Aggregated wisdom trait tendencies
"""

import json
import logging
from datetime import datetime
from typing import List, Optional
from pathlib import Path

from .models import Reflection, SelfEvaluationResult, WisdomProfile

logger = logging.getLogger(__name__)


class MemoryStore:
    """Abstract base class for memory storage."""
    
    def save_reflection(self, reflection: Reflection) -> bool:
        """Save a user reflection."""
        raise NotImplementedError
    
    def get_reflections(self, user_id: str) -> List[Reflection]:
        """Get all reflections for a user."""
        raise NotImplementedError
    
    def get_reflection(self, reflection_id: str) -> Optional[Reflection]:
        """Get a specific reflection."""
        raise NotImplementedError
    
    def delete_reflection(self, reflection_id: str) -> bool:
        """Delete a reflection."""
        raise NotImplementedError
    
    def save_evaluation(self, evaluation: SelfEvaluationResult) -> bool:
        """Save a self-evaluation result."""
        raise NotImplementedError
    
    def get_evaluations(self, user_id: str) -> List[SelfEvaluationResult]:
        """Get all evaluations for a user."""
        raise NotImplementedError
    
    def get_wisdom_profile(self, user_id: str) -> Optional[WisdomProfile]:
        """Get or create wisdom profile for a user."""
        raise NotImplementedError
    
    def update_wisdom_profile(self, profile: WisdomProfile) -> bool:
        """Update a wisdom profile."""
        raise NotImplementedError


class FileMemoryStore(MemoryStore):
    """File-based memory store for development/testing."""
    
    def __init__(self, data_dir: str = "./data/memory"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        (self.data_dir / "reflections").mkdir(exist_ok=True)
        (self.data_dir / "evaluations").mkdir(exist_ok=True)
        (self.data_dir / "profiles").mkdir(exist_ok=True)
    
    def _get_reflection_path(self, reflection_id: str) -> Path:
        return self.data_dir / "reflections" / f"{reflection_id}.json"
    
    def _get_evaluation_path(self, evaluation_id: str) -> Path:
        return self.data_dir / "evaluations" / f"{evaluation_id}.json"
    
    def _get_profile_path(self, user_id: str) -> Path:
        return self.data_dir / "profiles" / f"{user_id}.json"
    
    def save_reflection(self, reflection: Reflection) -> bool:
        """Save a reflection to file."""
        try:
            path = self._get_reflection_path(reflection.id)
            with open(path, 'w') as f:
                json.dump(reflection.dict(), f, indent=2, default=str)
            logger.info(f"Saved reflection {reflection.id}")
            return True
        except Exception as e:
            logger.error(f"Error saving reflection: {e}")
            return False
    
    def get_reflections(self, user_id: str) -> List[Reflection]:
        """Get all reflections for a user."""
        reflections = []
        reflections_dir = self.data_dir / "reflections"
        
        for file_path in reflections_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data.get("user_id") == user_id:
                        reflections.append(Reflection(**data))
            except Exception as e:
                logger.error(f"Error loading reflection from {file_path}: {e}")
        
        reflections.sort(key=lambda r: r.created_at, reverse=True)
        return reflections
    
    def get_reflection(self, reflection_id: str) -> Optional[Reflection]:
        """Get a specific reflection."""
        path = self._get_reflection_path(reflection_id)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return Reflection(**data)
        except Exception as e:
            logger.error(f"Error loading reflection {reflection_id}: {e}")
            return None
    
    def delete_reflection(self, reflection_id: str) -> bool:
        """Delete a reflection."""
        path = self._get_reflection_path(reflection_id)
        if path.exists():
            try:
                path.unlink()
                logger.info(f"Deleted reflection {reflection_id}")
                return True
            except Exception as e:
                logger.error(f"Error deleting reflection: {e}")
        return False
    
    def save_evaluation(self, evaluation: SelfEvaluationResult) -> bool:
        """Save a self-evaluation result."""
        try:
            path = self._get_evaluation_path(evaluation.id)
            with open(path, 'w') as f:
                json.dump(evaluation.dict(), f, indent=2, default=str)
            logger.info(f"Saved evaluation {evaluation.id}")
            return True
        except Exception as e:
            logger.error(f"Error saving evaluation: {e}")
            return False
    
    def get_evaluations(self, user_id: str) -> List[SelfEvaluationResult]:
        """Get all evaluations for a user."""
        evaluations = []
        evaluations_dir = self.data_dir / "evaluations"
        
        for file_path in evaluations_dir.glob("*.json"):
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if data.get("user_id") == user_id:
                        evaluations.append(SelfEvaluationResult(**data))
            except Exception as e:
                logger.error(f"Error loading evaluation from {file_path}: {e}")
        
        evaluations.sort(key=lambda e: e.completed_at, reverse=True)
        return evaluations
    
    def get_wisdom_profile(self, user_id: str) -> Optional[WisdomProfile]:
        """Get wisdom profile for a user."""
        path = self._get_profile_path(user_id)
        if not path.exists():
            return None
        
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                return WisdomProfile(**data)
        except Exception as e:
            logger.error(f"Error loading profile for {user_id}: {e}")
            return None
    
    def update_wisdom_profile(self, profile: WisdomProfile) -> bool:
        """Update a wisdom profile."""
        try:
            path = self._get_profile_path(profile.user_id)
            profile.updated_at = datetime.utcnow()
            with open(path, 'w') as f:
                json.dump(profile.dict(), f, indent=2, default=str)
            logger.info(f"Updated profile for user {profile.user_id}")
            return True
        except Exception as e:
            logger.error(f"Error updating profile: {e}")
            return False


class NoMemoryStore(MemoryStore):
    """No-op memory store for when memory is disabled."""
    
    def save_reflection(self, reflection: Reflection) -> bool:
        return True
    
    def get_reflections(self, user_id: str) -> List[Reflection]:
        return []
    
    def get_reflection(self, reflection_id: str) -> Optional[Reflection]:
        return None
    
    def delete_reflection(self, reflection_id: str) -> bool:
        return True
    
    def save_evaluation(self, evaluation: SelfEvaluationResult) -> bool:
        return True
    
    def get_evaluations(self, user_id: str) -> List[SelfEvaluationResult]:
        return []
    
    def get_wisdom_profile(self, user_id: str) -> Optional[WisdomProfile]:
        return None
    
    def update_wisdom_profile(self, profile: WisdomProfile) -> bool:
        return True
