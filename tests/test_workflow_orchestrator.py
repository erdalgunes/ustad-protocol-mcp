"""Tests for workflow orchestrator with LangGraph state machine."""

from unittest.mock import patch

import pytest


class TestWorkflowState:
    """Tests for WorkflowState TypedDict structure."""

    def test_workflow_state_structure(self):
        """Test that WorkflowState has all required fields."""
        from src.workflow_orchestrator import WorkflowState

        # Create a valid state
        state: WorkflowState = {
            "intent": "test intent",
            "needs_verification": True,
            "facts_to_verify": ["fact1", "fact2"],
            "verification_results": {"fact1": "verified"},
            "thinking_steps": ["step1", "step2"],
            "execution_result": None,
        }

        assert state["intent"] == "test intent"
        assert state["needs_verification"] is True
        assert len(state["facts_to_verify"]) == 2
        assert state["verification_results"]["fact1"] == "verified"
        assert len(state["thinking_steps"]) == 2
        assert state["execution_result"] is None

    def test_workflow_state_thinking_steps_minimum(self):
        """Test that thinking steps enforces minimum 10 steps."""
        from src.workflow_orchestrator import validate_thinking_steps

        # Should raise error with less than 10 steps
        with pytest.raises(ValueError, match="Minimum 10 thinking steps required"):
            validate_thinking_steps(["step1", "step2", "step3"])

        # Should pass with 10 or more steps
        steps = [f"step{i}" for i in range(10)]
        assert validate_thinking_steps(steps) is True


class TestIntentState:
    """Tests for IntentState node."""

    @pytest.mark.asyncio
    async def test_analyze_intent(self):
        """Test that IntentState analyzes user intent correctly."""
        from src.workflow_orchestrator import analyze_intent

        state = {
            "intent": "Find information about LangGraph",
            "needs_verification": False,
            "facts_to_verify": [],
            "verification_results": {},
            "thinking_steps": [],
            "execution_result": None,
        }

        result = await analyze_intent(state)

        # Should add thinking steps
        assert len(result["thinking_steps"]) >= 10
        assert "Analyzing user intent" in result["thinking_steps"][0]

        # Should identify need for verification
        assert result["needs_verification"] is True
        assert "What is LangGraph?" in result["facts_to_verify"]

    @pytest.mark.asyncio
    async def test_analyze_intent_no_verification_needed(self):
        """Test intent analysis when no verification is needed."""
        from src.workflow_orchestrator import analyze_intent

        state = {
            "intent": "Calculate 2 + 2",
            "needs_verification": False,
            "facts_to_verify": [],
            "verification_results": {},
            "thinking_steps": [],
            "execution_result": None,
        }

        result = await analyze_intent(state)

        # Should still have thinking steps
        assert len(result["thinking_steps"]) >= 10

        # No verification needed for simple calculation
        assert result["needs_verification"] is False
        assert len(result["facts_to_verify"]) == 0


class TestVerifyState:
    """Tests for VerifyState node."""

    @pytest.mark.asyncio
    @patch("src.workflow_orchestrator.search_tavily")
    async def test_verify_facts(self, mock_search):
        """Test that VerifyState verifies facts using Tavily."""
        from src.workflow_orchestrator import verify_facts

        mock_search.return_value = {"answer": "LangGraph is a graph framework"}

        state = {
            "intent": "Find information about LangGraph",
            "needs_verification": True,
            "facts_to_verify": ["What is LangGraph?"],
            "verification_results": {},
            "thinking_steps": ["Step 1"] * 10,
            "execution_result": None,
        }

        result = await verify_facts(state)

        # Should add verification results
        assert "What is LangGraph?" in result["verification_results"]
        assert "LangGraph is a graph framework" in str(
            result["verification_results"]["What is LangGraph?"]
        )

        # Should call Tavily search
        mock_search.assert_called_once_with("What is LangGraph?")

    @pytest.mark.asyncio
    async def test_skip_verify_when_not_needed(self):
        """Test that verification is skipped when not needed."""
        from src.workflow_orchestrator import verify_facts

        state = {
            "intent": "Calculate 2 + 2",
            "needs_verification": False,
            "facts_to_verify": [],
            "verification_results": {},
            "thinking_steps": ["Step 1"] * 10,
            "execution_result": None,
        }

        result = await verify_facts(state)

        # Should not add any verification results
        assert len(result["verification_results"]) == 0


