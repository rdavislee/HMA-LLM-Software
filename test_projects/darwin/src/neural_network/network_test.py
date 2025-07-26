import pytest
import numpy as np
import copy
from src.neural_network.network import Network

# Test partitions for Network.predict():
# 1. Normal Functionality:
#    - Single hidden layer network with various input values.
#    - Multi-hidden layer network with various input values.
#    - Networks with different numbers of neurons per layer.
#    - Known weights and biases, with expected outputs calculated manually for verification.
# 2. Input Edge Cases:
#    - All zero sensor inputs.
#    - Sensor inputs leading to very small/large `z` values (to test sigmoid/tanh behavior at extremes).
# 3. Error Handling:
#    - sensor_inputs is not a numpy array (TypeError).
#    - sensor_inputs is not 1D (ValueError).
#    - sensor_inputs size mismatches the expected input size of the first layer (ValueError).

class TestNetworkPredict:

    def test_predict_single_layer_network_simple(self):
        # Covers: Normal Functionality - Single hidden layer, known weights
        # Network: 2 inputs, 1 output (no hidden layers, just input to output)
        weights = [np.array([[0.5, 0.3]])]  # shape (1, 2)
        biases = [np.array([0.1])]          # shape (1,)
        network = Network(2, 1, [], weights=weights, biases=biases)

        sensor_inputs = np.array([1.0, 2.0]) # 1*0.5 + 2*0.3 + 0.1 = 0.5 + 0.6 + 0.1 = 1.2
        # Output layer uses sigmoid: 1 / (1 + exp(-1.2))
        expected_output = 1 / (1 + np.exp(-1.2))
        
        output = network.predict(sensor_inputs)
        assert np.isclose(output[0], expected_output)

    def test_predict_single_hidden_layer_network(self):
        # Covers: Normal Functionality - Single hidden layer, known weights
        # Network: 2 inputs, 2 hidden neurons, 1 output
        # Hidden layer weights (2,2), biases (2,)
        w1 = np.array([[0.1, 0.2],
                       [0.3, 0.4]])
        b1 = np.array([0.05, -0.05])

        # Output layer weights (1,2), biases (1,)
        w2 = np.array([[0.5, 0.6]])
        b2 = np.array([0.1])

        weights = [w1, w2]
        biases = [b1, b2]
        network = Network(2, 1, [2], weights=weights, biases=biases)

        sensor_inputs = np.array([1.0, 1.0])

        # Expected calculations:
        # Hidden layer (tanh activation):
        # z1 = (1*0.1 + 1*0.2) + 0.05 = 0.3 + 0.05 = 0.35
        # z2 = (1*0.3 + 1*0.4) - 0.05 = 0.7 - 0.05 = 0.65
        # activations_hidden = [tanh(0.35), tanh(0.65)]
        activations_hidden = np.array([np.tanh(0.35), np.tanh(0.65)])

        # Output layer (sigmoid activation):
        # z_out = (activations_hidden[0]*0.5 + activations_hidden[1]*0.6) + 0.1
        # expected_output = 1 / (1 + exp(-z_out))
        z_out = np.dot(w2, activations_hidden) + b2
        expected_output = 1 / (1 + np.exp(-z_out))

        output = network.predict(sensor_inputs)
        assert np.allclose(output, expected_output)

    def test_predict_multi_hidden_layer_network(self):
        # Covers: Normal Functionality - Multi-hidden layer, known weights
        # Network: 2 inputs, 2 hidden neurons (L1), 1 hidden neuron (L2), 1 output
        w1 = np.array([[0.1, 0.2], [0.3, 0.4]]) # (2,2)
        b1 = np.array([0.05, -0.05]) # (2,)

        w2 = np.array([[0.5, 0.6]]) # (1,2)
        b2 = np.array([0.1]) # (1,)

        w3 = np.array([[0.7]]) # (1,1)
        b3 = np.array([0.0]) # (1,)

        weights = [w1, w2, w3]
        biases = [b1, b2, b3]
        network = Network(2, 1, [2, 1], weights=weights, biases=biases)

        sensor_inputs = np.array([0.5, 0.5])

        # Expected calculations:
        # Layer 1 (tanh):
        # z_l1_0 = (0.5*0.1 + 0.5*0.2) + 0.05 = 0.05 + 0.1 + 0.05 = 0.2
        # z_l1_1 = (0.5*0.3 + 0.5*0.4) - 0.05 = 0.15 + 0.2 - 0.05 = 0.3
        activations_l1 = np.array([np.tanh(0.2), np.tanh(0.3)])

        # Layer 2 (tanh):
        # z_l2_0 = (activations_l1[0]*0.5 + activations_l1[1]*0.6) + 0.1
        activations_l2 = np.tanh(np.dot(w2, activations_l1) + b2)

        # Output Layer (sigmoid):
        # z_out = (activations_l2[0]*0.7) + 0.0
        expected_output = 1 / (1 + np.exp(-(np.dot(w3, activations_l2) + b3)))

        output = network.predict(sensor_inputs)
        assert np.allclose(output, expected_output)

    def test_predict_zero_inputs(self):
        # Covers: Input Edge Cases - All zero sensor inputs
        w1 = np.array([[0.1, 0.2], [0.3, 0.4]])
        b1 = np.array([0.05, -0.05])
        w2 = np.array([[0.5, 0.6]])
        b2 = np.array([0.1])
        network = Network(2, 1, [2], weights=[w1, w2], biases=[b1, b2])

        sensor_inputs = np.array([0.0, 0.0])

        # Expected calculations with zero inputs:
        # Hidden layer (tanh activation):
        # z1 = (0*0.1 + 0*0.2) + 0.05 = 0.05
        # z2 = (0*0.3 + 0*0.4) - 0.05 = -0.05
        # activations_hidden = [np.tanh(0.05), np.tanh(-0.05)]
        activations_hidden = np.array([np.tanh(0.05), np.tanh(-0.05)])

        # Output layer (sigmoid activation):
        # z_out = (activations_hidden[0]*0.5 + activations_hidden[1]*0.6) + 0.1
        z_out = np.dot(w2, activations_hidden) + b2
        expected_output = 1 / (1 + np.exp(-z_out))

        output = network.predict(sensor_inputs)
        assert np.allclose(output, expected_output)

    def test_predict_inputs_leading_to_extreme_activations(self):
        # Covers: Input Edge Cases - Inputs leading to very small/large `z` values
        # Network: 1 input, 1 hidden, 1 output
        w1 = np.array([[100.0]]) # (1,1)
        b1 = np.array([0.0]) # (1,)
        w2 = np.array([[100.0]]) # (1,1)
        b2 = np.array([0.0]) # (1,)
        network = Network(1, 1, [1], weights=[w1, w2], biases=[b1, b2])

        # Test large positive input
        sensor_inputs_pos = np.array([1.0])
        # Hidden: tanh(100) -> approx 1.0
        # Output: sigmoid(100) -> approx 1.0
        output_pos = network.predict(sensor_inputs_pos)
        assert np.isclose(output_pos[0], 1.0, atol=1e-5) # atol for sigmoid near 1

        # Test large negative input
        sensor_inputs_neg = np.array([-1.0])
        # Hidden: tanh(-100) -> approx -1.0
        # Output: sigmoid(-100) -> approx 0.0
        output_neg = network.predict(sensor_inputs_neg)
        assert np.isclose(output_neg[0], 0.0, atol=1e-5) # atol for sigmoid near 0

    def test_predict_type_error_sensor_inputs_not_ndarray(self):
        # Covers: Error Handling - sensor_inputs is not a numpy array
        network = Network(1, 1, [], weights=[np.array([[1.0]])], biases=[np.array([0.0])])
        with pytest.raises(TypeError, match="Sensor inputs must be a numpy array."):
            network.predict([1.0]) # Pass a list instead of ndarray

    def test_predict_value_error_sensor_inputs_not_1d(self):
        # Covers: Error Handling - sensor_inputs is not 1D
        network = Network(1, 1, [], weights=[np.array([[1.0]])], biases=[np.array([0.0])])
        with pytest.raises(ValueError, match="Sensor inputs must be a 1D numpy array."):
            network.predict(np.array([[1.0]])) # Pass 2D array

    def test_predict_value_error_sensor_inputs_size_mismatch(self):
        # Covers: Error Handling - sensor_inputs size mismatches
        network = Network(2, 1, [], weights=[np.array([[0.5, 0.3]])], biases=[np.array([0.1])]) # Expects 2 inputs
        with pytest.raises(ValueError, match="Input size mismatch: expected 2 inputs, got 1."):
            network.predict(np.array([1.0])) # Pass 1 input

        network = Network(2, 1, [], weights=[np.array([[0.5, 0.3]])], biases=[np.array([0.1])]) # Expects 2 inputs
        with pytest.raises(ValueError, match="Input size mismatch: expected 2 inputs, got 3."):
            network.predict(np.array([1.0, 2.0, 3.0])) # Pass 3 inputs


