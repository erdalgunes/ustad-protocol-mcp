#!/usr/bin/env python3
"""CLI Inspector for Sequential Thinking MCP Server.

Provides an interactive testing interface for validating MCP server functionality
using Python best practices including type hints, dataclasses, and SOLID principles.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, IntEnum
from typing import Any, Protocol

from sequential_thinking import SequentialThinkingServer


@dataclass
class TestResult:
    """Represents a single test result."""

    test_name: str
    status: str  # 'passed' or 'failed'
    result: dict[str, Any] | None = None
    error: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


class TestStatus(Enum):
    """Test status enumeration."""

    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"


class MenuChoice(IntEnum):
    """Menu choice enumeration."""

    EXIT = 0
    TEST_BASIC = 1
    TEST_REVISION = 2
    TEST_BRANCHING = 3
    TEST_ERROR_HANDLING = 4
    RUN_FULL_SUITE = 5
    INTERACTIVE = 6
    VIEW_SESSION = 7
    RESET_SESSION = 8
    VIEW_RESULTS = 9


class ColorCode(Enum):
    """ANSI color codes for terminal output."""

    GREEN = "\033[92m"
    RED = "\033[91m"
    RESET = "\033[0m"
    BLUE = "\033[94m"
    YELLOW = "\033[93m"


class ThoughtProcessor(Protocol):
    """Protocol for thought processing."""

    def process_thought(self, data: dict[str, Any]) -> dict[str, Any]: ...
    def reset(self) -> None: ...
    def get_summary(self) -> dict[str, Any]: ...
    def get_thought_history(self) -> list[dict[str, Any]]: ...
    def get_branches(self) -> dict[str, Any]: ...


class CLIInspector:
    """Interactive CLI for testing sequential thinking server.

    Attributes:
        server: The sequential thinking server instance
        session_start: Timestamp when the session started
        test_results: List of test results from this session
    """

    def __init__(self, server: ThoughtProcessor | None = None) -> None:
        """Initialize the CLI inspector.

        Args:
            server: Optional custom server instance for testing
        """
        self.server: ThoughtProcessor = server or SequentialThinkingServer()
        self.session_start: datetime = datetime.now()
        self.test_results: list[TestResult] = []

    def print_header(self) -> None:
        """Display the inspector header with session information."""
        header_width = 60
        print(f"\n{'=' * header_width}")
        print("🔍 Sequential Thinking MCP Inspector")
        print(f"{'=' * header_width}")
        print("Interactive testing interface for MCP server validation")
        print(f"Session started: {self.session_start:%Y-%m-%d %H:%M:%S}")
        print(f"{'-' * header_width}\n")

    def print_menu(self) -> None:
        """Display the main menu options."""
        menu_items = [
            (MenuChoice.TEST_BASIC, "Test Basic Thought Processing"),
            (MenuChoice.TEST_REVISION, "Test Revision Functionality"),
            (MenuChoice.TEST_BRANCHING, "Test Branching"),
            (MenuChoice.TEST_ERROR_HANDLING, "Test Error Handling"),
            (MenuChoice.RUN_FULL_SUITE, "Run Full Test Suite"),
            (MenuChoice.INTERACTIVE, "Interactive Thought Entry"),
            (MenuChoice.VIEW_SESSION, "View Current Session"),
            (MenuChoice.RESET_SESSION, "Reset Session"),
            (MenuChoice.VIEW_RESULTS, "View Test Results"),
            (MenuChoice.EXIT, "Exit"),
        ]

        print("\n📋 Available Commands:")
        print("-" * 40)
        for choice, description in menu_items:
            print(f"{choice.value}. {description}")
        print("-" * 40)

    def test_basic_thought(self) -> TestResult:
        """Test basic thought processing functionality.

        Returns:
            TestResult containing the test outcome
        """
        print("\n🧪 Testing Basic Thought Processing...")

        test_data = {
            "thought": "Testing basic sequential thinking",
            "thoughtNumber": 1,
            "totalThoughts": 3,
            "nextThoughtNeeded": True,
        }

        try:
            result = self.server.process_thought(test_data)
            self._print_colored("✅ Basic thought processing: PASSED", ColorCode.GREEN)
            return TestResult(
                test_name="basic_thought", status=TestStatus.PASSED.value, result=result
            )
        except Exception as e:
            self._print_colored(f"❌ Basic thought processing: FAILED - {e}", ColorCode.RED)
            return TestResult(
                test_name="basic_thought", status=TestStatus.FAILED.value, error=str(e)
            )

    def test_revision(self) -> TestResult:
        """Test revision functionality.

        Returns:
            TestResult containing the test outcome
        """
        print("\n🧪 Testing Revision Functionality...")

        # Setup: Add initial thought
        initial_thought_data = self._create_thought_data(
            thought="Initial thought to revise",
            thought_number=1,
            total_thoughts=2,
            next_needed=True,
        )
        self.server.process_thought(initial_thought_data)

        # Test: Revise the thought
        revision_data = self._create_thought_data(
            thought="Revising the initial thought",
            thought_number=2,
            total_thoughts=2,
            next_needed=False,
            is_revision=True,
            revises_thought=1,
        )

        try:
            result = self.server.process_thought(revision_data)
            self._print_colored("✅ Revision functionality: PASSED", ColorCode.GREEN)
            return TestResult(test_name="revision", status=TestStatus.PASSED.value, result=result)
        except Exception as e:
            self._print_colored(f"❌ Revision functionality: FAILED - {e}", ColorCode.RED)
            return TestResult(test_name="revision", status=TestStatus.FAILED.value, error=str(e))

    def test_branching(self) -> TestResult:
        """Test branching functionality.

        Returns:
            TestResult containing the test outcome
        """
        print("\n🧪 Testing Branching Functionality...")

        # Setup: Create main thought
        main_thought_data = self._create_thought_data(
            thought="Main path thought", thought_number=1, total_thoughts=3, next_needed=True
        )
        self.server.process_thought(main_thought_data)

        # Test: Create branch
        branch_data = self._create_thought_data(
            thought="Branching to explore alternative",
            thought_number=2,
            total_thoughts=3,
            next_needed=True,
            branch_from=1,
            branch_id="test-branch",
        )

        try:
            result = self.server.process_thought(branch_data)
            branches = self.server.get_branches()

            if "test-branch" not in branches:
                raise ValueError("Branch not created properly")

            self._print_colored("✅ Branching functionality: PASSED", ColorCode.GREEN)
            return TestResult(test_name="branching", status=TestStatus.PASSED.value, result=result)
        except Exception as e:
            self._print_colored(f"❌ Branching functionality: FAILED - {e}", ColorCode.RED)
            return TestResult(test_name="branching", status=TestStatus.FAILED.value, error=str(e))

    def test_error_handling(self) -> TestResult:
        """Test error handling for various edge cases.

        Returns:
            TestResult containing the test outcome
        """
        print("\n🧪 Testing Error Handling...")

        error_tests = [
            ("empty_thought", self._test_empty_thought_error),
            ("invalid_number", self._test_invalid_thought_number_error),
            ("invalid_revision", self._test_invalid_revision_error),
        ]

        errors_caught = []
        for test_name, test_func in error_tests:
            try:
                errors_caught.append(test_func())
            except Exception:
                errors_caught.append(False)

        passed_count = sum(errors_caught)
        total_count = len(errors_caught)

        if all(errors_caught):
            self._print_colored(
                f"✅ Error handling: PASSED ({passed_count}/{total_count} errors caught)",
                ColorCode.GREEN,
            )
            return TestResult(
                test_name="error_handling",
                status=TestStatus.PASSED.value,
                result={"errors_caught": passed_count},
            )
        self._print_colored(
            f"❌ Error handling: FAILED ({passed_count}/{total_count} errors caught)", ColorCode.RED
        )
        return TestResult(
            test_name="error_handling",
            status=TestStatus.FAILED.value,
            result={"errors_caught": passed_count},
        )

    def run_full_suite(self) -> None:
        """Execute the complete test suite."""
        print("\n🚀 Running Full Test Suite...")
        print("=" * 60)

        test_methods = [
            self.test_basic_thought,
            self.test_revision,
            self.test_branching,
            self.test_error_handling,
        ]

        results: list[TestResult] = []
        for test_method in test_methods:
            self.server.reset()
            results.append(test_method())

        # Calculate summary
        passed = sum(1 for r in results if r.status == TestStatus.PASSED.value)
        total = len(results)

        self._display_test_summary(passed, total)
        self.test_results.extend(results)

    def interactive_thought(self):
        """Interactive thought entry mode"""
        print("\n💭 Interactive Thought Entry")
        print("Enter 'back' to return to main menu")
        print("-" * 40)

        while True:
            try:
                thought = input("\nEnter thought: ").strip()
                if thought.lower() == "back":
                    break

                thought_num = int(input("Thought number: "))
                total = int(input("Total thoughts: "))
                next_needed = input("More thoughts needed? (y/n): ").lower() == "y"

                # Optional fields
                is_revision = input("Is this a revision? (y/n): ").lower() == "y"
                revises = None
                if is_revision:
                    revises = int(input("Which thought to revise: "))

                result = self.server.process_thought(
                    {
                        "thought": thought,
                        "thoughtNumber": thought_num,
                        "totalThoughts": total,
                        "nextThoughtNeeded": next_needed,
                        "isRevision": is_revision,
                        "revisesThought": revises,
                    }
                )

                self.print_success("✅ Thought processed successfully")
                print(json.dumps(result, indent=2))

            except ValueError as e:
                self.print_error(f"❌ Error: {e}")
            except KeyboardInterrupt:
                break

    def view_session(self):
        """View current session state"""
        print("\n📖 Current Session State")
        print("-" * 40)

        summary = self.server.get_summary()
        history = self.server.get_thought_history()
        branches = self.server.get_branches()

        print(f"Total thoughts: {summary['total_thoughts']}")
        print(f"Branches created: {summary['branches_created']}")
        print(f"Revisions made: {summary['revisions_made']}")
        print(f"Session complete: {summary['is_complete']}")

        if history:
            print("\n📝 Thought History:")
            for thought in history[-5:]:  # Show last 5 thoughts
                print(
                    f"  [{thought['thoughtNumber']}/{thought['totalThoughts']}] {thought['thought'][:50]}..."
                )

        if branches:
            print(f"\n🌿 Active Branches: {list(branches.keys())}")

    def view_test_results(self):
        """View test results from this session"""
        print("\n📊 Test Results Summary")
        print("-" * 40)

        if not self.test_results:
            print("No tests run yet in this session")
            return

        for result in self.test_results:
            status = "✅" if result["status"] == "passed" else "❌"
            print(f"{status} {result['test']}: {result['status'].upper()}")

    def _print_colored(self, message: str, color: ColorCode) -> None:
        """Print message with specified color.

        Args:
            message: The message to print
            color: The color code to use
        """
        print(f"{color.value}{message}{ColorCode.RESET.value}")

    def print_success(self, message: str) -> None:
        """Print success message in green.

        Args:
            message: The success message to display
        """
        self._print_colored(message, ColorCode.GREEN)

    def print_error(self, message: str) -> None:
        """Print error message in red.

        Args:
            message: The error message to display
        """
        self._print_colored(message, ColorCode.RED)

    def run(self):
        """Main run loop"""
        self.print_header()

        while True:
            self.print_menu()

            try:
                choice = input("\n👉 Enter command (0-9): ").strip()

                if choice == "0":
                    print("\n👋 Goodbye!")
                    break
                if choice == "1":
                    self.test_basic_thought()
                elif choice == "2":
                    self.test_revision()
                elif choice == "3":
                    self.test_branching()
                elif choice == "4":
                    self.test_error_handling()
                elif choice == "5":
                    self.run_full_suite()
                elif choice == "6":
                    self.interactive_thought()
                elif choice == "7":
                    self.view_session()
                elif choice == "8":
                    self.server.reset()
                    self.print_success("✅ Session reset")
                elif choice == "9":
                    self.view_test_results()
                else:
                    self.print_error("Invalid choice. Please enter 0-9.")

            except KeyboardInterrupt:
                print("\n\n👋 Interrupted. Goodbye!")
                break
            except Exception as e:
                self.print_error(f"Error: {e}")


def main():
    """Main entry point"""
    inspector = CLIInspector()
    inspector.run()


if __name__ == "__main__":
    main()
