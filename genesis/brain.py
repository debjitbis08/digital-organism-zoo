"""
Evolvable brain structures for digital organisms.

This is a minimal, dependency-free scaffolding that gives us a concrete
BrainGenome representation and a very simple Brain forward pass. It is
intentionally lightweight so it can be integrated gradually into
genesis/evolution.py without adding heavy ML libraries.

Focus for now:
- Randomly initialize a tiny feed-forward topology (1 hidden layer)
- Mutate weights slightly
- Provide a deterministic forward() that maps numeric inputs to outputs

Future work (kept small on purpose):
- Add multiple hidden layers and topology mutations
- Encode/express sensors and actuators in the genome
- Replace the toy math with real NN ops or a NEAT-style system
"""

import random
from typing import Dict, List


class BrainGenome:
    """Genotype encoding brain architecture and parameters."""

    def __init__(self, data=None):
        # Minimal genome representation: one hidden layer MLP
        # Stored as simple lists of lists for easy JSON serialization.
        if data is None:
            # Will be filled by random() factory
            self.data = {}
        else:
            self.data = data

    @staticmethod
    def random():
        """Generate a random brain genome."""
        # Minimal default: input_dim=4, hidden_dim=6, output_dim=2
        in_dim, hid_dim, out_dim = 4, 6, 2
        def rand_matrix(rows, cols):
            return [[random.uniform(-1.0, 1.0) for _ in range(cols)] for _ in range(rows)]

        genome = {
            'topology': {'in': in_dim, 'hid': hid_dim, 'out': out_dim},
            'w1': rand_matrix(in_dim, hid_dim),   # input -> hidden
            'b1': [random.uniform(-0.1, 0.1) for _ in range(hid_dim)],
            'w2': rand_matrix(hid_dim, out_dim),  # hidden -> output
            'b2': [random.uniform(-0.1, 0.1) for _ in range(out_dim)],
            'activation': 'relu'
        }
        return BrainGenome(data=genome)

    def mutate(self):
        """Mutate genome to create variation in brain structure."""
        if not self.data:
            return
        # Small gaussian noise to a few randomly selected weights
        def perturb_matrix(m, rate=0.1, scale=0.05):
            for r in range(len(m)):
                for c in range(len(m[r])):
                    if random.random() < rate:
                        m[r][c] += random.uniform(-scale, scale)

        def perturb_vector(v, rate=0.1, scale=0.05):
            for i in range(len(v)):
                if random.random() < rate:
                    v[i] += random.uniform(-scale, scale)

        perturb_matrix(self.data.get('w1', []))
        perturb_vector(self.data.get('b1', []))
        perturb_matrix(self.data.get('w2', []))
        perturb_vector(self.data.get('b2', []))

    def to_dict(self):
        """Serialize genome for persistence."""
        return {'data': self.data}

    @staticmethod
    def from_dict(obj):
        """Reconstruct genome from serialized form."""
        return BrainGenome(data=obj.get('data'))


class Brain:
    """Phenotype: neural or computational substrate instantiated from a genome."""

    def __init__(self, genome: BrainGenome):
        self.genome = genome
        self.topology = genome.data.get('topology', {'in': 4, 'hid': 6, 'out': 2})
        self.w1 = genome.data.get('w1', [])
        self.b1 = genome.data.get('b1', [])
        self.w2 = genome.data.get('w2', [])
        self.b2 = genome.data.get('b2', [])
        self.activation = genome.data.get('activation', 'relu')

    def forward(self, inputs):
        """Process sensory inputs and produce motor commands or internal activations."""
        # Defensive: coerce inputs to fixed length expected by topology
        in_dim = self.topology.get('in', 4)
        vec = list(inputs)[:in_dim]
        if len(vec) < in_dim:
            vec += [0.0] * (in_dim - len(vec))

        # Basic MLP: h = act(x @ W1 + b1); y = h @ W2 + b2
        def dot_vec_mat(v: List[float], m: List[List[float]]) -> List[float]:
            if not m:
                return []
            cols = len(m[0])
            return [sum(v[r] * m[r][c] for r in range(len(v))) for c in range(cols)]

        def add_bias(v: List[float], b: List[float]) -> List[float]:
            return [(v[i] + (b[i] if i < len(b) else 0.0)) for i in range(len(v))]

        def relu(v: List[float]) -> List[float]:
            return [x if x > 0 else 0.0 for x in v]

        h = dot_vec_mat(vec, self.w1)
        h = add_bias(h, self.b1)
        if self.activation == 'relu':
            h = relu(h)
        y = dot_vec_mat(h, self.w2)
        y = add_bias(y, self.b2)
        return y
