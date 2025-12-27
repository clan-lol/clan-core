import logging

from clan_cli.vars.list import get_machine_vars

from clan_lib.errors import ClanError
from clan_lib.machines.machines import Machine
from clan_lib.vars.generator import Var

log = logging.getLogger(__name__)


class VarNotFoundError(ClanError):
    pass


def get_machine_var(machine: Machine, var_id: str) -> Var:
    log.debug(f"getting var: {var_id} from machine: {machine.name}")
    vars_ = get_machine_vars(machine)
    results = []
    for var in vars_:
        if var.id == var_id:
            # exact match
            results = [var]
            break
        if var.id.startswith(var_id):
            results.append(var)
    if len(results) == 0:
        msg = f"Couldn't find var: {var_id} for machine: {machine.name}"
        raise VarNotFoundError(msg)
    if len(results) > 1:
        error = (
            f"Found multiple vars in {machine.name} for {var_id}:\n  - "
            + "\n  - ".join(
                [str(var) for var in results],
            )
        )
        raise ClanError(error)
    # we have exactly one result at this point
    var = results[0]
    if var_id == var.id:
        return var
    msg = f"Did you mean: {var.id}"
    raise ClanError(msg)
