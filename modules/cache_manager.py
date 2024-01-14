from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from agents.basic_agent import BasicAgent

def add_expire_instance(agent: BasicAgent, instance: object):
    """Adds an instance to the expire list in the cache manager."""
    agent.cache_manager[instance] = {}


def add_expire_function(agent: BasicAgent, instance, func: callable, max_count: int):
    """
    Adds a function to the expire list in the cache manager.
    The expire list is a list of functions that are called when the cache manager is full.
    The functions are called in order of the expire list, and the first function to return True is used.
    :param agent: The agent that owns the cache manager.
    :param instance: The instance of the function to add.
    :param func: The function to add.
    :param max_count: The maximum number of times the function can be called before it is removed.
    :return: None
    """
    agent.cache_manager[instance].update({func: {'max_count': max_count, 'count': 0}})


def update_my_functions(agent: BasicAgent, instance):
    """Gets the functions of an instance, that are added to the expire list."""
    for func in agent.cache_manager[instance]:
        agent.cache_manager[instance][func]['count'] += 1
        if agent.cache_manager[instance][func]['count'] >= agent.cache_manager[instance][func][
                'max_count']:
            func.cache_clear()
            agent.cache_manager[instance][func]['count'] = 0
