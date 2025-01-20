def SerializableClass(cls):
    """
    Class decorator that adds type hints and automatic type casting setters
    to class attributes based on their type hints.
    """
    original_annotations = getattr(cls, '__annotations__', {})
    
    for attr_name, attr_type in original_annotations.items():
        # Create the setter property name
        setter_name = f'set_{attr_name}'
        
        # Create the setter function
        def make_setter(name, expected_type):
            def setter(self, value):
                try:
                    # Attempt to cast the value to the expected type
                    casted_value = expected_type(value)
                    setattr(self, f'_{name}', casted_value)
                except (ValueError, TypeError) as e:
                    raise TypeError(f"Cannot cast value to {expected_type.__name__}: {str(e)}")
            return setter
        
        # Create the getter function
        def make_getter(name):
            def getter(self):
                return getattr(self, f'_{name}', None)
            return getter
            
        # Add private backing field
        setattr(cls, f'_{attr_name}', None)
        
        # Create property with getter and setter
        prop = property(
            make_getter(attr_name),
            make_setter(attr_name, attr_type)
        )
        
        # Set the property on the class
        setattr(cls, attr_name, prop)
    
    return cls