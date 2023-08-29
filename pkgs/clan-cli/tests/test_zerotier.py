from clan_cli.zerotier import create_network


def test_create_network() -> None:
    network = create_network()
    assert network["networkid"]
