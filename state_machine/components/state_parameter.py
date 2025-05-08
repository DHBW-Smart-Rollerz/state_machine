import threading
import time

import yasmin
from rclpy.parameter import Parameter
from smarty_utils.enums import Nodes


class GenericStateParameter:
    """Defines a generic state parameter for the state machine."""

    def __init__(self, name: str, value: any, type_: any):
        """
        Initialize the state parameter.

        Arguments:
            name -- Name of the parameter
            value -- Value of the parameter
        """
        self.name = name
        self.type_ = type_
        self._value = value

        self.notify()

    @property
    def value(self):
        """Get the value of the parameter."""
        return self._value

    @value.setter
    def value(self, value: any):
        """Set the value of the parameter."""
        if value is None:
            return
        try:
            if not isinstance(value, self.type_):
                raise RuntimeError(f"Value must be of type {self.type_}")
        except TypeError:
            # yasmin.YASMIN_LOG_WARN(f"Type not checked.")
            pass
        if self.value != value:
            self._value = value
            self.notify()

    def notify(self) -> None:
        """Notify the subscribers about the parameter change."""
        raise NotImplementedError("notify() not implemented")

    def __repr__(self):
        """String representation of the state parameter."""
        return f"{self.name}: {self.value}"


class StateParameter(GenericStateParameter):
    """State parameter without notification."""

    def __init__(
        self,
        name: str,
        value: any,
        type_: any,
    ):
        """
        Initialize the state parameter.

        Arguments:
            name -- Name of the parameter
            value -- Value of the parameter
            type_ -- Type of the parameter
        """
        super().__init__(name, value, type_)

    def notify(self) -> None:
        """Notify the subscribers about the parameter change."""
        pass


class CallbackStateParameter(GenericStateParameter):
    """Defines a state parameter of the state machine which is set by the callback."""

    def __init__(
        self,
        name: str,
        value: any,
        type_: any,
        callback: callable,
    ):
        """
        Initialize the state parameter.

        Arguments:
            name -- Name of the parameter
            value -- Value of the parameter
            type_ -- Type of the parameter
            callback -- Callback function to be called when the parameter changes
        """
        self.callback = callback
        super().__init__(name, value, type_)

    @property
    def callback(self):
        """Get the callback function."""
        return self._callback

    @callback.setter
    def callback(self, callback: callable):
        """Set the callback function."""
        if not callable(callback):
            raise TypeError("Callback must be callable")
        self._callback = callback

    def notify(self) -> None:
        """Notify the subscribers about the parameter change."""
        assert self.callback, "Callback is not set"
        self.callback(self.value)


class TopicStateParameter(GenericStateParameter):
    """Defines a state parameter for the state machine."""

    def __init__(
        self,
        name: str,
        value: any,
        type_: any,
        publisher_fun: callable,
    ):
        """
        Initialize the state parameter.

        Arguments:
            name -- Name of the parameter
            value -- Value of the parameter
        """
        self.publisher_fun = publisher_fun
        self._thread = threading.Thread(None, self.publish_thread)
        super().__init__(name, value, type_)

    @property
    def publisher_fun(self):
        """Get the publisher."""
        return self._publisher

    @publisher_fun.setter
    def publisher_fun(self, publisher_fun: callable):
        """Set the publisher."""
        self._publisher = publisher_fun

    def notify(self) -> None:
        """Notify the subscribers about the parameter change."""
        if self._thread.is_alive():
            return
        self._thread.start()

    def publish_thread(self):
        """Publish the parameter in a separate thread."""
        assert self.publisher_fun, "Publisher function is not set"
        while self._thread.is_alive():
            if self.publisher_fun:
                self.publisher_fun(self.value)
                last_time = time.time()
            else:
                yasmin.YASMIN_LOG_WARN("Publisher function is not set")
            time.sleep(1 / 30)


class ParameterStateParameter(GenericStateParameter):
    """Defines a ros2 param based state parameter for the state machine."""

    def __init__(
        self,
        name: str,
        value: any,
        type_: any,
        nodes: list[Nodes],
        client_setter_fun: callable,
    ):
        """
        Initialize the state parameter.

        Arguments:
            name -- _name_ of the parameter
            value -- _value_ of the parameter
            type_ -- _type_ of the parameter
            nodes -- _nodes_ to set the parameter
            client_setter_fun -- _client setter function_ to set the parameter
        """
        self.nodes = nodes
        self.client_setter_fun = client_setter_fun
        super().__init__(name, value, type_)

    @property
    def nodes(self):
        """Get the nodes."""
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: list[Nodes]):
        """Set the nodes."""
        if not isinstance(nodes, list):
            raise TypeError("Nodes must be a list")
        self._nodes = nodes

    def notify(self):
        """Notify the subscribers about the parameter change."""
        assert self.nodes, "Nodes are not set"
        assert self.client_setter_fun, "Client setter function is not set"
        for node in self.nodes:
            type2ParemeterType = {
                int: Parameter.Type.INTEGER,
                float: Parameter.Type.DOUBLE,
                str: Parameter.Type.STRING,
                bool: Parameter.Type.BOOL,
            }
            assert self.type_ in type2ParemeterType, f"Type {self.type_} not supported"
            param = Parameter(self.name, type2ParemeterType[self.type_], self.value)
            self.client_setter_fun(node, param)
