from .integrity_tester import IntegrityTester
from airflow.models import DagBag


class TestPSRSyncDAG(IntegrityTester):
    """Test the psr_sync DAG."""

    def test_dag_loaded(self, dag_psr_sync: DagBag) -> None:
        """Test if the DAG is correctly loaded."""
        assert DagBag().import_errors == {}, "Improper import"
        assert dag_psr_sync.id in DagBag().dags, f"DAG '{dag_psr_sync.id}' is missing"
        assert dag_psr_sync is not None, "DAG object is None"
        assert len(dag_psr_sync.tasks) > 0, "No tasks in the DAG"

    def test_dag_has_tag(self, dag_psr_sync: DagBag) -> None:
        """Test if the DAG contains the correct tag."""
        assert "half hourly" in dag_psr_sync.tags, "Tag 'half hourly' is missing in the DAG"

    def test_task_count(self, dag_psr_sync: DagBag) -> None:
        """Test the number of tasks in the DAG."""
        expected_task_count = 6
        assert len(dag_psr_sync.tasks) == expected_task_count, f"Expected 5 tasks, but got {len(dag_psr_sync.tasks)}"

    def test_task_dependencies(self, dag_psr_sync: DagBag) -> None:
        """Test the dependencies between the tasks."""
        # Define expected upstream and downstream dependencies
        task_deps = {
            "Processor.fetch": ["parameterize"],
            "Processor.validate": ["Processor.fetch"],
            "Processor.transform": ["Processor.validate"],
            "sync": ["Processor.transform"],
        }

        for task_id, upstream_ids in task_deps.items():
            task = dag_psr_sync.get_task(task_id)
            assert task is not None, f"Task '{task_id}' is missing in the DAG"
            upstream_tasks = [t.task_id for t in task.upstream_list]
            assert set(upstream_ids) == set(upstream_tasks), f"Task '{task_id}' has incorrect upstream dependencies"
