import numpy as np
import copy

class Network:
    '''
    Represents a neural network used to compute muscle outputs from sensor inputs.
    The network consists of multiple layers, each with a weight matrix and a bias vector.
    '''
    def __init__(self, input_size: int, output_size: int, hidden_layer_sizes: list[int], weights: list[np.ndarray] = None, biases: list[np.ndarray] = None, random_seed: int = None):
        '''
        Initializes the neural network with specified architecture, or with provided weights and biases.

        Args:
            input_size (int): The number of input neurons.
            output_size (int): The number of output neurons.
            hidden_layer_sizes (list[int]): A list of integers, where each integer
                                            represents the number of neurons in a hidden layer.
            weights (list[np.ndarray], optional): A list of numpy arrays representing the weight
                                                  matrices for each layer. If provided, biases must also be provided.
                                                  Used for cloning or loading a network.
            biases (list[np.ndarray], optional): A list of numpy arrays representing the bias
                                                 vectors for each layer. If provided, weights must also be provided.
                                                 Used for cloning or loading a network.
            random_seed (int, optional): Seed for the random number generator used in weight initialization.

        Raises:
            ValueError: If input sizes are non-positive, if weights/biases are provided but
                        do not match the expected architecture, or if shapes are inconsistent.
            TypeError: If weights or biases are not numpy arrays when provided.
        '''
        if input_size <= 0 or output_size <= 0:
            raise ValueError("Input and output sizes must be positive integers.")
        if not all(isinstance(s, int) and s > 0 for s in hidden_layer_sizes):
            raise ValueError("Hidden layer sizes must be positive integers.")

        self.input_size = input_size
        self.output_size = output_size
        self.hidden_layer_sizes = hidden_layer_sizes
        self._rng = np.random.default_rng(random_seed)

        if (weights is not None and biases is None) or (weights is None and biases is not None):
            raise ValueError("Both weights and biases must be provided together, or neither.")

        if weights is not None and biases is not None:
            # Initialize with provided weights and biases (e.g., for cloning)
            if not isinstance(weights, list) or not isinstance(biases, list):
                raise TypeError("Weights and biases must be lists of numpy arrays.")
            if len(weights) != len(biases):
                raise ValueError("Number of weight matrices must match number of bias vectors.")

            # Calculate expected layer sizes for validation
            expected_layer_sizes = [input_size] + hidden_layer_sizes + [output_size]
            if len(weights) != len(expected_layer_sizes) - 1:
                raise ValueError(f"Provided weights/biases (layers: {len(weights)}) do not match the number of layers implied by architecture ({len(expected_layer_sizes) - 1}).")

            self.weights = []
            self.biases = []
            for i in range(len(weights)):
                prev_size_expected = expected_layer_sizes[i]
                current_size_expected = expected_layer_sizes[i+1]

                w = weights[i]
                b = biases[i]

                if not isinstance(w, np.ndarray):
                    raise TypeError(f"Provided weight at index {i} is not a numpy array.")
                if not isinstance(b, np.ndarray):
                    raise TypeError(f"Provided bias at index {i} is not a numpy array.")
                
                # Check for shape consistency with the expected architecture
                if w.shape != (current_size_expected, prev_size_expected):
                    raise ValueError(f"Provided weight matrix at layer {i} has incorrect shape. Expected {(current_size_expected, prev_size_expected)}, got {w.shape}.")
                if b.shape != (current_size_expected,):
                    raise ValueError(f"Provided bias vector at layer {i} has incorrect shape. Expected {(current_size_expected,)}, got {b.shape}.")
                
                self.weights.append(copy.deepcopy(w))
                self.biases.append(copy.deepcopy(b))

        else:
            # Generate weights and biases based on architecture parameters
            self.weights = []
            self.biases = []

            layer_sizes = [input_size] + hidden_layer_sizes + [output_size]

            for i in range(len(layer_sizes) - 1):
                prev_size = layer_sizes[i]
                current_size = layer_sizes[i+1]

                # Weights: (current_size, prev_size)
                # He initialization: * np.sqrt(2.0 / prev_size)
                weight_matrix = self._rng.normal(loc=0.0, scale=1.0, size=(current_size, prev_size)) * np.sqrt(2.0 / prev_size)
                self.weights.append(weight_matrix)

                # Biases: (current_size,)
                bias_vector = np.zeros((current_size,))
                self.biases.append(bias_vector)

    def predict(self, sensor_inputs: np.ndarray) -> np.ndarray:
        '''
        Performs a forward pass through the neural network to predict muscle outputs.

        Args:
            sensor_inputs (np.ndarray): A 1D numpy array representing the sensor readings.
                                        The size must match the input size of the first layer.

        Returns:
            np.ndarray: A 1D numpy array representing the muscle outputs,
                        with values between 0 and 1 (due to sigmoid activation).

        Raises:
            TypeError: If sensor_inputs is not a numpy array.
            ValueError: If sensor_inputs is not 1D or its size mismatches the expected input.
        '''
        if not isinstance(sensor_inputs, np.ndarray):
            raise TypeError("Sensor inputs must be a numpy array.")
        if sensor_inputs.ndim != 1:
            raise ValueError("Sensor inputs must be a 1D numpy array.")

        # Check input size against the first layer's expected input size
        # The second dimension of the first weight matrix (weights[0].shape[1])
        # represents the expected number of inputs for the first layer.
        if sensor_inputs.shape[0] != self.weights[0].shape[1]:
            raise ValueError(f"Input size mismatch: expected {self.weights[0].shape[1]} inputs, got {sensor_inputs.shape[0]}.")

        # Start with the input layer activations
        activations = sensor_inputs

        # Iterate through layers, applying weights, biases, and activation functions
        for i in range(len(self.weights)):
            weights = self.weights[i]
            biases = self.biases[i]

            # Calculate weighted sum + bias (Z)
            # np.dot(weights, activations) performs matrix-vector multiplication
            # where weights is (output_size, input_size) and activations is (input_size,)
            # The result will be (output_size,)
            z = np.dot(weights, activations) + biases

            # Apply activation function
            if i == len(self.weights) - 1:
                # Output layer uses sigmoid activation
                activations = 1 / (1 + np.exp(-z))
            else:
                # Hidden layers use tanh activation
                activations = np.tanh(z)
        
        return activations

    def get_weights(self) -> list[np.ndarray]:
        '''
        Returns a deep copy of the network's weight matrices.
        '''
        return copy.deepcopy(self.weights)

    def get_biases(self) -> list[np.ndarray]:
        '''
        Returns a deep copy of the network's bias vectors.
        '''
        return copy.deepcopy(self.biases)

    def set_weights(self, new_weights: list[np.ndarray]):
        '''
        Sets the network's weight matrices. Performs deep copy and shape validation.

        Args:
            new_weights (list[np.ndarray]): A list of numpy arrays representing the new weight matrices.

        Raises:
            TypeError: If new_weights is not a list or contains non-numpy arrays.
            ValueError: If the number of weight matrices or their shapes do not match the current network.
        '''
        if not isinstance(new_weights, list):
            raise TypeError("new_weights must be a list of numpy arrays.")
        if len(new_weights) != len(self.weights):
            raise ValueError(f"Number of new weight matrices ({len(new_weights)}) must match current network layers ({len(self.weights)}).")
        
        for i, w in enumerate(new_weights):
            if not isinstance(w, np.ndarray):
                raise TypeError(f"New weight at index {i} is not a numpy array.")
            if w.shape != self.weights[i].shape:
                raise ValueError(f"Shape mismatch for weight matrix at layer {i}: expected {self.weights[i].shape}, got {w.shape}.")
        
        self.weights = copy.deepcopy(new_weights)

    def set_biases(self, new_biases: list[np.ndarray]):
        '''
        Sets the network's bias vectors. Performs deep copy and shape validation.

        Args:
            new_biases (list[np.ndarray]): A list of numpy arrays representing the new bias vectors.

        Raises:
            TypeError: If new_biases is not a list or contains non-numpy arrays.
            ValueError: If the number of bias vectors or their shapes do not match the current network.
        '''
        if not isinstance(new_biases, list):
            raise TypeError("new_biases must be a list of numpy arrays.")
        if len(new_biases) != len(self.biases):
            raise ValueError(f"Number of new bias vectors ({len(new_biases)}) must match current network layers ({len(self.biases)}).")
        
        for i, b in enumerate(new_biases):
            if not isinstance(b, np.ndarray):
                raise TypeError(f"New bias at index {i} is not a numpy array.")
            if b.shape != self.biases[i].shape:
                raise ValueError(f"Shape mismatch for bias vector at layer {i}: expected {self.biases[i].shape}, got {b.shape}.")
        
        self.biases = copy.deepcopy(new_biases)

    def clone(self):
        '''
        Creates and returns a deep copy of the current neural network instance.
        '''
        return Network(
            self.input_size,
            self.output_size,
            self.hidden_layer_sizes,
            weights=copy.deepcopy(self.weights),
            biases=copy.deepcopy(self.biases)
        )

    def update_input_topology(self, new_input_size: int):
        '''
        Updates the input topology of the network, re-initializing the weights and biases
        for the first layer to match the new input size.

        Args:
            new_input_size (int): The new number of input neurons.

        Raises:
            ValueError: If new_input_size is not a positive integer.
        '''
        if not isinstance(new_input_size, int) or new_input_size <= 0:
            raise ValueError("new_input_size must be a positive integer.")

        old_input_size = self.weights[0].shape[1]
        if new_input_size == old_input_size:
            return # No change needed

        self.input_size = new_input_size

        # The first layer connects input_size to the first hidden layer (or output layer if no hidden layers)
        # Weights[0] shape: (num_neurons_in_first_hidden_layer, old_input_size)
        # Biases[0] shape: (num_neurons_in_first_hidden_layer,)

        first_layer_output_neurons = self.weights[0].shape[0]

        if new_input_size < old_input_size:
            # Truncate weights for the first layer
            self.weights[0] = self.weights[0][:, :new_input_size]
        elif new_input_size > old_input_size:
            # Expand weights for the first layer with new random weights (He initialization)
            num_new_inputs = new_input_size - old_input_size
            # He initialization: * np.sqrt(2.0 / prev_size), where prev_size is new_input_size
            new_weight_cols = self._rng.normal(loc=0.0, scale=1.0, size=(first_layer_output_neurons, num_new_inputs)) * np.sqrt(2.0 / new_input_size)
            self.weights[0] = np.concatenate((self.weights[0], new_weight_cols), axis=1)
        
        # Biases for the first layer (self.biases[0]) are not affected by input size changes,
        # as they correspond to the number of neurons in the *next* layer, which remains constant.
        # No change needed for self.biases[0] or any subsequent weights/biases.
    def update_output_topology(self, new_output_size: int):
        '''
        Updates the output topology of the network, adjusting the weights and biases
        for the last layer to match the new output size.

        Args:
            new_output_size (int): The new number of output neurons.

        Raises:
            ValueError: If new_output_size is not a positive integer.
            TypeError: If new_output_size is not an integer.
        '''
        if not isinstance(new_output_size, int):
            raise TypeError("new_output_size must be a positive integer.")
        if new_output_size <= 0:
            raise ValueError("new_output_size must be a positive integer.")

        if new_output_size == self.output_size:
            return # No change needed

        # Get current last layer dimensions
        # The last weight matrix connects the last hidden layer (or input layer if no hidden layers)
        # to the output layer.
        # Its shape is (current_output_size, size_of_previous_layer).
        current_output_size = self.weights[-1].shape[0]
        last_hidden_layer_size = self.weights[-1].shape[1]

        # Update self.output_size
        self.output_size = new_output_size

        # Adjust the shape of the LAST weight matrix
        if new_output_size < current_output_size:
            # Truncate weights for the last layer
            self.weights[-1] = self.weights[-1][:new_output_size, :]
        elif new_output_size > current_output_size:
            # Expand weights for the last layer with new random weights (He initialization)
            num_new_rows = new_output_size - current_output_size
            # He initialization: * np.sqrt(2.0 / prev_size), where prev_size is last_hidden_layer_size
            new_weight_rows = self._rng.normal(loc=0.0, scale=1.0, size=(num_new_rows, last_hidden_layer_size)) * np.sqrt(2.0 / last_hidden_layer_size)
            self.weights[-1] = np.concatenate((self.weights[-1], new_weight_rows), axis=0)

        # Adjust the shape of the LAST bias vector
        if new_output_size < current_output_size:
            # Truncate biases for the last layer
            self.biases[-1] = self.biases[-1][:new_output_size]
        elif new_output_size > current_output_size:
            # Expand biases for the last layer with new zero-initialized biases
            num_new_elements = new_output_size - current_output_size
            new_bias_elements = np.zeros((num_new_elements,))
            self.biases[-1] = np.concatenate((self.biases[-1], new_bias_elements), axis=0)