class TestExecuteState:
    """Tests for ExecuteState node."""

    @pytest.mark.asyncio
    async def test_execute_with_verification(self):
        """Test execution with verified facts."""
        from src.workflow_orchestrator import execute_task

        state = {
            "intent": "Find information about LangGraph",
            "needs_verification": True,
            "facts_to_verify": ["What is LangGraph?"],
            "verification_results": {"What is LangGraph?": "A graph framework for LLMs"},
            "thinking_steps": ["Step 1"] * 10,
            "execution_result": None,
        }

        result = await execute_task(state)

        # Should set execution result
        assert result["execution_result"] is not None
        # Execution result should be "Information processed" since verification result is a plain string
        assert result["execution_result"] == "Information processed"

    @pytest.mark.asyncio
    async def test_execute_without_verification(self):
        """Test execution without verification needed."""
        from src.workflow_orchestrator import execute_task

        state = {
            "intent": "Calculate 2 + 2",
            "needs_verification": False,
            "facts_to_verify": [],
            "verification_results": {},
            "thinking_steps": ["Step 1"] * 10,
            "execution_result": None,
        }

        result = await execute_task(state)

        # Should calculate result
        assert result["execution_result"] == 4


class TestStateTransitions:
    """Tests for state machine transitions."""

    @pytest.mark.asyncio
    async def test_full_workflow_with_verification(self):
        """Test complete workflow: Intent -> Verify -> Execute."""
        from src.workflow_orchestrator import create_workflow

        with patch("src.workflow_orchestrator.LANGGRAPH_AVAILABLE", new=True):
            workflow = create_workflow()

            initial_state = {
                "intent": "Tell me about Python decorators",
                "needs_verification": False,
                "facts_to_verify": [],
                "verification_results": {},
                "thinking_steps": [],
                "execution_result": None,
            }

            with patch("src.workflow_orchestrator.search_tavily") as mock_search:
                mock_search.return_value = {"answer": "Python decorators are functions"}

                result = await workflow.ainvoke(initial_state)

                # Should have completed all steps
                assert len(result["thinking_steps"]) >= 10
                assert result["needs_verification"] is True
                assert len(result["verification_results"]) > 0
                assert result["execution_result"] is not None

    @pytest.mark.asyncio
    async def test_workflow_without_verification(self):
        """Test workflow that skips verification: Intent -> Execute."""
        from src.workflow_orchestrator import create_workflow

        with patch("src.workflow_orchestrator.LANGGRAPH_AVAILABLE", new=True):
            workflow = create_workflow()

            initial_state = {
                "intent": "Calculate 5 * 7",
                "needs_verification": False,
                "facts_to_verify": [],
                "verification_results": {},
                "thinking_steps": [],
                "execution_result": None,
            }

            result = await workflow.ainvoke(initial_state)

            # Should skip verification
            assert len(result["thinking_steps"]) >= 10
            assert result["needs_verification"] is False
            assert len(result["verification_results"]) == 0
            assert result["execution_result"] == 35

    @pytest.mark.asyncio
    async def test_graceful_fallback_without_langgraph(self):
        """Test that system works without LangGraph installed."""
        from src.workflow_orchestrator import create_workflow

        with patch("src.workflow_orchestrator.LANGGRAPH_AVAILABLE", new=False):
            workflow = create_workflow()

            initial_state = {
                "intent": "Test fallback",
                "needs_verification": False,
                "facts_to_verify": [],
                "verification_results": {},
                "thinking_steps": [],
                "execution_result": None,
            }

            result = await workflow.ainvoke(initial_state)

            # Should use fallback implementation
            assert len(result["thinking_steps"]) >= 10
            assert result["execution_result"] is not None


