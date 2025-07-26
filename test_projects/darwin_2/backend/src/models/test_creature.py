from backend.src.models.creature import Brain, Creature, Muscle, Node

def test_create_creature():
    nodes = [Node(id=0, position=(0, 0)), Node(id=1, position=(1, 1))]
    muscles = [Muscle(id=0, nodes=(0, 1), length=1.414, stiffness=100.0)]
    brain = Brain(weights=[0.1, -0.2, 0.3])
    creature = Creature(id=1, nodes=nodes, muscles=muscles, brain=brain, fitness=10.5)

    assert creature.id == 1
    assert len(creature.nodes) == 2
    assert creature.nodes[1].position == (1, 1)
    assert len(creature.muscles) == 1
    assert creature.muscles[0].nodes == (0, 1)
    assert creature.brain.weights[2] == 0.3
    assert creature.fitness == 10.5