class TestNetworkMethods:
    # Test partitions for Network methods:
    # - get_weights/get_biases:
    #   - Returns deep copy, not reference.
    #   - Returns correct values.
    # - set_weights/set_biases:
    #   - Correctly sets new values.
    #   - Raises TypeError for non-list/non-ndarray input.
    #   - Raises ValueError for shape/length mismatch.
    # - clone:
    #   - Creates an independent copy.
    #   - Copy has identical architecture and parameters.

    @pytest.fixture
    def sample_network(self):
        input_size = 3
        output_size = 2
        hidden_layer_sizes = [4, 5]
        # Create a network with random weights/biases for testing
        return Network(input_size, output_size, hidden_layer_sizes)

    def test_get_weights_returns_deep_copy(self, sample_network):
        original_weights = sample_network.get_weights()
        # Modify a weight in the returned copy
        original_weights[0][0, 0] += 100 
        # Check if the network's internal weights are unchanged
        assert not np.isclose(sample_network.weights[0][0, 0], original_weights[0][0, 0])
        assert np.allclose(sample_network.weights[0], original_weights[0] - np.array([[100,0,0],[0,0,0],[0,0,0],[0,0,0]])) # Adjusted for change

    def test_get_biases_returns_deep_copy(self, sample_network):
        original_biases = sample_network.get_biases()
        # Modify a bias in the returned copy
        original_biases[0][0] += 100
        # Check if the network's internal biases are unchanged
        assert not np.isclose(sample_network.biases[0][0], original_biases[0][0])
        assert np.allclose(sample_network.biases[0], original_biases[0] - np.array([100,0,0,0])) # Adjusted for change

    def test_get_weights_returns_correct_values(self, sample_network):
        weights = sample_network.get_weights()
        assert len(weights) == len(sample_network.weights)
        for i in range(len(weights)):
            assert np.array_equal(weights[i], sample_network.weights[i])

    def test_get_biases_returns_correct_values(self, sample_network):
        biases = sample_network.get_biases()
        assert len(biases) == len(sample_network.biases)
        for i in range(len(biases)):
            assert np.array_equal(biases[i], sample_network.biases[i])

    def test_set_weights_correctly_sets_values(self, sample_network):
        new_w1 = np.random.randn(*sample_network.weights[0].shape)
        new_w2 = np.random.randn(*sample_network.weights[1].shape)
        new_w3 = np.random.randn(*sample_network.weights[2].shape)
        new_weights = [new_w1, new_w2, new_w3]
        
        sample_network.set_weights(new_weights)
        
        retrieved_weights = sample_network.get_weights()
        for i in range(len(new_weights)):
            assert np.array_equal(retrieved_weights[i], new_weights[i])
            # Ensure deep copy
            new_weights[i][0,0] += 100
            assert not np.isclose(retrieved_weights[i][0,0], new_weights[i][0,0])

    def test_set_weights_type_error_not_list(self, sample_network):
        with pytest.raises(TypeError, match="new_weights must be a list of numpy arrays."):
            sample_network.set_weights(np.array([]))

    def test_set_weights_type_error_contains_non_ndarray(self, sample_network):
        new_weights = [sample_network.weights[0], sample_network.weights[1], "not_an_array"]
        with pytest.raises(TypeError, match="New weight at index 2 is not a numpy array."):
            sample_network.set_weights(new_weights)

    def test_set_weights_value_error_length_mismatch(self, sample_network):
        # Pass fewer weights than expected
        with pytest.raises(ValueError, match=f"Number of new weight matrices \\({len(sample_network.weights) - 1}\\) must match current network layers \\({len(sample_network.weights)}\\)."):
            sample_network.set_weights(sample_network.weights[:-1])

    def test_set_weights_value_error_shape_mismatch(self, sample_network):
        incorrect_shape_w = np.random.randn(2, 2) # Incorrect shape
        new_weights = [incorrect_shape_w] + sample_network.weights[1:]
        with pytest.raises(ValueError, match=f"Shape mismatch for weight matrix at layer 0: expected {sample_network.weights[0].shape}, got {incorrect_shape_w.shape}".replace("(", "\\(").replace(")", "\\)")):
            sample_network.set_weights(new_weights)

    def test_set_biases_correctly_sets_values(self, sample_network):
        new_b1 = np.random.randn(*sample_network.biases[0].shape)
        new_b2 = np.random.randn(*sample_network.biases[1].shape)
        new_b3 = np.random.randn(*sample_network.biases[2].shape)
        new_biases = [new_b1, new_b2, new_b3]
        
        sample_network.set_biases(new_biases)
        
        retrieved_biases = sample_network.get_biases()
        for i in range(len(new_biases)):
            assert np.array_equal(retrieved_biases[i], new_biases[i])
            # Ensure deep copy
            new_biases[i][0] += 100
            assert not np.isclose(retrieved_biases[i][0], new_biases[i][0])

    def test_set_biases_type_error_not_list(self, sample_network):
        with pytest.raises(TypeError, match="new_biases must be a list of numpy arrays."):
            sample_network.set_biases(np.array([]))

    def test_set_biases_type_error_contains_non_ndarray(self, sample_network):
        new_biases = [sample_network.biases[0], sample_network.biases[1], "not_an_array"]
        with pytest.raises(TypeError, match="New bias at index 2 is not a numpy array."):
            sample_network.set_biases(new_biases)

    def test_set_biases_value_error_length_mismatch(self, sample_network):
        # Pass fewer biases than expected
        with pytest.raises(ValueError, match=f"Number of new bias vectors \\({len(sample_network.biases) - 1}\\) must match current network layers \\({len(sample_network.biases)}\\)."):
            sample_network.set_biases(sample_network.biases[:-1])

    def test_set_biases_value_error_shape_mismatch(self, sample_network):
        incorrect_shape_b = np.random.randn(2,) # Incorrect shape
        new_biases = [incorrect_shape_b] + sample_network.biases[1:]
        with pytest.raises(ValueError, match=f"Shape mismatch for bias vector at layer 0: expected {sample_network.biases[0].shape}, got {incorrect_shape_b.shape}".replace("(", "\\(").replace(")", "\\)")):
            sample_network.set_biases(new_biases)

    def test_clone_creates_independent_copy(self, sample_network):
        cloned_network = sample_network.clone()

        # Ensure it's a new instance
        assert cloned_network is not sample_network

        # Modify original network's weights
        sample_network.weights[0][0, 0] += 100

        # Ensure cloned network's weights are unchanged
        assert not np.isclose(cloned_network.weights[0][0, 0], sample_network.weights[0][0, 0])

    def test_clone_has_identical_architecture_and_parameters(self, sample_network):
        cloned_network = sample_network.clone()

        assert cloned_network.input_size == sample_network.input_size
        assert cloned_network.output_size == sample_network.output_size
        assert cloned_network.hidden_layer_sizes == sample_network.hidden_layer_sizes

        # Check weights
        assert len(cloned_network.weights) == len(sample_network.weights)
        for i in range(len(cloned_network.weights)):
            assert np.array_equal(cloned_network.weights[i], sample_network.weights[i])
            # Ensure deep copy
            assert cloned_network.weights[i] is not sample_network.weights[i]

        # Check biases
        assert len(cloned_network.biases) == len(sample_network.biases)
        for i in range(len(cloned_network.biases)):
            assert np.array_equal(cloned_network.biases[i], sample_network.biases[i])
            # Ensure deep copy
            assert cloned_network.biases[i] is not sample_network.biases[i]