class TestRetryLogic:
    """Tests for retry logic and error recovery."""

    @pytest.mark.asyncio
    async def test_retry_on_verification_failure(self):
        """Test retry logic when verification fails."""
        from src.workflow_orchestrator import verify_facts_with_retry

        with patch("src.workflow_orchestrator.search_tavily") as mock_search:
            # First call fails, second succeeds
            mock_search.side_effect = [
                Exception("Network error"),
                {"answer": "Success on retry"},
            ]

            state = {
                "intent": "Test retry",
                "needs_verification": True,
                "facts_to_verify": ["Test fact"],
                "verification_results": {},
                "thinking_steps": ["Step 1"] * 10,
                "execution_result": None,
            }

            result = await verify_facts_with_retry(state, max_retries=3)

            # Should succeed after retry
            assert "Test fact" in result["verification_results"]
            assert "Success on retry" in str(result["verification_results"]["Test fact"])
            assert mock_search.call_count == 2

    @pytest.mark.asyncio
    async def test_max_retries_exceeded(self):
        """Test behavior when max retries are exceeded."""
        from src.workflow_orchestrator import verify_facts_with_retry

        with patch("src.workflow_orchestrator.search_tavily") as mock_search:
            # All calls fail
            mock_search.side_effect = Exception("Persistent error")

            state = {
                "intent": "Test max retries",
                "needs_verification": True,
                "facts_to_verify": ["Test fact"],
                "verification_results": {},
                "thinking_steps": ["Step 1"] * 10,
                "execution_result": None,
            }

            result = await verify_facts_with_retry(state, max_retries=3)

            # Should record error in verification results
            assert "Test fact" in result["verification_results"]
            assert "Error" in str(result["verification_results"]["Test fact"])
            assert mock_search.call_count == 3

    @pytest.mark.asyncio
    async def test_state_persistence_for_debugging(self):
        """Test that state is persisted for debugging purposes."""
        from src.workflow_orchestrator import load_state, persist_state

        state = {
            "intent": "Debug test",
            "needs_verification": True,
            "facts_to_verify": ["fact1"],
            "verification_results": {"fact1": "verified"},
            "thinking_steps": ["step1"] * 10,
            "execution_result": "Result",
        }

        # Persist state
        state_id = await persist_state(state)
        assert state_id is not None

        # Load state
        loaded_state = await load_state(state_id)
        assert loaded_state["intent"] == "Debug test"
        assert loaded_state["verification_results"]["fact1"] == "verified"


class TestAntiHallucination:
    """Tests for anti-hallucination safeguards."""

    @pytest.mark.asyncio
    async def test_force_verification_for_facts(self):
        """Test that verification is forced when facts are detected."""
        from src.workflow_orchestrator import analyze_intent

        state = {
            "intent": "LangGraph was released in 2023",  # Contains factual claim
            "needs_verification": False,
            "facts_to_verify": [],
            "verification_results": {},
            "thinking_steps": [],
            "execution_result": None,
        }

        result = await analyze_intent(state)

        # Should force verification for factual claims
        assert result["needs_verification"] is True
        assert any("2023" in fact for fact in result["facts_to_verify"])

    @pytest.mark.asyncio
    async def test_cannot_skip_to_execute(self):
        """Test that execution cannot happen without verification when needed."""
        from src.workflow_orchestrator import execute_task

        state = {
            "intent": "Tell me about quantum computing",
            "needs_verification": True,
            "facts_to_verify": ["quantum computing facts"],
            "verification_results": {},  # Empty - not verified
            "thinking_steps": ["step1"] * 10,
            "execution_result": None,
        }

        with pytest.raises(ValueError, match="Cannot execute without verification"):
            await execute_task(state)

    @pytest.mark.asyncio
    async def test_audit_log_for_verifications(self):
        """Test that all verification attempts are logged for audit."""
        from src.workflow_orchestrator import get_verification_audit_log

        with patch("src.workflow_orchestrator.search_tavily") as mock_search:
            mock_search.return_value = {"answer": "Verified fact"}

            from src.workflow_orchestrator import verify_facts

            state = {
                "intent": "Test audit",
                "needs_verification": True,
                "facts_to_verify": ["audit fact"],
                "verification_results": {},
                "thinking_steps": ["step1"] * 10,
                "execution_result": None,
            }

            await verify_facts(state)

            # Check audit log
            audit_log = await get_verification_audit_log()
            assert len(audit_log) > 0
            assert any("audit fact" in entry["fact"] for entry in audit_log)
            assert any("Verified fact" in entry["result"] for entry in audit_log)
