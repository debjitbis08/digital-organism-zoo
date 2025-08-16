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

# Allowed sensor/actuator genes
DEFAULT_SENSORS = [
    'energy', 'frustration', 'memory_load', 'scarcity', 'age', 'capability_density'
]
DEFAULT_ACTUATORS = [
    'explore', 'social', 'conserve', 'prefer_structured', 'risk'
]


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
        # Default topology aligned with current organism inputs/outputs
        sensors = list(DEFAULT_SENSORS)
        actuators = list(DEFAULT_ACTUATORS)
        in_dim, hid_dim, out_dim = len(sensors), 6, len(actuators)
        def rand_matrix(rows, cols):
            return [[random.uniform(-1.0, 1.0) for _ in range(cols)] for _ in range(rows)]

        genome = {
            'topology': {'in': in_dim, 'hid': hid_dim, 'out': out_dim},
            'w1': rand_matrix(in_dim, hid_dim),   # input -> hidden
            'b1': [random.uniform(-0.1, 0.1) for _ in range(hid_dim)],
            'w2': rand_matrix(hid_dim, out_dim),  # hidden -> output
            'b2': [random.uniform(-0.1, 0.1) for _ in range(out_dim)],
            'activation': 'relu',
            'sensors': sensors,
            'actuators': actuators
        }
        return BrainGenome(data=genome)

    def mutate(self):
        """Mutate genome to create variation in brain structure and weights."""
        if not self.data:
            return

        topo = self.data.get('topology', {'in': 6, 'hid': 6, 'out': 3})
        in_dim, hid_dim, out_dim = topo.get('in', 6), topo.get('hid', 6), topo.get('out', 3)

        # 1) Occasionally mutate hidden size (topology mutation)
        if random.random() < 0.15:
            new_hid = max(2, min(12, hid_dim + random.choice([-1, 1])))
            if new_hid != hid_dim:
                self._resize_hidden(new_hid)
                self.data['topology']['hid'] = new_hid
                hid_dim = new_hid

        # 1b) Occasionally mutate sensors (inputs)
        if random.random() < 0.08:
            sensors = self.data.get('sensors', list(DEFAULT_SENSORS))
            # Try add or remove with equal chance
            if random.random() < 0.5 and len(sensors) > 3:
                # remove last
                sensors = sensors[:-1]
            else:
                # add one if available
                candidates = [s for s in DEFAULT_SENSORS if s not in sensors]
                if candidates:
                    sensors.append(random.choice(candidates))
            new_in = len(sensors)
            if new_in != in_dim:
                self._resize_inputs(new_in)
                self.data['topology']['in'] = new_in
                self.data['sensors'] = sensors
                in_dim = new_in

        # 1c) Occasionally mutate actuators (outputs)
        if random.random() < 0.08:
            actuators = self.data.get('actuators', list(DEFAULT_ACTUATORS))
            if random.random() < 0.5 and len(actuators) > 3:
                actuators = actuators[:-1]
            else:
                candidates = [a for a in DEFAULT_ACTUATORS if a not in actuators]
                if candidates:
                    actuators.append(random.choice(candidates))
            new_out = len(actuators)
            if new_out != out_dim:
                self._resize_outputs(new_out)
                self.data['topology']['out'] = new_out
                self.data['actuators'] = actuators
                out_dim = new_out

        # 2) Small noise on existing weights/biases
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

    def _resize_hidden(self, new_hid: int):
        """Resize hidden layer while preserving as much structure as possible."""
        topo = self.data.get('topology', {'in': 4, 'hid': 6, 'out': 2})
        in_dim, hid_dim, out_dim = topo.get('in', 4), topo.get('hid', 6), topo.get('out', 2)

        w1 = self.data.get('w1', [])  # in_dim x hid_dim
        b1 = self.data.get('b1', [])  # hid_dim
        w2 = self.data.get('w2', [])  # hid_dim x out_dim
        b2 = self.data.get('b2', [])  # out_dim

        # Helper to create random values
        def rand_row(n):
            return [random.uniform(-1.0, 1.0) for _ in range(n)]

        # Adjust w1 (columns)
        if new_hid > hid_dim:
            add = new_hid - hid_dim
            for r in range(len(w1)):
                w1[r].extend([random.uniform(-1.0, 1.0) for _ in range(add)])
            b1.extend([random.uniform(-0.1, 0.1) for _ in range(add)])
            # Expand w2 rows
            for _ in range(add):
                w2.append(rand_row(len(b2) if b2 else out_dim))
        elif new_hid < hid_dim:
            trim = hid_dim - new_hid
            # Trim from the end
            for r in range(len(w1)):
                w1[r] = w1[r][:new_hid]
            b1 = b1[:new_hid]
            w2 = w2[:new_hid]

        self.data['w1'] = w1
        self.data['b1'] = b1
        self.data['w2'] = w2
        self.data['b2'] = b2

    def _resize_inputs(self, new_in: int):
        topo = self.data.get('topology', {'in': 6, 'hid': 6, 'out': 3})
        in_dim, hid_dim = topo.get('in', 6), topo.get('hid', 6)
        w1 = self.data.get('w1', [])  # in_dim x hid_dim

        if new_in > in_dim:
            add = new_in - in_dim
            for _ in range(add):
                w1.append([random.uniform(-1.0, 1.0) for _ in range(hid_dim)])
        elif new_in < in_dim:
            trim = in_dim - new_in
            w1 = w1[:new_in]
        self.data['w1'] = w1

    def _resize_outputs(self, new_out: int):
        topo = self.data.get('topology', {'in': 6, 'hid': 6, 'out': 3})
        hid_dim, out_dim = topo.get('hid', 6), topo.get('out', 3)
        w2 = self.data.get('w2', [])  # hid_dim x out_dim
        b2 = self.data.get('b2', [])
        if new_out > out_dim:
            add = new_out - out_dim
            for r in range(len(w2)):
                w2[r].extend([random.uniform(-1.0, 1.0) for _ in range(add)])
            b2.extend([random.uniform(-0.1, 0.1) for _ in range(add)])
        elif new_out < out_dim:
            for r in range(len(w2)):
                w2[r] = w2[r][:new_out]
            b2 = b2[:new_out]
        self.data['w2'] = w2
        self.data['b2'] = b2

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
        self.topology = genome.data.get('topology', {'in': 6, 'hid': 6, 'out': 3})
        self.w1 = genome.data.get('w1', [])
        self.b1 = genome.data.get('b1', [])
        self.w2 = genome.data.get('w2', [])
        self.b2 = genome.data.get('b2', [])
        self.activation = genome.data.get('activation', 'relu')
        self.sensors = genome.data.get('sensors', list(DEFAULT_SENSORS))
        self.actuators = genome.data.get('actuators', list(DEFAULT_ACTUATORS))

    def forward(self, inputs):
        """Process sensory inputs and produce motor commands or internal activations."""
        # Defensive: coerce inputs to fixed length expected by topology
        in_dim = self.topology.get('in', 6)
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
