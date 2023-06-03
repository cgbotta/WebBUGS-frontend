import unittest
from mermaid_to_bugs import translate_v2

class TestStringMethods(unittest.TestCase):

    def test_1(self):

        self.assertEqual(translate_v2("Node1 = 0.5\nNode2 = 20\nNode3 = binomial(Node1, Node2)\nNode4 = step(Y - 14.5)"), "model {\nNode1 <- 0.5\nNode2 <- 20.0\nNode3 <- dbin(0.5,20.0)\nNode4 <- step(Node3 - 14.5)\n}")

if __name__ == '__main__':
    unittest.main()