import numpy as np

class Joint:
    '''
    Represents a mass point in the 2D physics simulation.
    
    Attributes:
        position (np.ndarray): The (x, y) coordinates of the joint.
        velocity (np.ndarray): The (vx, vy) components of the joint's velocity.
        mass (float): The mass of the joint.
    '''
    def __init__(self, x: float, y: float, mass: float, vx: float = 0.0, vy: float = 0.0, ax: float = 0.0, ay: float = 0.0, fixed: bool = False):
        '''
        Initializes a new Joint instance.

        Args:
            x (float): Initial x-coordinate of the joint.
            y (float): Initial y-coordinate of the joint.
            mass (float): The mass of the joint. Must be non-negative.
            vx (float): Initial x-component of the velocity. Defaults to 0.0.
            vy (float): Initial y-component of the velocity. Defaults to 0.0.
            ax (float): Initial x-component of the acceleration. Defaults to 0.0.
            ay (float): Initial y-component of the acceleration. Defaults to 0.0.
            fixed (bool): If True, the joint's position is fixed and does not update. Defaults to False.
        '''
        if not isinstance(mass, (int, float)) or mass < 0:
            raise ValueError("Mass cannot be negative.")

        self.position = np.array([x, y], dtype=float)
        self.previous_position = np.copy(self.position)
        self.velocity = np.array([vx, vy], dtype=float)
        self.acceleration = np.array([ax, ay], dtype=float)
        self.mass = float(mass)
        self.fixed = fixed
    @property
    def x(self):
        return self.position[0]

    @x.setter
    def x(self, value):
        self.position[0] = value

    @property
    def y(self):
        return self.position[1]

    @y.setter
    def y(self, value):
        self.position[1] = value

    @property
    def vx(self):
        return self.velocity[0]

    @vx.setter
    def vx(self, value):
        self.velocity[0] = value

    @property
    def vy(self):
        return self.velocity[1]

    @vy.setter
    def vy(self, value):
        self.velocity[1] = value

    @property
    def ax(self):
        return self.acceleration[0]

    @ax.setter
    def ax(self, value):
        self.acceleration[0] = value

    @property
    def ay(self):
        return self.acceleration[1]

    @ay.setter
    def ay(self, value):
        self.acceleration[1] = value

    def __repr__(self):
        return f'Joint(x={self.position[0]}, y={self.position[1]}, mass={self.mass}, vx={self.velocity[0]}, vy={self.velocity[1]}, ax={self.acceleration[0]}, ay={self.acceleration[1]}, fixed={self.fixed})'