class TestNetworkUpdateOutputTopology:
    # Test partitions for update_output_topology():
    # 1. Invalid Input:
    #    - new_output_size is non-positive.
    #    - new_output_size is non-integer.
    # 2. No Change:
    #    - new_output_size is the same as current output_size.
    # 3. Smaller Output Size (Truncation):
    #    - new_output_size < current output_size.
    #    - Verify weights and biases are truncated correctly.
    #    - Verify other layers are unchanged.
    #    - Verify self.output_size is updated.
    # 4. Larger Output Size (Expansion):
    #    - new_output_size > current output_size.
    #    - Verify weights and biases are expanded correctly.
    #    - Verify new weights are He-initialized.
    #    - Verify new biases are zero-initialized.
    #    - Verify other layers are unchanged.
    #    - Verify self.output_size is updated.

    @pytest.fixture
    def initial_network(self):
        # A network with 2 inputs, 2 hidden layers (3, 4 neurons), and 5 outputs
        # This allows testing the last layer (output layer) specifically
        input_size = 2
        output_size = 5
        hidden_layer_sizes = [3, 4]
        return Network(input_size, output_size, hidden_layer_sizes, random_seed=42)

    def test_update_output_topology_invalid_input_type(self, initial_network):
        # Covers: Invalid Input - new_output_size is non-integer.
        with pytest.raises(TypeError, match="new_output_size must be a positive integer."):
            initial_network.update_output_topology(5.5)
        with pytest.raises(TypeError, match="new_output_size must be a positive integer."):
            initial_network.update_output_topology("5")

    def test_update_output_topology_invalid_input_value(self, initial_network):
        # Covers: Invalid Input - new_output_size is non-positive.
        with pytest.raises(ValueError, match="new_output_size must be a positive integer."):
            initial_network.update_output_topology(0)
        with pytest.raises(ValueError, match="new_output_size must be a positive integer."):
            initial_network.update_output_topology(-1)

    def test_update_output_topology_no_change(self, initial_network):
        # Covers: No Change - new_output_size is the same as current output_size.
        original_weights = initial_network.get_weights()
        original_biases = initial_network.get_biases()
        original_output_size = initial_network.output_size

        initial_network.update_output_topology(original_output_size)

        assert initial_network.output_size == original_output_size
        # Ensure weights and biases are exactly the same (no deep copy, just identity check)
        assert len(initial_network.weights) == len(original_weights)
        assert len(initial_network.biases) == len(original_biases)
        for i in range(len(original_weights)):
            assert np.array_equal(initial_network.weights[i], original_weights[i])
            assert np.array_equal(initial_network.biases[i], original_biases[i])

    def test_update_output_topology_smaller_output_size(self, initial_network):
        # Covers: Smaller Output Size (Truncation)
        old_output_size = initial_network.output_size # 5
        new_output_size = 3

        # Store original last layer parameters before update
        original_last_layer_weights = copy.deepcopy(initial_network.weights[-1])
        original_last_layer_biases = copy.deepcopy(initial_network.biases[-1])

        # Store original parameters of other layers to ensure they are unchanged
        original_other_weights = [copy.deepcopy(w) for w in initial_network.weights[:-1]]
        original_other_biases = [copy.deepcopy(b) for b in initial_network.biases[:-1]]

        initial_network.update_output_topology(new_output_size)

        assert initial_network.output_size == new_output_size

        # Verify weights and biases are truncated correctly
        assert initial_network.weights[-1].shape == (new_output_size, original_last_layer_weights.shape[1])
        assert initial_network.biases[-1].shape == (new_output_size,)

        # Check that the truncated parts match the original
        assert np.array_equal(initial_network.weights[-1], original_last_layer_weights[:new_output_size, :])
        assert np.array_equal(initial_network.biases[-1], original_last_layer_biases[:new_output_size])

        # Verify other layers are unchanged
        for i in range(len(original_other_weights)):
            assert np.array_equal(initial_network.weights[i], original_other_weights[i])
            assert np.array_equal(initial_network.biases[i], original_other_biases[i])


    def test_update_output_topology_larger_output_size(self, initial_network):
        # Covers: Larger Output Size (Expansion)
        old_output_size = initial_network.output_size # 5
        new_output_size = 7

        # Store original last layer parameters before update
        original_last_layer_weights = copy.deepcopy(initial_network.weights[-1])
        original_last_layer_biases = copy.deepcopy(initial_network.biases[-1])

        # Store original parameters of other layers to ensure they are unchanged
        original_other_weights = [copy.deepcopy(w) for w in initial_network.weights[:-1]]
        original_other_biases = [copy.deepcopy(b) for b in initial_network.biases[:-1]]

        initial_network.update_output_topology(new_output_size)

        assert initial_network.output_size == new_output_size

        # Verify weights and biases are expanded correctly
        assert initial_network.weights[-1].shape == (new_output_size, original_last_layer_weights.shape[1])
        assert initial_network.biases[-1].shape == (new_output_size,)

        # Check that the original parts of weights and biases are preserved
        assert np.array_equal(initial_network.weights[-1][:old_output_size, :], original_last_layer_weights)
        assert np.array_equal(initial_network.biases[-1][:old_output_size], original_last_layer_biases)

        # Verify new weights are He-initialized
        prev_layer_neurons = original_last_layer_weights.shape[1]
        expected_std_dev = np.sqrt(2.0 / prev_layer_neurons)
        newly_added_weights = initial_network.weights[-1][old_output_size:, :]
        
        # Statistical checks for He initialization
        # With only 8 samples (2 rows × 4 columns), sample statistics can deviate significantly from theoretical values
        assert np.isclose(np.mean(newly_added_weights), 0.0, atol=0.3) # Increased tolerance for small sample size
        assert np.isclose(np.std(newly_added_weights), expected_std_dev, atol=0.4) # Increased tolerance for small sample size

        # Verify new biases are zero-initialized
        newly_added_biases = initial_network.biases[-1][old_output_size:]
        assert np.allclose(newly_added_biases, 0.0)

        # Verify other layers are unchanged
        for i in range(len(original_other_weights)):
            assert np.array_equal(initial_network.weights[i], original_other_weights[i])
            assert np.array_equal(initial_network.biases[i], original_other_biases[i])
