from integrity_tester import IntegrityTester
from airflow.models import DagBag

class TestPowerDataSyncDAG(IntegrityTester):
    """Test the power_data_sync DAG."""

    def test_dag_loaded(self, power_data_sync_dag: DagBag) -> None:
        """Test if the DAG is correctly loaded."""
        assert DagBag().import_errors == {}, "Improper import"
        assert power_data_sync_dag.id in DagBag().dags, f"DAG '{power_data_sync_dag.id}' is missing"
        assert power_data_sync_dag is not None, "DAG object is None"
        assert len(power_data_sync_dag.tasks) > 0, "No tasks in the DAG"

    def test_dag_has_tag(self, power_data_sync_dag: DagBag) -> None:
        """Test if the DAG contains the correct tag."""
        assert "half hourly" in power_data_sync_dag.tags, "Tag 'half hourly' is missing in the DAG"

    def test_task_count(self, power_data_sync_dag: DagBag) -> None:
        """Test the number of tasks in the DAG."""
        expected_task_count = 7
        assert len(power_data_sync_dag.tasks) == expected_task_count, f"Expected 5 tasks, but got {len(power_data_sync_dag.tasks)}"

    def test_task_dependencies(self, power_data_sync_dag: DagBag) -> None:
        """Test the dependencies between the tasks."""
        # Define expected upstream and downstream dependencies
        task_deps = {
            "parameterize": ["table"],
            "fetch": ["parameterize"],
            "validate": ["fetch"],
            "transform": ["validate"],
            "sync": ["transform"],
        }

        for task_id, upstream_ids in task_deps.items():
            task = power_data_sync_dag.get_task(task_id)
            assert task is not None, f"Task '{task_id}' is missing in the DAG"
            upstream_tasks = [t.task_id for t in task.upstream_list]
            assert set(upstream_ids) == set(upstream_tasks), f"Task '{task_id}' has incorrect upstream dependencies"
