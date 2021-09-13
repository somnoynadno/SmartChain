import requests
import time

from uuid import uuid4


class Port:
    """A model representing a digital seaport (e.g. ESLCG001, A Coruna)."""
    def __init__(self, id: str, name: str, address: str):
        self.id = id
        self.name = name
        self.address = address
        self.balance = 100  # by default

    def serialize(self) -> {}:
        return {
            "id": self.id,
            "name": self.name,
            "address": self.address,
            "balance": self.balance,
        }


class SmartContract:
    """Executable part of blockchain, representing a contract between two ports."""
    def __init__(self, port_from: Port, port_to: Port, cost: int, id=None, timestamp=None, is_done=False, extra={}):
        self.uuid = id if id else str(uuid4())
        self.timestamp = timestamp if timestamp else int(time.time())
        self.port_from = port_from
        self.port_to = port_to
        self.cost = cost
        self.extra = extra
        self.is_done = is_done

    def serialize(self) -> {}:
        """Returns object with immutable fields for JSON transfer."""
        return {
            'uuid': self.uuid,
            'cost': self.cost,
            'timestamp': self.timestamp,
            'to_address': self.port_to.id,
            'from_address': self.port_from.id,
            'is_done': self.is_done,
        }

    def execute(self, to_address: str):
        """Interface to run a contract specification."""
        if self.is_done:
            raise SmartContractException("already done")

        if not self.is_contract_done():
            raise SmartContractException("not done yet")

        self.port_from.balance += self.cost
        self.port_to.balance -= self.cost
        self.is_done = True

    def is_contract_done(self) -> bool:
        """Makes request to an oracle to check if this contract is fulfilled."""
        r = requests.get(f'{self.port_to.address}/contract/{self.uuid}/is_done')
        if r.status_code == 200:
            return True

        return False


class SmartContractException(Exception):
    """Any kind of error in SmartContract execution process."""
    def __init__(self, message):
        super().__init__(message)
