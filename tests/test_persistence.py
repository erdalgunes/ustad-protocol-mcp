"""
Test suite for persistence layer.
Following TDD - tests before implementation.
"""

import pytest
import tempfile
import os
from pathlib import Path
import json


class TestPersistenceLayer:
    """Test database persistence functionality"""
    
    @pytest.fixture
    def temp_db(self):
        """Create a temporary database file"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_save_session_to_db(self, temp_db):
        """Test saving a thinking session to database"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        server = PersistentSequentialThinking(db_path=temp_db)
        
        # Create a session
        thought1 = {
            "thought": "First persistent thought",
            "thoughtNumber": 1,
            "totalThoughts": 2,
            "nextThoughtNeeded": True,
            "confidence": 0.85
        }
        server.process_thought(thought1)
        
        thought2 = {
            "thought": "Second persistent thought",
            "thoughtNumber": 2,
            "totalThoughts": 2,
            "nextThoughtNeeded": False,
            "confidence": 0.90
        }
        server.process_thought(thought2)
        
        # Save session
        session_id = server.save_session("test_session", metadata={"user": "test"})
        
        assert session_id is not None
        assert isinstance(session_id, str)
        
        # Verify saved
        sessions = server.list_sessions()
        assert len(sessions) > 0
        assert any(s["name"] == "test_session" for s in sessions)
    
    def test_load_session_from_db(self, temp_db):
        """Test loading a saved session from database"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        # Save a session
        server1 = PersistentSequentialThinking(db_path=temp_db)
        
        thought = {
            "thought": "Thought to persist",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False,
            "confidence": 0.75
        }
        server1.process_thought(thought)
        session_id = server1.save_session("load_test")
        
        # Load in new server instance
        server2 = PersistentSequentialThinking(db_path=temp_db)
        loaded = server2.load_session(session_id)
        
        assert loaded == True
        history = server2.get_thought_history()
        assert len(history) == 1
        assert history[0]["thought"] == "Thought to persist"
        assert history[0]["confidence"] == 0.75
    
    def test_list_sessions(self, temp_db):
        """Test listing all saved sessions"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        server = PersistentSequentialThinking(db_path=temp_db)
        
        # Save multiple sessions
        for i in range(3):
            server.reset()
            thought = {
                "thought": f"Session {i} thought",
                "thoughtNumber": 1,
                "totalThoughts": 1,
                "nextThoughtNeeded": False
            }
            server.process_thought(thought)
            server.save_session(f"session_{i}")
        
        # List sessions
        sessions = server.list_sessions()
        
        assert len(sessions) == 3
        assert all("session_id" in s for s in sessions)
        assert all("name" in s for s in sessions)
        assert all("created_at" in s for s in sessions)
    
    def test_delete_session(self, temp_db):
        """Test deleting a saved session"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        server = PersistentSequentialThinking(db_path=temp_db)
        
        # Save a session
        thought = {
            "thought": "To be deleted",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        server.process_thought(thought)
        session_id = server.save_session("delete_me")
        
        # Verify it exists
        sessions = server.list_sessions()
        assert len(sessions) == 1
        
        # Delete it
        deleted = server.delete_session(session_id)
        assert deleted == True
        
        # Verify deleted
        sessions = server.list_sessions()
        assert len(sessions) == 0
    
    def test_auto_save_on_completion(self, temp_db):
        """Test auto-saving when thinking completes"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        server = PersistentSequentialThinking(
            db_path=temp_db,
            auto_save=True,
            session_name="auto_save_test"
        )
        
        # Process thoughts
        thought1 = {
            "thought": "Working through problem",
            "thoughtNumber": 1,
            "totalThoughts": 2,
            "nextThoughtNeeded": True
        }
        server.process_thought(thought1)
        
        # This should trigger auto-save
        thought2 = {
            "thought": "Final conclusion",
            "thoughtNumber": 2,
            "totalThoughts": 2,
            "nextThoughtNeeded": False
        }
        server.process_thought(thought2)
        
        # Check if auto-saved
        sessions = server.list_sessions()
        assert len(sessions) == 1
        assert sessions[0]["name"] == "auto_save_test"
    
    def test_search_sessions_by_content(self, temp_db):
        """Test searching sessions by thought content"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        server = PersistentSequentialThinking(db_path=temp_db)
        
        # Create sessions with different content
        server.reset()
        thought1 = {
            "thought": "Python programming concepts",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        server.process_thought(thought1)
        server.save_session("python_session")
        
        server.reset()
        thought2 = {
            "thought": "JavaScript async patterns",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        server.process_thought(thought2)
        server.save_session("js_session")
        
        # Search for Python content
        results = server.search_sessions("Python")
        assert len(results) == 1
        assert results[0]["name"] == "python_session"
        
        # Search for async
        results = server.search_sessions("async")
        assert len(results) == 1
        assert results[0]["name"] == "js_session"
    
    def test_session_versioning(self, temp_db):
        """Test version control for thought sessions"""
        from src.sequential_thinking_persistent import PersistentSequentialThinking
        
        server = PersistentSequentialThinking(db_path=temp_db)
        
        # Create initial version
        thought1 = {
            "thought": "Version 1 thought",
            "thoughtNumber": 1,
            "totalThoughts": 1,
            "nextThoughtNeeded": False
        }
        server.process_thought(thought1)
        session_id = server.save_session("versioned", create_version=True)
        
        # Modify and save new version
        thought2 = {
            "thought": "Version 2 thought",
            "thoughtNumber": 2,
            "totalThoughts": 2,
            "nextThoughtNeeded": False
        }
        server.process_thought(thought2)
        server.save_session_version(session_id, "Added second thought")
        
        # Get version history
        versions = server.get_session_versions(session_id)
        assert len(versions) == 2
        assert versions[0]["version_number"] == 1
        assert versions[1]["version_number"] == 2
        assert versions[1]["description"] == "Added second thought"
        
        # Load specific version
        server.load_session_version(session_id, version=1)
        history = server.get_thought_history()
        assert len(history) == 1
        assert history[0]["thought"] == "Version 1 thought"