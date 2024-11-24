from abc import ABC, abstractmethod
from airflow.models import DagBag


class IntegrityTester(ABC):
    """Abstract class for integrity test."""

    @abstractmethod
    def test_dag_loaded(self, dag_bag: DagBag) -> None:
        """Test if the DAG is correctly loaded."""
        pass

    @abstractmethod
    def test_task_count(self, dag_bag: DagBag) -> None:
        """Test the number of tasks in the DAG."""
        pass

    @abstractmethod
    def test_task_dependencies(self, dag_bag: DagBag) -> None:
        """Test the dependencies between the tasks."""
        pass
