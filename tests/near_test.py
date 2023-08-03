"""
NEAR Integration tests.
"""

import unittest
from neurosym.near.near_graph import near_graph
from neurosym.programs.s_expression import SExpression

from neurosym.search.bfs import bfs
from neurosym.search.bounded_astar import bounded_astar

from neurosym.examples.differentiable_arith import (
    differentiable_arith_dsl,
    float_type,
    list_float_type,
)
import torch

from neurosym.search_graph.metadata_computer import NoMetadataComputer


class TestNEAR(unittest.TestCase):
    def test_near_bfs(self):
        self.maxDiff = None
        dsl = differentiable_arith_dsl(10)
        g = near_graph(
            dsl,
            float_type,
            is_goal=lambda x: dsl.compute_on_pytorch(dsl.initialize(x.program)) == 4,
        )
        node = next(bfs(g)).program
        self.assertEqual(
            str(node),
            str(
                SExpression(
                    symbol="int_int_add",
                    children=(
                        SExpression(symbol="one", children=()),
                        SExpression(
                            symbol="int_int_add",
                            children=(
                                SExpression(symbol="one", children=()),
                                SExpression(
                                    symbol="int_int_add",
                                    children=(
                                        SExpression(symbol="one", children=()),
                                        SExpression(symbol="one", children=()),
                                    ),
                                ),
                            ),
                        ),
                    ),
                )
            ),
        )

    def test_near_astar(self):
        self.maxDiff = None
        input_size = 10
        dsl = differentiable_arith_dsl(input_size)
        fours = torch.full((input_size,), 4.0)

        def checker(x):
            x = x.program
            xx = dsl.compute_on_pytorch(dsl.initialize(x))
            if isinstance(xx, torch.Tensor):
                return torch.all(torch.eq(xx, fours))
            else:
                return False

        g = near_graph(dsl, list_float_type, is_goal=checker)

        cost = (
            lambda x: len(str(x.program.children[0]))
            if isinstance(x.program, SExpression) and x.program.children
            else 0
        )
        node = next(bounded_astar(g, cost, max_depth=7)).program
        self.assertEqual(
            node,
            SExpression(
                symbol="Tint_int_add",
                children=(
                    SExpression(symbol="ones", children=()),
                    SExpression(
                        symbol="int_int_add",
                        children=(
                            SExpression(
                                symbol="int_int_add",
                                children=(
                                    SExpression(symbol="one", children=()),
                                    SExpression(symbol="one", children=()),
                                ),
                            ),
                            SExpression(symbol="one", children=()),
                        ),
                    ),
                ),
            ),
        )