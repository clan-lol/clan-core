import argparse
import importlib
import logging

from clan_cli.api import API
from clan_cli.completions import add_dynamic_completer, complete_machines
from clan_cli.machines.machines import Machine

from ._types import Generator, Prompt, StoreBase, Var

log = logging.getLogger(__name__)


def public_store(machine: Machine) -> StoreBase:
    public_vars_module = importlib.import_module(machine.public_vars_module)
    return public_vars_module.FactStore(machine=machine)


def secret_store(machine: Machine) -> StoreBase:
    secret_vars_module = importlib.import_module(machine.secret_vars_module)
    return secret_vars_module.SecretStore(machine=machine)


def get_vars(machine: Machine) -> list[Var]:
    pub_store = public_store(machine)
    sec_store = secret_store(machine)
    return pub_store.get_all() + sec_store.get_all()


def _get_prompt_value(
    machine: Machine, generator: Generator, prompt: Prompt
) -> str | None:
    if not prompt.has_file:
        return None
    pub_store = public_store(machine)
    if pub_store.exists(generator.name, prompt.name, shared=generator.share):
        return pub_store.get(
            generator.name, prompt.name, shared=generator.share
        ).decode()
    return None


@API.register
def get_prompts(machine: Machine) -> list[Generator]:
    generators = []
    for gen_name, generator in machine.vars_generators.items():
        prompts: list[Prompt] = []
        gen = Generator(
            name=gen_name,
            prompts=prompts,
            share=generator["share"],
        )
        for prompt_name, prompt in generator["prompts"].items():
            prompt = Prompt(
                name=prompt_name,
                description=prompt["description"],
                type=prompt["type"],
                has_file=prompt["createFile"],
                generator=gen_name,
            )
            prompt.previous_value = _get_prompt_value(machine, gen, prompt)
            prompts.append(prompt)

        generators.append(gen)
    return generators


def stringify_vars(_vars: list[Var]) -> str:
    return "\n".join([str(var) for var in _vars])


def stringify_all_vars(machine: Machine) -> str:
    return stringify_vars(get_vars(machine))


def list_command(args: argparse.Namespace) -> None:
    machine = Machine(name=args.machine, flake=args.flake)
    print(stringify_all_vars(machine))


def register_list_parser(parser: argparse.ArgumentParser) -> None:
    machines_arg = parser.add_argument(
        "machine",
        help="The machine to print vars for",
    )
    add_dynamic_completer(machines_arg, complete_machines)

    parser.set_defaults(func=list_command)
