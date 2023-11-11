import deal

from clan_cli.task_manager import get_task


@deal.cases(get_task)
def test_get_task(case: deal.TestCase) -> None:
    case()
